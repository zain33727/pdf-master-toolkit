# 📄 PDF Master Toolkit (iLovePDF Offline Suite)

A powerful, all-in-one Python toolkit for converting **100+ PowerPoint (PPT/PPTX) files to PDF in bulk**, plus a full offline suite of PDF utilities (Merge, Split, Compress, Images to PDF, PDF to Images, Watermark, Password Protect, and Text Extraction).

**100% Offline & Private:** No files are uploaded to any external servers. Everything runs locally on your PC at maximum native speed.

---

## 🚀 Quick Start (Choose Your Preferred Interface)

You have **3 ways** to use the toolkit:

### Option 1: Desktop GUI (Recommended for Everyday Use)
Double-click `run_desktop_gui.bat` or run:
```bash
python gui.py
```
- Select an entire folder with 100+ presentation files or individual files.
- Live progress bar, file count, and status logs.
- Click **"Open Output Folder"** to view your converted PDFs immediately.

### Option 2: Browser Web App (iLovePDF Offline Clone)
Double-click `run_web_app.bat` or run:
```bash
streamlit run app_web.py
```
- Modern browser interface inspired by iLovePDF.
- Drag & drop files, live previews, and one-click ZIP downloads.

### Option 3: Command Line (CLI)
Automate bulk tasks with PowerShell or CMD:
```bash
# Bulk convert an entire folder of 100+ PPT/PPTX files
python cli.py ppt2pdf "C:\Presentations" -o "C:\Converted_PDFs" --recursive

# Merge multiple PDFs into one
python cli.py merge report1.pdf report2.pdf report3.pdf -o merged_report.pdf

# Split a PDF by page ranges
python cli.py split document.pdf -o ./output --ranges "1-5, 8, 12-15"

# Compress and optimize PDF file size
python cli.py compress big_file.pdf -o compressed.pdf

# Export all pages of a PDF to high-res PNG images
python cli.py pdf2img presentation.pdf -o ./slides_png --dpi 200

# Combine images (JPG/PNG) into a single PDF
python cli.py img2pdf page1.jpg page2.png page3.webp -o combined.pdf

# Add custom diagonal watermark
python cli.py watermark document.pdf -o watermarked.pdf --text "CONFIDENTIAL"

# Password protect (encrypt) a PDF
python cli.py protect document.pdf -o protected.pdf --password "Secret123"

# Remove password (unlock) a PDF
python cli.py unlock protected.pdf -o unlocked.pdf --password "Secret123"

# Extract text from PDF
python cli.py text document.pdf -o extracted_text.txt
```

---

## ⚡ High-Speed Bulk Conversion (100+ Files)

Converting 100+ PowerPoint files is optimized specifically for Windows:
1. **Single Instance COM Automation:** Uses native Microsoft PowerPoint in headless background mode without opening 100 separate app instances, preventing system slowdowns.
2. **Alert Suppression:** Suppresses dialog popups (macro warnings, font replacements, repair dialogs) so the batch conversion runs continuously without pausing.
3. **Crash Recovery:** If a single corrupted PPT file causes an exception, it is logged and the engine automatically continues converting the remaining files.
4. **Subfolder Support:** Toggle `--recursive` to scan nested subdirectories and convert all presentations.

---

## 📦 What's Inside?

| Feature | Description |
| :--- | :--- |
| **📊 Bulk PPT to PDF** | Converts `.ppt`, `.pptx`, `.pps`, and `.ppsx` files with 100% layout and font fidelity. |
| **📝 Word to PDF** | Converts `.doc` and `.docx` files to PDF. |
| **📑 Merge PDFs** | Combines multiple PDFs into a single file with custom reordering. |
| **✂️ Split PDF** | Extracts custom page ranges (`1-5, 8-10`) or splits into individual pages. |
| **🗜️ Compress PDF** | Reduces PDF file size by stripping redundant objects and compressing image streams. |
| **🖼️ Images to PDF** | Combines JPG, PNG, WEBP, and BMP images into a clean PDF. |
| **📄 PDF to Images** | Exports each PDF page to high-res images (PNG/JPG at 72, 150, 200, 300 DPI). |
| **💧 Watermark** | Overlays rotated watermark text with custom opacity and font size. |
| **🔒 Protect & Unlock** | Applies 128-bit AES password encryption or removes protection from PDFs. |
| **🔍 Extract Content** | Extracts raw text to `.txt` or dumps all embedded photos and figures without recompression loss. |

---

## 🛠️ Requirements & Installation

If running on a new computer:
```bash
pip install -r requirements.txt
```

Dependencies:
- `pywin32` (PowerPoint & Word native COM automation on Windows)
- `pymupdf` (Ultra-fast PDF rendering and compression)
- `pypdf` (Merging, splitting, password protection, and metadata)
- `pillow` (Image processing)
- `reportlab` (Watermarking)
- `streamlit` (Web app UI)
