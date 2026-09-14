"""
Core PDF Operations - All-Purpose PDF Toolkit (iLovePDF offline equivalent)
Includes: Merge, Split, Compress, PDF to Images, Text/Image Extraction,
Rotate, Watermark, Password Protect, and Unlock.
"""

import io
import os
import pymupdf as fitz
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Union
from pypdf import PdfReader, PdfWriter, Transformation
from reportlab.pdfgen import canvas
from reportlab.lib import colors


def get_pdf_info(pdf_path: str) -> Dict[str, any]:
    """Get metadata, page count, and encryption info for a PDF."""
    reader = PdfReader(pdf_path)
    is_encrypted = reader.is_encrypted
    num_pages = 0
    title = ""
    if not is_encrypted:
        try:
            num_pages = len(reader.pages)
            title = reader.metadata.title if (reader.metadata and reader.metadata.title) else ""
        except Exception:
            pass
    return {
        "file_name": os.path.basename(pdf_path),
        "file_size_kb": round(os.path.getsize(pdf_path) / 1024, 2),
        "pages": num_pages,
        "is_encrypted": is_encrypted,
        "title": title or "N/A"
    }


def merge_pdfs(pdf_paths: List[str], output_path: str) -> str:
    """
    Merge multiple PDF files into a single PDF in the given sequence.
    """
    if not pdf_paths:
        raise ValueError("No PDF files provided to merge.")
    if len(pdf_paths) == 1:
        raise ValueError("Please provide at least 2 PDF files to merge.")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    writer = PdfWriter()

    for path in pdf_paths:
        reader = PdfReader(path)
        for page in reader.pages:
            writer.add_page(page)

    with open(output_path, "wb") as f_out:
        writer.write(f_out)

    return output_path


def parse_page_ranges(range_str: str, max_pages: int) -> List[int]:
    """
    Parse a range string like '1-3, 5, 8-10' into 0-indexed page indices.
    """
    indices = set()
    parts = range_str.replace(" ", "").split(",")
    for part in parts:
        if not part:
            continue
        if "-" in part:
            start_s, end_s = part.split("-", 1)
            start = max(1, int(start_s))
            end = min(max_pages, int(end_s))
            for p in range(start, end + 1):
                indices.add(p - 1)
        else:
            p = int(part)
            if 1 <= p <= max_pages:
                indices.add(p - 1)
    return sorted(list(indices))


def split_pdf(
    pdf_path: str,
    output_dir: str,
    split_mode: str = "all_pages",
    range_str: Optional[str] = None
) -> List[str]:
    """
    Split a PDF:
    - 'all_pages': Each page becomes a separate PDF (e.g. filename_page_1.pdf).
    - 'ranges': Extract pages defined in range_str (e.g. '1-3, 5') into a single or grouped PDF.
    - 'burst_ranges': Each range or comma group becomes a separate PDF.
    """
    os.makedirs(output_dir, exist_ok=True)
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_files = []

    if split_mode == "all_pages":
        for i, page in enumerate(reader.pages, start=1):
            writer = PdfWriter()
            writer.add_page(page)
            out_file = os.path.join(output_dir, f"{base_name}_page_{i:03d}.pdf")
            with open(out_file, "wb") as f:
                writer.write(f)
            output_files.append(out_file)

    elif split_mode == "ranges" and range_str:
        # Single output with extracted pages
        page_indices = parse_page_ranges(range_str, total_pages)
        if not page_indices:
            raise ValueError(f"No valid pages found in range '{range_str}' for {total_pages}-page PDF.")
        writer = PdfWriter()
        for idx in page_indices:
            writer.add_page(reader.pages[idx])
        out_file = os.path.join(output_dir, f"{base_name}_extracted.pdf")
        with open(out_file, "wb") as f:
            writer.write(f)
        output_files.append(out_file)

    elif split_mode == "burst_ranges" and range_str:
        # Each group in comma separated list becomes a PDF
        groups = [g.strip() for g in range_str.split(",") if g.strip()]
        for g_idx, grp in enumerate(groups, start=1):
            indices = parse_page_ranges(grp, total_pages)
            if not indices:
                continue
            writer = PdfWriter()
            for idx in indices:
                writer.add_page(reader.pages[idx])
            safe_grp = grp.replace("-", "_to_")
            out_file = os.path.join(output_dir, f"{base_name}_part{g_idx}_{safe_grp}.pdf")
            with open(out_file, "wb") as f:
                writer.write(f)
            output_files.append(out_file)

    return output_files


def compress_pdf(
    input_path: str,
    output_path: str,
    deflate_images: bool = True,
    image_quality: int = 60
) -> Dict[str, any]:
    """
    Compress PDF:
    - Compresses text & vector content streams
    - Cleans up duplicate objects
    - Optionally compresses / re-encodes embedded images using PyMuPDF and pypdf
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    initial_size = os.path.getsize(input_path)

    # Use PyMuPDF's built-in advanced garbage collection and compression
    doc = fitz.open(input_path)
    # garbage=4 strips unused objects, deflate=True compresses streams, clean=True sanitizes syntax
    doc.save(
        output_path,
        garbage=4,
        deflate=True,
        deflate_images=deflate_images,
        deflate_fonts=True,
        clean=True
    )
    doc.close()

    final_size = os.path.getsize(output_path)
    saved_bytes = max(0, initial_size - final_size)
    percent_saved = round((saved_bytes / initial_size) * 100, 1) if initial_size > 0 else 0

    return {
        "original_size_kb": round(initial_size / 1024, 2),
        "compressed_size_kb": round(final_size / 1024, 2),
        "saved_kb": round(saved_bytes / 1024, 2),
        "percent_reduction": percent_saved,
        "output_path": output_path
    }


def pdf_to_images(
    pdf_path: str,
    output_dir: str,
    dpi: int = 150,
    img_format: str = "png"
) -> List[str]:
    """
    Convert all pages of a PDF into high-res images (PNG or JPG).
    """
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    doc = fitz.open(pdf_path)
    output_images = []

    # Calculate zoom factor: standard PDF 72 DPI
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)

    for i, page in enumerate(doc, start=1):
        pix = page.get_pixmap(matrix=mat, alpha=False if img_format.lower() in ["jpg", "jpeg"] else True)
        out_path = os.path.join(output_dir, f"{base_name}_page_{i:03d}.{img_format.lower()}")
        pix.save(out_path)
        output_images.append(out_path)

    doc.close()
    return output_images


def extract_text_from_pdf(pdf_path: str, output_txt_path: Optional[str] = None) -> str:
    """
    Extract all readable text from a PDF file.
    """
    doc = fitz.open(pdf_path)
    text_chunks = []
    for i, page in enumerate(doc, start=1):
        page_text = page.get_text()
        text_chunks.append(f"--- PAGE {i} ---\n" + page_text.strip())
    doc.close()

    full_text = "\n\n".join(text_chunks)
    if output_txt_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_txt_path)), exist_ok=True)
        with open(output_txt_path, "w", encoding="utf-8") as f:
            f.write(full_text)

    return full_text


def extract_embedded_images(pdf_path: str, output_dir: str) -> List[str]:
    """
    Extract all embedded bitmap images from the PDF without recompression.
    """
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    doc = fitz.open(pdf_path)
    extracted = []
    image_count = 0

    for page_idx in range(len(doc)):
        page = doc[page_idx]
        image_list = page.get_images(full=True)
        for img_info in image_list:
            xref = img_info[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_count += 1
            out_file = os.path.join(output_dir, f"{base_name}_img_{image_count:03d}.{image_ext}")
            with open(out_file, "wb") as f:
                f.write(image_bytes)
            extracted.append(out_file)

    doc.close()
    return extracted


def rotate_pdf_pages(
    input_path: str,
    output_path: str,
    angle: int = 90,
    page_indices: Optional[List[int]] = None
) -> str:
    """
    Rotate PDF pages by 90, 180, or 270 degrees clockwise.
    """
    if angle not in (90, 180, 270):
        raise ValueError("Rotation angle must be 90, 180, or 270 degrees.")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for idx, page in enumerate(reader.pages):
        if page_indices is None or idx in page_indices:
            page.rotate(angle)
        writer.add_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path


def create_watermark_layer(
    width: float,
    height: float,
    watermark_text: str,
    font_size: int = 40,
    angle: float = 45,
    opacity: float = 0.25,
    text_color: Tuple[float, float, float] = (0.5, 0.5, 0.5)
) -> io.BytesIO:
    """Generate a single-page PDF containing a centered rotated watermark."""
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(width, height))
    can.saveState()
    can.setFillColorRGB(text_color[0], text_color[1], text_color[2], alpha=opacity)
    can.setFont("Helvetica-Bold", font_size)
    can.translate(width / 2.0, height / 2.0)
    can.rotate(angle)
    can.drawCentredString(0, 0, watermark_text)
    can.restoreState()
    can.save()
    packet.seek(0)
    return packet


def watermark_pdf(
    input_path: str,
    output_path: str,
    text: str,
    font_size: int = 45,
    angle: float = 45,
    opacity: float = 0.22
) -> str:
    """
    Apply a diagonal text watermark across every page of the PDF.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        box = page.mediabox
        width = float(box.width)
        height = float(box.height)

        wm_stream = create_watermark_layer(width, height, text, font_size, angle, opacity)
        wm_reader = PdfReader(wm_stream)
        wm_page = wm_reader.pages[0]

        page.merge_page(wm_page)
        writer.add_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path


def protect_pdf(
    input_path: str,
    output_path: str,
    user_password: str,
    owner_password: Optional[str] = None
) -> str:
    """
    Encrypt PDF with a password.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.encrypt(
        user_password=user_password,
        owner_password=owner_password or user_password,
        use_128bit=True
    )

    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path


def unlock_pdf(input_path: str, output_path: str, password: str) -> bool:
    """
    Remove password protection from an encrypted PDF.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    reader = PdfReader(input_path)

    if reader.is_encrypted:
        success = reader.decrypt(password)
        if not success:
            return False

    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)

    return True
