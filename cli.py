#!/usr/bin/env python3
"""
Command-Line Interface for All-in-One PDF Toolkit
Usage:
    python cli.py ppt2pdf "C:/path/to/presentations" -o "C:/path/to/output" --recursive
    python cli.py word2pdf "C:/path/to/docs" -o "C:/path/to/output"
    python cli.py merge file1.pdf file2.pdf file3.pdf -o merged.pdf
    python cli.py split input.pdf -o output_dir --ranges "1-3, 5-7"
    python cli.py compress input.pdf -o compressed.pdf
    python cli.py pdf2img input.pdf -o output_dir --dpi 200
    python cli.py img2pdf img1.png img2.jpg -o output.pdf
    python cli.py text input.pdf -o extracted.txt
    python cli.py watermark input.pdf -o watermarked.pdf --text "CONFIDENTIAL"
    python cli.py protect input.pdf -o protected.pdf --password "secret123"
    python cli.py unlock input.pdf -o unlocked.pdf --password "secret123"
"""

import sys
import os
import argparse
from pathlib import Path
from core import (
    bulk_convert_ppt_to_pdf,
    bulk_convert_word_to_pdf,
    find_presentation_files,
    images_to_pdf,
    merge_pdfs,
    split_pdf,
    compress_pdf,
    pdf_to_images,
    extract_text_from_pdf,
    extract_embedded_images,
    rotate_pdf_pages,
    watermark_pdf,
    protect_pdf,
    unlock_pdf,
    get_pdf_info
)


def print_banner():
    print("=" * 60)
    print("           PDF MASTER TOOLKIT (iLovePDF Offline)           ")
    print("=" * 60)


def handle_ppt2pdf(args):
    target = args.input
    output_dir = args.output
    recursive = args.recursive

    files = []
    if os.path.isfile(target):
        files = [target]
    elif os.path.isdir(target):
        print(f"[*] Scanning folder: {target} (recursive={recursive})...")
        files = find_presentation_files(target, recursive=recursive)
    else:
        print(f"[!] Error: Path '{target}' does not exist.")
        return

    if not files:
        print("[!] No PPT, PPTX, PPS, or PPSX files found.")
        return

    print(f"[+] Found {len(files)} presentation file(s) to convert.")
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        print(f"[+] Output directory: {output_dir}")
    else:
        print("[+] Output will be saved in each file's directory.")

    def progress(cur, total, name, success, msg):
        status = "OK" if success else "FAILED"
        extra = f" ({msg})" if msg else ""
        print(f"[{cur}/{total}] [{status}] {name}{extra}")

    print("\nStarting batch conversion...")
    summary = bulk_convert_ppt_to_pdf(
        files,
        output_dir=output_dir,
        progress_callback=progress,
        overwrite=args.overwrite
    )

    print("\n" + "-" * 50)
    print(f"Conversion Finished: {summary['success']} succeeded, {summary['failed']} failed.")
    print("-" * 50)


def handle_word2pdf(args):
    target = args.input
    output_dir = args.output
    files = []
    if os.path.isfile(target):
        files = [target]
    elif os.path.isdir(target):
        valid_exts = {".doc", ".docx"}
        p = Path(target)
        for f in p.glob("*"):
            if f.is_file() and f.suffix.lower() in valid_exts and not f.name.startswith("~$"):
                files.append(str(f.resolve()))
    else:
        print(f"[!] Error: Path '{target}' does not exist.")
        return

    if not files:
        print("[!] No Word documents found.")
        return

    print(f"[+] Converting {len(files)} Word document(s)...")

    def progress(cur, total, name, success, msg):
        status = "OK" if success else "FAILED"
        extra = f" ({msg})" if msg else ""
        print(f"[{cur}/{total}] [{status}] {name}{extra}")

    summary = bulk_convert_word_to_pdf(files, output_dir=output_dir, progress_callback=progress)
    print(f"[+] Finished: {summary['success']} succeeded, {summary['failed']} failed.")


def handle_merge(args):
    if len(args.inputs) < 2:
        print("[!] Please specify at least 2 PDF files to merge.")
        return
    print(f"[*] Merging {len(args.inputs)} PDF files into '{args.output}'...")
    out = merge_pdfs(args.inputs, args.output)
    print(f"[+] Successfully created merged PDF: {out}")


def handle_split(args):
    mode = "ranges" if args.ranges else "all_pages"
    print(f"[*] Splitting '{args.input}' into '{args.output}' (mode={mode})...")
    results = split_pdf(args.input, args.output, split_mode=mode, range_str=args.ranges)
    print(f"[+] Generated {len(results)} file(s).")


def handle_compress(args):
    print(f"[*] Compressing '{args.input}' -> '{args.output}'...")
    res = compress_pdf(args.input, args.output)
    print(f"[+] Original: {res['original_size_kb']} KB | Compressed: {res['compressed_size_kb']} KB")
    print(f"[+] Saved: {res['saved_kb']} KB ({res['percent_reduction']}%)")


def handle_pdf2img(args):
    print(f"[*] Converting pages of '{args.input}' to {args.format.upper()} ({args.dpi} DPI)...")
    images = pdf_to_images(args.input, args.output, dpi=args.dpi, img_format=args.format)
    print(f"[+] Exported {len(images)} page images to '{args.output}'")


def handle_img2pdf(args):
    print(f"[*] Combining {len(args.inputs)} image(s) into '{args.output}'...")
    images_to_pdf(args.inputs, args.output)
    print(f"[+] Successfully created PDF: {args.output}")


def handle_text(args):
    print(f"[*] Extracting text from '{args.input}'...")
    extract_text_from_pdf(args.input, output_txt_path=args.output)
    print(f"[+] Text saved to: {args.output}")


def handle_extract_images(args):
    print(f"[*] Extracting embedded images from '{args.input}'...")
    imgs = extract_embedded_images(args.input, args.output)
    print(f"[+] Extracted {len(imgs)} images to: {args.output}")


def handle_watermark(args):
    print(f"[*] Applying watermark '{args.text}' to '{args.input}'...")
    watermark_pdf(args.input, args.output, text=args.text, font_size=args.size, opacity=args.opacity)
    print(f"[+] Watermarked PDF saved to: {args.output}")


def handle_rotate(args):
    print(f"[*] Rotating '{args.input}' by {args.angle} degrees...")
    rotate_pdf_pages(args.input, args.output, angle=args.angle)
    print(f"[+] Rotated PDF saved to: {args.output}")


def handle_protect(args):
    print(f"[*] Encrypting '{args.input}'...")
    protect_pdf(args.input, args.output, user_password=args.password)
    print(f"[+] Protected PDF saved to: {args.output}")


def handle_unlock(args):
    print(f"[*] Decrypting '{args.input}'...")
    ok = unlock_pdf(args.input, args.output, password=args.password)
    if ok:
        print(f"[+] Unlocked PDF saved to: {args.output}")
    else:
        print("[!] Incorrect password or decryption failed.")


def handle_info(args):
    info = get_pdf_info(args.input)
    print("\n--- PDF Information ---")
    for k, v in info.items():
        print(f"{k:18s}: {v}")


def main():
    parser = argparse.ArgumentParser(description="PDF Master Toolkit - All-in-One Offline PDF Utilities")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # ppt2pdf
    p_ppt = subparsers.add_parser("ppt2pdf", help="Bulk convert PPT/PPTX to PDF")
    p_ppt.add_argument("input", help="File path or folder path containing PPT files")
    p_ppt.add_argument("-o", "--output", help="Output directory (default: same folder)", default=None)
    p_ppt.add_argument("-r", "--recursive", action="store_true", help="Recursively search subdirectories")
    p_ppt.add_argument("--no-overwrite", dest="overwrite", action="store_false", help="Do not overwrite existing PDFs")
    p_ppt.set_defaults(func=handle_ppt2pdf)

    # word2pdf
    p_word = subparsers.add_parser("word2pdf", help="Bulk convert Word DOC/DOCX to PDF")
    p_word.add_argument("input", help="File or folder path containing Word files")
    p_word.add_argument("-o", "--output", help="Output directory", default=None)
    p_word.set_defaults(func=handle_word2pdf)

    # merge
    p_merge = subparsers.add_parser("merge", help="Merge multiple PDF files into one")
    p_merge.add_argument("inputs", nargs="+", help="Input PDF files in sequence")
    p_merge.add_argument("-o", "--output", required=True, help="Output merged PDF path")
    p_merge.set_defaults(func=handle_merge)

    # split
    p_split = subparsers.add_parser("split", help="Split PDF into separate files or ranges")
    p_split.add_argument("input", help="Input PDF file")
    p_split.add_argument("-o", "--output", required=True, help="Output directory")
    p_split.add_argument("--ranges", help="Page ranges, e.g. '1-3, 5, 8-10'", default=None)
    p_split.set_defaults(func=handle_split)

    # compress
    p_comp = subparsers.add_parser("compress", help="Compress and optimize PDF file size")
    p_comp.add_argument("input", help="Input PDF file")
    p_comp.add_argument("-o", "--output", required=True, help="Output PDF file path")
    p_comp.set_defaults(func=handle_compress)

    # pdf2img
    p_p2i = subparsers.add_parser("pdf2img", help="Convert PDF pages to images")
    p_p2i.add_argument("input", help="Input PDF file")
    p_p2i.add_argument("-o", "--output", required=True, help="Output directory for images")
    p_p2i.add_argument("--dpi", type=int, default=150, help="Image DPI resolution (default: 150)")
    p_p2i.add_argument("--format", choices=["png", "jpg"], default="png", help="Image format (default: png)")
    p_p2i.set_defaults(func=handle_pdf2img)

    # img2pdf
    p_i2p = subparsers.add_parser("img2pdf", help="Combine images into a single PDF")
    p_i2p.add_argument("inputs", nargs="+", help="Input image files")
    p_i2p.add_argument("-o", "--output", required=True, help="Output PDF file path")
    p_i2p.set_defaults(func=handle_img2pdf)

    # text
    p_txt = subparsers.add_parser("text", help="Extract text from PDF")
    p_txt.add_argument("input", help="Input PDF file")
    p_txt.add_argument("-o", "--output", required=True, help="Output TXT file path")
    p_txt.set_defaults(func=handle_text)

    # extract-images
    p_eimg = subparsers.add_parser("extract-images", help="Extract all embedded images from PDF")
    p_eimg.add_argument("input", help="Input PDF file")
    p_eimg.add_argument("-o", "--output", required=True, help="Output directory")
    p_eimg.set_defaults(func=handle_extract_images)

    # watermark
    p_wm = subparsers.add_parser("watermark", help="Add diagonal text watermark")
    p_wm.add_argument("input", help="Input PDF file")
    p_wm.add_argument("-o", "--output", required=True, help="Output PDF file")
    p_wm.add_argument("--text", default="CONFIDENTIAL", help="Watermark text")
    p_wm.add_argument("--size", type=int, default=45, help="Font size (default: 45)")
    p_wm.add_argument("--opacity", type=float, default=0.22, help="Opacity (0.0 to 1.0)")
    p_wm.set_defaults(func=handle_watermark)

    # rotate
    p_rot = subparsers.add_parser("rotate", help="Rotate PDF pages")
    p_rot.add_argument("input", help="Input PDF file")
    p_rot.add_argument("-o", "--output", required=True, help="Output PDF file")
    p_rot.add_argument("--angle", type=int, choices=[90, 180, 270], default=90, help="Rotation degrees")
    p_rot.set_defaults(func=handle_rotate)

    # protect
    p_prot = subparsers.add_parser("protect", help="Password protect a PDF")
    p_prot.add_argument("input", help="Input PDF file")
    p_prot.add_argument("-o", "--output", required=True, help="Output PDF file")
    p_prot.add_argument("--password", required=True, help="User password")
    p_prot.set_defaults(func=handle_protect)

    # unlock
    p_unl = subparsers.add_parser("unlock", help="Remove password from protected PDF")
    p_unl.add_argument("input", help="Input PDF file")
    p_unl.add_argument("-o", "--output", required=True, help="Output PDF file")
    p_unl.add_argument("--password", required=True, help="Password")
    p_unl.set_defaults(func=handle_unlock)

    # info
    p_info = subparsers.add_parser("info", help="Display PDF metadata and page count")
    p_info.add_argument("input", help="Input PDF file")
    p_info.set_defaults(func=handle_info)

    args = parser.parse_args()
    if not hasattr(args, "func"):
        print_banner()
        parser.print_help()
        return

    print_banner()
    args.func(args)


if __name__ == "__main__":
    main()
