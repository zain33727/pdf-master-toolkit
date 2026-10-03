"""
PDF Master Toolkit - All-in-One Offline Suite
Clean modern UI with wide sidebar, sleek icons, and unified tool workspaces.
"""

import os
import io
import json
import zipfile
import tempfile
from datetime import datetime
from pathlib import Path
import streamlit as st

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

st.set_page_config(
    page_title="PDF Master Toolkit",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Persistent Recent Files Helper
RECENT_FILES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recent_files.json")


def load_recent_files():
    if os.path.exists(RECENT_FILES_PATH):
        try:
            with open(RECENT_FILES_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_recent_file(filename: str, tool_name: str, file_size_kb: float):
    recent = load_recent_files()
    entry = {
        "filename": filename,
        "tool": tool_name,
        "size_kb": round(file_size_kb, 1),
        "timestamp": datetime.now().strftime("%b %d, %Y - %I:%M %p")
    }
    recent.insert(0, entry)
    recent = recent[:25]
    try:
        with open(RECENT_FILES_PATH, "w", encoding="utf-8") as f:
            json.dump(recent, f, indent=2)
    except Exception:
        pass


def get_zip_bytes(files_dict: dict):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for fname, data in files_dict.items():
            zip_file.writestr(fname, data)
    zip_buffer.seek(0)
    return zip_buffer.getvalue()


# Navigation state
if "current_view" not in st.session_state:
    st.session_state.current_view = "dashboard"

# Complete CSS Overrides for a Premium SaaS Look & Feel
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main, section.main {
        background-color: #F8F9FA !important;
        color: #1E293B !important;
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Sidebar Width: Wide enough so text NEVER wraps awkwardly */
    [data-testid="stSidebar"], section[data-testid="stSidebar"] {
        min-width: 275px !important;
        max-width: 275px !important;
        width: 275px !important;
        background-color: #FFFFFF !important;
        border-right: 1px solid #EAEBEF !important;
    }
    [data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem !important;
        padding-left: 1.1rem !important;
        padding-right: 1.1rem !important;
        background-color: #FFFFFF !important;
    }

    /* Brand Header in Sidebar */
    .sidebar-brand-box {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 6px 4px 18px 4px;
        border-bottom: 1px solid #F1F5F9;
        margin-bottom: 14px;
    }
    .brand-icon-sq {
        width: 32px;
        height: 32px;
        border-radius: 8px;
        background-color: #18181B;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 1rem;
    }
    .brand-title-text {
        font-size: 0.95rem;
        font-weight: 700;
        color: #0F172A;
        letter-spacing: -0.01em;
    }

    /* Sleek Sidebar Nav Links */
    [data-testid="stSidebar"] .stButton > button {
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        width: 100% !important;
        height: 40px !important;
        padding: 0 12px !important;
        border: none !important;
        border-radius: 8px !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        color: #475569 !important;
        background: transparent !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        box-shadow: none !important;
        margin-bottom: 2px !important;
        transition: all 0.15s ease !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #F8FAFC !important;
        color: #FF5A36 !important;
    }
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background-color: #FFF0EB !important;
        color: #FF5A36 !important;
        font-weight: 700 !important;
    }

    /* Main Container */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3.5rem !important;
        padding-left: 2.5rem !important;
        padding-right: 2.5rem !important;
        max-width: 1300px !important;
        background-color: #F8F9FA !important;
    }

    /* Dashboard Header */
    .dash-header-title {
        font-size: 1.85rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 4px;
        letter-spacing: -0.02em;
    }
    .dash-header-sub {
        font-size: 0.95rem;
        color: #64748B;
        margin-bottom: 24px;
    }

    /* Dashboard Card Containers */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border: 1px solid #EAEBEF !important;
        border-radius: 14px !important;
        padding: 22px 20px 18px 20px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02) !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease !important;
        min-height: 250px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        margin-bottom: 14px !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #FFD4C9 !important;
        box-shadow: 0 6px 18px rgba(255, 90, 54, 0.09) !important;
        transform: translateY(-2px) !important;
    }

    .card-icon-box {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        background-color: #FFF0EB;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 14px;
    }

    .card-title {
        font-size: 1.12rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 4px;
    }

    .card-desc {
        font-size: 0.86rem;
        color: #64748B;
        line-height: 1.4;
        margin-bottom: 16px;
        min-height: 38px;
    }

    /* Coral Action Buttons */
    .stButton > button[kind="primary"] {
        background-color: #FF5A36 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        padding: 0.65rem 1.2rem !important;
        width: 100% !important;
        box-shadow: 0 1px 2px rgba(255, 90, 54, 0.2) !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #E64724 !important;
        box-shadow: 0 4px 10px rgba(255, 90, 54, 0.3) !important;
    }
    .stButton > button[kind="primary"]:active {
        transform: translateY(1px);
    }

    .card-subtext {
        font-size: 0.78rem;
        color: #94A3B8;
        text-align: center;
        margin-top: 6px;
    }

    /* Tool Workspace Hero Container */
    .tool-hero-box {
        display: flex;
        align-items: center;
        gap: 16px;
        margin: 12px 0 20px 0;
        padding-bottom: 16px;
        border-bottom: 1px solid #ECEEF1;
    }
    .tool-hero-icon {
        width: 54px;
        height: 54px;
        border-radius: 12px;
        background-color: #FFF0EB;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .tool-hero-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: #111827;
        margin: 0;
        letter-spacing: -0.01em;
    }
    .tool-hero-desc {
        font-size: 0.92rem;
        color: #64748B;
        margin: 2px 0 0 0;
    }

    /* Tool Workspace Card */
    .tool-card-panel {
        background: #FFFFFF;
        border: 1px solid #EAEBEF;
        border-radius: 16px;
        padding: 28px 32px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
        max-width: 920px;
        margin-bottom: 24px;
    }

    /* Beautiful Styled File Uploader */
    [data-testid="stFileUploader"] {
        background-color: #FAFAFC !important;
        border: 1.5px dashed #CBD5E1 !important;
        border-radius: 12px !important;
        padding: 16px 20px !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #FF5A36 !important;
        background-color: #FFF9F7 !important;
    }
    [data-testid="stFileUploader"] button {
        background-color: #FFFFFF !important;
        color: #1E293B !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
    }

    /* Back Button */
    .back-btn-box .stButton > button {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        color: #475569 !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        padding: 6px 14px !important;
        border-radius: 8px !important;
        width: auto !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02) !important;
    }
    .back-btn-box .stButton > button:hover {
        background-color: #F8FAFC !important;
        border-color: #CBD5E1 !important;
        color: #0F172A !important;
    }

    /* Recent Files Header */
    .recent-section-header {
        margin-top: 36px;
        margin-bottom: 16px;
        padding-top: 20px;
        border-top: 1px solid #ECEEF1;
    }
    .recent-title {
        font-size: 1.18rem;
        font-weight: 700;
        color: #111827;
    }
</style>
""", unsafe_allow_html=True)


# =====================================================================
# SIDEBAR
# =====================================================================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand-box">
        <div class="brand-icon-sq">⚡</div>
        <div class="brand-title-text">PDF Master Toolkit</div>
    </div>
    """, unsafe_allow_html=True)

    tools_menu = [
        ("dashboard", "🏠  Dashboard"),
        ("ppt2pdf", "📊  Bulk PPT to PDF"),
        ("merge", "📑  Merge PDF"),
        ("split", "✂️  Split PDF"),
        ("compress", "🗜️  Compress PDF"),
        ("word2pdf", "📝  Word to PDF"),
        ("images2pdf", "🖼️  Images to PDF"),
        ("pdf2images", "📄  PDF to Images"),
        ("watermark", "💧  Watermark PDF"),
        ("protect", "🔒  Protect & Unlock"),
        ("extract", "🔍  Extract Content"),
        ("rotate", "🔄  Rotate PDF"),
    ]

    for key, label in tools_menu:
        is_active = (st.session_state.current_view == key)
        btn_type = "primary" if is_active else "secondary"
        if st.button(label, key=f"nav_{key}", type=btn_type):
            st.session_state.current_view = key
            st.rerun()

    st.markdown("<hr style='border: none; border-top: 1px solid #F1F5F9; margin: 18px 0 12px 0;'>", unsafe_allow_html=True)

    if st.button("🕒  Recent Files", key="nav_recent", type="secondary"):
        st.session_state.current_view = "recent_view"
        st.rerun()

    if st.button("⚙️  Settings", key="nav_settings", type="secondary"):
        st.session_state.current_view = "settings_view"
        st.rerun()

    if st.button("❓  Help & Tips", key="nav_help", type="secondary"):
        st.session_state.current_view = "help_view"
        st.rerun()


def switch_view(view_name):
    st.session_state.current_view = view_name
    st.rerun()


def render_tool_header(title: str, description: str, svg_path: str):
    """Renders a consistent back button and hero card across all tools."""
    st.markdown('<div class="back-btn-box">', unsafe_allow_html=True)
    if st.button("← Back to Dashboard", key=f"back_btn_{st.session_state.current_view}"):
        switch_view("dashboard")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="tool-hero-box">
        <div class="tool-hero-icon">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#FF5A36" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                {svg_path}
            </svg>
        </div>
        <div>
            <h2 class="tool-hero-title">{title}</h2>
            <p class="tool-hero-desc">{description}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


# =====================================================================
# VIEW 1: DASHBOARD (ALL 10+ REAL TOOLS AS UNIFIED CARDS)
# =====================================================================
if st.session_state.current_view == "dashboard":
    st.markdown("""
    <div class="dash-header-title">PDF Master Toolkit</div>
    <div class="dash-header-sub">All-in-one offline workspace • 100% private processing on your local machine</div>
    """, unsafe_allow_html=True)

    # ROW 1 (3 Tools): Bulk PPT to PDF, Merge PDF, Split PDF
    r1c1, r1c2, r1c3 = st.columns(3, gap="medium")

    # 1. Bulk PPT to PDF
    with r1c1:
        with st.container(border=True):
            st.markdown("""
            <div class="card-icon-box">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#FF5A36" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="2" y="3" width="20" height="14" rx="2"/>
                    <line x1="8" y1="21" x2="16" y2="21"/>
                    <line x1="12" y1="17" x2="12" y2="21"/>
                    <path d="M9 8H12C12.8 8 13.5 8.7 13.5 9.5C13.5 10.3 12.8 11 12 11H9V13"/>
                </svg>
            </div>
            <div class="card-title">Bulk PPT to PDF</div>
            <div class="card-desc">Batch convert 100+ PowerPoint (.pptx, .ppt) files with native fidelity.</div>
            """, unsafe_allow_html=True)
            if st.button("Select Files / Folder", key="btn_c_ppt", type="primary"):
                switch_view("ppt2pdf")
            st.markdown('<div class="card-subtext">No files selected</div>', unsafe_allow_html=True)

    # 2. Merge PDF
    with r1c2:
        with st.container(border=True):
            st.markdown("""
            <div class="card-icon-box">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#FF5A36" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M8 2H14L19 7V17C19 18.1 18.1 19 17 19H8C6.9 19 6 18.1 6 17V4C6 2.9 6.9 2 8 2Z"/>
                    <path d="M14 2V7H19"/>
                    <path d="M4 8H3C2.45 8 2 8.45 2 9V21C2 22.1 2.9 23 4 23H13C13.55 23 14 22.55 14 22V21"/>
                </svg>
            </div>
            <div class="card-title">Merge PDF</div>
            <div class="card-desc">Combine multiple PDF documents into a single file in any order.</div>
            """, unsafe_allow_html=True)
            if st.button("Select Files", key="btn_c_merge", type="primary"):
                switch_view("merge")
            st.markdown('<div class="card-subtext">No files selected</div>', unsafe_allow_html=True)

    # 3. Split PDF
    with r1c3:
        with st.container(border=True):
            st.markdown("""
            <div class="card-icon-box">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#FF5A36" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V8L14 2Z"/>
                    <line x1="2" y1="12" x2="22" y2="12" stroke-dasharray="3 3"/>
                </svg>
            </div>
            <div class="card-title">Split PDF</div>
            <div class="card-desc">Extract custom page ranges or burst all pages into individual files.</div>
            """, unsafe_allow_html=True)
            if st.button("Select File", key="btn_c_split", type="primary"):
                switch_view("split")
            st.markdown('<div class="card-subtext">No file selected</div>', unsafe_allow_html=True)

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # ROW 2 (3 Tools): Compress PDF, Word to PDF, Images to PDF
    r2c1, r2c2, r2c3 = st.columns(3, gap="medium")

    # 4. Compress PDF
    with r2c1:
        with st.container(border=True):
            st.markdown("""
            <div class="card-icon-box">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#FF5A36" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M4 14H10V20"/>
                    <path d="M10 14L3 21"/>
                    <path d="M20 10H14V4"/>
                    <path d="M14 10L21 3"/>
                </svg>
            </div>
            <div class="card-title">Compress PDF</div>
            <div class="card-desc">Shrink PDF file size while keeping text and image quality sharp.</div>
            """, unsafe_allow_html=True)
            if st.button("Select File", key="btn_c_comp", type="primary"):
                switch_view("compress")
            st.markdown('<div class="card-subtext">No file selected</div>', unsafe_allow_html=True)

    # 5. Word to PDF
    with r2c2:
        with st.container(border=True):
            st.markdown("""
            <div class="card-icon-box">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#FF5A36" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V8L14 2Z"/>
                    <polyline points="14 2 14 8 20 8"/>
                    <path d="M9 15L10.5 12L12 15L13.5 12L15 15"/>
                </svg>
            </div>
            <div class="card-title">Word to PDF</div>
            <div class="card-desc">Convert Word documents (.doc, .docx) to high-fidelity PDF format.</div>
            """, unsafe_allow_html=True)
            if st.button("Select File", key="btn_c_word", type="primary"):
                switch_view("word2pdf")
            st.markdown('<div class="card-subtext">No file selected</div>', unsafe_allow_html=True)

    # 6. Images to PDF
    with r2c3:
        with st.container(border=True):
            st.markdown("""
            <div class="card-icon-box">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#FF5A36" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                    <circle cx="8.5" cy="8.5" r="1.5"/>
                    <polyline points="21 15 16 10 5 21"/>
                </svg>
            </div>
            <div class="card-title">Images to PDF</div>
            <div class="card-desc">Merge multiple JPG, PNG, WEBP, and BMP images into a clean PDF.</div>
            """, unsafe_allow_html=True)
            if st.button("Select Images", key="btn_c_i2p", type="primary"):
                switch_view("images2pdf")
            st.markdown('<div class="card-subtext">No images selected</div>', unsafe_allow_html=True)

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # ROW 3 (3 Tools): PDF to Images, Watermark PDF, Protect & Unlock
    r3c1, r3c2, r3c3 = st.columns(3, gap="medium")

    # 7. PDF to Images
    with r3c1:
        with st.container(border=True):
            st.markdown("""
            <div class="card-icon-box">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#FF5A36" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                    <circle cx="10" cy="13" r="1.5"/>
                    <path d="m8 18 3-3 4 4"/>
                </svg>
            </div>
            <div class="card-title">PDF to Images</div>
            <div class="card-desc">Export each PDF page into high-resolution PNG or JPG image files.</div>
            """, unsafe_allow_html=True)
            if st.button("Select File", key="btn_c_p2i", type="primary"):
                switch_view("pdf2images")
            st.markdown('<div class="card-subtext">No file selected</div>', unsafe_allow_html=True)

    # 8. Watermark PDF
    with r3c2:
        with st.container(border=True):
            st.markdown("""
            <div class="card-icon-box">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#FF5A36" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="9"/>
                    <path d="M12 3v18"/>
                    <path d="m4.93 4.93 14.14 14.14"/>
                </svg>
            </div>
            <div class="card-title">Watermark PDF</div>
            <div class="card-desc">Stamp custom diagonal text watermarks with opacity and font size control.</div>
            """, unsafe_allow_html=True)
            if st.button("Select File", key="btn_c_wm", type="primary"):
                switch_view("watermark")
            st.markdown('<div class="card-subtext">No file selected</div>', unsafe_allow_html=True)

    # 9. Protect & Unlock
    with r3c3:
        with st.container(border=True):
            st.markdown("""
            <div class="card-icon-box">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#FF5A36" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                    <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
            </div>
            <div class="card-title">Protect & Unlock</div>
            <div class="card-desc">Add 128-bit password encryption or remove protection from PDF files.</div>
            """, unsafe_allow_html=True)
            if st.button("Select File", key="btn_c_sec", type="primary"):
                switch_view("protect")
            st.markdown('<div class="card-subtext">No file selected</div>', unsafe_allow_html=True)

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # ROW 4 (2 Tools): Extract Content, Rotate Pages
    r4c1, r4c2, r4c3 = st.columns(3, gap="medium")

    # 10. Extract Content
    with r4c1:
        with st.container(border=True):
            st.markdown("""
            <div class="card-icon-box">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#FF5A36" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="11" cy="11" r="8"/>
                    <line x1="21" y1="21" x2="16.65" y2="16.65"/>
                    <line x1="11" y1="8" x2="11" y2="14"/>
                    <line x1="8" y1="11" x2="14" y2="11"/>
                </svg>
            </div>
            <div class="card-title">Extract Content</div>
            <div class="card-desc">Extract all readable text to TXT or dump all raw embedded images.</div>
            """, unsafe_allow_html=True)
            if st.button("Select File", key="btn_c_ext", type="primary"):
                switch_view("extract")
            st.markdown('<div class="card-subtext">No file selected</div>', unsafe_allow_html=True)

    # 11. Rotate Pages
    with r4c2:
        with st.container(border=True):
            st.markdown("""
            <div class="card-icon-box">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#FF5A36" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21.5 2v6h-6"/>
                    <path d="M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/>
                </svg>
            </div>
            <div class="card-title">Rotate PDF</div>
            <div class="card-desc">Permanently rotate page orientation by 90°, 180°, or 270° clockwise.</div>
            """, unsafe_allow_html=True)
            if st.button("Select File", key="btn_c_rot", type="primary"):
                switch_view("rotate")
            st.markdown('<div class="card-subtext">No file selected</div>', unsafe_allow_html=True)

    with r4c3:
        pass

    # -------------------------------------------------------------
    # RECENT FILES SECTION
    # -------------------------------------------------------------
    st.markdown("""
    <div class="recent-section-header">
        <div class="recent-title">Recent Files</div>
    </div>
    """, unsafe_allow_html=True)

    recent_list = load_recent_files()

    if not recent_list:
        st.markdown("""
        <div style="background-color: #FFFFFF; border: 1px dashed #CBD5E1; border-radius: 12px; padding: 26px; text-align: center; color: #94A3B8;">
            <p style="margin: 0; font-size: 0.95rem;">No recent files yet. Select any tool above to start processing documents.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for idx, item in enumerate(recent_list[:6]):
            c_icon, c_info, c_time = st.columns([0.6, 6, 2])
            with c_icon:
                st.markdown("""
                <div style="background: #FFF0EB; width: 36px; height: 36px; border-radius: 8px; display: flex; align-items: center; justify-content: center;">
                    <span style="color: #FF5A36; font-size: 1rem;">📄</span>
                </div>
                """, unsafe_allow_html=True)
            with c_info:
                st.markdown(f"**{item['filename']}** &nbsp; <span style='background: #F1F5F9; color: #475569; font-size: 0.75rem; padding: 2px 8px; border-radius: 4px;'>{item['tool']}</span> &nbsp; <span style='color: #94A3B8; font-size: 0.8rem;'>{item['size_kb']} KB</span>", unsafe_allow_html=True)
            with c_time:
                st.caption(item.get("timestamp", ""))
            st.markdown("<hr style='border: none; border-top: 1px solid #F1F5F9; margin: 4px 0 8px 0;'>", unsafe_allow_html=True)


# =====================================================================
# VIEW 2: BULK PPT TO PDF (HERO PANEL)
# =====================================================================
elif st.session_state.current_view == "ppt2pdf":
    render_tool_header(
        "Bulk PowerPoint to PDF",
        "Convert single presentations or scan an entire folder of 100+ files at native speed.",
        '<rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/><path d="M9 8H12C12.8 8 13.5 8.7 13.5 9.5C13.5 10.3 12.8 11 12 11H9V13"/>'
    )

    tab_bulk, tab_upload = st.tabs(["📁 Bulk Folder Mode (Recommended for 100+ Presentations)", "📤 Upload Files via Browser"])

    with tab_bulk:
        st.markdown('<div class="tool-card-panel">', unsafe_allow_html=True)
        st.markdown("#### ⚡ Batch Folder Converter")
        st.caption("Point to any folder on your computer containing .ppt, .pptx, .pps, or .ppsx files.")

        folder_input = st.text_input(
            "Folder path on your computer:",
            placeholder=r"C:\Users\username\Desktop\Presentations"
        )
        c_sub, c_out = st.columns(2)
        with c_sub:
            recursive_check = st.checkbox("Scan subfolders recursively", value=True)
        with c_out:
            dest_folder = st.text_input("Custom Output Directory (Leave empty to save alongside originals):", "")

        if folder_input:
            if os.path.isdir(folder_input):
                found = find_presentation_files(folder_input, recursive=recursive_check)
                st.success(f"✓ Found **{len(found)}** presentation file(s) in `{folder_input}`")

                if found:
                    with st.expander(f"View list of {len(found)} presentations"):
                        for f in found[:40]:
                            st.caption(f"• {f}")
                        if len(found) > 40:
                            st.caption(f"... and {len(found) - 40} more files.")

                    if st.button(f"⚡ Start Bulk Conversion of {len(found)} Files", type="primary"):
                        progress_bar = st.progress(0)
                        status_lbl = st.empty()
                        out_dir = dest_folder.strip() if dest_folder.strip() else None

                        def cb(cur, tot, name, ok, msg):
                            progress_bar.progress(cur / tot)
                            status_lbl.markdown(f"**Converting [{cur}/{tot}]:** `{name}`")

                        with st.spinner("Converting presentations with native PowerPoint engine..."):
                            res = bulk_convert_ppt_to_pdf(found, output_dir=out_dir, progress_callback=cb)

                        st.success(f"🎉 Completed! Successfully converted **{res['success']}** files ({res['failed']} failed).")
                        save_recent_file(f"Batch ({res['success']} PPT files)", "Bulk PPT to PDF", 1024.0)

                        if out_dir and os.path.isdir(out_dir):
                            st.info(f"PDF files saved in: `{out_dir}`")
            else:
                st.warning("Specified path does not exist or is not a directory.")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_upload:
        st.markdown('<div class="tool-card-panel">', unsafe_allow_html=True)
        uploaded_ppts = st.file_uploader(
            "Drag and drop PowerPoint files here:",
            type=["pptx", "ppt", "pps", "ppsx"],
            accept_multiple_files=True
        )

        if uploaded_ppts:
            st.info(f"Selected **{len(uploaded_ppts)}** presentation(s).")
            if st.button("⚡ Convert & Download ZIP", type="primary", key="btn_run_ppt_upload"):
                with tempfile.TemporaryDirectory() as temp_dir:
                    in_paths = []
                    for uf in uploaded_ppts:
                        p = os.path.join(temp_dir, uf.name)
                        with open(p, "wb") as f:
                            f.write(uf.getbuffer())
                        in_paths.append(p)

                    out_dir = os.path.join(temp_dir, "out_pdfs")
                    os.makedirs(out_dir, exist_ok=True)

                    p_bar = st.progress(0)
                    s_txt = st.empty()

                    def cb2(cur, tot, name, ok, msg):
                        p_bar.progress(cur / tot)
                        s_txt.text(f"Converting [{cur}/{tot}]: {name}")

                    with st.spinner("Converting files..."):
                        res = bulk_convert_ppt_to_pdf(in_paths, output_dir=out_dir, progress_callback=cb2)

                    files_dict = {}
                    for item in res["results"]:
                        if item["status"] == "success" and os.path.isfile(item["output"]):
                            with open(item["output"], "rb") as pf:
                                files_dict[os.path.basename(item["output"])] = pf.read()

                    if files_dict:
                        zip_data = get_zip_bytes(files_dict)
                        save_recent_file(uploaded_ppts[0].name, "Bulk PPT to PDF", len(zip_data) / 1024)
                        st.success(f"🎉 Successfully converted {len(files_dict)} presentation(s)!")
                        st.download_button(
                            label="📥 Download Converted PDFs (.ZIP)",
                            data=zip_data,
                            file_name="converted_presentations.zip",
                            mime="application/zip",
                            type="primary"
                        )
                    else:
                        st.error("Conversion failed. Please verify PowerPoint is available.")
        st.markdown('</div>', unsafe_allow_html=True)


# =====================================================================
# VIEW 3: MERGE PDF
# =====================================================================
elif st.session_state.current_view == "merge":
    render_tool_header(
        "Merge PDF Files",
        "Combine multiple PDF documents into a single document in any desired order.",
        '<path d="M8 2H14L19 7V17C19 18.1 18.1 19 17 19H8C6.9 19 6 18.1 6 17V4C6 2.9 6.9 2 8 2Z"/><path d="M14 2V7H19"/><path d="M4 8H3C2.45 8 2 8.45 2 9V21C2 22.1 2.9 23 4 23H13C13.55 23 14 22.55 14 22V21"/>'
    )

    st.markdown('<div class="tool-card-panel">', unsafe_allow_html=True)
    uploaded_pdfs = st.file_uploader("Select PDF files to merge (order matters):", type=["pdf"], accept_multiple_files=True, key="up_merge")

    if uploaded_pdfs:
        st.markdown(f"**Files ready to combine ({len(uploaded_pdfs)}):**")
        for idx, f in enumerate(uploaded_pdfs, 1):
            st.caption(f"{idx}. {f.name} ({round(len(f.getvalue()) / 1024, 1)} KB)")

        if len(uploaded_pdfs) >= 2:
            if st.button("⚡ Merge PDFs Now", type="primary", key="btn_run_m"):
                with tempfile.TemporaryDirectory() as temp_dir:
                    in_paths = []
                    for up in uploaded_pdfs:
                        p = os.path.join(temp_dir, up.name)
                        with open(p, "wb") as pf:
                            pf.write(up.getbuffer())
                        in_paths.append(p)

                    out_merged = os.path.join(temp_dir, "merged_document.pdf")
                    merge_pdfs(in_paths, out_merged)

                    with open(out_merged, "rb") as mf:
                        merged_bytes = mf.read()

                    save_recent_file("merged_document.pdf", "Merge PDF", len(merged_bytes) / 1024)
                    st.success("🎉 Merged successfully!")
                    st.download_button(
                        label="📥 Download Merged PDF",
                        data=merged_bytes,
                        file_name="merged_document.pdf",
                        mime="application/pdf",
                        type="primary"
                    )
        else:
            st.warning("Please upload at least 2 PDF files to merge.")
    st.markdown('</div>', unsafe_allow_html=True)


# =====================================================================
# VIEW 4: SPLIT PDF
# =====================================================================
elif st.session_state.current_view == "split":
    render_tool_header(
        "Split PDF Document",
        "Extract individual pages or custom page ranges into clean separate PDF documents.",
        '<path d="M14 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V8L14 2Z"/><line x1="2" y1="12" x2="22" y2="12" stroke-dasharray="3 3"/>'
    )

    st.markdown('<div class="tool-card-panel">', unsafe_allow_html=True)
    uploaded_pdf = st.file_uploader("Upload PDF file to split:", type=["pdf"], key="up_split")

    if uploaded_pdf:
        split_mode = st.radio("Splitting Strategy:", ["Split into individual pages (1 PDF per page)", "Extract custom page ranges (e.g. 1-3, 5)"])
        range_val = ""
        if "Extract" in split_mode:
            range_val = st.text_input("Enter Page Ranges (e.g., 1-3, 5, 8-10):", "1-3, 5")

        if st.button("⚡ Split PDF Now", type="primary", key="btn_run_s"):
            with tempfile.TemporaryDirectory() as temp_dir:
                in_path = os.path.join(temp_dir, uploaded_pdf.name)
                with open(in_path, "wb") as f:
                    f.write(uploaded_pdf.getbuffer())

                mode = "ranges" if "Extract" in split_mode else "all_pages"
                out_dir = os.path.join(temp_dir, "split_results")
                generated = split_pdf(in_path, out_dir, split_mode=mode, range_str=range_val)

                files_dict = {}
                for g in generated:
                    with open(g, "rb") as gf:
                        files_dict[os.path.basename(g)] = gf.read()

                zip_data = get_zip_bytes(files_dict)
                save_recent_file(uploaded_pdf.name, "Split PDF", len(zip_data) / 1024)
                st.success(f"🎉 Generated {len(generated)} split PDF file(s)!")
                st.download_button(
                    label="📥 Download Split Pages (.ZIP)",
                    data=zip_data,
                    file_name="split_pages.zip",
                    mime="application/zip",
                    type="primary"
                )
    st.markdown('</div>', unsafe_allow_html=True)


# =====================================================================
# VIEW 5: COMPRESS PDF
# =====================================================================
elif st.session_state.current_view == "compress":
    render_tool_header(
        "Compress PDF",
        "Shrink PDF file size while keeping text and graphic elements clear and readable.",
        '<path d="M4 14H10V20"/><path d="M10 14L3 21"/><path d="M20 10H14V4"/><path d="M14 10L21 3"/>'
    )

    st.markdown('<div class="tool-card-panel">', unsafe_allow_html=True)
    uploaded_pdf = st.file_uploader("Upload PDF file to compress:", type=["pdf"], key="up_comp")

    if uploaded_pdf:
        orig_kb = round(len(uploaded_pdf.getvalue()) / 1024, 2)
        st.info(f"Original File Size: **{orig_kb} KB** ({round(orig_kb / 1024, 2)} MB)")

        if st.button("⚡ Compress PDF Now", type="primary", key="btn_run_c"):
            with tempfile.TemporaryDirectory() as temp_dir:
                in_path = os.path.join(temp_dir, uploaded_pdf.name)
                out_path = os.path.join(temp_dir, "compressed.pdf")
                with open(in_path, "wb") as f:
                    f.write(uploaded_pdf.getbuffer())

                with st.spinner("Optimizing PDF stream objects and images..."):
                    res = compress_pdf(in_path, out_path)

                with open(out_path, "rb") as cf:
                    comp_bytes = cf.read()

                save_recent_file(uploaded_pdf.name, "Compress PDF", res["compressed_size_kb"])
                st.success(
                    f"🎉 **Compression Complete!**\n\n"
                    f"• **Original:** {res['original_size_kb']} KB\n"
                    f"• **Compressed:** {res['compressed_size_kb']} KB\n"
                    f"• **Saved:** {res['saved_kb']} KB ({res['percent_reduction']}% reduction)"
                )
                st.download_button(
                    label="📥 Download Compressed PDF",
                    data=comp_bytes,
                    file_name=f"compressed_{uploaded_pdf.name}",
                    mime="application/pdf",
                    type="primary"
                )
    st.markdown('</div>', unsafe_allow_html=True)


# =====================================================================
# VIEW 6: WORD TO PDF
# =====================================================================
elif st.session_state.current_view == "word2pdf":
    render_tool_header(
        "Word to PDF Converter",
        "Convert Microsoft Word documents (.docx, .doc) to PDF with accurate fonts and margins.",
        '<path d="M14 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V8L14 2Z"/><polyline points="14 2 14 8 20 8"/><path d="M9 15L10.5 12L12 15L13.5 12L15 15"/>'
    )

    st.markdown('<div class="tool-card-panel">', unsafe_allow_html=True)
    uploaded_words = st.file_uploader("Upload Word documents (.doc, .docx):", type=["doc", "docx"], accept_multiple_files=True, key="up_word")

    if uploaded_words:
        st.info(f"Selected **{len(uploaded_words)}** document(s).")
        if st.button("⚡ Convert Word to PDF", type="primary", key="btn_run_w"):
            with tempfile.TemporaryDirectory() as temp_dir:
                in_paths = []
                for uw in uploaded_words:
                    p = os.path.join(temp_dir, uw.name)
                    with open(p, "wb") as f:
                        f.write(uw.getbuffer())
                    in_paths.append(p)

                out_dir = os.path.join(temp_dir, "word_pdfs")
                os.makedirs(out_dir, exist_ok=True)

                with st.spinner("Converting Word documents via Word engine..."):
                    res = bulk_convert_word_to_pdf(in_paths, output_dir=out_dir)

                files_dict = {}
                for item in res["results"]:
                    if item["status"] == "success" and os.path.isfile(item["output"]):
                        with open(item["output"], "rb") as pf:
                            files_dict[os.path.basename(item["output"])] = pf.read()

                if files_dict:
                    zip_data = get_zip_bytes(files_dict)
                    save_recent_file(uploaded_words[0].name, "Word to PDF", len(zip_data) / 1024)
                    st.success(f"🎉 Successfully converted {len(files_dict)} document(s)!")
                    st.download_button("📥 Download Converted PDFs (.ZIP)", data=zip_data, file_name="word_converted_pdfs.zip", mime="application/zip", type="primary")
                else:
                    st.error("Conversion failed. Please verify Microsoft Word is available.")
    st.markdown('</div>', unsafe_allow_html=True)


# =====================================================================
# VIEW 7: IMAGES TO PDF
# =====================================================================
elif st.session_state.current_view == "images2pdf":
    render_tool_header(
        "Images to PDF Converter",
        "Merge JPG, PNG, WEBP, and BMP images into a unified, cleanly sized PDF file.",
        '<rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/>'
    )

    st.markdown('<div class="tool-card-panel">', unsafe_allow_html=True)
    uploaded_imgs = st.file_uploader("Select images to combine (JPG, PNG, WEBP, BMP):", type=["jpg", "png", "webp", "jpeg", "bmp"], accept_multiple_files=True, key="up_i2p")

    if uploaded_imgs:
        st.write(f"Selected **{len(uploaded_imgs)}** image(s)")
        if st.button("⚡ Convert Images to Single PDF", type="primary", key="btn_run_i2p"):
            with tempfile.TemporaryDirectory() as temp_dir:
                img_paths = []
                for img in uploaded_imgs:
                    ip = os.path.join(temp_dir, img.name)
                    with open(ip, "wb") as f:
                        f.write(img.getbuffer())
                    img_paths.append(ip)

                out_pdf = os.path.join(temp_dir, "images_combined.pdf")
                images_to_pdf(img_paths, out_pdf)

                with open(out_pdf, "rb") as f:
                    pdf_bytes = f.read()

                save_recent_file("images_combined.pdf", "Images to PDF", len(pdf_bytes) / 1024)
                st.success("🎉 Combined PDF generated successfully!")
                st.download_button("📥 Download Combined PDF", data=pdf_bytes, file_name="images_combined.pdf", mime="application/pdf", type="primary")
    st.markdown('</div>', unsafe_allow_html=True)


# =====================================================================
# VIEW 8: PDF TO IMAGES
# =====================================================================
elif st.session_state.current_view == "pdf2images":
    render_tool_header(
        "PDF to Images Converter",
        "Convert each page of your PDF into crisp PNG or JPG images at custom resolution.",
        '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><circle cx="10" cy="13" r="1.5"/><path d="m8 18 3-3 4 4"/>'
    )

    st.markdown('<div class="tool-card-panel">', unsafe_allow_html=True)
    uploaded_pdf = st.file_uploader("Upload PDF file:", type=["pdf"], key="up_p2i")

    if uploaded_pdf:
        c1, c2 = st.columns(2)
        with c1:
            img_format = st.selectbox("Format:", ["png", "jpg"], key="p2i_fmt")
        with c2:
            dpi = st.selectbox("Resolution (DPI):", [150, 200, 300, 72], index=0, key="p2i_dpi")

        if st.button("⚡ Export Pages as Images", type="primary", key="btn_run_p2i"):
            with tempfile.TemporaryDirectory() as temp_dir:
                in_pdf = os.path.join(temp_dir, uploaded_pdf.name)
                with open(in_pdf, "wb") as f:
                    f.write(uploaded_pdf.getbuffer())

                out_dir = os.path.join(temp_dir, "exported_imgs")
                imgs = pdf_to_images(in_pdf, out_dir, dpi=dpi, img_format=img_format)

                files_dict = {}
                for im in imgs:
                    with open(im, "rb") as imf:
                        files_dict[os.path.basename(im)] = imf.read()

                zip_data = get_zip_bytes(files_dict)
                save_recent_file(uploaded_pdf.name, "PDF to Images", len(zip_data) / 1024)
                st.success(f"🎉 Exported {len(imgs)} page(s) as images!")
                st.download_button("📥 Download Images (.ZIP)", data=zip_data, file_name="pdf_pages_images.zip", mime="application/zip", type="primary")
    st.markdown('</div>', unsafe_allow_html=True)


# =====================================================================
# VIEW 9: WATERMARK PDF
# =====================================================================
elif st.session_state.current_view == "watermark":
    render_tool_header(
        "Watermark PDF",
        "Add custom diagonal text watermarks across every page of your PDF.",
        '<circle cx="12" cy="12" r="9"/><path d="M12 3v18"/><path d="m4.93 4.93 14.14 14.14"/>'
    )

    st.markdown('<div class="tool-card-panel">', unsafe_allow_html=True)
    uploaded_pdf = st.file_uploader("Upload PDF to watermark:", type=["pdf"], key="up_wm")

    if uploaded_pdf:
        col1, col2, col3 = st.columns(3)
        with col1:
            wm_text = st.text_input("Watermark Text:", "CONFIDENTIAL", key="wm_text_val")
        with col2:
            font_size = st.number_input("Font Size:", min_value=10, max_value=120, value=45, key="wm_size_val")
        with col3:
            opacity = st.slider("Opacity:", min_value=0.05, max_value=0.8, value=0.22, step=0.05, key="wm_op_val")

        if st.button("⚡ Apply Watermark", type="primary", key="btn_run_wm"):
            with tempfile.TemporaryDirectory() as temp_dir:
                in_pdf = os.path.join(temp_dir, uploaded_pdf.name)
                out_pdf = os.path.join(temp_dir, "watermarked.pdf")
                with open(in_pdf, "wb") as f:
                    f.write(uploaded_pdf.getbuffer())

                watermark_pdf(in_pdf, out_pdf, text=wm_text, font_size=font_size, opacity=opacity)
                with open(out_pdf, "rb") as wf:
                    wm_bytes = wf.read()

                save_recent_file(f"watermarked_{uploaded_pdf.name}", "Watermark PDF", len(wm_bytes) / 1024)
                st.success("🎉 Watermark applied successfully!")
                st.download_button("📥 Download Watermarked PDF", data=wm_bytes, file_name=f"watermarked_{uploaded_pdf.name}", mime="application/pdf", type="primary")
    st.markdown('</div>', unsafe_allow_html=True)


# =====================================================================
# VIEW 10: PROTECT & UNLOCK
# =====================================================================
elif st.session_state.current_view == "protect":
    render_tool_header(
        "Protect & Unlock PDF",
        "Add 128-bit password encryption to your PDF or remove passwords from protected files.",
        '<rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>'
    )

    st.markdown('<div class="tool-card-panel">', unsafe_allow_html=True)
    sec_action = st.radio("Choose Action:", ["Encrypt & Set Password", "Decrypt & Remove Password"], horizontal=True, key="sec_act_choice")
    uploaded_pdf = st.file_uploader("Upload PDF file:", type=["pdf"], key="up_sec")

    if uploaded_pdf:
        password = st.text_input("Enter Password:", type="password", key="sec_pwd_val")
        if st.button("⚡ Process PDF", type="primary", key="btn_run_sec"):
            if not password:
                st.warning("Please enter a password.")
            else:
                with tempfile.TemporaryDirectory() as temp_dir:
                    in_path = os.path.join(temp_dir, uploaded_pdf.name)
                    out_path = os.path.join(temp_dir, "result.pdf")
                    with open(in_path, "wb") as f:
                        f.write(uploaded_pdf.getbuffer())

                    if "Encrypt" in sec_action:
                        protect_pdf(in_path, out_path, user_password=password)
                        with open(out_path, "rb") as pf:
                            p_bytes = pf.read()
                        save_recent_file(f"protected_{uploaded_pdf.name}", "Protect PDF", len(p_bytes) / 1024)
                        st.success("🎉 PDF encrypted successfully!")
                        st.download_button("📥 Download Protected PDF", data=p_bytes, file_name=f"protected_{uploaded_pdf.name}", mime="application/pdf", type="primary")
                    else:
                        ok = unlock_pdf(in_path, out_path, password=password)
                        if ok:
                            with open(out_path, "rb") as pf:
                                u_bytes = pf.read()
                            save_recent_file(f"unlocked_{uploaded_pdf.name}", "Unlock PDF", len(u_bytes) / 1024)
                            st.success("🎉 PDF unlocked successfully!")
                            st.download_button("📥 Download Unlocked PDF", data=u_bytes, file_name=f"unlocked_{uploaded_pdf.name}", mime="application/pdf", type="primary")
                        else:
                            st.error("❌ Incorrect password or decryption failed.")
    st.markdown('</div>', unsafe_allow_html=True)


# =====================================================================
# VIEW 11: EXTRACT CONTENT (TEXT & IMAGES) - HERO PANEL
# =====================================================================
elif st.session_state.current_view == "extract":
    render_tool_header(
        "Extract Content (Text & Media)",
        "Extract all readable text to TXT or export all raw embedded images at original quality.",
        '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/><line x1="11" y1="8" x2="11" y2="14"/><line x1="8" y1="11" x2="14" y2="11"/>'
    )

    st.markdown('<div class="tool-card-panel">', unsafe_allow_html=True)
    uploaded_pdf = st.file_uploader("Upload PDF file to extract from:", type=["pdf"], key="up_ext")

    if uploaded_pdf:
        t_text, t_imgs = st.tabs(["📄 Extract Readable Text", "🖼️ Extract Embedded Images"])

        with t_text:
            st.caption("Extracts all readable textual paragraphs into formatted plain text.")
            if st.button("⚡ Extract Text Now", type="primary", key="btn_ext_txt"):
                with tempfile.TemporaryDirectory() as temp_dir:
                    in_p = os.path.join(temp_dir, uploaded_pdf.name)
                    with open(in_p, "wb") as f:
                        f.write(uploaded_pdf.getbuffer())
                    raw_text = extract_text_from_pdf(in_p)
                    save_recent_file(uploaded_pdf.name, "Extract Text", len(raw_text.encode('utf-8')) / 1024)
                    st.success("🎉 Text extracted successfully!")
                    st.text_area("Extracted Content Preview:", raw_text, height=300)
                    st.download_button("📥 Download Text File (.TXT)", data=raw_text, file_name=f"{uploaded_pdf.name}.txt", mime="text/plain", type="primary")

        with t_imgs:
            st.caption("Dumps all original bitmap images (JPEG, PNG) embedded within the PDF.")
            if st.button("⚡ Extract Embedded Images", type="primary", key="btn_ext_imgs"):
                with tempfile.TemporaryDirectory() as temp_dir:
                    in_p = os.path.join(temp_dir, uploaded_pdf.name)
                    with open(in_p, "wb") as f:
                        f.write(uploaded_pdf.getbuffer())
                    img_dir = os.path.join(temp_dir, "extracted_imgs")
                    imgs = extract_embedded_images(in_p, img_dir)
                    if imgs:
                        files_dict = {}
                        for im in imgs:
                            with open(im, "rb") as imf:
                                files_dict[os.path.basename(im)] = imf.read()
                        zip_data = get_zip_bytes(files_dict)
                        save_recent_file(uploaded_pdf.name, "Extract Images", len(zip_data) / 1024)
                        st.success(f"🎉 Extracted **{len(imgs)}** embedded image(s)!")
                        st.download_button("📥 Download Extracted Images (.ZIP)", data=zip_data, file_name="extracted_images.zip", mime="application/zip", type="primary")
                    else:
                        st.info("No embedded raster images found in this PDF.")
    st.markdown('</div>', unsafe_allow_html=True)


# =====================================================================
# VIEW 12: ROTATE PDF
# =====================================================================
elif st.session_state.current_view == "rotate":
    render_tool_header(
        "Rotate PDF Pages",
        "Permanently rotate page orientation by 90°, 180°, or 270° clockwise.",
        '<path d="M21.5 2v6h-6"/><path d="M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/>'
    )

    st.markdown('<div class="tool-card-panel">', unsafe_allow_html=True)
    uploaded_pdf = st.file_uploader("Upload PDF file to rotate:", type=["pdf"], key="up_rot")

    if uploaded_pdf:
        rot_angle = st.selectbox("Rotation Angle:", [90, 180, 270], format_func=lambda a: f"{a}° Clockwise", key="rot_deg")
        if st.button("⚡ Rotate & Download", type="primary", key="btn_run_rot"):
            with tempfile.TemporaryDirectory() as temp_dir:
                in_p = os.path.join(temp_dir, uploaded_pdf.name)
                out_p = os.path.join(temp_dir, "rot.pdf")
                with open(in_p, "wb") as f:
                    f.write(uploaded_pdf.getbuffer())

                rotate_pdf_pages(in_p, out_p, angle=rot_angle)
                with open(out_p, "rb") as f:
                    rot_bytes = f.read()

                save_recent_file(f"rotated_{uploaded_pdf.name}", "Rotate PDF", len(rot_bytes) / 1024)
                st.success("🎉 PDF rotated successfully!")
                st.download_button("📥 Download Rotated PDF", data=rot_bytes, file_name=f"rotated_{uploaded_pdf.name}", mime="application/pdf", type="primary")
    st.markdown('</div>', unsafe_allow_html=True)


# =====================================================================
# VIEW 13: RECENT FILES FULL VIEW
# =====================================================================
elif st.session_state.current_view == "recent_view":
    st.markdown('<div class="back-btn-box">', unsafe_allow_html=True)
    if st.button("← Back to Dashboard", key="b_rec"):
        switch_view("dashboard")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("## 🕒 Recent Processed Files")
    recent_list = load_recent_files()
    if recent_list:
        for item in recent_list:
            st.markdown(f"""
            <div style="background: #FFFFFF; border: 1px solid #ECEEF1; border-radius: 8px; padding: 14px 18px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="font-weight: 700; color: #111827;">{item['filename']}</span>
                    <span style="background: #FFF0EB; color: #FF5A36; font-size: 0.78rem; font-weight: 600; padding: 2px 8px; border-radius: 4px; margin-left: 10px;">{item['tool']}</span>
                    <div style="color: #64748B; font-size: 0.8rem; margin-top: 4px;">Size: {item['size_kb']} KB</div>
                </div>
                <div style="color: #94A3B8; font-size: 0.82rem;">{item.get('timestamp', '')}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No recent files logged yet.")


# =====================================================================
# VIEW 14: SETTINGS & HELP
# =====================================================================
elif st.session_state.current_view in ("settings_view", "help_view"):
    st.markdown('<div class="back-btn-box">', unsafe_allow_html=True)
    if st.button("← Back to Dashboard", key="b_sh"):
        switch_view("dashboard")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.current_view == "settings_view":
        st.markdown("## ⚙️ Application Settings")
        st.markdown("""
        - **Project Name:** PDF Master Toolkit
        - **Engine:** Native PowerPoint COM + Word COM + PyMuPDF + PyPDF
        - **Mode:** 100% Offline, Local & Private
        - **Bulk Capability:** Unlimited files (optimized for 100+ presentations)
        """)
    else:
        st.markdown("## ❓ Help & Tips")
        st.markdown("""
        **Quick Tips:**
        1. **Bulk PPT to PDF:** When you have 100+ files, use the **Bulk Folder Mode**. It bypasses browser file upload limits and runs directly at native system speed.
        2. **Merge PDFs:** Drag & drop your PDF documents in the order you want them combined.
        3. **Compress PDF:** PyMuPDF optimizes stream objects and downsamples large embedded photos without visible quality degradation.
        4. **Extract Content:** Quickly grab text or extract embedded photos without recompressing.
        """)
