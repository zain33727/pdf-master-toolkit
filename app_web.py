"""
PDF Master Toolkit - Modern Web Application
Matching exact Document Automation Dashboard UI
(Merge PDF, Split PDF, Compress PDF, Protect PDF, PPT to PDF)
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
    page_title="Document Automation - PDF Master Toolkit",
    page_icon="📄",
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
    recent = recent[:20]
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


# Initialize session state for navigation
if "current_view" not in st.session_state:
    st.session_state.current_view = "dashboard"

# Complete CSS Overrides to Force Light Theme and Exact Card Layout
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    /* Force Light Mode Global Backgrounds */
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main, section.main {
        background-color: #F8F9FA !important;
        color: #1E293B !important;
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }

    /* Hide standard Streamlit header & footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Main container width & padding */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        padding-left: 2.5rem !important;
        padding-right: 2.5rem !important;
        max-width: 1260px !important;
        background-color: #F8F9FA !important;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"], section[data-testid="stSidebar"], [data-testid="stSidebarContent"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #ECEEF1 !important;
    }
    [data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem !important;
        padding-left: 1.2rem !important;
        padding-right: 1.2rem !important;
        background-color: #FFFFFF !important;
    }

    /* Dark Badge in Sidebar */
    .sidebar-badge {
        display: inline-block;
        background-color: #18181B;
        color: #FFFFFF;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding: 5px 12px;
        border-radius: 4px;
        margin-bottom: 1.2rem;
    }

    /* Clean Sidebar Nav Buttons */
    [data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        border: none !important;
        color: #475569 !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 9px 14px !important;
        font-weight: 500 !important;
        font-size: 0.92rem !important;
        border-radius: 8px !important;
        box-shadow: none !important;
        width: 100% !important;
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

    /* Card Containers (st.container with border=True) */
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
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #FFD4C9 !important;
        box-shadow: 0 6px 16px rgba(255, 90, 54, 0.08) !important;
        transform: translateY(-2px) !important;
    }

    /* Icon Box Inside Cards */
    .card-icon-box {
        width: 48px;
        height: 48px;
        border-radius: 10px;
        background-color: #FFF0EB;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 14px;
    }

    .card-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 4px;
    }

    .card-desc {
        font-size: 0.88rem;
        color: #64748B;
        line-height: 1.4;
        margin-bottom: 16px;
        min-height: 38px;
    }

    /* Primary Coral Buttons Inside Cards */
    .stButton > button[kind="primary"] {
        background-color: #FF5A36 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        padding: 0.65rem 1rem !important;
        width: 100% !important;
        box-shadow: 0 1px 2px rgba(255, 90, 54, 0.2) !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #E64724 !important;
        box-shadow: 0 4px 8px rgba(255, 90, 54, 0.3) !important;
    }
    .stButton > button[kind="primary"]:active {
        transform: translateY(1px);
    }

    .card-subtext {
        font-size: 0.8rem;
        color: #94A3B8;
        text-align: center;
        margin-top: 8px;
        margin-bottom: 2px;
    }

    /* Promo / Feature Card Styling */
    .promo-container {
        background-color: #FFF5F0;
        border: 1px solid #FFE4D9;
        border-radius: 14px;
        padding: 24px 22px;
        min-height: 250px;
        box-sizing: border-box;
    }
    .promo-icon-box {
        width: 44px;
        height: 44px;
        border-radius: 10px;
        background-color: #FFFFFF;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 14px;
    }
    .promo-title {
        font-size: 1.12rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 16px;
        line-height: 1.35;
    }
    .promo-item {
        font-size: 0.88rem;
        color: #334155;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .promo-check {
        color: #FF5A36;
        font-weight: 700;
        font-size: 1rem;
    }

    /* Recent Files Section */
    .recent-section-header {
        margin-top: 36px;
        margin-bottom: 16px;
        padding-top: 18px;
        border-top: 1px solid #ECEEF1;
    }
    .recent-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #111827;
    }

    /* Tool Workspace Panels */
    .action-panel {
        background: #FFFFFF;
        border: 1px solid #EAEBEF;
        border-radius: 14px;
        padding: 26px 30px;
        margin-top: 12px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
    }
</style>
""", unsafe_allow_html=True)


# =====================================================================
# SIDEBAR
# =====================================================================
with st.sidebar:
    st.markdown('<div class="sidebar-badge">DOCUMENT AUTOMATION</div>', unsafe_allow_html=True)

    nav_items = [
        ("dashboard", "🏠 Dashboard"),
        ("merge", "📑 Merge PDF"),
        ("split", "✂️ Split PDF"),
        ("compress", "🗜️ Compress PDF"),
        ("protect", "🔒 Protect PDF"),
        ("ppt2pdf", "📊 PPT to PDF"),
        ("more_tools", "🛠️ More Tools"),
    ]

    for key, label in nav_items:
        is_active = (st.session_state.current_view == key)
        btn_type = "primary" if is_active else "secondary"
        if st.button(label, key=f"nav_{key}", type=btn_type):
            st.session_state.current_view = key
            st.rerun()

    st.markdown("<hr style='border: none; border-top: 1px solid #ECEEF1; margin: 20px 0 14px 0;'>", unsafe_allow_html=True)

    if st.button("🕒 Recent Files", key="nav_recent", type="secondary"):
        st.session_state.current_view = "recent_view"
        st.rerun()

    if st.button("⚙️ Settings", key="nav_settings", type="secondary"):
        st.session_state.current_view = "settings_view"
        st.rerun()

    if st.button("❓ Help", key="nav_help", type="secondary"):
        st.session_state.current_view = "help_view"
        st.rerun()


def switch_view(view_name):
    st.session_state.current_view = view_name
    st.rerun()


# =====================================================================
# VIEW 1: DASHBOARD (EXACT SCREENSHOT LAYOUT - UNIFIED CARDS)
# =====================================================================
if st.session_state.current_view == "dashboard":
    # Row 1: Merge PDF, Split PDF, Compress PDF
    c1, c2, c3 = st.columns(3, gap="medium")

    # Card 1: Merge PDF
    with c1:
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
            <div class="card-desc">Combine multiple PDF files into one.</div>
            """, unsafe_allow_html=True)
            if st.button("Select Files", key="btn_card_merge", type="primary"):
                switch_view("merge")
            st.markdown('<div class="card-subtext">No files selected</div>', unsafe_allow_html=True)

    # Card 2: Split PDF
    with c2:
        with st.container(border=True):
            st.markdown("""
            <div class="card-icon-box">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#FF5A36" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V8L14 2Z"/>
                    <line x1="2" y1="12" x2="22" y2="12" stroke-dasharray="3 3"/>
                </svg>
            </div>
            <div class="card-title">Split PDF</div>
            <div class="card-desc">Extract pages or split into multiple files.</div>
            """, unsafe_allow_html=True)
            if st.button("Select File", key="btn_card_split", type="primary"):
                switch_view("split")
            st.markdown('<div class="card-subtext">No file selected</div>', unsafe_allow_html=True)

    # Card 3: Compress PDF
    with c3:
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
            <div class="card-desc">Reduce file size while keeping quality.</div>
            """, unsafe_allow_html=True)
            if st.button("Select File", key="btn_card_compress", type="primary"):
                switch_view("compress")
            st.markdown('<div class="card-subtext">No file selected</div>', unsafe_allow_html=True)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Row 2: Protect PDF, PPT to PDF, Promo Banner Card
    c4, c5, c6 = st.columns(3, gap="medium")

    # Card 4: Protect PDF
    with c4:
        with st.container(border=True):
            st.markdown("""
            <div class="card-icon-box">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#FF5A36" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                    <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
            </div>
            <div class="card-title">Protect PDF</div>
            <div class="card-desc">Add a password and set permissions.</div>
            """, unsafe_allow_html=True)
            if st.button("Select File", key="btn_card_protect", type="primary"):
                switch_view("protect")
            st.markdown('<div class="card-subtext">No file selected</div>', unsafe_allow_html=True)

    # Card 5: PPT to PDF
    with c5:
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
            <div class="card-title">PPT to PDF</div>
            <div class="card-desc">Convert PowerPoint files to PDF.</div>
            """, unsafe_allow_html=True)
            if st.button("Select File", key="btn_card_ppt", type="primary"):
                switch_view("ppt2pdf")
            st.markdown('<div class="card-subtext">No file selected</div>', unsafe_allow_html=True)

    # Card 6: Promo Value Banner Card
    with c6:
        st.markdown("""
        <div class="promo-container">
            <div class="promo-icon-box">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#FF5A36" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V8L14 2Z"/>
                    <path d="M14 2V8H20"/>
                    <line x1="16" y1="13" x2="8" y2="13"/>
                    <line x1="16" y1="17" x2="8" y2="17"/>
                </svg>
            </div>
            <div class="promo-title">Five powerful tools.<br>One reliable workspace.</div>
            <div class="promo-item"><span class="promo-check">✓</span> 100% offline</div>
            <div class="promo-item"><span class="promo-check">✓</span> Your files stay on your computer</div>
            <div class="promo-item"><span class="promo-check">✓</span> Fast and easy to use</div>
        </div>
        """, unsafe_allow_html=True)

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
        <div style="background-color: #FFFFFF; border: 1px dashed #CBD5E1; border-radius: 10px; padding: 26px; text-align: center; color: #94A3B8;">
            <p style="margin: 0; font-size: 0.95rem;">No recent files yet. Select a tool above to start converting or processing your documents.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for idx, item in enumerate(recent_list[:5]):
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
# VIEW 2: PPT TO PDF (WITH HIGH-SPEED BULK 100+ FILES SUPPORT)
# =====================================================================
elif st.session_state.current_view == "ppt2pdf":
    c_back, _ = st.columns([2, 8])
    with c_back:
        if st.button("← Back to Dashboard", key="back_from_ppt"):
            switch_view("dashboard")

    st.markdown("""
    <div style="display: flex; align-items: center; gap: 14px; margin: 12px 0 20px 0;">
        <div class="card-icon-box" style="margin: 0;">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#FF5A36" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="2" y="3" width="20" height="14" rx="2"/>
                <line x1="8" y1="21" x2="16" y2="21"/>
                <line x1="12" y1="17" x2="12" y2="21"/>
                <path d="M9 8H12C12.8 8 13.5 8.7 13.5 9.5C13.5 10.3 12.8 11 12 11H9V13"/>
            </svg>
        </div>
        <div>
            <h2 style="margin: 0; font-size: 1.55rem; color: #111827;">PowerPoint to PDF Converter</h2>
            <p style="margin: 0; color: #64748B; font-size: 0.92rem;">Convert single presentations or scan an entire folder of 100+ files in seconds.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_bulk, tab_upload = st.tabs(["📁 Bulk Folder Mode (Fastest for 100+ Presentations)", "📤 Upload Files via Browser"])

    with tab_bulk:
        st.markdown('<div class="action-panel">', unsafe_allow_html=True)
        st.markdown("#### ⚡ Bulk Folder Converter")
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
                        save_recent_file(f"Batch ({res['success']} PPT files)", "PPT to PDF", 1024.0)

                        if out_dir and os.path.isdir(out_dir):
                            st.info(f"PDF files saved in: `{out_dir}`")
            else:
                st.warning("Specified path does not exist or is not a directory.")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_upload:
        st.markdown('<div class="action-panel">', unsafe_allow_html=True)
        st.markdown("#### 📤 Upload Files")
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
                        save_recent_file(uploaded_ppts[0].name, "PPT to PDF", len(zip_data) / 1024)
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
    c_back, _ = st.columns([2, 8])
    with c_back:
        if st.button("← Back to Dashboard", key="back_from_merge"):
            switch_view("dashboard")

    st.markdown("""
    <div style="display: flex; align-items: center; gap: 14px; margin: 12px 0 20px 0;">
        <div class="card-icon-box" style="margin: 0;">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#FF5A36" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M8 2H14L19 7V17C19 18.1 18.1 19 17 19H8C6.9 19 6 18.1 6 17V4C6 2.9 6.9 2 8 2Z"/>
                <path d="M14 2V7H19"/>
                <path d="M4 8H3C2.45 8 2 8.45 2 9V21C2 22.1 2.9 23 4 23H13C13.55 23 14 22.55 14 22V21"/>
            </svg>
        </div>
        <div>
            <h2 style="margin: 0; font-size: 1.55rem; color: #111827;">Merge PDF Files</h2>
            <p style="margin: 0; color: #64748B; font-size: 0.92rem;">Combine two or more PDF documents into a single document.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="action-panel">', unsafe_allow_html=True)
    uploaded_pdfs = st.file_uploader(
        "Select PDF files to merge (order matters):",
        type=["pdf"],
        accept_multiple_files=True,
        key="uploader_merge"
    )

    if uploaded_pdfs:
        st.markdown(f"**Files ready to combine ({len(uploaded_pdfs)}):**")
        for idx, f in enumerate(uploaded_pdfs, 1):
            st.caption(f"{idx}. {f.name} ({round(len(f.getvalue()) / 1024, 1)} KB)")

        if len(uploaded_pdfs) >= 2:
            if st.button("⚡ Merge PDFs Now", type="primary", key="btn_run_merge"):
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
    c_back, _ = st.columns([2, 8])
    with c_back:
        if st.button("← Back to Dashboard", key="back_from_split"):
            switch_view("dashboard")

    st.markdown("""
    <div style="display: flex; align-items: center; gap: 14px; margin: 12px 0 20px 0;">
        <div class="card-icon-box" style="margin: 0;">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#FF5A36" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V8L14 2Z"/>
                <line x1="2" y1="12" x2="22" y2="12" stroke-dasharray="3 3"/>
            </svg>
        </div>
        <div>
            <h2 style="margin: 0; font-size: 1.55rem; color: #111827;">Split PDF</h2>
            <p style="margin: 0; color: #64748B; font-size: 0.92rem;">Extract individual pages or custom page ranges into new documents.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="action-panel">', unsafe_allow_html=True)
    uploaded_pdf = st.file_uploader("Upload PDF file to split:", type=["pdf"], key="uploader_split")

    if uploaded_pdf:
        split_mode = st.radio("Splitting Strategy:", ["Split into individual pages (1 PDF per page)", "Extract custom page ranges (e.g. 1-3, 5)"])
        range_val = ""
        if "Extract" in split_mode:
            range_val = st.text_input("Enter Page Ranges:", "1-3, 5")

        if st.button("⚡ Split PDF Now", type="primary", key="btn_run_split"):
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
    c_back, _ = st.columns([2, 8])
    with c_back:
        if st.button("← Back to Dashboard", key="back_from_comp"):
            switch_view("dashboard")

    st.markdown("""
    <div style="display: flex; align-items: center; gap: 14px; margin: 12px 0 20px 0;">
        <div class="card-icon-box" style="margin: 0;">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#FF5A36" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M4 14H10V20"/>
                <path d="M10 14L3 21"/>
                <path d="M20 10H14V4"/>
                <path d="M14 10L21 3"/>
            </svg>
        </div>
        <div>
            <h2 style="margin: 0; font-size: 1.55rem; color: #111827;">Compress PDF</h2>
            <p style="margin: 0; color: #64748B; font-size: 0.92rem;">Shrink PDF file size while preserving high visual fidelity.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="action-panel">', unsafe_allow_html=True)
    uploaded_pdf = st.file_uploader("Upload PDF file to compress:", type=["pdf"], key="uploader_comp")

    if uploaded_pdf:
        orig_kb = round(len(uploaded_pdf.getvalue()) / 1024, 2)
        st.info(f"Original File Size: **{orig_kb} KB** ({round(orig_kb / 1024, 2)} MB)")

        if st.button("⚡ Compress PDF Now", type="primary", key="btn_run_comp"):
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
# VIEW 6: PROTECT PDF
# =====================================================================
elif st.session_state.current_view == "protect":
    c_back, _ = st.columns([2, 8])
    with c_back:
        if st.button("← Back to Dashboard", key="back_from_protect"):
            switch_view("dashboard")

    st.markdown("""
    <div style="display: flex; align-items: center; gap: 14px; margin: 12px 0 20px 0;">
        <div class="card-icon-box" style="margin: 0;">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#FF5A36" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
            </svg>
        </div>
        <div>
            <h2 style="margin: 0; font-size: 1.55rem; color: #111827;">Protect & Unlock PDF</h2>
            <p style="margin: 0; color: #64748B; font-size: 0.92rem;">Add 128-bit password encryption or remove protection from your documents.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="action-panel">', unsafe_allow_html=True)
    sec_action = st.radio("Choose Action:", ["Encrypt & Set Password", "Decrypt & Remove Password"], horizontal=True)
    uploaded_pdf = st.file_uploader("Upload PDF file:", type=["pdf"], key="uploader_sec")

    if uploaded_pdf:
        password = st.text_input("Enter Password:", type="password", key="sec_pwd")
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
                        st.success("🎉 PDF encrypted and protected successfully!")
                        st.download_button(
                            label="📥 Download Protected PDF",
                            data=p_bytes,
                            file_name=f"protected_{uploaded_pdf.name}",
                            mime="application/pdf",
                            type="primary"
                        )
                    else:
                        ok = unlock_pdf(in_path, out_path, password=password)
                        if ok:
                            with open(out_path, "rb") as pf:
                                u_bytes = pf.read()
                            save_recent_file(f"unlocked_{uploaded_pdf.name}", "Unlock PDF", len(u_bytes) / 1024)
                            st.success("🎉 PDF unlocked successfully!")
                            st.download_button(
                                label="📥 Download Unlocked PDF",
                                data=u_bytes,
                                file_name=f"unlocked_{uploaded_pdf.name}",
                                mime="application/pdf",
                                type="primary"
                            )
                        else:
                            st.error("❌ Incorrect password or decryption failed.")
    st.markdown('</div>', unsafe_allow_html=True)


# =====================================================================
# VIEW 7: MORE TOOLS
# =====================================================================
elif st.session_state.current_view == "more_tools":
    c_back, _ = st.columns([2, 8])
    with c_back:
        if st.button("← Back to Dashboard", key="back_from_more"):
            switch_view("dashboard")

    st.markdown("## 🛠️ Additional PDF Master Tools")
    t1, t2, t3, t4 = st.tabs(["🖼️ Images ↔ PDF", "💧 Add Watermark", "🔄 Rotate PDF", "📝 Extract Text"])

    with t1:
        st.markdown("#### Convert Images to PDF")
        uploaded_imgs = st.file_uploader("Select JPG/PNG images:", type=["jpg", "png", "webp", "jpeg"], accept_multiple_files=True)
        if uploaded_imgs and st.button("⚡ Combine Images to PDF", type="primary"):
            with tempfile.TemporaryDirectory() as temp_dir:
                img_paths = []
                for img in uploaded_imgs:
                    ip = os.path.join(temp_dir, img.name)
                    with open(ip, "wb") as f:
                        f.write(img.getbuffer())
                    img_paths.append(ip)
                out_pdf = os.path.join(temp_dir, "combined_images.pdf")
                images_to_pdf(img_paths, out_pdf)
                with open(out_pdf, "rb") as f:
                    pdf_data = f.read()
                st.success("✓ Combined PDF created!")
                st.download_button("📥 Download PDF", pdf_data, file_name="images_combined.pdf", mime="application/pdf")

    with t2:
        st.markdown("#### Apply Diagonal Watermark")
        wm_pdf = st.file_uploader("Select PDF to watermark:", type=["pdf"], key="wm_uploader")
        wm_txt = st.text_input("Watermark text:", "CONFIDENTIAL")
        if wm_pdf and st.button("⚡ Apply Watermark", type="primary"):
            with tempfile.TemporaryDirectory() as temp_dir:
                in_p = os.path.join(temp_dir, wm_pdf.name)
                out_p = os.path.join(temp_dir, "wm.pdf")
                with open(in_p, "wb") as f:
                    f.write(wm_pdf.getbuffer())
                watermark_pdf(in_p, out_p, text=wm_txt)
                with open(out_p, "rb") as f:
                    st.download_button("📥 Download Watermarked PDF", f.read(), file_name=f"watermarked_{wm_pdf.name}", mime="application/pdf")

    with t3:
        st.markdown("#### Rotate PDF Pages")
        rot_pdf = st.file_uploader("Select PDF to rotate:", type=["pdf"], key="rot_uploader")
        rot_angle = st.selectbox("Angle:", [90, 180, 270], format_func=lambda a: f"{a}° Clockwise")
        if rot_pdf and st.button("⚡ Rotate & Download", type="primary"):
            with tempfile.TemporaryDirectory() as temp_dir:
                in_p = os.path.join(temp_dir, rot_pdf.name)
                out_p = os.path.join(temp_dir, "rot.pdf")
                with open(in_p, "wb") as f:
                    f.write(rot_pdf.getbuffer())
                rotate_pdf_pages(in_p, out_p, angle=rot_angle)
                with open(out_p, "rb") as f:
                    st.download_button("📥 Download Rotated PDF", f.read(), file_name=f"rotated_{rot_pdf.name}", mime="application/pdf")

    with t4:
        st.markdown("#### Extract Text")
        txt_pdf = st.file_uploader("Select PDF to extract text from:", type=["pdf"], key="txt_uploader")
        if txt_pdf and st.button("⚡ Extract Text Now", type="primary"):
            with tempfile.TemporaryDirectory() as temp_dir:
                in_p = os.path.join(temp_dir, txt_pdf.name)
                with open(in_p, "wb") as f:
                    f.write(txt_pdf.getbuffer())
                raw_text = extract_text_from_pdf(in_p)
                st.text_area("Extracted Content:", raw_text, height=260)
                st.download_button("📥 Download .txt", raw_text, file_name=f"{txt_pdf.name}.txt")


# =====================================================================
# VIEW 8: RECENT FILES FULL VIEW
# =====================================================================
elif st.session_state.current_view == "recent_view":
    c_back, _ = st.columns([2, 8])
    with c_back:
        if st.button("← Back to Dashboard"):
            switch_view("dashboard")

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
# VIEW 9: SETTINGS & HELP
# =====================================================================
elif st.session_state.current_view in ("settings_view", "help_view"):
    c_back, _ = st.columns([2, 8])
    with c_back:
        if st.button("← Back to Dashboard"):
            switch_view("dashboard")

    if st.session_state.current_view == "settings_view":
        st.markdown("## ⚙️ Application Settings")
        st.markdown("""
        - **Engine:** Native Microsoft PowerPoint COM + PyMuPDF + PyPDF
        - **Execution Mode:** 100% Offline & Local
        - **Temporary Storage:** Automatically sanitized upon task completion
        """)
    else:
        st.markdown("## ❓ Help & Documentation")
        st.markdown("""
        **Quick Tips:**
        1. **Bulk PPT to PDF:** Use the **Bulk Folder Mode** when you have 100+ presentations. It avoids browser upload limits and runs at native speed.
        2. **Merge PDFs:** Drag & drop PDFs in the order you want them combined.
        3. **Compress PDF:** PyMuPDF optimizes object streams and downsamples large embedded photos without visible quality degradation.
        """)
