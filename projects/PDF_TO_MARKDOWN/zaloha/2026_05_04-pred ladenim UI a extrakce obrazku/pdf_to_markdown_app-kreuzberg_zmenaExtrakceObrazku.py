import asyncio
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import pathlib
import os
import io
import shutil
import re

# =========================
# Optional dependencies
# =========================
try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    import pytesseract
except ImportError:
    pytesseract = None

try:
    import onnxruntime
except ImportError:
    onnxruntime = None

try:
    import pymupdf4llm
    from pymupdf4llm.helpers.document_layout import select_ocr_function
except ImportError:
    pymupdf4llm = None
    select_ocr_function = None

try:
    from kreuzberg import (
        extract_file,
        ExtractionConfig,
        ImageExtractionConfig,
        OcrConfig,
        OutputFormat,
    )
except ImportError:
    extract_file = None
    ExtractionConfig = None
    ImageExtractionConfig = None
    OcrConfig = None
    OutputFormat = None


# =========================
# ONNXRuntime workaround
# =========================
if onnxruntime is not None:
    _orig_run = onnxruntime.InferenceSession.run

    def _patched_run(self, output_names, input_feed, run_options=None):
        input_feed = {
            k: v.astype("int64") if hasattr(v, "dtype") and v.dtype == "int32" else v
            for k, v in input_feed.items()
        }
        return _orig_run(self, output_names, input_feed, run_options)

    onnxruntime.InferenceSession.run = _patched_run


# =========================
# Main application
# =========================
class PDFToMarkdownApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF to Markdown Converter")
        self.root.geometry("600x650")
        self.root.minsize(550, 600)

        self.selected_file = None
        self.is_converting = False

        # Capability detection
        self.kreuzberg_installed = extract_file is not None
        self.pymupdf_installed = pymupdf4llm is not None

        self.tesseract_path = self._find_tesseract_cmd()
        self.tessdata_dir = self._find_tessdata_dir(self.tesseract_path)
        self._update_tesseract_environment()

        self.ocr_installed = pytesseract is not None and self.tesseract_path is not None
        self.ocr_supported = self._check_ocr_support()
        self.ocr_pdf_available = fitz is not None and Image is not None and self.ocr_installed

        self.ocr_enabled_var = tk.BooleanVar(value=self.ocr_installed)
        self.ocr_lang_var = tk.StringVar(value="ces")
        self.ocr_lang_var.trace_add("write", lambda *_: self._refresh_tesseract_info())

        self.mode_var = tk.StringVar(value="markdown")
        self.engine_var = tk.StringVar(
            value="kreuzberg"
            if self.kreuzberg_installed
            else "pymupdf"
        )

        # ================= UI =================

        main = tk.Frame(root, padx=30, pady=10)
        main.pack(fill=tk.BOTH, expand=True)

        tk.Label(main, text="PDF to Markdown Converter",
                 font=("Calibri", 18, "bold")).pack(pady=(0, 20))

        file_frame = tk.Frame(main)
        file_frame.pack(fill=tk.X)

        tk.Button(
            file_frame,
            text="Vybrat PDF",
            height=2,
            bg="#4CAF50",
            fg="white",
            command=self.select_file
        ).pack(fill=tk.X)

        self.file_label = tk.Label(
            file_frame, text="Žádný soubor vybrán",
            fg="#666666", wraplength=500
        )
        self.file_label.pack(pady=5)

        settings = tk.Frame(main)
        settings.pack(fill=tk.X, pady=10)

        tk.Radiobutton(
            settings, text="Markdown",
            variable=self.mode_var, value="markdown",
            command=self._update_ui_state
        ).pack(side=tk.LEFT)

        tk.Radiobutton(
            settings, text="OCR PDF",
            variable=self.mode_var, value="ocr_pdf",
            command=self._update_ui_state
        ).pack(side=tk.LEFT, padx=10)

        tk.Radiobutton(
            settings, text="Kreuzberg",
            variable=self.engine_var, value="kreuzberg"
        ).pack(side=tk.LEFT, padx=10)

        tk.Radiobutton(
            settings, text="PyMuPDF",
            variable=self.engine_var, value="pymupdf"
        ).pack(side=tk.LEFT)

        tk.Checkbutton(
            main, text="Použít OCR",
            variable=self.ocr_enabled_var
        ).pack(anchor="w")

        self.convert_btn = tk.Button(
            main,
            text="Převést",
            height=2,
            bg="#2196F3",
            fg="white",
            state=tk.DISABLED,
            command=self.convert_file
        )
        self.convert_btn.pack(fill=tk.X, pady=20)

        self.status_label = tk.Label(main, text="", fg="#444444")
        self.status_label.pack()

        status = tk.Frame(root, relief=tk.SUNKEN, bd=1)
        status.pack(side=tk.BOTTOM, fill=tk.X)

        self.tesseract_info_label = tk.Label(
            status, font=("Consolas", 8),
            text=self._build_tesseract_info_text()
        )
        self.tesseract_info_label.pack(anchor="w", padx=10)

        self._update_ui_state()

    # ================= OCR helpers =================

    def _find_tesseract_cmd(self):
        candidates = [
            shutil.which("tesseract"),
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ]
        for c in candidates:
            if c and os.path.isfile(c):
                return c
        return None

    def _find_tessdata_dir(self, tesseract_path):
        if not tesseract_path:
            return None
        base = pathlib.Path(tesseract_path).parent
        for p in [base / "tessdata", base.parent / "tessdata"]:
            if p.is_dir():
                return str(p)
        return None

    def _update_tesseract_environment(self):
        if pytesseract is None:
            return
        if self.tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
        if self.tessdata_dir:
            os.environ["TESSDATA_PREFIX"] = self.tessdata_dir

    def _build_tesseract_info_text(self):
        return f"Tesseract: {self.tesseract_path or 'nenalezen'} | Jazyk: {self.ocr_lang_var.get()}"

    def _refresh_tesseract_info(self):
        self.tesseract_info_label.config(
            text=self._build_tesseract_info_text()
        )

    def _check_ocr_support(self):
        if select_ocr_function is None:
            return False
        try:
            return callable(select_ocr_function())
        except Exception:
            return False

    # ================= UI helpers =================

    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if path:
            self.selected_file = path
            self.file_label.config(text=path)
            self._update_ui_state()

    def _update_ui_state(self):
        enabled = bool(self.selected_file)
        self.convert_btn.config(state=tk.NORMAL if enabled else tk.DISABLED)

    # ================= Conversion =================

    def convert_file(self):
        ext = ".pdf" if self.mode_var.get() == "ocr_pdf" else ".md"
        out = filedialog.asksaveasfilename(defaultextension=ext)
        if not out:
            return

        self.status_label.config(text="Zpracovávám...")
        self.convert_btn.config(state=tk.DISABLED)

        threading.Thread(
            target=self._convert_thread,
            args=(out,),
            daemon=True
        ).start()

    def _convert_thread(self, out_path):
        try:
            if self.mode_var.get() == "ocr_pdf":
                pdf = self._extract_searchable_pdf_with_ocr(self.selected_file)
                pdf.save(out_path)
            else:
                img_dir = os.path.join(os.path.dirname(out_path), "images")

                md = self._extract_markdown_with_pymupdf(self.selected_file)

                images_by_page = self._extract_embedded_images_only(
                    self.selected_file, img_dir
                )

                md = self._inject_image_links_into_markdown(
                    md, images_by_page, "images"
                )

                pathlib.Path(out_path).write_text(md, encoding="utf-8")

            self.root.after(
                0, lambda: messagebox.showinfo("Hotovo", "Zpracování dokončeno.")
            )
        except Exception as e:
            self.root.after(
                0, lambda: messagebox.showerror("Chyba", str(e))
            )
        finally:
            self.root.after(
                0, lambda: self.convert_btn.config(state=tk.NORMAL)
            )

    # ================= Engines =================

    def _extract_markdown_with_pymupdf(self, path):
        return pymupdf4llm.to_markdown(
            path,
            use_ocr=self.ocr_enabled_var.get(),
            ocr_language=self.ocr_lang_var.get(),
            page_separators=True,
            write_images=False
        )

    def _extract_embedded_images_only(self, pdf_path, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        doc = fitz.open(pdf_path)
        images_by_page = {}
        idx = 0

        for pno, page in enumerate(doc, start=1):
            for img in page.get_images(full=True):
                base = doc.extract_image(img[0])
                name = f"img_p{pno}_{idx}.{base['ext']}"
                with open(os.path.join(output_dir, name), "wb") as f:
                    f.write(base["image"])
                images_by_page.setdefault(pno, []).append(name)
                idx += 1

        doc.close()
        return images_by_page

    def _inject_image_links_into_markdown(self, md, images_by_page, img_path):
        blocks = re.split(r"\n-{3,}\n", md)
        result = []

        for i, block in enumerate(blocks, start=1):
            result.append(block)
            if i in images_by_page:
                result.append("\n**Obrázky:**\n")
                for img in images_by_page[i]:
                    result.append(f"{img_path}/{img}\n")

        return "\n\n---\n\n".join(result)

    def _extract_searchable_pdf_with_ocr(self, path):
        doc = fitz.open(path)
        out = fitz.open()
        for page in doc:
            pix = page.get_pixmap(dpi=300)
            pdf = pytesseract.image_to_pdf_or_hocr(
                Image.open(io.BytesIO(pix.tobytes())),
                lang=self.ocr_lang_var.get()
            )
            out.insert_pdf(fitz.open(stream=pdf, filetype="pdf"))
        doc.close()
        return out


# =========================
# Run
# =========================
if __name__ == "__main__":
    root = tk.Tk()
    app = PDFToMarkdownApp(root)
    root.mainloop()