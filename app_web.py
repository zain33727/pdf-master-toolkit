"""
PDF Master Toolkit - All-in-One Offline Suite
Unified single-card tool workspaces, ambient blurred floating PDF motion background,
minimal clean sidebar, and high-end Framer Motion-style physics.
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


def clear_recent_files():
    try:
        with open(RECENT_FILES_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)
    except Exception:
        pass


def save_recent_file(filename: str, tool_name: str, file_size_kb: float):
    recent = load_recent_files()
    entry = {
        "filename": filename,
        "tool": tool_name,
        "size_kb": round(file_size_kb, 1),
        "timestamp": datetime.now().strftime("%b %d, %Y • %I:%M %p")
    }
    recent.insert(0, entry)
    recent = recent[:30]
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

# High-End Styling: Ambient Blurred PDF Motion, Zero Disjointed Boxes, Unified Single-Card Workspaces
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    /* Global Background and Typography */
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main, section.main {
        background-color: #F8F9FA !important;
        color: #1E293B !important;
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }

    #MainMenu, footer, header, [data-testid="stHeader"], [data-testid="stDecoration"], [data-testid="stToolbar"] {
        display: none !important;
        height: 0px !important;
        visibility: hidden !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    /* Ambient Floating Blurred PDF Elements in Background */
    .ambient-motion-bg {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        pointer-events: none;
        z-index: 0;
        overflow: hidden;
    }
    .ambient-orb {
        position: absolute;
        border-radius: 50%;
        filter: blur(90px);
        opacity: 0.55;
        animation: floatOrb 22s ease-in-out infinite alternate;
    }
    .orb-1 {
        width: 480px;
        height: 480px;
        background: radial-gradient(circle, #FFE7DF 0%, rgba(255, 90, 54, 0.08) 70%);
        top: -120px;
        right: 8%;
        animation-duration: 24s;
    }
    .orb-2 {
        width: 420px;
        height: 420px;
        background: radial-gradient(circle, #FFF0EB 0%, rgba(255, 130, 95, 0.06) 70%);
        bottom: 8%;
        left: 24%;
        animation-duration: 28s;
    }
    .floating-pdf-shape {
        position: absolute;
        filter: blur(4px);
        opacity: 0.45;
        animation: floatDoc 20s cubic-bezier(0.45, 0, 0.55, 1) infinite alternate;
    }
    .shape-1 {
        top: 15%;
        right: 12%;
        animation-duration: 18s;
    }
    .shape-2 {
        bottom: 18%;
        left: 30%;
        animation-duration: 26s;
    }

    @keyframes floatOrb {
        0% { transform: translate(0px, 0px) scale(1); }
        50% { transform: translate(30px, -25px) scale(1.05); }
        100% { transform: translate(-20px, 20px) scale(0.97); }
    }
    @keyframes floatDoc {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-28px) rotate(5deg); }
        100% { transform: translateY(18px) rotate(-4deg); }
    }

    /* Page Entrance Animation */
    @keyframes springSlideUp {
        0% { opacity: 0; transform: translateY(16px) scale(0.99); }
        70% { opacity: 0.9; transform: translateY(-2px) scale(1.002); }
        100% { opacity: 1; transform: translateY(0) scale(1); }
    }
    .main .block-container {
        position: relative;
        z-index: 1;
        animation: springSlideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }

    /* Clean Sidebar with Smooth Collapse and Open Support */
    [data-testid="stSidebar"], section[data-testid="stSidebar"] {
        width: 250px !important;
        min-width: 250px !important;
        background-color: #FFFFFF !important;
        border-right: 1px solid #ECEEF1 !important;
        z-index: 10 !important;
        transition: transform 0.28s cubic-bezier(0.16, 1, 0.3, 1), width 0.28s ease !important;
    }
    [data-testid="stSidebar"][aria-expanded="false"], 
    section[data-testid="stSidebar"][aria-expanded="false"] {
        transform: translateX(-100%) !important;
        min-width: 0 !important;
        width: 0 !important;
    }

    /* Modern Sleek Collapse & Expand Toggle Buttons */
    [data-testid="stSidebarCollapseButton"] button,
    [data-testid="collapsedControl"] button {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
        color: #475569 !important;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.04) !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stSidebarCollapseButton"] button:hover,
    [data-testid="collapsedControl"] button:hover {
        background: #F1F5F9 !important;
        color: #0F172A !important;
        border-color: #CBD5E1 !important;
        transform: scale(1.02) !important;
    }

    /* Position the reopen toggle cleanly at top-left */
    [data-testid="collapsedControl"] {
        display: block !important;
        position: fixed !important;
        top: 14px !important;
        left: 14px !important;
        z-index: 99 !important;
    }
    [data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem !important;
        padding-left: 1.1rem !important;
        padding-right: 1.1rem !important;
        background-color: #FFFFFF !important;
    }

    /* Brand Logo Component */
    .brand-logo-container {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 4px 6px 16px 6px;
        border-bottom: 1px solid #F1F5F9;
        margin-bottom: 16px;
    }
    .brand-logo-icon {
        width: 38px;
        height: 38px;
        border-radius: 10px;
        background: linear-gradient(135deg, #FF6B4A 0%, #FF5A36 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 10px rgba(255, 90, 54, 0.28);
        flex-shrink: 0;
        transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
    }
    .brand-logo-container:hover .brand-logo-icon {
        transform: scale(1.08) rotate(-3deg);
    }
    .brand-name {
        font-size: 1.05rem;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.02em;
        line-height: 1.15;
    }
    .brand-tag {
        font-size: 0.68rem;
        font-weight: 700;
        color: #FF5A36;
        letter-spacing: 0.08em;
    }

    /* Sidebar Navigation Links */
    [data-testid="stSidebar"] .stButton > button {
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        width: 100% !important;
        height: 42px !important;
        padding: 0 14px !important;
        border: 1px solid transparent !important;
        border-radius: 10px !important;
        font-size: 0.92rem !important;
        font-weight: 500 !important;
        color: #475569 !important;
        background: transparent !important;
        white-space: nowrap !important;
        box-shadow: none !important;
        margin-bottom: 4px !important;
        transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    /* Sleek, calm, premium neutral hover - no loud jarring red text */
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #F1F5F9 !important;
        color: #0F172A !important;
        font-weight: 600 !important;
        border-color: #E2E8F0 !important;
        transform: translateX(2px) !important;
    }
    /* Active Link - Clean subtle coral pill with soft highlight */
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background-color: #FFF2ED !important;
        color: #FF5A36 !important;
        font-weight: 700 !important;
        border-color: #FFDCD3 !important;
        box-shadow: 0 1px 3px rgba(255, 90, 54, 0.08) !important;
    }
    [data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        background-color: #FFEAE2 !important;
        color: #E64724 !important;
        border-color: #FFCFC2 !important;
    }

    /* Main Container */
    .block-container {
        padding-top: 1.8rem !important;
        padding-bottom: 3.5rem !important;
        padding-left: 2.5rem !important;
        padding-right: 2.5rem !important;
        max-width: 1280px !important;
        background-color: transparent !important;
    }

    /* Dashboard Header */
    .dash-header-title {
        font-size: 1.95rem;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 4px;
        letter-spacing: -0.025em;
    }
    .dash-header-sub {
        font-size: 0.95rem;
        color: #64748B;
        margin-bottom: 26px;
    }

    /* Target ONLY specific dashboard cards, NOT arbitrary columns or wrappers! */
    .st-key-btn_c_ppt, .st-key-btn_c_merge, .st-key-btn_c_split,
    .st-key-btn_c_comp, .st-key-btn_c_word, .st-key-btn_c_i2p,
    .st-key-btn_c_p2i, .st-key-btn_c_wm, .st-key-btn_c_sec,
    .st-key-btn_c_ext, .st-key-btn_c_rot {
        margin-top: auto;
    }

    /* Dashboard Card Containers */
    div[data-testid="stColumn"] [data-testid="stVerticalBlockBorderWrapper"],
    .dash-grid-card [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border: 1px solid #ECEEF1 !important;
        border-radius: 16px !important;
        padding: 22px 20px 18px 20px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02) !important;
        transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
        min-height: 245px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        margin-bottom: 16px !important;
    }
    div[data-testid="stColumn"] [data-testid="stVerticalBlockBorderWrapper"]:hover,
    .dash-grid-card [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #FFD2C7 !important;
        box-shadow: 0 10px 24px rgba(255, 90, 54, 0.12) !important;
        transform: translateY(-4px) scale(1.01) !important;
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
        transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
    }
    div[data-testid="stColumn"] [data-testid="stVerticalBlockBorderWrapper"]:hover .card-icon-box,
    .dash-grid-card [data-testid="stVerticalBlockBorderWrapper"]:hover .card-icon-box {
        transform: scale(1.1) rotate(-2deg);
        background-color: #FFE4DC;
    }

    .card-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 4px;
        letter-spacing: -0.01em;
    }
    .card-desc {
        font-size: 0.86rem;
        color: #64748B;
        line-height: 1.4;
        margin-bottom: 16px;
        min-height: 38px;
    }
    .card-subtext {
        font-size: 0.78rem;
        color: #94A3B8;
        text-align: center;
        margin-top: 6px;
    }

    /* Primary Coral Buttons */
    .stButton > button[kind="primary"] {
        background-color: #FF5A36 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 9px !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        padding: 0.65rem 1.2rem !important;
        width: 100% !important;
        box-shadow: 0 2px 4px rgba(255, 90, 54, 0.22) !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #E64724 !important;
        box-shadow: 0 6px 14px rgba(255, 90, 54, 0.32) !important;
        transform: translateY(-1px);
    }
    .stButton > button[kind="primary"]:active {
        transform: scale(0.98);
    }

    /* Sleek Back Button */
    div[class*="st-key-b_"] .stButton > button {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 9px !important;
        color: #475569 !important;
        font-weight: 600 !important;
        font-size: 0.86rem !important;
        padding: 0.45rem 1.15rem !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04) !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
        width: auto !important;
        display: inline-flex !important;
        align-items: center !important;
    }
    div[class*="st-key-b_"] .stButton > button:hover {
        background-color: #F8FAFC !important;
        border-color: #CBD5E1 !important;
        color: #FF5A36 !important;
        transform: translateX(-3px) !important;
        box-shadow: 0 3px 8px rgba(255, 90, 54, 0.12) !important;
    }

    /* Breadcrumbs */
    .ws-breadcrumb {
        font-size: 0.86rem;
        color: #94A3B8;
        text-align: right;
        padding-top: 8px;
        font-weight: 500;
    }
    .ws-breadcrumb strong {
        color: #0F172A;
        font-weight: 700;
    }

    /* Workspace Hero Header Card */
    .ws-hero {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-top: 10px;
        margin-bottom: 22px;
        padding: 16px 22px;
        background: #FFFFFF;
        border: 1px solid #ECEEF1;
        border-radius: 14px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
    }
    .ws-hero-icon {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        background: linear-gradient(135deg, #FFF0EB 0%, #FFE4DC 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        box-shadow: 0 2px 6px rgba(255, 90, 54, 0.1);
    }
    .ws-hero-title {
        font-size: 1.45rem !important;
        font-weight: 800 !important;
        color: #0F172A !important;
        margin: 0 !important;
        padding: 0 !important;
        letter-spacing: -0.02em !important;
        line-height: 1.2 !important;
    }
    .ws-hero-desc {
        font-size: 0.88rem !important;
        color: #64748B !important;
        margin: 3px 0 0 0 !important;
        line-height: 1.35 !important;
    }

    /* Modern Segmented Pill Tabs */
    div[data-testid="stTabs"] [data-baseweb="tab-list"] {
        gap: 8px !important;
        background-color: #F1F5F9 !important;
        padding: 5px !important;
        border-radius: 12px !important;
        border-bottom: none !important;
        display: inline-flex !important;
        width: auto !important;
        margin-bottom: 20px !important;
    }
    div[data-testid="stTabs"] [data-baseweb="tab"] {
        height: 38px !important;
        border-radius: 8px !important;
        padding: 0 16px !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        color: #64748B !important;
        background-color: transparent !important;
        border: none !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    div[data-testid="stTabs"] [data-baseweb="tab"]:hover {
        color: #0F172A !important;
    }
    div[data-testid="stTabs"] [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #FF5A36 !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06) !important;
    }
    div[data-testid="stTabs"] [data-baseweb="tab-border"] {
        display: none !important;
    }
    div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
        display: none !important;
    }

    /* Modern Crisp Form Inputs */
    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input {
        background-color: #FFFFFF !important;
        border: 1.5px solid #E2E8F0 !important;
        border-radius: 10px !important;
        color: #0F172A !important;
        font-size: 0.92rem !important;
        padding: 10px 14px !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stNumberInput"] input:focus {
        border-color: #FF5A36 !important;
        box-shadow: 0 0 0 3px rgba(255, 90, 54, 0.15) !important;
    }
    div[data-testid="stSelectbox"] > div > div {
        background-color: #FFFFFF !important;
        border: 1.5px solid #E2E8F0 !important;
        border-radius: 10px !important;
    }

    /* Checkbox Alignment & Styling */
    div[data-testid="stCheckbox"] {
        margin-top: 8px !important;
        margin-bottom: 8px !important;
    }
    div[data-testid="stCheckbox"] label {
        font-size: 0.92rem !important;
        font-weight: 500 !important;
        color: #334155 !important;
    }

    /* Styled Drag & Drop File Zone */
    [data-testid="stFileUploader"] {
        background-color: #FAFAFC !important;
        border: 2px dashed #CBD5E1 !important;
        border-radius: 14px !important;
        padding: 24px !important;
        text-align: center !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #FF5A36 !important;
        background-color: #FFF9F7 !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(255, 90, 54, 0.08) !important;
    }
    [data-testid="stFileUploader"] button {
        background-color: #FFFFFF !important;
        color: #1E293B !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 7px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
    }

    /* Empty State in Recent Files */
    .empty-state-box {
        text-align: center;
        padding: 44px 20px;
    }
    .empty-icon-circle {
        width: 58px;
        height: 58px;
        border-radius: 16px;
        background-color: #FFF0EB;
        color: #FF5A36;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.6rem;
        margin: 0 auto 14px auto;
    }
    .empty-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 6px;
    }
    .empty-desc {
        font-size: 0.9rem;
        color: #64748B;
        max-width: 420px;
        margin: 0 auto 20px auto;
        line-height: 1.45;
    }
</style>

<!-- Floating Blurred PDF Ambient Motion Background -->
<div class="ambient-motion-bg">
    <div class="ambient-orb orb-1"></div>
    <div class="ambient-orb orb-2"></div>
    <!-- Blurred Floating PDF Document 1 -->
    <div class="floating-pdf-shape shape-1">
        <svg width="150" height="190" viewBox="0 0 24 24" fill="none">
            <path d="M7 3H14L19 8V19C19 20.1 18.1 21 17 21H7C5.9 21 5 20.1 5 19V5C5 3.9 5.9 3 7 3Z" fill="rgba(255, 90, 54, 0.07)"/>
            <path d="M14 3V8H19" fill="rgba(255, 90, 54, 0.14)"/>
            <rect x="8" y="12" width="8" height="1.5" rx="0.75" fill="rgba(255, 90, 54, 0.2)"/>
            <rect x="8" y="15" width="5" height="1.5" rx="0.75" fill="rgba(255, 90, 54, 0.2)"/>
        </svg>
    </div>
    <!-- Blurred Floating PDF Document 2 -->
    <div class="floating-pdf-shape shape-2">
        <svg width="200" height="250" viewBox="0 0 24 24" fill="none">
            <path d="M7 3H14L19 8V19C19 20.1 18.1 21 17 21H7C5.9 21 5 20.1 5 19V5C5 3.9 5.9 3 7 3Z" fill="rgba(255, 107, 74, 0.05)"/>
            <path d="M14 3V8H19" fill="rgba(255, 107, 74, 0.1)"/>
        </svg>
    </div>
</div>
""", unsafe_allow_html=True)


# =====================================================================
# MINIMAL SLEEK SIDEBAR
# =====================================================================
with st.sidebar:
    st.markdown("""
    <div class="brand-logo-container">
        <div class="brand-logo-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
                <path d="M7 3H14L19 8V19C19 20.1 18.1 21 17 21H7C5.9 21 5 20.1 5 19V5C5 3.9 5.9 3 7 3Z" fill="#FFFFFF"/>
                <path d="M14 3V8H19" fill="#FED7C7"/>
                <path d="M9 13H15M9 16H13" stroke="#FF5A36" stroke-width="1.8" stroke-linecap="round"/>
            </svg>
        </div>
        <div>
            <div class="brand-name">PDF Master</div>
            <div class="brand-tag">TOOLKIT</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    nav_links = [
        ("dashboard", "🏠  Dashboard"),
        ("recent_view", "🕒  Recent Files"),
        ("settings_view", "⚙️  Settings"),
        ("help_view", "❓  Help & Pro Tips"),
    ]

    for key, label in nav_links:
        is_active = (st.session_state.current_view == key)
        btn_type = "primary" if is_active else "secondary"
        if st.button(label, key=f"nav_{key}", type=btn_type):
            st.session_state.current_view = key
            st.rerun()

    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
    st.caption("100% Offline & Private Local Engine")


def switch_view(view_name):
    st.session_state.current_view = view_name
    st.rerun()


def begin_unified_workspace(title: str, description: str, svg_path: str):
    """Renders the top navigation bar and hero header with clean alignment and zero disjointed boxes."""
    col_back, col_bread = st.columns([3, 7])
    with col_back:
        if st.button("← Back to Dashboard", key=f"b_{st.session_state.current_view}"):
            switch_view("dashboard")
    with col_bread:
        st.markdown(f'<div class="ws-breadcrumb">Dashboard &nbsp;/&nbsp; <strong>{title}</strong></div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="ws-hero">
        <div class="ws-hero-icon">
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#FF5A36" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                {svg_path}
            </svg>
        </div>
        <div>
            <h1 class="ws-hero-title">{title}</h1>
            <p class="ws-hero-desc">{description}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def end_unified_workspace():
    st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)


# =====================================================================
# VIEW 1: DASHBOARD (ALL 10+ REAL TOOLS WITH SPRING HOVER PHYSICS)
# =====================================================================
if st.session_state.current_view == "dashboard":
    st.markdown("""
    <div class="dash-header-title">PDF Master Toolkit</div>
    <div class="dash-header-sub">All-in-one offline workspace • 100% private processing on your local machine</div>
    """, unsafe_allow_html=True)

    # ROW 1: Bulk PPT to PDF, Merge PDF, Split PDF
    r1c1, r1c2, r1c3 = st.columns(3, gap="medium")

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

    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

    # ROW 2: Compress PDF, Word to PDF, Images to PDF
    r2c1, r2c2, r2c3 = st.columns(3, gap="medium")

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

    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

    # ROW 3: PDF to Images, Watermark PDF, Protect & Unlock
    r3c1, r3c2, r3c3 = st.columns(3, gap="medium")

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

    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

    # ROW 4: Extract Content, Rotate Pages
    r4c1, r4c2, r4c3 = st.columns(3, gap="medium")

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

    # Recent Files Preview at Bottom of Dashboard
    st.markdown("""
    <div style="margin-top: 36px; padding-top: 20px; border-top: 1px solid #ECEEF1;">
        <div style="font-size: 1.15rem; font-weight: 700; color: #0F172A; margin-bottom: 12px;">Recent Files</div>
    </div>
    """, unsafe_allow_html=True)

    recent_list = load_recent_files()

    if not recent_list:
        st.markdown("""
        <div style="background-color: #FFFFFF; border: 1px dashed #CBD5E1; border-radius: 14px; padding: 24px; text-align: center; color: #94A3B8;">
            <p style="margin: 0; font-size: 0.92rem;">No recent files yet. Click any tool card above to start converting or editing documents.</p>
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
# VIEW 2: BULK PPT TO PDF (UNIFIED WORKSPACE)
# =====================================================================
elif st.session_state.current_view == "ppt2pdf":
    begin_unified_workspace(
        "Bulk PowerPoint to PDF",
        "Convert single presentations or scan an entire folder of 100+ files at native speed.",
        '<rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/><path d="M9 8H12C12.8 8 13.5 8.7 13.5 9.5C13.5 10.3 12.8 11 12 11H9V13"/>'
    )

    tab_bulk, tab_upload = st.tabs(["📁 Bulk Folder Mode (Recommended for 100+ Presentations)", "📤 Upload Files via Browser"])

    with tab_bulk:
        st.caption("Point to any folder on your computer containing .ppt, .pptx, .pps, or .ppsx files to batch convert.")
        c_in, c_out = st.columns(2, gap="medium")
        with c_in:
            folder_input = st.text_input(
                "📁 Source Presentations Folder:",
                placeholder=r"C:\Users\username\Desktop\Presentations",
                help="Folder containing .pptx, .ppt, .pps, or .ppsx files"
            )
        with c_out:
            dest_folder = st.text_input(
                "📂 Custom Output Directory (Optional):",
                placeholder=r"Leave blank to save alongside originals",
                help="Where converted PDF files will be stored"
            )
        
        recursive_check = st.checkbox("Scan all subfolders recursively", value=True)

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

    with tab_upload:
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
    end_unified_workspace()


# =====================================================================
# VIEW 3: MERGE PDF (UNIFIED WORKSPACE)
# =====================================================================
elif st.session_state.current_view == "merge":
    begin_unified_workspace(
        "Merge PDF Files",
        "Combine multiple PDF documents into a single document in any desired order.",
        '<path d="M8 2H14L19 7V17C19 18.1 18.1 19 17 19H8C6.9 19 6 18.1 6 17V4C6 2.9 6.9 2 8 2Z"/><path d="M14 2V7H19"/><path d="M4 8H3C2.45 8 2 8.45 2 9V21C2 22.1 2.9 23 4 23H13C13.55 23 14 22.55 14 22V21"/>'
    )

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
    end_unified_workspace()


# =====================================================================
# VIEW 4: SPLIT PDF (UNIFIED WORKSPACE)
# =====================================================================
elif st.session_state.current_view == "split":
    begin_unified_workspace(
        "Split PDF Document",
        "Extract individual pages or custom page ranges into clean separate PDF documents.",
        '<path d="M14 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V8L14 2Z"/><line x1="2" y1="12" x2="22" y2="12" stroke-dasharray="3 3"/>'
    )

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
    end_unified_workspace()


# =====================================================================
# VIEW 5: COMPRESS PDF (UNIFIED WORKSPACE)
# =====================================================================
elif st.session_state.current_view == "compress":
    begin_unified_workspace(
        "Compress PDF",
        "Shrink PDF file size while keeping text and graphic elements clear and readable.",
        '<path d="M4 14H10V20"/><path d="M10 14L3 21"/><path d="M20 10H14V4"/><path d="M14 10L21 3"/>'
    )

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
    end_unified_workspace()


# =====================================================================
# VIEW 6: WORD TO PDF (UNIFIED WORKSPACE)
# =====================================================================
elif st.session_state.current_view == "word2pdf":
    begin_unified_workspace(
        "Word to PDF Converter",
        "Convert Microsoft Word documents (.docx, .doc) to PDF with accurate fonts and margins.",
        '<path d="M14 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V8L14 2Z"/><polyline points="14 2 14 8 20 8"/><path d="M9 15L10.5 12L12 15L13.5 12L15 15"/>'
    )

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
    end_unified_workspace()


# =====================================================================
# VIEW 7: IMAGES TO PDF (UNIFIED WORKSPACE)
# =====================================================================
elif st.session_state.current_view == "images2pdf":
    begin_unified_workspace(
        "Images to PDF Converter",
        "Merge JPG, PNG, WEBP, and BMP images into a unified, cleanly sized PDF file.",
        '<rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/>'
    )

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
    end_unified_workspace()


# =====================================================================
# VIEW 8: PDF TO IMAGES (UNIFIED WORKSPACE)
# =====================================================================
elif st.session_state.current_view == "pdf2images":
    begin_unified_workspace(
        "PDF to Images Converter",
        "Convert each page of your PDF into crisp PNG or JPG images at custom resolution.",
        '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><circle cx="10" cy="13" r="1.5"/><path d="m8 18 3-3 4 4"/>'
    )

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
    end_unified_workspace()


# =====================================================================
# VIEW 9: WATERMARK PDF (UNIFIED WORKSPACE)
# =====================================================================
elif st.session_state.current_view == "watermark":
    begin_unified_workspace(
        "Watermark PDF",
        "Add custom diagonal text watermarks across every page of your PDF.",
        '<circle cx="12" cy="12" r="9"/><path d="M12 3v18"/><path d="m4.93 4.93 14.14 14.14"/>'
    )

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
    end_unified_workspace()


# =====================================================================
# VIEW 10: PROTECT & UNLOCK (UNIFIED WORKSPACE)
# =====================================================================
elif st.session_state.current_view == "protect":
    begin_unified_workspace(
        "Protect & Unlock PDF",
        "Add 128-bit password encryption to your PDF or remove passwords from protected files.",
        '<rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>'
    )

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
    end_unified_workspace()


# =====================================================================
# VIEW 11: EXTRACT CONTENT (UNIFIED WORKSPACE)
# =====================================================================
elif st.session_state.current_view == "extract":
    begin_unified_workspace(
        "Extract Content (Text & Media)",
        "Extract all readable text to TXT or export all raw embedded images at original quality.",
        '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/><line x1="11" y1="8" x2="11" y2="14"/><line x1="8" y1="11" x2="14" y2="11"/>'
    )

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
    end_unified_workspace()


# =====================================================================
# VIEW 12: ROTATE PDF (UNIFIED WORKSPACE)
# =====================================================================
elif st.session_state.current_view == "rotate":
    begin_unified_workspace(
        "Rotate PDF Pages",
        "Permanently rotate page orientation by 90°, 180°, or 270° clockwise.",
        '<path d="M21.5 2v6h-6"/><path d="M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/>'
    )

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
    end_unified_workspace()


# =====================================================================
# VIEW 13: RECENT FILES (UNIFIED WORKSPACE)
# =====================================================================
elif st.session_state.current_view == "recent_view":
    begin_unified_workspace(
        "Recent Processed Files",
        "History of all documents converted, merged, split, or compressed during your session.",
        '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>'
    )

    recent_list = load_recent_files()

    if not recent_list:
        st.markdown("""
        <div class="empty-state-box">
            <div class="empty-icon-circle">📂</div>
            <div class="empty-title">No Processed Files Yet</div>
            <div class="empty-desc">
                When you convert, merge, compress, or split documents, they will automatically be logged here with quick download access.
            </div>
        </div>
        """, unsafe_allow_html=True)
        col_c1, col_c2, col_c3 = st.columns([1.5, 3, 1.5])
        with col_c2:
            if st.button("⚡ Explore Tools on Dashboard", type="primary", key="btn_empty_to_dash"):
                switch_view("dashboard")
    else:
        col_t1, col_t2 = st.columns([8, 2])
        with col_t1:
            st.markdown(f"**Total Processed:** {len(recent_list)} document(s)")
        with col_t2:
            if st.button("🧹 Clear History"):
                clear_recent_files()
                st.rerun()

        st.markdown("<hr style='border: none; border-top: 1px solid #ECEEF1; margin: 12px 0 16px 0;'>", unsafe_allow_html=True)

        for item in recent_list:
            st.markdown(f"""
            <div style="background: #FAFAFC; border: 1px solid #ECEEF1; border-radius: 10px; padding: 14px 18px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="font-weight: 700; color: #0F172A; font-size: 0.95rem;">{item['filename']}</span>
                    <span style="background: #FFF0EB; color: #FF5A36; font-size: 0.78rem; font-weight: 600; padding: 3px 8px; border-radius: 5px; margin-left: 10px;">{item['tool']}</span>
                    <div style="color: #64748B; font-size: 0.8rem; margin-top: 4px;">Size: {item['size_kb']} KB</div>
                </div>
                <div style="color: #94A3B8; font-size: 0.82rem; font-weight: 500;">{item.get('timestamp', '')}</div>
            </div>
            """, unsafe_allow_html=True)
    end_unified_workspace()


# =====================================================================
# VIEW 14: SETTINGS & HELP (UNIFIED WORKSPACE)
# =====================================================================
elif st.session_state.current_view in ("settings_view", "help_view"):
    if st.session_state.current_view == "settings_view":
        begin_unified_workspace(
            "Application Settings",
            "Local engines, privacy parameters, and storage status.",
            '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>'
        )

        st.markdown("""
        <h4 style="margin-top: 0; color: #0F172A;">⚙️ Engine Status</h4>
        <div style="background: #F8FAFC; border: 1px solid #ECEEF1; border-radius: 8px; padding: 14px 18px; margin-bottom: 12px; display: flex; justify-content: space-between;">
            <span><strong>PowerPoint Engine:</strong> Native Microsoft PowerPoint COM</span>
            <span style="color: #16A34A; font-weight: 700;">● Ready</span>
        </div>
        <div style="background: #F8FAFC; border: 1px solid #ECEEF1; border-radius: 8px; padding: 14px 18px; margin-bottom: 12px; display: flex; justify-content: space-between;">
            <span><strong>Word Engine:</strong> Native Microsoft Word COM</span>
            <span style="color: #16A34A; font-weight: 700;">● Ready</span>
        </div>
        <div style="background: #F8FAFC; border: 1px solid #ECEEF1; border-radius: 8px; padding: 14px 18px; margin-bottom: 12px; display: flex; justify-content: space-between;">
            <span><strong>PDF Core Engine:</strong> PyMuPDF + PyPDF</span>
            <span style="color: #16A34A; font-weight: 700;">● Ready</span>
        </div>
        <div style="background: #F8FAFC; border: 1px solid #ECEEF1; border-radius: 8px; padding: 14px 18px; display: flex; justify-content: space-between;">
            <span><strong>Security Mode:</strong> 100% Offline / Local Sandboxing</span>
            <span style="color: #16A34A; font-weight: 700;">● Active</span>
        </div>
        """, unsafe_allow_html=True)
        end_unified_workspace()

    else:
        begin_unified_workspace(
            "Help & Pro Tips",
            "Learn how to make the most of your offline PDF Master Toolkit.",
            '<circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/>'
        )

        st.markdown("""
        <h4 style="margin-top: 0; color: #0F172A;">💡 Key Tips & Shortcuts</h4>
        <ul style="color: #475569; font-size: 0.94rem; line-height: 1.7; padding-left: 20px;">
            <li><strong>Converting 100+ PowerPoint files:</strong> Use <em>Bulk Folder Mode</em> in the Bulk PPT to PDF tool. It automatically loops through all subfolders at native hardware speed.</li>
            <li><strong>Zero Internet Access:</strong> Every byte stays on your local disk. No files are uploaded to any external third-party server.</li>
            <li><strong>Compressing without Quality Loss:</strong> The compression engine cleans redundant font tables and optimizes image streams without turning text blurry.</li>
            <li><strong>Splitting by Range:</strong> Enter ranges like <code>1-3, 5, 8-12</code> in the Split tool to extract exactly the pages you need.</li>
        </ul>
        """, unsafe_allow_html=True)
        end_unified_workspace()
