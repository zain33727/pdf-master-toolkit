"""
All-in-One PDF & Document Toolkit
"""

from .converters import (
    bulk_convert_ppt_to_pdf,
    bulk_convert_word_to_pdf,
    find_presentation_files,
    images_to_pdf,
    is_powerpoint_available,
    is_word_available,
    is_libreoffice_available
)

from .pdf_ops import (
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
    get_pdf_info,
    remove_watermark_from_pdf,
    csv_or_excel_to_pdf,
    pdf_to_excel_or_csv
)

__all__ = [
    "bulk_convert_ppt_to_pdf",
    "bulk_convert_word_to_pdf",
    "find_presentation_files",
    "images_to_pdf",
    "is_powerpoint_available",
    "is_word_available",
    "is_libreoffice_available",
    "merge_pdfs",
    "split_pdf",
    "compress_pdf",
    "pdf_to_images",
    "extract_text_from_pdf",
    "extract_embedded_images",
    "rotate_pdf_pages",
    "watermark_pdf",
    "protect_pdf",
    "unlock_pdf",
    "get_pdf_info",
    "remove_watermark_from_pdf",
    "csv_or_excel_to_pdf",
    "pdf_to_excel_or_csv"
]
