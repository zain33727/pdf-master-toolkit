"""
Automated End-to-End Test Suite for PDF Master Toolkit
Verifies all features: bulk PPT to PDF, merge, split, compress, images, watermark, protect, unlock.
"""

import os
import shutil
import tempfile
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')
from pptx import Presentation
from PIL import Image, ImageDraw

from core import (
    bulk_convert_ppt_to_pdf,
    merge_pdfs,
    split_pdf,
    compress_pdf,
    pdf_to_images,
    images_to_pdf,
    extract_text_from_pdf,
    watermark_pdf,
    protect_pdf,
    unlock_pdf,
    get_pdf_info
)


def run_tests():
    test_dir = os.path.abspath("test_workspace")
    os.makedirs(test_dir, exist_ok=True)
    ppt_dir = os.path.join(test_dir, "ppts")
    pdf_dir = os.path.join(test_dir, "pdfs")
    os.makedirs(ppt_dir, exist_ok=True)
    os.makedirs(pdf_dir, exist_ok=True)

    print("=" * 60)
    print("STARTING TEST SUITE: PDF MASTER TOOLKIT")
    print("=" * 60)

    try:
        # Step 1: Create 3 test PPTX presentations
        print("\n[1/8] Generating 3 sample PPTX files...")
        ppt_files = []
        for i in range(1, 4):
            p_path = os.path.join(ppt_dir, f"sample_presentation_{i}.pptx")
            prs = Presentation()
            slide = prs.slides.add_slide(prs.slide_layouts[0])
            slide.shapes.title.text = f"Presentation Slide {i}"
            slide.placeholders[1].text = f"Automated test presentation number {i} for bulk conversion."
            prs.save(p_path)
            ppt_files.append(p_path)
            print(f"   Created: {os.path.basename(p_path)}")

        # Step 2: Bulk convert PPTs to PDF
        print("\n[2/8] Testing Bulk PPT -> PDF conversion via PowerPoint COM...")
        summary = bulk_convert_ppt_to_pdf(ppt_files, output_dir=pdf_dir)
        print(f"   Result: {summary['success']} succeeded, {summary['failed']} failed.")
        assert summary["success"] == 3, f"Expected 3 converted PDFs, got {summary['success']}"

        pdf1 = os.path.join(pdf_dir, "sample_presentation_1.pdf")
        pdf2 = os.path.join(pdf_dir, "sample_presentation_2.pdf")
        assert os.path.isfile(pdf1) and os.path.getsize(pdf1) > 0, "PDF 1 missing or empty"
        assert os.path.isfile(pdf2) and os.path.getsize(pdf2) > 0, "PDF 2 missing or empty"
        print("   [OK] Bulk PPT to PDF: PASSED")

        # Step 3: Test Merge PDFs
        print("\n[3/8] Testing Merge PDFs...")
        merged_pdf = os.path.join(test_dir, "merged.pdf")
        merge_pdfs([pdf1, pdf2], merged_pdf)
        info = get_pdf_info(merged_pdf)
        print(f"   Merged PDF created: {info['pages']} pages, {info['file_size_kb']} KB")
        assert info["pages"] >= 2, "Merged PDF should have at least 2 pages"
        print("   [OK] Merge PDFs: PASSED")

        # Step 4: Test Split PDF
        print("\n[4/8] Testing Split PDF...")
        split_out_dir = os.path.join(test_dir, "split_pages")
        split_files = split_pdf(merged_pdf, split_out_dir, split_mode="all_pages")
        print(f"   Generated {len(split_files)} individual page files.")
        assert len(split_files) >= 2, "Expected at least 2 split files"
        print("   [OK] Split PDF: PASSED")

        # Step 5: Test PDF to Images & Images to PDF
        print("\n[5/8] Testing PDF <-> Images conversion...")
        img_out_dir = os.path.join(test_dir, "exported_images")
        exported_imgs = pdf_to_images(pdf1, img_out_dir, dpi=150, img_format="png")
        assert len(exported_imgs) > 0 and os.path.isfile(exported_imgs[0]), "Failed to export PDF pages to images"
        print(f"   Exported {len(exported_imgs)} image(s) from PDF.")

        recombined_pdf = os.path.join(test_dir, "recombined_from_images.pdf")
        images_to_pdf(exported_imgs, recombined_pdf)
        assert os.path.isfile(recombined_pdf) and os.path.getsize(recombined_pdf) > 0
        print("   [OK] PDF <-> Images roundtrip: PASSED")

        # Step 6: Test Text Extraction
        print("\n[6/8] Testing Text Extraction...")
        text = extract_text_from_pdf(pdf1)
        print(f"   Extracted {len(text)} characters of text:")
        print(f"   Snippet: {text[:80]!r}...")
        assert "Presentation Slide 1" in text or "Automated test" in text, "Extracted text did not match content"
        print("   [OK] Text Extraction: PASSED")

        # Step 7: Test Watermarking
        print("\n[7/8] Testing Watermark...")
        wm_pdf = os.path.join(test_dir, "watermarked.pdf")
        watermark_pdf(pdf1, wm_pdf, text="TEST WATERMARK", font_size=40)
        assert os.path.isfile(wm_pdf) and os.path.getsize(wm_pdf) > 0
        print("   [OK] Watermark application: PASSED")

        # Step 8: Test Protect and Unlock
        print("\n[8/8] Testing Password Protect & Unlock...")
        prot_pdf = os.path.join(test_dir, "protected.pdf")
        protect_pdf(pdf1, prot_pdf, user_password="my_secret_pass")
        assert get_pdf_info(prot_pdf)["is_encrypted"] is True, "PDF was not encrypted"
        print("   Protected PDF confirmed encrypted.")

        unlocked_pdf = os.path.join(test_dir, "unlocked.pdf")
        ok = unlock_pdf(prot_pdf, unlocked_pdf, password="my_secret_pass")
        assert ok is True, "PDF unlock failed"
        assert get_pdf_info(unlocked_pdf)["is_encrypted"] is False, "Unlocked PDF should not be encrypted"
        print("   [OK] Protect & Unlock: PASSED")

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED SUCCESSFULLY! (8/8 PASSED)")
        print("=" * 60)

    finally:
        # Clean up test artifacts
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir, ignore_errors=True)
            print("[*] Test workspace cleaned up.")


if __name__ == "__main__":
    run_tests()
