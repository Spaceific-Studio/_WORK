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
    from kreuzberg import extract_file, ExtractionConfig, OcrConfig, TesseractConfig, OutputFormat
except ImportError:
    extract_file = None
    ExtractionConfig = None
    OcrConfig = None
    TesseractConfig = None
    OutputFormat = None
 
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
        self.root.geometry("520x480")
        self.root.minsize(520, 420)
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
        convert_btn = tk.Button(main_frame, text="Převést PDF na Markdown",
                               command=self.convert_file,
                               width=30, height=2, bg="#2196F3",
                               fg="white", font=("Arial", 10),
                               state=tk.DISABLED)
        self.convert_btn = convert_btn
        convert_btn.pack(pady=10)
       
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
        # common Windows install locations
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
        # search one level deeper if still not found
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
            messagebox.showerror(
                "Chyba",
                "Knihovna pytesseract není nainstalovaná. Nainstalujte ji pomocí `pip install pytesseract`."
            )
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
            messagebox.showerror(
                "Chyba",
                "Tesseract nebyl nalezen. Zkontrolujte cestu a zkuste to znovu."
            )
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
            self.ocr_function = None
            return False
        if not self.ocr_installed:
            self.ocr_function = None
            return False
        try:
            self.ocr_function = select_ocr_function()
            return callable(self.ocr_function)
        except Exception:
            self.ocr_function = None
            return False
 
    def select_file(self):
        """Otevře dialog pro výběr PDF souboru."""
        self.root.lift()
        self.root.focus_force()
        self.root.update_idletasks()
 
        try:
            file_path = filedialog.askopenfilename(
                parent=self.root,
                title="Vyberte PDF soubor",
                initialdir=os.path.expanduser("~"),
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
            )
        except Exception as exc:
            messagebox.showerror("Chyba", f"Dialog pro výběr souboru selhal:\n{exc}")
            return
 
        if file_path:
            self._set_selected_file(file_path)
 
    def enter_file_path(self):
        """Zobrazí okno pro ruční zadání cesty k PDF souboru."""
        file_path = simpledialog.askstring(
            "Zadat cestu",
            "Zadejte úplnou cestu k PDF souboru:",
            parent=self.root
        )
        if not file_path:
            return
 
        file_path = file_path.strip()
        if not file_path.lower().endswith(".pdf"):
            messagebox.showerror("Chyba", "Zadejte cestu k souboru s koncovkou .pdf")
            return
 
        if not os.path.isfile(file_path):
            messagebox.showerror("Chyba", "Soubor neexistuje. Zkontrolujte cestu a zkuste to znovu.")
            return
 
        self._set_selected_file(file_path)
 
    def _set_selected_file(self, file_path):
        self.selected_file = file_path
        display_path = file_path
        if len(display_path) > 50:
            display_path = "..." + display_path[-47:]
 
        self.file_label.config(text=f"Vybrán: {display_path}")
        self.status_label.config(text="", fg="#333333")
        self._update_ui_state()
 
    def _update_ui_state(self, initial=False):
        mode = self.mode_var.get()
        if mode == "ocr_pdf":
            for widget in self.engine_radios:
                widget.config(state=tk.DISABLED)
            self.ocr_enabled_var.set(True)
            self.ocr_check.config(state=tk.DISABLED)
            if not self.ocr_pdf_available:
                self.convert_btn.config(state=tk.DISABLED)
                if self.tesseract_path:
                    self.status_label.config(
                        text="OCR PDF režim vyžaduje PyMuPDF/PIL a platnou cestu k Tesseract.",
                        fg="#FF9800",
                    )
                else:
                    self.status_label.config(
                        text="OCR PDF režim vyžaduje Tesseract. Zadejte cestu k tesseract.exe.",
                        fg="#FF9800",
                    )
                return
            if self.selected_file:
                self.convert_btn.config(state=tk.NORMAL)
            else:
                self.convert_btn.config(state=tk.DISABLED)
            self.status_label.config(
                text="OCR PDF režim připraven. Výstup bude vektorový PDF s OCR textovou vrstvou.",
                fg="#4CAF50",
            )
            return
 
        for widget in self.engine_radios:
            widget.config(state=tk.NORMAL)
        self.ocr_check.config(state=tk.NORMAL)
 
        engine = self.engine_var.get()
        if engine == "kreuzberg":
            engine_available = self.kreuzberg_installed
            engine_name = "Kreuzberg"
        else:
            engine_available = self.pymupdf_installed
            engine_name = "PyMuPDF"
 
        if not engine_available:
            self.convert_btn.config(state=tk.DISABLED)
            self.status_label.config(
                text=f"{engine_name} není nainstalován. Vyberte jiný engine nebo jej nainstalujte.",
                fg="#FF9800",
            )
            return
 
        if self.selected_file:
            self.convert_btn.config(state=tk.NORMAL)
        else:
            self.convert_btn.config(state=tk.DISABLED)
 
        if engine == "kreuzberg":
            if not self.ocr_installed:
                self.status_label.config(
                    text="Kreuzberg je připraveno. OCR není nainstalované nebo není v PATH.",
                    fg="#FF9800",
                )
            else:
                self.status_label.config(
                    text="Kreuzberg je připraveno. OCR je dostupné a lze ho použít.",
                    fg="#4CAF50",
                )
        else:
            if not self.ocr_supported:
                self.status_label.config(
                    text="PyMuPDF engine je připraven. OCR není plně podporováno.",
                    fg="#FF9800",
                )
            else:
                self.status_label.config(
                    text="PyMuPDF engine je připraven. OCR je dostupné a lze ho použít.",
                    fg="#4CAF50",
                )
 
    def convert_file(self):
        """Spustí převod PDF na pozadí, aby GUI nezamrzlo."""
        if not self.selected_file:
            messagebox.showerror("Chyba", "Nejdříve vyberte soubor!")
            return
 
        selected_mode = self.mode_var.get()
        if selected_mode == "ocr_pdf":
            if not self.ocr_pdf_available:
                messagebox.showerror(
                    "Chyba",
                    "OCR PDF režim vyžaduje Tesseract a knihovny PyMuPDF/PIL."
                )
                return
        else:
            selected_engine = self.engine_var.get()
            if selected_engine == "kreuzberg" and not self.kreuzberg_installed:
                messagebox.showerror(
                    "Chyba",
                    "Knihovna kreuzberg není nainstalovaná. Nainstalujte ji pomocí `pip install kreuzberg`."
                )
                return
            if selected_engine == "pymupdf" and not self.pymupdf_installed:
                messagebox.showerror(
                    "Chyba",
                    "Knihovna pymupdf4llm není nainstalovaná. Nainstalujte ji pomocí `pip install pymupdf4llm`."
                )
                return
 
        if self.is_converting:
            return
 
        proceed = messagebox.askyesno(
            "Potvrdit převod",
            "Opravdu chcete převést vybraný PDF soubor na Markdown?"
        )
        if not proceed:
            return
 
        if self.ocr_enabled_var.get() and selected_mode != "ocr_pdf":
            selected_engine = self.engine_var.get()
            if selected_engine == "kreuzberg" and not self.ocr_installed:
                proceed = messagebox.askyesno(
                    "OCR není dostupné",
                    "OCR není nainstalované nebo není dostupné v PATH. "
                    "Přepnout na převod bez OCR?"
                )
                if not proceed:
                    return
                self.ocr_enabled_var.set(False)
            elif selected_engine == "pymupdf" and not self.ocr_supported:
                proceed = messagebox.askyesno(
                    "OCR není plně podporováno",
                    "OCR není plně podporováno tímto modulem. "
                    "Přepnout na převod bez OCR?"
                )
                if not proceed:
                    return
                self.ocr_enabled_var.set(False)
 
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
                return
            
            if self.engine_var.get() == "kreuzberg":
                result = self._extract_markdown_with_kreuzberg(self.selected_file)
                md_text = result.content or ""
                self.root.after(0, self._post_conversion, md_text, result, None)
            else:
                md_text = self._extract_markdown_with_pymupdf(self.selected_file)
                # PyMuPDF doesn't return images - they're embedded in markdown
                self.root.after(0, self._post_conversion, md_text, None, None)
        except Exception as e:
            self.root.after(0, self._post_conversion, None, None, e)

    def _extract_markdown_with_kreuzberg(self, file_path):
        if extract_file is None:
            raise ImportError("Knihovna kreuzberg není nainstalovaná. Nainstalujte ji pomocí `pip install kreuzberg`.")

        config_kwargs = {
            "output_format": OutputFormat.MARKDOWN if OutputFormat is not None else "markdown",
            "include_document_structure": True,
            "images": True,
        }
        if self.ocr_enabled_var.get():
            if OcrConfig is None:
                raise RuntimeError("OCR konfigurace není dostupná v knihovně kreuzberg.")
            ocr_kwargs = {
                "backend": "tesseract",
                "language": self.ocr_lang_var.get(),
            }
            if TesseractConfig is not None:
                ocr_kwargs["tesseract_config"] = TesseractConfig()
            config_kwargs["force_ocr"] = True
            config_kwargs["ocr"] = OcrConfig(**ocr_kwargs)
 
        config = ExtractionConfig(**config_kwargs) if ExtractionConfig is not None else None
        result = asyncio.run(extract_file(file_path, config=config))
        
        # Debug: Print result structure
        print(f"DEBUG Kreuzberg result type: {type(result)}")
        print(f"DEBUG Kreuzberg result attrs: {[a for a in dir(result) if not a.startswith('_')]}")
        if hasattr(result, 'images'):
            print(f"DEBUG Kreuzberg result.images type: {type(result.images)}")
            print(f"DEBUG Kreuzberg result.images value: {result.images}")
        
        return result
 
    def _extract_markdown_with_pymupdf(self, file_path):
        if pymupdf4llm is None:
            raise ImportError("Knihovna pymupdf4llm není nainstalovaná. Nainstalujte ji pomocí `pip install pymupdf4llm`.")
 
        params = {
            "show_progress": False,
            "use_ocr": self.ocr_enabled_var.get() and self.ocr_supported,
            "force_ocr": self.ocr_enabled_var.get() and self.ocr_supported,
            "page_separators": True,
        }
        if self.ocr_enabled_var.get() and self.ocr_supported:
            params["ocr_language"] = self.ocr_lang_var.get()
            if getattr(self, "ocr_function", None) is not None:
                params["ocr_function"] = self.ocr_function
 
        return pymupdf4llm.to_markdown(file_path, **params)
 
    def _extract_searchable_pdf_with_ocr(self, file_path):
        if fitz is None or Image is None:
            raise ImportError(
                "Pro OCR PDF konverzi je potřeba nainstalovat PyMuPDF a Pillow."
            )
        if pytesseract is None or not self.tesseract_path:
            raise ImportError(
                "Pro OCR PDF konverzi je potřeba nainstalovat Tesseract a zadat jeho cestu. "
                "Použijte tlačítko 'Zadat cestu k Tesseract'."
            )
        if self.tessdata_dir is None:
            raise ImportError(
                "Tesseract našel binární soubor, ale nenašel adresář tessdata. "
                "Zkontrolujte instalaci Tesseractu a nastavte správnou cestu."
            )
        lang = self.ocr_lang_var.get()
        trained_file = pathlib.Path(self.tessdata_dir) / f"{lang}.traineddata"
        if not trained_file.is_file():
            raise ImportError(
                f"Nebylo nalezeno {trained_file}. "
                f"Nainstalujte model {lang}.traineddata nebo přepněte OCR jazyk."
            )
 
        doc = fitz.open(file_path)
        out_doc = fitz.open()
        matrix = fitz.Matrix(300 / 72, 300 / 72)
 
        for page in doc:
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            image_bytes = pix.tobytes("png")
            image = Image.open(io.BytesIO(image_bytes))
            if image.mode != "RGB":
                image = image.convert("RGB")
            config = self._get_tesseract_config()
            lang = self.ocr_lang_var.get()
            trained_file = pathlib.Path(self.tessdata_dir) / f"{lang}.traineddata"
            if not trained_file.is_file():
                raise ImportError(
                    f"Nebylo nalezeno {trained_file}. "
                    "Nainstalujte jazykový model nebo přepněte OCR jazyk."
                )
            pdf_bytes = pytesseract.image_to_pdf_or_hocr(
                image,
                extension="pdf",
                lang=lang,
                config=config,
            )
            page_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            out_doc.insert_pdf(page_doc)
            page_doc.close()
 
        doc.close()
        return out_doc
 
    def _save_extracted_images(self, output_file, markdown_text, result):
        if result is None or not getattr(result, "images", None):
            return markdown_text
 
        images = result.images
        if not images:
            return markdown_text
 
        # Debug: identify image structure
        if images and len(images) > 0:
            import json
            sample = images[0]
            print(f"DEBUG: First image type: {type(sample)}")
            if isinstance(sample, dict):
                print(f"DEBUG: First image keys: {list(sample.keys())}")
            else:
                print(f"DEBUG: First image repr: {repr(sample)[:200]}")
        
        image_folder = output_file.parent / output_file.stem
        image_folder.mkdir(parents=True, exist_ok=True)
        saved_names = set()
 
        for idx, image in enumerate(images):
            if not isinstance(image, dict):
                # Try to handle different image formats
                print(f"DEBUG: Image {idx} is not dict: {type(image)}")
                continue
            fmt = image.get("format", "png")
            image_idx = image.get("image_index", idx)
            file_name = f"image_{image_idx}.{fmt}"
            file_path = image_folder / file_name
            data = image.get("data") or b""
            if data:
                file_path.write_bytes(data)
                saved_names.add(file_name)
 
        def replace_link(match):
            alt_text = match.group(1)
            url = match.group(2).strip()
            base = pathlib.Path(url).name
            if base in saved_names:
                return f"![{alt_text}]({output_file.stem}/{base})"
            return match.group(0)
 
        return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replace_link, markdown_text)
 
    def _post_conversion(self, md_text, result, error):
        self.is_converting = False
        self.convert_btn.config(state=tk.NORMAL)
 
        if error:
            self.status_label.config(text="Chyba při konverzi!", fg="#F44336")
            msg = str(error)
            if "Always OCR is True but no OCR function available" in msg:
                msg = (
                    "OCR není dostupný. Nainstalujte Tesseract a pytesseract "
                    "nebo RapidOCR/PaddleOCR, a opakujte konverzi."
                )
            messagebox.showerror("Chyba", f"Došlo k chybě:\n\n{msg}")
            return
 
        if not md_text or not md_text.strip():
            self.status_label.config(
                text="Nebylo extrahováno žádné textové obsah.", fg="#F44336"
            )
            messagebox.showwarning(
                "Prázdný výsledek",
                "Z PDF se nepodařilo extrahovat text. "
                "Pokud je dokument skenovaný, je potřeba nainstalovat OCR "
                "(Tesseract + pytesseract) nebo použít PDF s textovou vrstvou.",
            )
            return
 
        mode = self.mode_var.get()
        pdf_path = pathlib.Path(self.selected_file)
 
        if mode == "ocr_pdf":
            default_name = pdf_path.with_name(pdf_path.stem + "_ocr.pdf")
            output_path = filedialog.asksaveasfilename(
                parent=self.root,
                title="Uložit OCR PDF",
                defaultextension=".pdf",
                filetypes=[("PDF soubory", "*.pdf"), ("All files", "*.*")],
                initialdir=str(pdf_path.parent),
                initialfile=default_name.name,
            )
            if not output_path:
                self.status_label.config(text="Konverze zrušena", fg="#F44336")
                return
            output_file = pathlib.Path(output_path)
            result.save(str(output_file))
            result.close()
            self.status_label.config(
                text=f"✓ Úspěšně uloženo: {output_file.name}",
                fg="#4CAF50"
            )
            messagebox.showinfo(
                "Úspěch",
                f"Soubor byl úspěšně převeden a uložen:\n\n{output_file}"
            )
            return
 
        default_name = pdf_path.with_suffix(".md")
        output_path = filedialog.asksaveasfilename(
            parent=self.root,
            title="Uložit Markdown",
            defaultextension=".md",
            filetypes=[("Markdown soubory", "*.md"), ("All files", "*.*")],
            initialdir=str(pdf_path.parent),
            initialfile=default_name.name,
        )
        if not output_path:
            self.status_label.config(text="Konverze zrušena", fg="#F44336")
            return
        output_file = pathlib.Path(output_path)
        md_text = self._save_extracted_images(output_file, md_text, result)
        output_file.write_text(md_text, encoding="utf-8")
        self.status_label.config(
            text=f"✓ Úspěšně uloženo: {output_file.name}",
            fg="#4CAF50"
        )
        messagebox.showinfo(
            "Úspěch",
            f"Soubor byl úspěšně převeden a uložen:\n\n{output_file}"
        )
 
 
if __name__ == "__main__":
    root = tk.Tk()
    app = PDFToMarkdownApp(root)
    root.mainloop()