"""
PDF Master Toolkit - Desktop GUI Application
Modern Tkinter / ttk desktop interface with multi-threading, live progress bars,
and comprehensive PDF & presentation conversion tools.
"""

import os
import sys
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List

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


class PDFMasterApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("PDF Master Toolkit - All-in-One Offline PDF Suite")
        self.geometry("920x680")
        self.minsize(800, 580)

        # Style configuration
        self._setup_styles()

        # Header Banner
        self._build_header()

        # Notebook (Tabs)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 10))

        # Build individual tabs
        self.tab_ppt = ttk.Frame(self.notebook, padding=12)
        self.tab_merge_split = ttk.Frame(self.notebook, padding=12)
        self.tab_compress = ttk.Frame(self.notebook, padding=12)
        self.tab_images = ttk.Frame(self.notebook, padding=12)
        self.tab_security_wm = ttk.Frame(self.notebook, padding=12)
        self.tab_extract_rotate = ttk.Frame(self.notebook, padding=12)

        self.notebook.add(self.tab_ppt, text=" 📊 Bulk PPT to PDF ")
        self.notebook.add(self.tab_merge_split, text=" 📑 Merge & Split ")
        self.notebook.add(self.tab_compress, text=" 🗜️ Compress PDF ")
        self.notebook.add(self.tab_images, text=" 🖼️ Images ↔ PDF ")
        self.notebook.add(self.tab_security_wm, text=" 🛡️ Watermark & Protect ")
        self.notebook.add(self.tab_extract_rotate, text=" ⚙️ Extract & Rotate ")

        # Populate tabs
        self._build_ppt_tab()
        self._build_merge_split_tab()
        self._build_compress_tab()
        self._build_images_tab()
        self._build_security_tab()
        self._build_extract_rotate_tab()

    def _setup_styles(self):
        self.style = ttk.Style(self)
        # Try native themes if available
        available_themes = self.style.theme_names()
        if "clam" in available_themes:
            self.style.theme_use("clam")

        self.configure(bg="#F4F6F9")

        # Fonts
        self.font_title = ("Segoe UI", 13, "bold")
        self.font_heading = ("Segoe UI", 11, "bold")
        self.font_body = ("Segoe UI", 10)
        self.font_mono = ("Consolas", 9)

        # Custom ttk styles
        self.style.configure("TNotebook", background="#F4F6F9")
        self.style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[10, 6])
        self.style.configure("TFrame", background="#F4F6F9")
        self.style.configure("Card.TFrame", background="#FFFFFF", relief="solid", borderwidth=1)
        self.style.configure("TLabel", background="#F4F6F9", font=self.font_body)
        self.style.configure("Card.TLabel", background="#FFFFFF", font=self.font_body)
        self.style.configure("Heading.TLabel", font=self.font_heading, background="#F4F6F9", foreground="#1E293B")
        self.style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), padding=6)
        self.style.configure("Action.TButton", font=("Segoe UI", 10), padding=4)

    def _build_header(self):
        header_frame = tk.Frame(self, bg="#1E3A8A", height=55)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)

        title_lbl = tk.Label(
            header_frame,
            text="⚡ PDF Master Toolkit",
            font=("Segoe UI", 14, "bold"),
            fg="#FFFFFF",
            bg="#1E3A8A"
        )
        title_lbl.pack(side=tk.LEFT, padx=16, pady=8)

        sub_lbl = tk.Label(
            header_frame,
            text="Bulk PPT to PDF • Merge • Split • Compress • Images • Watermark • 100% Offline",
            font=("Segoe UI", 9),
            fg="#93C5FD",
            bg="#1E3A8A"
        )
        sub_lbl.pack(side=tk.LEFT, padx=8, pady=8)

    # -------------------------------------------------------------
    # TAB 1: BULK PPT TO PDF
    # -------------------------------------------------------------
    def _build_ppt_tab(self):
        tab = self.tab_ppt

        # Top Control Card
        card = ttk.LabelFrame(tab, text=" Source Presentations ", padding=10)
        card.pack(fill=tk.X, pady=(0, 8))

        btn_row = ttk.Frame(card)
        btn_row.pack(fill=tk.X, pady=4)

        ttk.Button(btn_row, text="📁 Select Folder (Auto-Scan 100+)", style="Action.TButton", command=self._ppt_pick_folder).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_row, text="📄 Select PPT Files", style="Action.TButton", command=self._ppt_pick_files).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_row, text="🧹 Clear List", style="Action.TButton", command=self._ppt_clear_files).pack(side=tk.LEFT, padx=4)

        self.ppt_recursive_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(btn_row, text="Scan Subfolders (Recursive)", variable=self.ppt_recursive_var).pack(side=tk.LEFT, padx=12)

        # File count and listbox
        list_frame = ttk.Frame(card)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=4)

        self.ppt_count_lbl = ttk.Label(list_frame, text="0 file(s) selected", font=("Segoe UI", 9, "bold"))
        self.ppt_count_lbl.pack(anchor="w", pady=(0, 2))

        self.ppt_listbox = tk.Listbox(list_frame, height=6, font=self.font_mono, selectmode=tk.EXTENDED)
        ppt_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.ppt_listbox.yview)
        self.ppt_listbox.config(yscrollcommand=ppt_scroll.set)
        self.ppt_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ppt_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Output options Card
        out_card = ttk.LabelFrame(tab, text=" Output Settings ", padding=10)
        out_card.pack(fill=tk.X, pady=(0, 8))

        out_row = ttk.Frame(out_card)
        out_row.pack(fill=tk.X, pady=2)

        self.ppt_same_dir_var = tk.BooleanVar(value=False)
        ttk.Radiobutton(out_row, text="Save alongside original files", variable=self.ppt_same_dir_var, value=True, command=self._ppt_toggle_out_mode).pack(side=tk.LEFT, padx=4)
        ttk.Radiobutton(out_row, text="Custom Output Folder:", variable=self.ppt_same_dir_var, value=False, command=self._ppt_toggle_out_mode).pack(side=tk.LEFT, padx=4)

        self.ppt_out_entry = ttk.Entry(out_row, width=45)
        self.ppt_out_entry.pack(side=tk.LEFT, padx=4, fill=tk.X, expand=True)
        self.ppt_out_btn = ttk.Button(out_row, text="Browse...", command=self._ppt_browse_out)
        self.ppt_out_btn.pack(side=tk.LEFT, padx=2)

        # Action & Progress Card
        action_card = ttk.Frame(tab)
        action_card.pack(fill=tk.BOTH, expand=True)

        ctrl_row = ttk.Frame(action_card)
        ctrl_row.pack(fill=tk.X, pady=4)

        self.ppt_start_btn = ttk.Button(
            ctrl_row,
            text="⚡ Start Bulk PPT to PDF Conversion",
            style="Primary.TButton",
            command=self._ppt_start_conversion
        )
        self.ppt_start_btn.pack(side=tk.LEFT, padx=4)

        self.ppt_open_folder_btn = ttk.Button(
            ctrl_row,
            text="📂 Open Output Folder",
            style="Action.TButton",
            state=tk.DISABLED,
            command=self._ppt_open_out_folder
        )
        self.ppt_open_folder_btn.pack(side=tk.LEFT, padx=4)

        self.ppt_status_lbl = ttk.Label(ctrl_row, text="Ready", foreground="#475569")
        self.ppt_status_lbl.pack(side=tk.LEFT, padx=12)

        # Progress bar
        self.ppt_progress = ttk.Progressbar(action_card, orient=tk.HORIZONTAL, mode="determinate")
        self.ppt_progress.pack(fill=tk.X, pady=4)

        # Console Log
        self.ppt_log = tk.Text(action_card, height=7, font=self.font_mono, bg="#1E293B", fg="#F8FAFC", state=tk.DISABLED)
        self.ppt_log.pack(fill=tk.BOTH, expand=True)

        self.ppt_files: List[str] = []
        self.ppt_last_out_dir = ""

    def _ppt_toggle_out_mode(self):
        if self.ppt_same_dir_var.get():
            self.ppt_out_entry.config(state=tk.DISABLED)
            self.ppt_out_btn.config(state=tk.DISABLED)
        else:
            self.ppt_out_entry.config(state=tk.NORMAL)
            self.ppt_out_btn.config(state=tk.NORMAL)

    def _ppt_browse_out(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.ppt_out_entry.delete(0, tk.END)
            self.ppt_out_entry.insert(0, os.path.normpath(folder))

    def _ppt_pick_folder(self):
        folder = filedialog.askdirectory(title="Select Folder Containing Presentations")
        if not folder:
            return
        recursive = self.ppt_recursive_var.get()
        found = find_presentation_files(folder, recursive=recursive)
        if not found:
            messagebox.showinfo("No Files", "No .ppt or .pptx files found in selected directory.")
            return

        self.ppt_files = found
        self.ppt_listbox.delete(0, tk.END)
        for f in found:
            self.ppt_listbox.insert(tk.END, f)
        self.ppt_count_lbl.config(text=f"{len(found)} file(s) found in {os.path.basename(folder)}")

        # Default output folder to folder/converted_pdf if not set
        if not self.ppt_out_entry.get():
            default_out = os.path.join(folder, "converted_pdfs")
            self.ppt_out_entry.delete(0, tk.END)
            self.ppt_out_entry.insert(0, os.path.normpath(default_out))

    def _ppt_pick_files(self):
        files = filedialog.askopenfilenames(
            title="Select PPT/PPTX Files",
            filetypes=[("PowerPoint Presentations", "*.pptx;*.ppt;*.pps;*.ppsx"), ("All Files", "*.*")]
        )
        if not files:
            return
        self.ppt_files = list(files)
        self.ppt_listbox.delete(0, tk.END)
        for f in self.ppt_files:
            self.ppt_listbox.insert(tk.END, f)
        self.ppt_count_lbl.config(text=f"{len(self.ppt_files)} file(s) selected")

    def _ppt_clear_files(self):
        self.ppt_files = []
        self.ppt_listbox.delete(0, tk.END)
        self.ppt_count_lbl.config(text="0 file(s) selected")

    def _log_ppt(self, msg: str):
        self.ppt_log.config(state=tk.NORMAL)
        self.ppt_log.insert(tk.END, msg + "\n")
        self.ppt_log.see(tk.END)
        self.ppt_log.config(state=tk.DISABLED)

    def _ppt_start_conversion(self):
        if not self.ppt_files:
            messagebox.showwarning("No Files", "Please select a folder or files first.")
            return

        out_dir = None
        if not self.ppt_same_dir_var.get():
            out_dir = self.ppt_out_entry.get().strip()
            if not out_dir:
                messagebox.showwarning("Output Folder", "Please specify an output directory.")
                return
            os.makedirs(out_dir, exist_ok=True)
            self.ppt_last_out_dir = out_dir
        else:
            self.ppt_last_out_dir = os.path.dirname(self.ppt_files[0])

        self.ppt_start_btn.config(state=tk.DISABLED)
        self.ppt_open_folder_btn.config(state=tk.DISABLED)
        self.ppt_progress["value"] = 0
        self.ppt_progress["maximum"] = len(self.ppt_files)
        self.ppt_status_lbl.config(text=f"Converting 0 / {len(self.ppt_files)}...")

        self.ppt_log.config(state=tk.NORMAL)
        self.ppt_log.delete("1.0", tk.END)
        self.ppt_log.config(state=tk.DISABLED)
        self._log_ppt(f"[*] Starting conversion of {len(self.ppt_files)} files...")

        # Run in thread
        threading.Thread(target=self._ppt_worker, args=(self.ppt_files, out_dir), daemon=True).start()

    def _ppt_worker(self, files: List[str], out_dir: str):
        total = len(files)

        def callback(cur, tot, fname, success, msg):
            status = "✓ OK" if success else "✗ FAIL"
            extra = f" ({msg})" if msg else ""
            self.after(0, self._log_ppt, f"[{cur}/{tot}] [{status}] {fname}{extra}")
            self.after(0, self._ppt_update_progress, cur, tot, fname)

        try:
            res = bulk_convert_ppt_to_pdf(files, output_dir=out_dir, progress_callback=callback)
            self.after(0, self._ppt_finished, res)
        except Exception as e:
            self.after(0, messagebox.showerror, "Conversion Error", str(e))
            self.after(0, self._ppt_reset_controls)

    def _ppt_update_progress(self, cur, tot, fname):
        self.ppt_progress["value"] = cur
        pct = int((cur / tot) * 100)
        self.ppt_status_lbl.config(text=f"Converting: {cur}/{tot} ({pct}%) - {fname[:35]}...")

    def _ppt_finished(self, res):
        self.ppt_start_btn.config(state=tk.NORMAL)
        self.ppt_open_folder_btn.config(state=tk.NORMAL)
        self.ppt_status_lbl.config(
            text=f"Completed! {res['success']} succeeded, {res['failed']} failed.",
            foreground="#16A34A" if res["failed"] == 0 else "#DC2626"
        )
        self._log_ppt("=" * 50)
        self._log_ppt(f"[✓] Completed: {res['success']} converted, {res['failed']} failed.")
        messagebox.showinfo("Finished", f"Bulk conversion complete!\n\nSuccess: {res['success']}\nFailed: {res['failed']}")

    def _ppt_reset_controls(self):
        self.ppt_start_btn.config(state=tk.NORMAL)
        self.ppt_status_lbl.config(text="Ready")

    def _ppt_open_out_folder(self):
        if self.ppt_last_out_dir and os.path.isdir(self.ppt_last_out_dir):
            os.startfile(self.ppt_last_out_dir)

    # -------------------------------------------------------------
    # TAB 2: MERGE & SPLIT
    # -------------------------------------------------------------
    def _build_merge_split_tab(self):
        tab = self.tab_merge_split

        # Merge Card
        m_card = ttk.LabelFrame(tab, text=" 📑 Merge Multiple PDFs ", padding=10)
        m_card.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        m_btn_row = ttk.Frame(m_card)
        m_btn_row.pack(fill=tk.X, pady=2)

        ttk.Button(m_btn_row, text="➕ Add PDF Files", command=self._merge_add_files).pack(side=tk.LEFT, padx=4)
        ttk.Button(m_btn_row, text="⬆️ Move Up", command=self._merge_move_up).pack(side=tk.LEFT, padx=4)
        ttk.Button(m_btn_row, text="⬇️ Move Down", command=self._merge_move_down).pack(side=tk.LEFT, padx=4)
        ttk.Button(m_btn_row, text="❌ Remove", command=self._merge_remove).pack(side=tk.LEFT, padx=4)
        ttk.Button(m_btn_row, text="🧹 Clear All", command=self._merge_clear).pack(side=tk.LEFT, padx=4)

        self.merge_listbox = tk.Listbox(m_card, height=5, font=self.font_mono)
        self.merge_listbox.pack(fill=tk.BOTH, expand=True, pady=4)

        m_action_row = ttk.Frame(m_card)
        m_action_row.pack(fill=tk.X, pady=4)

        ttk.Button(m_action_row, text="⚡ Merge PDFs Now", style="Primary.TButton", command=self._merge_run).pack(side=tk.LEFT, padx=4)
        self.merge_status_lbl = ttk.Label(m_action_row, text="Add at least 2 PDF files to merge.")
        self.merge_status_lbl.pack(side=tk.LEFT, padx=8)

        # Split Card
        s_card = ttk.LabelFrame(tab, text=" ✂️ Split PDF ", padding=10)
        s_card.pack(fill=tk.BOTH, expand=True)

        s_file_row = ttk.Frame(s_card)
        s_file_row.pack(fill=tk.X, pady=2)

        ttk.Label(s_file_row, text="Input PDF:").pack(side=tk.LEFT, padx=4)
        self.split_entry = ttk.Entry(s_file_row, width=50)
        self.split_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        ttk.Button(s_file_row, text="Browse...", command=self._split_browse).pack(side=tk.LEFT, padx=2)

        s_opts_row = ttk.Frame(s_card)
        s_opts_row.pack(fill=tk.X, pady=6)

        self.split_mode_var = tk.StringVar(value="all_pages")
        ttk.Radiobutton(s_opts_row, text="Split into individual pages (1 PDF per page)", variable=self.split_mode_var, value="all_pages").pack(anchor="w")
        
        range_frame = ttk.Frame(s_opts_row)
        range_frame.pack(fill=tk.X, pady=2)
        ttk.Radiobutton(range_frame, text="Custom Page Ranges:", variable=self.split_mode_var, value="ranges").pack(side=tk.LEFT)
        self.split_range_entry = ttk.Entry(range_frame, width=25)
        self.split_range_entry.insert(0, "1-3, 5, 7-10")
        self.split_range_entry.pack(side=tk.LEFT, padx=6)
        ttk.Label(range_frame, text="(e.g., '1-3, 5, 8-10')", foreground="#64748B").pack(side=tk.LEFT)

        s_action_row = ttk.Frame(s_card)
        s_action_row.pack(fill=tk.X, pady=4)
        ttk.Button(s_action_row, text="⚡ Split PDF Now", style="Primary.TButton", command=self._split_run).pack(side=tk.LEFT, padx=4)
        self.split_status_lbl = ttk.Label(s_action_row, text="")
        self.split_status_lbl.pack(side=tk.LEFT, padx=8)

    def _merge_add_files(self):
        files = filedialog.askopenfilenames(title="Select PDFs to Merge", filetypes=[("PDF Files", "*.pdf")])
        for f in files:
            self.merge_listbox.insert(tk.END, f)
        self.merge_status_lbl.config(text=f"{self.merge_listbox.size()} file(s) ready.")

    def _merge_move_up(self):
        sel = self.merge_listbox.curselection()
        if not sel or sel[0] == 0:
            return
        idx = sel[0]
        text = self.merge_listbox.get(idx)
        self.merge_listbox.delete(idx)
        self.merge_listbox.insert(idx - 1, text)
        self.merge_listbox.selection_set(idx - 1)

    def _merge_move_down(self):
        sel = self.merge_listbox.curselection()
        if not sel or sel[0] == self.merge_listbox.size() - 1:
            return
        idx = sel[0]
        text = self.merge_listbox.get(idx)
        self.merge_listbox.delete(idx)
        self.merge_listbox.insert(idx + 1, text)
        self.merge_listbox.selection_set(idx + 1)

    def _merge_remove(self):
        sel = self.merge_listbox.curselection()
        if sel:
            self.merge_listbox.delete(sel[0])

    def _merge_clear(self):
        self.merge_listbox.delete(0, tk.END)

    def _merge_run(self):
        items = list(self.merge_listbox.get(0, tk.END))
        if len(items) < 2:
            messagebox.showwarning("Merge", "Please add at least 2 PDF files to merge.")
            return

        out_path = filedialog.asksaveasfilename(
            title="Save Merged PDF As",
            defaultextension=".pdf",
            filetypes=[("PDF File", "*.pdf")]
        )
        if not out_path:
            return

        try:
            merge_pdfs(items, out_path)
            messagebox.showinfo("Success", f"Successfully merged {len(items)} PDFs!\n\nSaved to: {out_path}")
            self.merge_status_lbl.config(text="Merge completed successfully!", foreground="#16A34A")
        except Exception as e:
            messagebox.showerror("Merge Failed", str(e))

    def _split_browse(self):
        f = filedialog.askopenfilename(title="Select PDF to Split", filetypes=[("PDF Files", "*.pdf")])
        if f:
            self.split_entry.delete(0, tk.END)
            self.split_entry.insert(0, f)

    def _split_run(self):
        pdf_path = self.split_entry.get().strip()
        if not os.path.isfile(pdf_path):
            messagebox.showwarning("Split", "Please select a valid PDF file.")
            return

        out_dir = filedialog.askdirectory(title="Select Destination Folder for Split Pages")
        if not out_dir:
            return

        mode = self.split_mode_var.get()
        range_str = self.split_range_entry.get().strip() if mode == "ranges" else None

        try:
            files = split_pdf(pdf_path, out_dir, split_mode=mode, range_str=range_str)
            messagebox.showinfo("Split Complete", f"Successfully generated {len(files)} PDF file(s)!")
            self.split_status_lbl.config(text=f"Generated {len(files)} files in output folder.", foreground="#16A34A")
            os.startfile(out_dir)
        except Exception as e:
            messagebox.showerror("Split Failed", str(e))

    # -------------------------------------------------------------
    # TAB 3: COMPRESS PDF
    # -------------------------------------------------------------
    def _build_compress_tab(self):
        tab = self.tab_compress

        card = ttk.LabelFrame(tab, text=" 🗜️ PDF Size Compression & Optimization ", padding=12)
        card.pack(fill=tk.BOTH, expand=True)

        row1 = ttk.Frame(card)
        row1.pack(fill=tk.X, pady=4)
        ttk.Label(row1, text="Source PDF:").pack(side=tk.LEFT, padx=4)
        self.comp_in_entry = ttk.Entry(row1, width=50)
        self.comp_in_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        ttk.Button(row1, text="Browse...", command=self._comp_browse).pack(side=tk.LEFT, padx=2)

        self.comp_info_lbl = ttk.Label(card, text="Select a PDF to view current size", foreground="#64748B")
        self.comp_info_lbl.pack(anchor="w", padx=6, pady=4)

        row2 = ttk.Frame(card)
        row2.pack(fill=tk.X, pady=8)
        self.comp_deflate_img = tk.BooleanVar(value=True)
        ttk.Checkbutton(row2, text="Compress embedded images & streams", variable=self.comp_deflate_img).pack(side=tk.LEFT, padx=4)

        btn_row = ttk.Frame(card)
        btn_row.pack(fill=tk.X, pady=10)
        ttk.Button(btn_row, text="⚡ Compress PDF", style="Primary.TButton", command=self._comp_run).pack(side=tk.LEFT, padx=4)

        self.comp_result_frame = ttk.LabelFrame(card, text=" Results ", padding=10)
        self.comp_result_frame.pack(fill=tk.BOTH, expand=True, pady=8)
        self.comp_result_lbl = ttk.Label(self.comp_result_frame, text="No compression run yet.", font=self.font_mono)
        self.comp_result_lbl.pack(anchor="w", padx=4, pady=4)

    def _comp_browse(self):
        f = filedialog.askopenfilename(title="Select PDF to Compress", filetypes=[("PDF Files", "*.pdf")])
        if f:
            self.comp_in_entry.delete(0, tk.END)
            self.comp_in_entry.insert(0, f)
            size_kb = round(os.path.getsize(f) / 1024, 2)
            self.comp_info_lbl.config(text=f"Original File Size: {size_kb} KB ({round(size_kb/1024, 2)} MB)")

    def _comp_run(self):
        pdf_path = self.comp_in_entry.get().strip()
        if not os.path.isfile(pdf_path):
            messagebox.showwarning("Compress", "Please select a valid PDF file.")
            return

        out_path = filedialog.asksaveasfilename(
            title="Save Compressed PDF As",
            defaultextension=".pdf",
            initialfile=os.path.splitext(os.path.basename(pdf_path))[0] + "_compressed.pdf",
            filetypes=[("PDF File", "*.pdf")]
        )
        if not out_path:
            return

        try:
            res = compress_pdf(pdf_path, out_path, deflate_images=self.comp_deflate_img.get())
            txt = (
                f"✓ COMPRESSION COMPLETED!\n\n"
                f"• Original Size   : {res['original_size_kb']} KB\n"
                f"• Compressed Size : {res['compressed_size_kb']} KB\n"
                f"• Storage Saved   : {res['saved_kb']} KB ({res['percent_reduction']}% reduction)\n"
                f"• Output Path     : {res['output_path']}"
            )
            self.comp_result_lbl.config(text=txt)
            messagebox.showinfo("Compressed", f"PDF compressed successfully!\nSaved {res['saved_kb']} KB ({res['percent_reduction']}%)")
        except Exception as e:
            messagebox.showerror("Compression Failed", str(e))

    # -------------------------------------------------------------
    # TAB 4: IMAGES <-> PDF
    # -------------------------------------------------------------
    def _build_images_tab(self):
        tab = self.tab_images

        # Images -> PDF
        i2p_card = ttk.LabelFrame(tab, text=" 🖼️ Images to PDF (Combine JPG, PNG, WEBP) ", padding=10)
        i2p_card.pack(fill=tk.BOTH, expand=True, pady=(0, 6))

        i_btn_row = ttk.Frame(i2p_card)
        i_btn_row.pack(fill=tk.X, pady=2)
        ttk.Button(i_btn_row, text="➕ Select Images", command=self._i2p_select).pack(side=tk.LEFT, padx=4)
        ttk.Button(i_btn_row, text="🧹 Clear", command=lambda: self.i2p_listbox.delete(0, tk.END)).pack(side=tk.LEFT, padx=4)

        self.i2p_listbox = tk.Listbox(i2p_card, height=4, font=self.font_mono)
        self.i2p_listbox.pack(fill=tk.BOTH, expand=True, pady=4)

        i_act_row = ttk.Frame(i2p_card)
        i_act_row.pack(fill=tk.X, pady=2)
        ttk.Button(i_act_row, text="⚡ Convert to Single PDF", style="Primary.TButton", command=self._i2p_run).pack(side=tk.LEFT, padx=4)

        # PDF -> Images
        p2i_card = ttk.LabelFrame(tab, text=" 📄 PDF to Images (Convert Pages to High-Res PNG/JPG) ", padding=10)
        p2i_card.pack(fill=tk.BOTH, expand=True)

        p_row1 = ttk.Frame(p2i_card)
        p_row1.pack(fill=tk.X, pady=2)
        ttk.Label(p_row1, text="PDF File:").pack(side=tk.LEFT, padx=4)
        self.p2i_entry = ttk.Entry(p_row1, width=45)
        self.p2i_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        ttk.Button(p_row1, text="Browse...", command=self._p2i_browse).pack(side=tk.LEFT, padx=2)

        p_row2 = ttk.Frame(p2i_card)
        p_row2.pack(fill=tk.X, pady=4)
        ttk.Label(p_row2, text="Format:").pack(side=tk.LEFT, padx=4)
        self.p2i_fmt_var = tk.StringVar(value="png")
        ttk.Combobox(p_row2, textvariable=self.p2i_fmt_var, values=["png", "jpg"], width=6, state="readonly").pack(side=tk.LEFT, padx=4)

        ttk.Label(p_row2, text="Resolution (DPI):").pack(side=tk.LEFT, padx=8)
        self.p2i_dpi_var = tk.StringVar(value="150")
        ttk.Combobox(p_row2, textvariable=self.p2i_dpi_var, values=["72", "150", "200", "300"], width=6, state="readonly").pack(side=tk.LEFT, padx=4)

        ttk.Button(p_row2, text="⚡ Export Pages as Images", style="Primary.TButton", command=self._p2i_run).pack(side=tk.LEFT, padx=12)

    def _i2p_select(self):
        files = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.webp;*.bmp;*.tiff"), ("All Files", "*.*")]
        )
        for f in files:
            self.i2p_listbox.insert(tk.END, f)

    def _i2p_run(self):
        items = list(self.i2p_listbox.get(0, tk.END))
        if not items:
            messagebox.showwarning("Images to PDF", "Please select at least one image.")
            return

        out_path = filedialog.asksaveasfilename(
            title="Save PDF As",
            defaultextension=".pdf",
            filetypes=[("PDF File", "*.pdf")]
        )
        if not out_path:
            return

        try:
            images_to_pdf(items, out_path)
            messagebox.showinfo("Success", f"Successfully converted {len(items)} images to PDF!\n\nSaved to: {out_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _p2i_browse(self):
        f = filedialog.askopenfilename(title="Select PDF", filetypes=[("PDF Files", "*.pdf")])
        if f:
            self.p2i_entry.delete(0, tk.END)
            self.p2i_entry.insert(0, f)

    def _p2i_run(self):
        pdf_path = self.p2i_entry.get().strip()
        if not os.path.isfile(pdf_path):
            messagebox.showwarning("PDF to Images", "Please select a valid PDF file.")
            return

        out_dir = filedialog.askdirectory(title="Select Destination Folder for Exported Images")
        if not out_dir:
            return

        try:
            dpi = int(self.p2i_dpi_var.get())
            fmt = self.p2i_fmt_var.get()
            imgs = pdf_to_images(pdf_path, out_dir, dpi=dpi, img_format=fmt)
            messagebox.showinfo("Exported", f"Successfully exported {len(imgs)} pages as {fmt.upper()} images!")
            os.startfile(out_dir)
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))

    # -------------------------------------------------------------
    # TAB 5: WATERMARK & SECURITY
    # -------------------------------------------------------------
    def _build_security_tab(self):
        tab = self.tab_security_wm

        # Watermark
        wm_card = ttk.LabelFrame(tab, text=" 💧 Add Watermark ", padding=10)
        wm_card.pack(fill=tk.BOTH, expand=True, pady=(0, 6))

        w_row1 = ttk.Frame(wm_card)
        w_row1.pack(fill=tk.X, pady=2)
        ttk.Label(w_row1, text="PDF File:").pack(side=tk.LEFT, padx=4)
        self.wm_in_entry = ttk.Entry(w_row1, width=45)
        self.wm_in_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        ttk.Button(w_row1, text="Browse...", command=lambda: self._browse_entry(self.wm_in_entry)).pack(side=tk.LEFT, padx=2)

        w_row2 = ttk.Frame(wm_card)
        w_row2.pack(fill=tk.X, pady=4)
        ttk.Label(w_row2, text="Watermark Text:").pack(side=tk.LEFT, padx=4)
        self.wm_text_entry = ttk.Entry(w_row2, width=22)
        self.wm_text_entry.insert(0, "CONFIDENTIAL")
        self.wm_text_entry.pack(side=tk.LEFT, padx=4)

        ttk.Label(w_row2, text="Font Size:").pack(side=tk.LEFT, padx=6)
        self.wm_size_entry = ttk.Entry(w_row2, width=6)
        self.wm_size_entry.insert(0, "45")
        self.wm_size_entry.pack(side=tk.LEFT, padx=4)

        ttk.Button(w_row2, text="⚡ Apply Watermark", style="Primary.TButton", command=self._wm_run).pack(side=tk.LEFT, padx=12)

        # Protect & Unlock
        sec_card = ttk.LabelFrame(tab, text=" 🔒 Password Protect & Unlock PDF ", padding=10)
        sec_card.pack(fill=tk.BOTH, expand=True)

        s_row1 = ttk.Frame(sec_card)
        s_row1.pack(fill=tk.X, pady=2)
        ttk.Label(s_row1, text="PDF File:").pack(side=tk.LEFT, padx=4)
        self.sec_in_entry = ttk.Entry(s_row1, width=45)
        self.sec_in_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        ttk.Button(s_row1, text="Browse...", command=lambda: self._browse_entry(self.sec_in_entry)).pack(side=tk.LEFT, padx=2)

        s_row2 = ttk.Frame(sec_card)
        s_row2.pack(fill=tk.X, pady=4)
        ttk.Label(s_row2, text="Password:").pack(side=tk.LEFT, padx=4)
        self.sec_pwd_entry = ttk.Entry(s_row2, width=20, show="*")
        self.sec_pwd_entry.pack(side=tk.LEFT, padx=4)

        ttk.Button(s_row2, text="🔒 Protect (Encrypt)", style="Primary.TButton", command=self._sec_protect).pack(side=tk.LEFT, padx=6)
        ttk.Button(s_row2, text="🔓 Unlock (Decrypt)", style="Action.TButton", command=self._sec_unlock).pack(side=tk.LEFT, padx=6)

    def _browse_entry(self, entry_widget):
        f = filedialog.askopenfilename(title="Select PDF", filetypes=[("PDF Files", "*.pdf")])
        if f:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, f)

    def _wm_run(self):
        pdf_path = self.wm_in_entry.get().strip()
        text = self.wm_text_entry.get().strip()
        if not os.path.isfile(pdf_path):
            messagebox.showwarning("Watermark", "Please select a valid PDF.")
            return
        if not text:
            messagebox.showwarning("Watermark", "Please specify watermark text.")
            return

        out_path = filedialog.asksaveasfilename(
            title="Save Watermarked PDF As",
            defaultextension=".pdf",
            initialfile=os.path.splitext(os.path.basename(pdf_path))[0] + "_watermarked.pdf",
            filetypes=[("PDF File", "*.pdf")]
        )
        if not out_path:
            return

        try:
            size = int(self.wm_size_entry.get() or "45")
            watermark_pdf(pdf_path, out_path, text=text, font_size=size)
            messagebox.showinfo("Success", f"Watermark applied successfully!\n\nSaved to: {out_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _sec_protect(self):
        pdf_path = self.sec_in_entry.get().strip()
        pwd = self.sec_pwd_entry.get().strip()
        if not os.path.isfile(pdf_path) or not pwd:
            messagebox.showwarning("Protect", "Please specify a PDF and a password.")
            return
        out_path = filedialog.asksaveasfilename(
            title="Save Protected PDF As",
            defaultextension=".pdf",
            initialfile=os.path.splitext(os.path.basename(pdf_path))[0] + "_protected.pdf",
            filetypes=[("PDF File", "*.pdf")]
        )
        if not out_path:
            return
        try:
            protect_pdf(pdf_path, out_path, user_password=pwd)
            messagebox.showinfo("Success", "Password protection added successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _sec_unlock(self):
        pdf_path = self.sec_in_entry.get().strip()
        pwd = self.sec_pwd_entry.get().strip()
        if not os.path.isfile(pdf_path) or not pwd:
            messagebox.showwarning("Unlock", "Please specify a PDF and the password.")
            return
        out_path = filedialog.asksaveasfilename(
            title="Save Unlocked PDF As",
            defaultextension=".pdf",
            initialfile=os.path.splitext(os.path.basename(pdf_path))[0] + "_unlocked.pdf",
            filetypes=[("PDF File", "*.pdf")]
        )
        if not out_path:
            return
        try:
            ok = unlock_pdf(pdf_path, out_path, password=pwd)
            if ok:
                messagebox.showinfo("Success", "PDF unlocked and password removed successfully!")
            else:
                messagebox.showerror("Failed", "Incorrect password or decryption failed.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # -------------------------------------------------------------
    # TAB 6: EXTRACT & ROTATE
    # -------------------------------------------------------------
    def _build_extract_rotate_tab(self):
        tab = self.tab_extract_rotate

        # Extraction Card
        ex_card = ttk.LabelFrame(tab, text=" 📝 Extract Text & Embedded Media ", padding=10)
        ex_card.pack(fill=tk.BOTH, expand=True, pady=(0, 6))

        e_row1 = ttk.Frame(ex_card)
        e_row1.pack(fill=tk.X, pady=2)
        ttk.Label(e_row1, text="PDF File:").pack(side=tk.LEFT, padx=4)
        self.ex_in_entry = ttk.Entry(e_row1, width=45)
        self.ex_in_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        ttk.Button(e_row1, text="Browse...", command=lambda: self._browse_entry(self.ex_in_entry)).pack(side=tk.LEFT, padx=2)

        e_row2 = ttk.Frame(ex_card)
        e_row2.pack(fill=tk.X, pady=6)
        ttk.Button(e_row2, text="📄 Extract All Text (.txt)", style="Action.TButton", command=self._ex_text).pack(side=tk.LEFT, padx=4)
        ttk.Button(e_row2, text="🖼️ Extract Embedded Images", style="Action.TButton", command=self._ex_images).pack(side=tk.LEFT, padx=4)

        # Rotate Card
        rot_card = ttk.LabelFrame(tab, text=" 🔄 Rotate PDF Pages ", padding=10)
        rot_card.pack(fill=tk.BOTH, expand=True)

        r_row1 = ttk.Frame(rot_card)
        r_row1.pack(fill=tk.X, pady=2)
        ttk.Label(r_row1, text="PDF File:").pack(side=tk.LEFT, padx=4)
        self.rot_in_entry = ttk.Entry(r_row1, width=45)
        self.rot_in_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        ttk.Button(r_row1, text="Browse...", command=lambda: self._browse_entry(self.rot_in_entry)).pack(side=tk.LEFT, padx=2)

        r_row2 = ttk.Frame(rot_card)
        r_row2.pack(fill=tk.X, pady=4)
        ttk.Label(r_row2, text="Rotation Angle:").pack(side=tk.LEFT, padx=4)
        self.rot_angle_var = tk.IntVar(value=90)
        ttk.Radiobutton(r_row2, text="90° Clockwise", variable=self.rot_angle_var, value=90).pack(side=tk.LEFT, padx=4)
        ttk.Radiobutton(r_row2, text="180° Upside Down", variable=self.rot_angle_var, value=180).pack(side=tk.LEFT, padx=4)
        ttk.Radiobutton(r_row2, text="270° Counter-Clockwise", variable=self.rot_angle_var, value=270).pack(side=tk.LEFT, padx=4)

        ttk.Button(r_row2, text="⚡ Rotate & Save", style="Primary.TButton", command=self._rot_run).pack(side=tk.LEFT, padx=12)

    def _ex_text(self):
        pdf_path = self.ex_in_entry.get().strip()
        if not os.path.isfile(pdf_path):
            messagebox.showwarning("Extract", "Please select a valid PDF.")
            return
        out_txt = filedialog.asksaveasfilename(
            title="Save Extracted Text As",
            defaultextension=".txt",
            filetypes=[("Text File", "*.txt")]
        )
        if not out_txt:
            return
        try:
            extract_text_from_pdf(pdf_path, output_txt_path=out_txt)
            messagebox.showinfo("Success", f"Text extracted successfully!\nSaved to: {out_txt}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _ex_images(self):
        pdf_path = self.ex_in_entry.get().strip()
        if not os.path.isfile(pdf_path):
            messagebox.showwarning("Extract", "Please select a valid PDF.")
            return
        out_dir = filedialog.askdirectory(title="Select Destination Folder for Extracted Images")
        if not out_dir:
            return
        try:
            imgs = extract_embedded_images(pdf_path, out_dir)
            messagebox.showinfo("Success", f"Extracted {len(imgs)} image(s) from PDF!")
            os.startfile(out_dir)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _rot_run(self):
        pdf_path = self.rot_in_entry.get().strip()
        if not os.path.isfile(pdf_path):
            messagebox.showwarning("Rotate", "Please select a valid PDF.")
            return
        angle = self.rot_angle_var.get()
        out_path = filedialog.asksaveasfilename(
            title="Save Rotated PDF As",
            defaultextension=".pdf",
            initialfile=os.path.splitext(os.path.basename(pdf_path))[0] + f"_rotated_{angle}.pdf",
            filetypes=[("PDF File", "*.pdf")]
        )
        if not out_path:
            return
        try:
            rotate_pdf_pages(pdf_path, out_path, angle=angle)
            messagebox.showinfo("Success", f"Rotated PDF saved to: {out_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))


def main():
    app = PDFMasterApp()
    app.mainloop()


if __name__ == "__main__":
    main()
