import asyncio
import threading
import re
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import pathlib
import os
import shutil
import io
 
try:
    import fitz
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
    from kreuzberg import extract_file, ExtractionConfig, ImageExtractionConfig, OcrConfig, TesseractConfig, OutputFormat
except ImportError:
    extract_file = None
    ExtractionConfig = None
    OcrConfig = None
    TesseractConfig = None
    OutputFormat = None
    ImageExtractionConfig = None
 
if onnxruntime is not None:
    # Workaround for ONNXRuntime requiring int64 inputs when the model produces int32.
    original_run = onnxruntime.InferenceSession.run
    def patched_run(self, output_names, input_feed, run_options=None):
        input_feed = {k: v.astype('int64') if hasattr(v, 'dtype') and v.dtype == 'int32' else v for k, v in input_feed.items()}
        return original_run(self, output_names, input_feed, run_options)
    onnxruntime.InferenceSession.run = patched_run
 
 
class PDFToMarkdownApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF to Markdown Converter")
        # ZVÝŠENÁ VÝŠKA OKNA[cite: 3]
        self.root.geometry("520x720")
        self.root.minsize(520, 680)
        self.root.resizable(False, True)
       
        self.selected_file = None
        self.is_converting = False
        self.kreuzberg_installed = extract_file is not None
        self.pymupdf_installed = pymupdf4llm is not None
        self.tesseract_path = self._find_tesseract_cmd()
        self.tessdata_dir = self._find_tessdata_dir(self.tesseract_path)
        self._update_tesseract_environment()
        self.ocr_installed = pytesseract is not None and self.tesseract_path is not None
        self.ocr_supported = self._check_ocr_support()
        self.ocr_pdf_available = (
            fitz is not None and Image is not None and self.ocr_installed
        )
        self.ocr_enabled_var = tk.BooleanVar(value=self.ocr_installed and self.ocr_supported)
        self.ocr_lang_var = tk.StringVar(value="ces")
        self.ocr_lang_var.trace_add("write", lambda *args: self._refresh_tesseract_info())
        self.mode_var = tk.StringVar(value="markdown")
        self.engine_var = tk.StringVar(
            value="kreuzberg"
            if self.kreuzberg_installed
            else ("pymupdf" if self.pymupdf_installed else "kreuzberg")
        )
       
        # Main frame
        main_frame = tk.Frame(root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
       
        # Title
        title = tk.Label(main_frame, text="PDF to Markdown Converter",
                        font=("Arial", 16, "bold"))
        title.pack(pady=10)
       
        # Select file button
        select_btn = tk.Button(main_frame, text="Vybrat PDF soubor",
                              command=self.select_file,
                              width=30, height=2, bg="#4CAF50",
                              fg="white", font=("Arial", 10))
        select_btn.pack(pady=10)
 
        # Manual path button for slow file dialogs
        manual_btn = tk.Button(main_frame, text="Zadat cestu k PDF",
                               command=self.enter_file_path,
                               width=30, height=2, bg="#FFC107",
                               fg="white", font=("Arial", 10))
        manual_btn.pack(pady=5)
 
        mode_frame = tk.Frame(main_frame)
        mode_label = tk.Label(mode_frame, text="Výstupní režim:", font=("Arial", 10, "bold"))
        mode_label.pack(side=tk.LEFT, padx=(0, 10))
        markdown_radio = tk.Radiobutton(
            mode_frame,
            text="Markdown",
            variable=self.mode_var,
            value="markdown",
            command=self._update_ui_state,
        )
        ocr_pdf_radio = tk.Radiobutton(
            mode_frame,
            text="OCR PDF",
            variable=self.mode_var,
            value="ocr_pdf",
            command=self._update_ui_state,
        )
        markdown_radio.pack(side=tk.LEFT)
        ocr_pdf_radio.pack(side=tk.LEFT, padx=(10, 0))
        mode_frame.pack(pady=5)
 
        engine_frame = tk.Frame(main_frame)
        engine_label = tk.Label(engine_frame, text="Engine:", font=("Arial", 10, "bold"))
        engine_label.pack(side=tk.LEFT, padx=(0, 10))
        kreuzberg_radio = tk.Radiobutton(
            engine_frame,
            text="Kreuzberg",
            variable=self.engine_var,
            value="kreuzberg",
            command=self._update_ui_state,
        )
        pymupdf_radio = tk.Radiobutton(
            engine_frame,
            text="PyMuPDF",
            variable=self.engine_var,
            value="pymupdf",
            command=self._update_ui_state,
        )
        kreuzberg_radio.pack(side=tk.LEFT)
        pymupdf_radio.pack(side=tk.LEFT, padx=(10, 0))
        engine_frame.pack(pady=5)
        self.engine_radios = [kreuzberg_radio, pymupdf_radio]
 
        ocr_check = tk.Checkbutton(
            main_frame,
            text="Použít OCR (pokud dostupné)",
            variable=self.ocr_enabled_var,
            onvalue=True,
            offvalue=False,
        )
        self.ocr_check = ocr_check
        ocr_check.pack(pady=5)
 
        self.tesseract_button = tk.Button(
            main_frame,
            text="Zadat cestu k Tesseract",
            command=self.ask_tesseract_path,
            width=30, height=1, bg="#9E9E9E",
            fg="white", font=("Arial", 9)
        )
        self.tesseract_button.pack(pady=2)
 
        lang_frame = tk.Frame(main_frame)
        lang_label = tk.Label(lang_frame, text="OCR jazyk:", font=("Arial", 10, "bold"))
        lang_label.pack(side=tk.LEFT, padx=(0, 10))
        lang_menu = tk.OptionMenu(
            lang_frame,
            self.ocr_lang_var,
            "ces",
            "eng",
            "deu",
            "spa",
        )
        lang_menu.config(width=10)
        lang_menu.pack(side=tk.LEFT)
        lang_frame.pack(pady=5)
 
        self.tesseract_info_label = tk.Label(
            main_frame,
            text=self._build_tesseract_info_text(),
            wraplength=400,
            justify=tk.LEFT,
            fg="#555555",
            font=("Arial", 8)
        )
        self.tesseract_info_label.pack(pady=(2, 8))
 
        # Selected file label
        self.file_label = tk.Label(main_frame, text="Žádný soubor vybrán",
                                   wraplength=400, justify=tk.LEFT,
                                   fg="#666666")
        self.file_label.pack(pady=10)
       
        # Convert button
        self.convert_btn = tk.Button(main_frame, text="Převést PDF na Markdown",
                               command=self.convert_file,
                               width=30, height=2, bg="#2196F3",
                               fg="white", font=("Arial", 10),
                               state=tk.DISABLED)
        self.convert_btn.pack(pady=10)
       
        # Status label
        self.status_label = tk.Label(main_frame, text="",
                                    wraplength=400, justify=tk.LEFT,
                                    fg="#333333", font=("Arial", 9))
        self.status_label.pack(pady=10)
 
        self._update_ui_state(initial=True)
 
    def _find_tesseract_cmd(self):
        candidates = []
        if pytesseract is not None:
            try:
                cmd = pytesseract.pytesseract.tesseract_cmd
                if cmd:
                    candidates.append(cmd)
            except Exception:
                pass
        candidates.append(shutil.which("tesseract"))
        candidates.extend([
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"C:\Users\%USERNAME%\AppData\Local\Programs\Tesseract-OCR\tesseract.exe",
        ])
        for candidate in candidates:
            if not candidate:
                continue
            candidate = os.path.expandvars(candidate)
            if os.path.isfile(candidate):
                return candidate
        return None
 
    def _find_tessdata_dir(self, tesseract_path):
        if not tesseract_path:
            return None
        base = pathlib.Path(tesseract_path).resolve().parent
        candidates = [
            base / "tessdata",
            base / "share" / "tessdata",
            base.parent / "tessdata",
            base / "../tessdata",
        ]
        for candidate in candidates:
            candidate = candidate.resolve()
            if candidate.is_dir():
                return str(candidate)
        for candidate in base.glob("**/tessdata"):
            if candidate.is_dir():
                return str(candidate)
        return None
 
    def _update_tesseract_environment(self):
        if pytesseract is None:
            return
        if self.tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
        if self.tessdata_dir:
            os.environ["TESSDATA_PREFIX"] = self.tessdata_dir
        else:
            os.environ.pop("TESSDATA_PREFIX", None)
 
    def _get_tesseract_config(self):
        if self.tessdata_dir:
            return f'--tessdata-dir {self.tessdata_dir}'
        return ""
 
    def _build_tesseract_info_text(self):
        path_text = self.tesseract_path or "Tesseract nenalezen"
        tessdata_text = self.tessdata_dir or "tessdata nenalezen"
        return f"Tesseract: {path_text}\nTessdata: {tessdata_text}\nJazyk: {self.ocr_lang_var.get()}"
 
    def _refresh_tesseract_info(self):
        if hasattr(self, 'tesseract_info_label'):
            self.tesseract_info_label.config(text=self._build_tesseract_info_text())
 
    def ask_tesseract_path(self):
        if pytesseract is None:
            messagebox.showerror("Chyba", "Knihovna pytesseract není nainstalovaná.")
            return
        path = simpledialog.askstring(
            "Cesta k Tesseract",
            "Zadejte úplnou cestu k tesseract.exe:",
            initialvalue=self.tesseract_path or "",
            parent=self.root,
        )
        if not path:
            return
        path = os.path.expandvars(path.strip())
        if not os.path.isfile(path):
            messagebox.showerror("Chyba", "Tesseract nebyl nalezen.")
            return
        self.tesseract_path = path
        self.tessdata_dir = self._find_tessdata_dir(path)
        self._update_tesseract_environment()
        self.ocr_installed = True
        self.ocr_supported = self._check_ocr_support()
        self.ocr_pdf_available = fitz is not None and Image is not None and self.ocr_installed
        self._update_ui_state()
 
    def _check_ocr_support(self):
        if select_ocr_function is None or pymupdf4llm is None:
            return False
        if not self.ocr_installed:
            return False
        try:
            self.ocr_function = select_ocr_function()
            return callable(self.ocr_function)
        except Exception:
            return False
 
    def select_file(self):
        try:
            file_path = filedialog.askopenfilename(
                parent=self.root,
                title="Vyberte PDF soubor",
                initialdir=os.path.expanduser("~"),
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
            )
            if file_path:
                self._set_selected_file(file_path)
        except Exception as exc:
            messagebox.showerror("Chyba", f"Dialog selhal: {exc}")
 
    def enter_file_path(self):
        file_path = simpledialog.askstring("Zadat cestu", "Zadejte úplnou cestu k PDF:", parent=self.root)
        if file_path and os.path.isfile(file_path.strip()):
            self._set_selected_file(file_path.strip())
 
    def _set_selected_file(self, file_path):
        self.selected_file = file_path
        display_path = file_path if len(file_path) <= 50 else "..." + file_path[-47:]
        self.file_label.config(text=f"Vybrán: {display_path}")
        self._update_ui_state()
 
    def _update_ui_state(self, initial=False):
        mode = self.mode_var.get()
        self.convert_btn.config(text="Provést OCR konverzi PDF" if mode == "ocr_pdf" else "Převést PDF na Markdown")

        if mode == "ocr_pdf":
            for widget in self.engine_radios:
                widget.config(state=tk.DISABLED)
            self.ocr_enabled_var.set(True)
            self.ocr_check.config(state=tk.DISABLED)
            if not self.ocr_pdf_available:
                self.convert_btn.config(state=tk.DISABLED)
                return
            self.convert_btn.config(state=tk.NORMAL if self.selected_file else tk.DISABLED)
        else:
            for widget in self.engine_radios:
                widget.config(state=tk.NORMAL)
            self.ocr_check.config(state=tk.NORMAL)
            self.convert_btn.config(state=tk.NORMAL if self.selected_file else tk.DISABLED)
 
    def convert_file(self):
        if not self.selected_file: return
        self.is_converting = True
        self.convert_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Převádím... prosím čekejte", fg="#FF9800")
        threading.Thread(target=self._convert_file_thread, daemon=True).start()
 
    def _convert_file_thread(self):
        try:
            mode = self.mode_var.get()
            if mode == "ocr_pdf":
                pdf_doc = self._extract_searchable_pdf_with_ocr(self.selected_file)
                self.root.after(0, self._post_conversion, None, pdf_doc, None)
            elif self.engine_var.get() == "kreuzberg":
                result = self._extract_markdown_with_kreuzberg(self.selected_file)
                self.root.after(0, self._post_conversion, result.content, result, None)
            else:
                md_text = self._extract_markdown_with_pymupdf(self.selected_file)
                self.root.after(0, self._post_conversion, md_text, None, None)
        except Exception as e:
            self.root.after(0, self._post_conversion, None, None, e)

    def _extract_markdown_with_kreuzberg(self, file_path):
        config_kwargs = {
            "output_format": OutputFormat.MARKDOWN if OutputFormat else "markdown",
            "include_document_structure": True,
            "images": ImageExtractionConfig() if ImageExtractionConfig else True,
        }
        if self.ocr_enabled_var.get():
            config_kwargs["force_ocr"] = True
            config_kwargs["ocr"] = OcrConfig(backend="tesseract", language=self.ocr_lang_var.get())
 
        return asyncio.run(extract_file(file_path, config=ExtractionConfig(**config_kwargs)))
 
    def _extract_markdown_with_pymupdf(self, file_path):
        params = {"use_ocr": self.ocr_enabled_var.get(), "page_separators": True}
        if self.ocr_enabled_var.get(): params["ocr_language"] = self.ocr_lang_var.get()
        return pymupdf4llm.to_markdown(file_path, **params)
 
    def _extract_searchable_pdf_with_ocr(self, file_path):
        doc = fitz.open(file_path)
        out_doc = fitz.open()
        for page in doc:
            pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
            pdf_bytes = pytesseract.image_to_pdf_or_hocr(Image.open(io.BytesIO(pix.tobytes())), lang=self.ocr_lang_var.get(), config=self._get_tesseract_config())
            out_doc.insert_pdf(fitz.open(stream=pdf_bytes, filetype="pdf"))
        doc.close()
        return out_doc
 
    def _save_extracted_images(self, output_file, markdown_text, result):
        if not result or not getattr(result, "images", None): return markdown_text
        img_dir = output_file.parent / output_file.stem
        img_dir.mkdir(exist_ok=True)
        for idx, img in enumerate(result.images):
            if isinstance(img, dict) and img.get("data"):
                (img_dir / f"image_{idx}.png").write_bytes(img["data"])
        return markdown_text
 
    def _post_conversion(self, md_text, result, error):
        self.is_converting = False
        self.update_ui = lambda: self._update_ui_state()
        self.root.after(0, self.update_ui)
 
        if error:
            messagebox.showerror("Chyba", str(error))
            return
 
        path = pathlib.Path(self.selected_file)
        ext = ".pdf" if self.mode_var.get() == "ocr_pdf" else ".md"
        out = filedialog.asksaveasfilename(defaultextension=ext, initialfile=path.stem + ("_ocr" if ext==".pdf" else "") + ext)
        
        if out:
            if ext == ".pdf": result.save(out)
            else:
                md_text = self._save_extracted_images(pathlib.Path(out), md_text, result)
                pathlib.Path(out).write_text(md_text, encoding="utf-8")
            messagebox.showinfo("Hotovo", f"Uloženo do: {out}")
 
if __name__ == "__main__":
    root = tk.Tk()
    app = PDFToMarkdownApp(root)
    root.mainloop()