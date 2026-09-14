"""
Core file conversion utilities for PowerPoint (PPT/PPTX), Word (DOC/DOCX), and Images to PDF.
Optimized for high-speed bulk conversion of 100+ files using native Windows COM automation
with headless mode, alert suppression, and robust error recovery.
"""

import os
import sys
import shutil
import subprocess
import time
from pathlib import Path
from typing import List, Optional, Callable, Dict, Tuple
from PIL import Image


def is_powerpoint_available() -> bool:
    """Check if Microsoft PowerPoint is installed and accessible via COM."""
    if sys.platform != "win32":
        return False
    try:
        import win32com.client
        app = win32com.client.Dispatch("PowerPoint.Application")
        app.Quit()
        return True
    except Exception:
        return False


def is_word_available() -> bool:
    """Check if Microsoft Word is installed and accessible via COM."""
    if sys.platform != "win32":
        return False
    try:
        import win32com.client
        app = win32com.client.Dispatch("Word.Application")
        app.Quit()
        return True
    except Exception:
        return False


def is_libreoffice_available() -> Optional[str]:
    """Check if LibreOffice soffice command is available."""
    cmd = shutil.which("soffice")
    if cmd:
        return cmd
    
    common_paths = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    ]
    for p in common_paths:
        if os.path.isfile(p):
            return p
    return None


def convert_single_ppt_com(powerpoint_app, input_path: str, output_path: str) -> bool:
    """
    Convert a single PPT/PPTX file to PDF using an existing PowerPoint COM instance.
    Format type 32 corresponds to ppSaveAsPDF.
    """
    abs_input = os.path.abspath(input_path)
    abs_output = os.path.abspath(output_path)
    os.makedirs(os.path.dirname(abs_output), exist_ok=True)

    pres = None
    try:
        pres = powerpoint_app.Presentations.Open(
            abs_input,
            ReadOnly=1,
            Untitled=0,
            WithWindow=0
        )
        # 32 = ppSaveAsPDF
        pres.SaveAs(abs_output, 32)
        return True
    finally:
        if pres is not None:
            try:
                pres.Close()
            except Exception:
                pass


def convert_ppt_libreoffice(soffice_path: str, input_path: str, output_dir: str) -> bool:
    """Fallback conversion using LibreOffice headless command line."""
    try:
        os.makedirs(output_dir, exist_ok=True)
        res = subprocess.run(
            [soffice_path, "--headless", "--convert-to", "pdf", "--outdir", output_dir, input_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=120,
            check=True
        )
        return res.returncode == 0
    except Exception:
        return False


def bulk_convert_ppt_to_pdf(
    file_paths: List[str],
    output_dir: Optional[str] = None,
    progress_callback: Optional[Callable[[int, int, str, bool, Optional[str]], None]] = None,
    overwrite: bool = True
) -> Dict[str, any]:
    """
    Bulk convert a list of PPT / PPTX / PPS / PPSX files to PDF.
    
    Args:
        file_paths: List of paths to presentation files.
        output_dir: Destination folder. If None, saves alongside original files.
        progress_callback: Optional callback(current, total, filename, is_success, error_msg)
        overwrite: Whether to overwrite existing PDF files.
        
    Returns:
        Dictionary summary: {"total": int, "success": int, "failed": int, "results": list}
    """
    total = len(file_paths)
    results = []
    success_count = 0
    failed_count = 0

    if total == 0:
        return {"total": 0, "success": 0, "failed": 0, "results": []}

    has_com = False
    powerpoint = None

    if sys.platform == "win32":
        try:
            import win32com.client
            import pythoncom
            pythoncom.CoInitialize()
            powerpoint = win32com.client.Dispatch("PowerPoint.Application")
            has_com = True
        except Exception:
            powerpoint = None
            has_com = False

    soffice_path = is_libreoffice_available() if not has_com else None

    if not has_com and not soffice_path:
        raise RuntimeError(
            "Neither Microsoft PowerPoint nor LibreOffice was detected on this system. "
            "Please install Microsoft PowerPoint or LibreOffice to convert PPT/PPTX files."
        )

    try:
        for idx, input_path in enumerate(file_paths, start=1):
            file_name = os.path.basename(input_path)
            base_name = os.path.splitext(file_name)[0]
            
            if output_dir:
                out_path = os.path.join(output_dir, f"{base_name}.pdf")
            else:
                out_path = os.path.join(os.path.dirname(input_path), f"{base_name}.pdf")

            if not overwrite and os.path.exists(out_path):
                results.append({
                    "input": input_path,
                    "output": out_path,
                    "status": "skipped",
                    "error": "File already exists"
                })
                if progress_callback:
                    progress_callback(idx, total, file_name, True, "Skipped (already exists)")
                continue

            success = False
            err_msg = None

            if has_com and powerpoint:
                try:
                    success = convert_single_ppt_com(powerpoint, input_path, out_path)
                except Exception as ex:
                    err_msg = str(ex)
                    # Attempt to recover COM if PowerPoint crashed or hung
                    try:
                        powerpoint.Quit()
                    except Exception:
                        pass
                    try:
                        import win32com.client
                        powerpoint = win32com.client.Dispatch("PowerPoint.Application")
                    except Exception:
                        pass
            elif soffice_path:
                dest_dir = os.path.dirname(out_path)
                success = convert_ppt_libreoffice(soffice_path, input_path, dest_dir)
                if not success:
                    err_msg = "LibreOffice conversion failed"

            if success and os.path.exists(out_path) and os.path.getsize(out_path) > 0:
                success_count += 1
                results.append({"input": input_path, "output": out_path, "status": "success", "error": None})
                if progress_callback:
                    progress_callback(idx, total, file_name, True, None)
            else:
                failed_count += 1
                results.append({"input": input_path, "output": out_path, "status": "failed", "error": err_msg or "Unknown error"})
                if progress_callback:
                    progress_callback(idx, total, file_name, False, err_msg)

    finally:
        if powerpoint:
            try:
                powerpoint.Quit()
            except Exception:
                pass
        if sys.platform == "win32":
            try:
                import pythoncom
                pythoncom.CoUninitialize()
            except Exception:
                pass

    return {
        "total": total,
        "success": success_count,
        "failed": failed_count,
        "results": results
    }


def find_presentation_files(folder_path: str, recursive: bool = False) -> List[str]:
    """Find all presentation files (.ppt, .pptx, .pps, .ppsx) in folder."""
    valid_exts = {".ppt", ".pptx", ".pps", ".ppsx"}
    matched = []
    p = Path(folder_path)
    if not p.exists() or not p.is_dir():
        return matched

    if recursive:
        for file in p.rglob("*"):
            if file.is_file() and file.suffix.lower() in valid_exts and not file.name.startswith("~$"):
                matched.append(str(file.resolve()))
    else:
        for file in p.glob("*"):
            if file.is_file() and file.suffix.lower() in valid_exts and not file.name.startswith("~$"):
                matched.append(str(file.resolve()))

    return sorted(matched)


def bulk_convert_word_to_pdf(
    file_paths: List[str],
    output_dir: Optional[str] = None,
    progress_callback: Optional[Callable[[int, int, str, bool, Optional[str]], None]] = None,
    overwrite: bool = True
) -> Dict[str, any]:
    """Bulk convert Word (.doc, .docx) files to PDF using Word COM."""
    total = len(file_paths)
    results = []
    success_count = 0
    failed_count = 0

    if total == 0:
        return {"total": 0, "success": 0, "failed": 0, "results": []}

    import win32com.client
    import pythoncom
    pythoncom.CoInitialize()

    word = None
    try:
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0  # wdAlertsNone

        for idx, input_path in enumerate(file_paths, start=1):
            file_name = os.path.basename(input_path)
            base_name = os.path.splitext(file_name)[0]
            if output_dir:
                out_path = os.path.join(output_dir, f"{base_name}.pdf")
            else:
                out_path = os.path.join(os.path.dirname(input_path), f"{base_name}.pdf")

            if not overwrite and os.path.exists(out_path):
                if progress_callback:
                    progress_callback(idx, total, file_name, True, "Skipped")
                continue

            doc = None
            try:
                abs_in = os.path.abspath(input_path)
                abs_out = os.path.abspath(out_path)
                doc = word.Documents.Open(abs_in, ReadOnly=True, Visible=False)
                # 17 = wdExportFormatPDF
                doc.SaveAs(abs_out, FileFormat=17)
                success_count += 1
                results.append({"input": input_path, "output": out_path, "status": "success"})
                if progress_callback:
                    progress_callback(idx, total, file_name, True, None)
            except Exception as ex:
                failed_count += 1
                results.append({"input": input_path, "output": out_path, "status": "failed", "error": str(ex)})
                if progress_callback:
                    progress_callback(idx, total, file_name, False, str(ex))
            finally:
                if doc:
                    try:
                        doc.Close(SaveChanges=0)
                    except Exception:
                        pass
    finally:
        if word:
            try:
                word.Quit()
            except Exception:
                pass
        pythoncom.CoUninitialize()

    return {"total": total, "success": success_count, "failed": failed_count, "results": results}


def images_to_pdf(
    image_paths: List[str],
    output_pdf_path: str
) -> str:
    """
    Convert multiple images (PNG, JPG, WEBP, BMP, etc.) into a single merged PDF file.
    """
    if not image_paths:
        raise ValueError("No images provided for conversion.")

    os.makedirs(os.path.dirname(os.path.abspath(output_pdf_path)), exist_ok=True)
    images = []

    for img_path in image_paths:
        img = Image.open(img_path)
        if img.mode != "RGB":
            rgb_img = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "RGBA":
                rgb_img.paste(img, mask=img.split()[3])
            else:
                rgb_img.paste(img.convert("RGB"))
            img = rgb_img
        images.append(img)

    first = images[0]
    rest = images[1:] if len(images) > 1 else []
    first.save(output_pdf_path, save_all=True, append_images=rest, resolution=100.0)
    return output_pdf_path
