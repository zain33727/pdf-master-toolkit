"""
PDF Master Toolkit - Web Application (iLovePDF Offline Clone)
Run with: streamlit run app_web.py
"""

import os
import io
import zipfile
import tempfile
import streamlit as st
from pathlib import Path

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
    page_title="PDF Master Toolkit (Offline iLovePDF)",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .card-box {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


def get_zip_download(files_dict: dict, zip_filename: str):
    """Creates in-memory zip archive from filename -> bytes dictionary."""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for fname, data in files_dict.items():
            zip_file.writestr(fname, data)
    zip_buffer.seek(0)
    return zip_buffer.getvalue()


# Sidebar Navigation
st.sidebar.markdown("## 🛠️ **PDF Master Tools**")
tool_choice = st.sidebar.radio(
    "Choose Tool:",
    [
        "📊 Bulk PPT to PDF",
        "📑 Merge PDFs",
        "✂️ Split PDF",
        "🗜️ Compress PDF",
        "🖼️ Images to PDF",
        "📄 PDF to Images",
        "💧 Add Watermark",
        "🔒 Protect / Unlock",
        "📝 Extract Text & Images",
        "🔄 Rotate PDF"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**100% Offline & Private**\n\n"
    "All file conversions happen locally on your computer with full privacy and high-speed native automation."
)

# =====================================================================
# 1. BULK PPT TO PDF
# =====================================================================
if tool_choice == "📊 Bulk PPT to PDF":
    st.markdown('<div class="main-title">📊 Bulk PowerPoint to PDF Converter</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Convert 100+ PPT and PPTX presentations to PDF with high fidelity using native PowerPoint automation.</div>', unsafe_allow_html=True)

    mode = st.radio("Choose Input Method:", ["Select Folder Path on Disk (Fastest for 100+ files)", "Upload Files via Browser"], horizontal=True)

    if mode == "Select Folder Path on Disk (Fastest for 100+ files)":
        st.markdown("##### 📁 Scan Local Folder")
        folder_path = st.text_input("Enter Folder Path on your computer:", placeholder=r"C:\Users\username\Documents\Presentations")
        col_opt1, col_opt2 = st.columns([1, 1])
        with col_opt1:
            recursive = st.checkbox("Scan subfolders recursively", value=True)
        with col_opt2:
            out_folder = st.text_input("Output Directory (Optional, leave blank for same folder):", "")

        if folder_path:
            if os.path.isdir(folder_path):
                found_files = find_presentation_files(folder_path, recursive=recursive)
                st.success(f"Found **{len(found_files)}** presentation file(s) in `{folder_path}`")
                
                if found_files:
                    with st.expander("View Discovered Files"):
                        for f in found_files[:50]:
                            st.caption(f)
                        if len(found_files) > 50:
                            st.caption(f"... and {len(found_files) - 50} more files.")

                    if st.button("⚡ Convert All Presentations to PDF Now", type="primary"):
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        out_dir = out_folder.strip() if out_folder.strip() else None

                        def cb(cur, tot, name, success, msg):
                            progress_bar.progress(cur / tot)
                            status_text.text(f"Converting [{cur}/{tot}]: {name}")

                        with st.spinner("Converting files in bulk..."):
                            summary = bulk_convert_ppt_to_pdf(found_files, output_dir=out_dir, progress_callback=cb)
                        
                        st.success(f"🎉 Done! Converted {summary['success']} files successfully ({summary['failed']} failed).")
                        if out_dir:
                            st.info(f"PDFs saved to: `{out_dir}`")
                        else:
                            st.info("PDFs saved alongside each original file.")
            else:
                st.warning("Please enter a valid directory path.")

    else:
        st.markdown("##### 📤 Upload Presentation Files")
        uploaded_files = st.file_uploader("Upload .pptx or .ppt files (select multiple)", type=["pptx", "ppt", "pps", "ppsx"], accept_multiple_files=True)
        
        if uploaded_files:
            st.info(f"Selected {len(uploaded_files)} presentation(s).")
            if st.button("⚡ Convert & Download ZIP", type="primary"):
                with tempfile.TemporaryDirectory() as temp_dir:
                    input_paths = []
                    for uf in uploaded_files:
                        in_p = os.path.join(temp_dir, uf.name)
                        with open(in_p, "wb") as f:
                            f.write(uf.getbuffer())
                        input_paths.append(in_p)

                    out_dir = os.path.join(temp_dir, "pdfs")
                    os.makedirs(out_dir, exist_ok=True)

                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    def cb(cur, tot, name, success, msg):
                        progress_bar.progress(cur / tot)
                        status_text.text(f"Converting [{cur}/{tot}]: {name}")

                    with st.spinner("Processing..."):
                        res = bulk_convert_ppt_to_pdf(input_paths, output_dir=out_dir, progress_callback=cb)

                    # Prepare ZIP download
                    files_dict = {}
                    for res_item in res["results"]:
                        if res_item["status"] == "success" and os.path.isfile(res_item["output"]):
                            pdf_name = os.path.basename(res_item["output"])
                            with open(res_item["output"], "rb") as pf:
                                files_dict[pdf_name] = pf.read()

                    if files_dict:
                        zip_data = get_zip_download(files_dict, "converted_pdfs.zip")
                        st.download_button(
                            label="📥 Download Converted PDFs (.ZIP)",
                            data=zip_data,
                            file_name="converted_presentations.zip",
                            mime="application/zip",
                            type="primary"
                        )
                    else:
                        st.error("No files could be converted.")

# =====================================================================
# 2. MERGE PDFS
# =====================================================================
elif tool_choice == "📑 Merge PDFs":
    st.markdown('<div class="main-title">📑 Merge PDF Files</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Combine multiple PDF documents into a single file in any desired sequence.</div>', unsafe_allow_html=True)

    uploaded_pdfs = st.file_uploader("Select 2 or more PDF files to combine:", type=["pdf"], accept_multiple_files=True)
    if uploaded_pdfs and len(uploaded_pdfs) >= 2:
        st.write(f"**Files to merge ({len(uploaded_pdfs)}):**")
        for i, up in enumerate(uploaded_pdfs, 1):
            st.caption(f"{i}. {up.name} ({round(len(up.getvalue())/1024, 1)} KB)")

        if st.button("⚡ Merge PDFs Now", type="primary"):
            with tempfile.TemporaryDirectory() as temp_dir:
                paths = []
                for up in uploaded_pdfs:
                    p = os.path.join(temp_dir, up.name)
                    with open(p, "wb") as f:
                        f.write(up.getbuffer())
                    paths.append(p)

                out_merged = os.path.join(temp_dir, "merged_document.pdf")
                merge_pdfs(paths, out_merged)

                with open(out_merged, "rb") as mf:
                    merged_bytes = mf.read()

                st.success("✅ PDFs merged successfully!")
                st.download_button(
                    label="📥 Download Merged PDF",
                    data=merged_bytes,
                    file_name="merged_document.pdf",
                    mime="application/pdf",
                    type="primary"
                )

# =====================================================================
# 3. SPLIT PDF
# =====================================================================
elif tool_choice == "✂️ Split PDF":
    st.markdown('<div class="main-title">✂️ Split PDF</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Separate pages or extract specific page ranges from your PDF.</div>', unsafe_allow_html=True)

    uploaded_pdf = st.file_uploader("Upload PDF file to split:", type=["pdf"])
    if uploaded_pdf:
        split_type = st.radio("Splitting Mode:", ["Split every page into a separate PDF", "Extract custom page ranges (e.g. 1-3, 5, 8-10)"])
        range_input = ""
        if "Extract" in split_type:
            range_input = st.text_input("Enter Page Ranges:", "1-3, 5")

        if st.button("⚡ Split PDF", type="primary"):
            with tempfile.TemporaryDirectory() as temp_dir:
                in_pdf = os.path.join(temp_dir, uploaded_pdf.name)
                with open(in_pdf, "wb") as f:
                    f.write(uploaded_pdf.getbuffer())

                mode = "ranges" if "Extract" in split_type else "all_pages"
                out_split_dir = os.path.join(temp_dir, "split_output")
                results = split_pdf(in_pdf, out_split_dir, split_mode=mode, range_str=range_input)

                files_dict = {}
                for r in results:
                    with open(r, "rb") as rf:
                        files_dict[os.path.basename(r)] = rf.read()

                st.success(f"✅ Generated {len(results)} split file(s)!")
                zip_data = get_zip_download(files_dict, "split_pages.zip")
                st.download_button("📥 Download Split Files (.ZIP)", data=zip_data, file_name="split_pages.zip", mime="application/zip", type="primary")

# =====================================================================
# 4. COMPRESS PDF
# =====================================================================
elif tool_choice == "🗜️ Compress PDF":
    st.markdown('<div class="main-title">🗜️ Compress & Optimize PDF</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Reduce PDF file size while preserving high visual quality.</div>', unsafe_allow_html=True)

    uploaded_pdf = st.file_uploader("Upload PDF to compress:", type=["pdf"])
    if uploaded_pdf:
        orig_kb = round(len(uploaded_pdf.getvalue()) / 1024, 2)
        st.info(f"Original File Size: **{orig_kb} KB** ({round(orig_kb/1024, 2)} MB)")

        if st.button("⚡ Compress PDF Now", type="primary"):
            with tempfile.TemporaryDirectory() as temp_dir:
                in_pdf = os.path.join(temp_dir, uploaded_pdf.name)
                out_pdf = os.path.join(temp_dir, "compressed.pdf")
                with open(in_pdf, "wb") as f:
                    f.write(uploaded_pdf.getbuffer())

                with st.spinner("Optimizing streams and images..."):
                    res = compress_pdf(in_pdf, out_pdf)

                with open(out_pdf, "rb") as cf:
                    comp_bytes = cf.read()

                st.success(
                    f"🎉 Compression Complete!\n\n"
                    f"• **Before:** {res['original_size_kb']} KB\n"
                    f"• **After:** {res['compressed_size_kb']} KB\n"
                    f"• **Saved:** {res['saved_kb']} KB ({res['percent_reduction']}% reduction)"
                )
                st.download_button("📥 Download Compressed PDF", data=comp_bytes, file_name=f"compressed_{uploaded_pdf.name}", mime="application/pdf", type="primary")

# =====================================================================
# 5. IMAGES TO PDF
# =====================================================================
elif tool_choice == "🖼️ Images to PDF":
    st.markdown('<div class="main-title">🖼️ Images to PDF</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Convert JPG, PNG, WEBP, and BMP images into a clean PDF document.</div>', unsafe_allow_html=True)

    uploaded_imgs = st.file_uploader("Upload images to combine:", type=["jpg", "jpeg", "png", "webp", "bmp"], accept_multiple_files=True)
    if uploaded_imgs:
        st.write(f"Selected **{len(uploaded_imgs)}** image(s)")
        if st.button("⚡ Convert Images to PDF", type="primary"):
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

                st.success("✅ Combined PDF generated successfully!")
                st.download_button("📥 Download Combined PDF", data=pdf_bytes, file_name="images_combined.pdf", mime="application/pdf", type="primary")

# =====================================================================
# 6. PDF TO IMAGES
# =====================================================================
elif tool_choice == "📄 PDF to Images":
    st.markdown('<div class="main-title">📄 PDF to Images</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Export PDF pages as high-resolution PNG or JPG image files.</div>', unsafe_allow_html=True)

    uploaded_pdf = st.file_uploader("Upload PDF file:", type=["pdf"])
    if uploaded_pdf:
        c1, c2 = st.columns(2)
        with c1:
            img_format = st.selectbox("Image Format:", ["png", "jpg"])
        with c2:
            dpi = st.selectbox("Resolution (DPI):", [150, 200, 300, 72], index=0)

        if st.button("⚡ Export Pages as Images", type="primary"):
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

                st.success(f"✅ Exported {len(imgs)} page(s) as images!")
                zip_data = get_zip_download(files_dict, "pdf_pages_images.zip")
                st.download_button("📥 Download Images (.ZIP)", data=zip_data, file_name="pdf_pages_images.zip", mime="application/zip", type="primary")

# =====================================================================
# 7. ADD WATERMARK
# =====================================================================
elif tool_choice == "💧 Add Watermark":
    st.markdown('<div class="main-title">💧 Add Watermark</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Stamp custom text watermarks across every page of your PDF.</div>', unsafe_allow_html=True)

    uploaded_pdf = st.file_uploader("Upload PDF:", type=["pdf"])
    if uploaded_pdf:
        col1, col2, col3 = st.columns(3)
        with col1:
            wm_text = st.text_input("Watermark Text:", "CONFIDENTIAL")
        with col2:
            font_size = st.number_input("Font Size:", min_value=10, max_value=120, value=45)
        with col3:
            opacity = st.slider("Opacity:", min_value=0.05, max_value=0.8, value=0.22, step=0.05)

        if st.button("⚡ Apply Watermark", type="primary"):
            with tempfile.TemporaryDirectory() as temp_dir:
                in_pdf = os.path.join(temp_dir, uploaded_pdf.name)
                out_pdf = os.path.join(temp_dir, "watermarked.pdf")
                with open(in_pdf, "wb") as f:
                    f.write(uploaded_pdf.getbuffer())

                watermark_pdf(in_pdf, out_pdf, text=wm_text, font_size=font_size, opacity=opacity)
                with open(out_pdf, "rb") as wf:
                    wm_bytes = wf.read()

                st.success("✅ Watermark applied successfully!")
                st.download_button("📥 Download Watermarked PDF", data=wm_bytes, file_name=f"watermarked_{uploaded_pdf.name}", mime="application/pdf", type="primary")

# =====================================================================
# 8. PROTECT / UNLOCK
# =====================================================================
elif tool_choice == "🔒 Protect / Unlock":
    st.markdown('<div class="main-title">🔒 Protect & Unlock PDF</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Add 128-bit password encryption or remove passwords from protected PDFs.</div>', unsafe_allow_html=True)

    action = st.radio("Action:", ["Encrypt / Protect with Password", "Decrypt / Remove Password"], horizontal=True)
    uploaded_pdf = st.file_uploader("Upload PDF:", type=["pdf"])

    if uploaded_pdf:
        password = st.text_input("Enter Password:", type="password")
        if st.button("⚡ Process PDF", type="primary"):
            if not password:
                st.warning("Please enter a password.")
            else:
                with tempfile.TemporaryDirectory() as temp_dir:
                    in_pdf = os.path.join(temp_dir, uploaded_pdf.name)
                    out_pdf = os.path.join(temp_dir, "result.pdf")
                    with open(in_pdf, "wb") as f:
                        f.write(uploaded_pdf.getbuffer())

                    if "Encrypt" in action:
                        protect_pdf(in_pdf, out_pdf, user_password=password)
                        st.success("✅ PDF encrypted and protected successfully!")
                        with open(out_pdf, "rb") as f:
                            st.download_button("📥 Download Protected PDF", data=f.read(), file_name=f"protected_{uploaded_pdf.name}", mime="application/pdf", type="primary")
                    else:
                        ok = unlock_pdf(in_pdf, out_pdf, password=password)
                        if ok:
                            st.success("✅ PDF unlocked and decrypted successfully!")
                            with open(out_pdf, "rb") as f:
                                st.download_button("📥 Download Unlocked PDF", data=f.read(), file_name=f"unlocked_{uploaded_pdf.name}", mime="application/pdf", type="primary")
                        else:
                            st.error("❌ Incorrect password or decryption failed.")

# =====================================================================
# 9. EXTRACT TEXT & IMAGES
# =====================================================================
elif tool_choice == "📝 Extract Text & Images":
    st.markdown('<div class="main-title">📝 Extract Text & Embedded Images</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Extract readable text or dump all raw embedded photos and diagrams from your PDF.</div>', unsafe_allow_html=True)

    uploaded_pdf = st.file_uploader("Upload PDF:", type=["pdf"])
    if uploaded_pdf:
        sub_tab1, sub_tab2 = st.tabs(["📄 Extract Text", "🖼️ Extract Embedded Images"])

        with sub_tab1:
            if st.button("⚡ Extract Text Now"):
                with tempfile.TemporaryDirectory() as temp_dir:
                    in_pdf = os.path.join(temp_dir, uploaded_pdf.name)
                    with open(in_pdf, "wb") as f:
                        f.write(uploaded_pdf.getbuffer())
                    extracted = extract_text_from_pdf(in_pdf)
                    st.text_area("Extracted Content:", extracted, height=300)
                    st.download_button("📥 Download as .txt", data=extracted, file_name=f"{os.path.splitext(uploaded_pdf.name)[0]}_text.txt", mime="text/plain")

        with sub_tab2:
            if st.button("⚡ Extract All Images"):
                with tempfile.TemporaryDirectory() as temp_dir:
                    in_pdf = os.path.join(temp_dir, uploaded_pdf.name)
                    with open(in_pdf, "wb") as f:
                        f.write(uploaded_pdf.getbuffer())
                    img_dir = os.path.join(temp_dir, "imgs")
                    imgs = extract_embedded_images(in_pdf, img_dir)
                    if imgs:
                        files_dict = {}
                        for im in imgs:
                            with open(im, "rb") as imf:
                                files_dict[os.path.basename(im)] = imf.read()
                        st.success(f"Found {len(imgs)} embedded image(s)!")
                        zip_data = get_zip_download(files_dict, "extracted_images.zip")
                        st.download_button("📥 Download Extracted Images (.ZIP)", data=zip_data, file_name="extracted_images.zip", mime="application/zip")
                    else:
                        st.info("No embedded raster images found in this PDF.")

# =====================================================================
# 10. ROTATE PDF
# =====================================================================
elif tool_choice == "🔄 Rotate PDF":
    st.markdown('<div class="main-title">🔄 Rotate PDF Pages</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Permanently rotate PDF orientation.</div>', unsafe_allow_html=True)

    uploaded_pdf = st.file_uploader("Upload PDF to rotate:", type=["pdf"])
    if uploaded_pdf:
        angle = st.selectbox("Rotation Angle:", [90, 180, 270], format_func=lambda x: f"{x}° Clockwise")
        if st.button("⚡ Rotate & Download", type="primary"):
            with tempfile.TemporaryDirectory() as temp_dir:
                in_pdf = os.path.join(temp_dir, uploaded_pdf.name)
                out_pdf = os.path.join(temp_dir, "rotated.pdf")
                with open(in_pdf, "wb") as f:
                    f.write(uploaded_pdf.getbuffer())

                rotate_pdf_pages(in_pdf, out_pdf, angle=angle)
                with open(out_pdf, "rb") as rf:
                    rot_bytes = rf.read()

                st.success("✅ PDF rotated successfully!")
                st.download_button("📥 Download Rotated PDF", data=rot_bytes, file_name=f"rotated_{uploaded_pdf.name}", mime="application/pdf", type="primary")
