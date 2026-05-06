import asyncio
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import pathlib
import os
import shutil
import io

# --- Optional dependencies ---
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


# Workaround for ONNXRuntime requiring int64 inputs when the model produces int32.
if onnxruntime is not None:
    original_run = onnxruntime.InferenceSession.run

    def patched_run(self, output_names, input_feed, run_options=None):
        input_feed = {
            k: v.astype("int64")
            if hasattr(v, "dtype") and v.dtype == "int32"
            else v
            for k, v in input_feed.items()
        }
        return original_run(self, output_names, input_feed, run_options)

    onnxruntime.InferenceSession.run = patched_run


class PDFToMarkdownApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF to Markdown Converter")
        # UI layout retained from the post-UI tuned version.
        self.root.geometry("600x650")
        self.root.minsize(550, 600)

        self.selected_file = None
        self.is_converting = False
        self.btn_font = ("Calibri", 11, "bold")

        # --- Runtime capability detection ---
        self.kreuzberg_installed = extract_file is not None
        self.pymupdf_installed = pymupdf4llm is not None

        # --- Tesseract discovery (enhanced logic preserved) ---
        self.tesseract_path = self._find_tesseract_cmd()
        self.tessdata_dir = self._find_tessdata_dir(self.tesseract_path)
        self._update_tesseract_environment()

        self.ocr_installed = pytesseract is not None and self.tesseract_path is not None
        self.ocr_supported = self._check_ocr_support()
        self.ocr_pdf_available = fitz is not None and Image is not None and self.ocr_installed

        self.ocr_enabled_var = tk.BooleanVar(value=self.ocr_installed and self.ocr_supported)
        self.ocr_lang_var = tk.StringVar(value="ces")
        self.ocr_lang_var.trace_add("write", lambda *args: self._refresh_tesseract_info())

        self.mode_var = tk.StringVar(value="markdown")
        self.engine_var = tk.StringVar(
            value=(
                "kreuzberg"
                if self.kreuzberg_installed
                else ("pymupdf" if self.pymupdf_installed else "kreuzberg")
            )
        )

        # --- UI ---
        main_container = tk.Frame(root, padx=30, pady=10)
        main_container.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            main_container,
            text="PDF to Markdown Converter",
            font=("Calibri", 18, "bold"),
        ).pack(pady=(0, 20))

        # --- SECTION 1: FILE SELECTION ---
        file_frame = tk.Frame(main_container, pady=10)
        file_frame.pack(fill=tk.X)
        tk.Label(
            file_frame,
            text="1. VÝBĚR SOUBORU",
            font=("Calibri", 10, "bold"),
            fg="#333333",
        ).pack(anchor="w")

        self.select_btn = tk.Button(
            file_frame,
            text="VYBRAT PDF SOUBOR",
            command=self.select_file,
            height=2,
            bg="#4CAF50",
            fg="white",
            font=self.btn_font,
            relief="flat",
        )
        self.select_btn.pack(fill=tk.X, pady=5)

        self.file_label = tk.Label(
            file_frame,
            text="Žádný soubor vybrán",
            wraplength=500,
            fg="#666666",
            font=("Calibri", 9),
        )
        self.file_label.pack(pady=5, anchor="w")

        # --- SECTION 2: SETTINGS ---
        settings_frame = tk.Frame(main_container, pady=10)
        settings_frame.pack(fill=tk.X)
        tk.Label(
            settings_frame,
            text="2. REŽIM A ENGINE",
            font=("Calibri", 10, "bold"),
            fg="#333333",
        ).pack(anchor="w")

        mode_sub = tk.Frame(settings_frame)
        mode_sub.pack(fill=tk.X, pady=5)
        tk.Label(mode_sub, text="Výstup:", font=("Calibri", 10, "bold")).pack(
            side=tk.LEFT, padx=(0, 10)
        )
        tk.Radiobutton(
            mode_sub,
            text="Markdown",
            variable=self.mode_var,
            value="markdown",
            command=self._update_ui_state,
            font=("Calibri", 10),
        ).pack(side=tk.LEFT)
        tk.Radiobutton(
            mode_sub,
            text="OCR PDF",
            variable=self.mode_var,
            value="ocr_pdf",
            command=self._update_ui_state,
            font=("Calibri", 10),
        ).pack(side=tk.LEFT, padx=(10, 0))

        engine_sub = tk.Frame(settings_frame)
        engine_sub.pack(fill=tk.X, pady=5)
        tk.Label(engine_sub, text="Engine:", font=("Calibri", 10, "bold")).pack(
            side=tk.LEFT, padx=(0, 10)
        )
        kr_radio = tk.Radiobutton(
            engine_sub,
            text="Kreuzberg",
            variable=self.engine_var,
            value="kreuzberg",
            command=self._update_ui_state,
            font=("Calibri", 10),
        )
        py_radio = tk.Radiobutton(
            engine_sub,
            text="PyMuPDF",
            variable=self.engine_var,
            value="pymupdf",
            command=self._update_ui_state,
            font=("Calibri", 10),
        )
        kr_radio.pack(side=tk.LEFT)
        py_radio.pack(side=tk.LEFT, padx=(10, 0))
        self.engine_radios = [kr_radio, py_radio]

        self.ocr_check = tk.Checkbutton(
            settings_frame,
            text="Aktivovat OCR vrstvu",
            variable=self.ocr_enabled_var,
            font=("Calibri", 10),
        )
        self.ocr_check.pack(anchor="w", pady=5)

        # --- SECTION 3: ACTION ---
        action_frame = tk.Frame(main_container, pady=20)
        action_frame.pack(fill=tk.X)
        self.convert_btn = tk.Button(
            action_frame,
            text="SPUSTIT PŘEVOD",
            command=self.convert_file,
            height=2,
            bg="#2196F3",
            fg="white",
            font=self.btn_font,
            relief="flat",
            state=tk.DISABLED,
        )
        self.convert_btn.pack(fill=tk.X)

        self.status_label = tk.Label(
            action_frame,
            text="",
            wraplength=500,
            font=("Calibri", 10, "italic"),
        )
        self.status_label.pack(pady=10)

        # --- STATUS BAR ---
        status_bar = tk.Frame(root, bd=1, relief=tk.SUNKEN, bg="#f0f0f0")
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.tesseract_info_label = tk.Label(
            status_bar,
            text=self._build_tesseract_info_text(),
            justify=tk.LEFT,
            font=("Consolas", 8),
            bg="#f0f0f0",
            anchor="w",
        )
        self.tesseract_info_label.pack(side=tk.LEFT, padx=10, pady=5)

        self.path_btn = tk.Button(
            status_bar,
            text="ZMĚNIT CESTU",
            command=self.ask_tesseract_path,
            bg="#9E9E9E",
            fg="white",
            font=("Calibri", 8, "bold"),
            relief="flat",
            padx=8,
        )
        self.path_btn.pack(side=tk.LEFT, padx=10)

        lang_frame = tk.Frame(status_bar, bg="#f0f0f0")
        lang_frame.pack(side=tk.RIGHT, padx=10)
        tk.Label(
            lang_frame,
            text="Jazyk:",
            font=("Calibri", 8, "bold"),
            bg="#f0f0f0",
        ).pack(side=tk.LEFT)
        lang_menu = tk.OptionMenu(lang_frame, self.ocr_lang_var, "ces", "eng", "deu", "spa")
        lang_menu.config(font=("Calibri", 8), width=5, relief="flat")
        lang_menu.pack(side=tk.LEFT, padx=5)

        self._update_ui_state(initial=True)

    # -------------------- TESSERACT / OCR --------------------
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
        candidates.extend(
            [
                r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
                r"C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe",
                r"C:\\Users\\%USERNAME%\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract.exe",
            ]
        )
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
            (base / "../tessdata"),
        ]
        for candidate in candidates:
            try:
                candidate = candidate.resolve()
            except Exception:
                pass
            if candidate.is_dir():
                return str(candidate)
        # More flexible search: any nested */tessdata under base
        try:
            for cand in base.glob("**/tessdata"):
                if cand.is_dir():
                    return str(cand)
        except Exception:
            pass
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
            # pytesseract expects string config
            return f"--tessdata-dir {self.tessdata_dir}"
        return ""

    def _build_tesseract_info_text(self):
        path_text = self.tesseract_path or "Tesseract nenalezen"
        tessdata_text = self.tessdata_dir or "tessdata nenalezen"
        return f"Tesseract: {path_text}\nTessdata: {tessdata_text}\nJazyk: {self.ocr_lang_var.get()}"

    def _refresh_tesseract_info(self):
        if hasattr(self, "tesseract_info_label"):
            self.tesseract_info_label.config(text=self._build_tesseract_info_text())

    def ask_tesseract_path(self):
        if pytesseract is None:
            messagebox.showerror("Chyba", "Knihovna pytesseract není nainstalovaná.")
            return
        path = filedialog.askopenfilename(
            title="Vyberte tesseract.exe",
            filetypes=[("Executable", "*.exe"), ("All", "*.*")],
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
        if not (pytesseract is not None and self.tesseract_path):
            # OCR layer depends on Tesseract
            return False
        try:
            fn = select_ocr_function()
            return callable(fn)
        except Exception:
            return False

    # -------------------- UI HELPERS --------------------
    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Vyberte PDF soubor", filetypes=[("PDF files", "*.pdf")]
        )
        if file_path:
            self.selected_file = file_path
            display = file_path if len(file_path) <= 60 else "..." + file_path[-57:]
            self.file_label.config(text=f"VYBRÁNO: {display}")
            self._update_ui_state()

    def _update_ui_state(self, initial=False):
        mode = self.mode_var.get()
        self.convert_btn.config(
            text="SPUSTIT OCR PDF" if mode == "ocr_pdf" else "PŘEVÉST NA MARKDOWN"
        )

        state = tk.NORMAL if self.selected_file else tk.DISABLED

        if mode == "ocr_pdf":
            for r in self.engine_radios:
                r.config(state=tk.DISABLED)
            self.ocr_check.config(state=tk.DISABLED)
            if not self.ocr_pdf_available:
                state = tk.DISABLED
        else:
            for r in self.engine_radios:
                r.config(state=tk.NORMAL)
            self.ocr_check.config(state=tk.NORMAL)

        self.convert_btn.config(state=state)
        self._refresh_tesseract_info()

    # -------------------- CONVERSION FLOW --------------------
    def convert_file(self):
        # Ask for output path BEFORE conversion so we can derive image folder reliably.
        ext = ".pdf" if self.mode_var.get() == "ocr_pdf" else ".md"
        save_path = filedialog.asksaveasfilename(
            defaultextension=ext, filetypes=[("Cílový soubor", f"*{ext}")]
        )
        if not save_path:
            return

        self.is_converting = True
        self.convert_btn.config(state=tk.DISABLED)
        if ext == ".md":
            self.status_label.config(
                text="Zpracovávám dokument a extrahuji obrázky...", fg="#FF9800"
            )
        else:
            self.status_label.config(text="Vytvářím OCR PDF...", fg="#FF9800")

        threading.Thread(
            target=self._convert_file_thread, args=(save_path,), daemon=True
        ).start()

    def _convert_file_thread(self, save_path):
        try:
            mode = self.mode_var.get()
            save_dir = os.path.dirname(save_path)

            # Unified images folder name under the output directory.
            img_rel_path = "images"
            img_full_path = os.path.join(save_dir, img_rel_path)
            os.makedirs(img_full_path, exist_ok=True)

            if mode == "ocr_pdf":
                res = self._extract_searchable_pdf_with_ocr(self.selected_file)
                res.save(save_path)
                self.root.after(
                    0, lambda: messagebox.showinfo("Hotovo", "OCR PDF bylo vytvořeno.")
                )
                return

            # Markdown mode
            if self.engine_var.get() == "kreuzberg":
                res = asyncio.run(self._extract_kreuzberg(self.selected_file))
                md_text = res.content
                # Save any embedded images (if provided by Kreuzberg) into /images
                md_text = self._save_kreuzberg_images(
                    pathlib.Path(save_path), md_text, res, img_rel_path, img_full_path
                )
                pathlib.Path(save_path).write_text(md_text, encoding="utf-8")
                self.root.after(
                    0,
                    lambda: messagebox.showinfo(
                        "Hotovo",
                        "Markdown byl uložen (Kreuzberg).",
                    ),
                )
            else:
                # PyMuPDF engine: keep image extraction + improved markdown formatting.
                md_text = self._extract_markdown_with_pymupdf(
                    self.selected_file,
                    img_rel_path=img_rel_path,
                    img_full_path=img_full_path,
                )
                pathlib.Path(save_path).write_text(md_text, encoding="utf-8")
                self.root.after(
                    0,
                    lambda: messagebox.showinfo(
                        "Hotovo",
                        f"Markdown a obrázky (ve složce /{img_rel_path}) byly uloženy.",
                    ),
                )

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Chyba", str(e)))
        finally:
            self.root.after(0, self._cleanup_after_conversion)

    def _cleanup_after_conversion(self):
        self.is_converting = False
        self.status_label.config(text="")
        self._update_ui_state()

    # -------------------- ENGINES --------------------
    async def _extract_kreuzberg(self, path):
        if not (extract_file and ExtractionConfig):
            raise RuntimeError("Kreuzberg není nainstalovaný nebo není dostupný.")

        config_kwargs = {
            "output_format": OutputFormat.MARKDOWN if OutputFormat else "markdown",
            # Better formatting / structure (preserved).
            "include_document_structure": True,
            # Enable image extraction if available in this Kreuzberg version.
            "images": ImageExtractionConfig() if ImageExtractionConfig else True,
        }

        if self.ocr_enabled_var.get():
            config_kwargs["force_ocr"] = True
            config_kwargs["ocr"] = OcrConfig(
                backend="tesseract", language=self.ocr_lang_var.get()
            )

        return await extract_file(path, config=ExtractionConfig(**config_kwargs))

    def _extract_markdown_with_pymupdf(self, path, img_rel_path, img_full_path):
        if pymupdf4llm is None:
            raise RuntimeError("PyMuPDF/pymupdf4llm není nainstalovaný.")

        params = {
            "use_ocr": self.ocr_enabled_var.get(),
            # Better formatting: page separators.
            "page_separators": True,
            # Keep image extraction to subfolder.
            "write_images": True,
            "image_path": img_rel_path,  # relative path inside MD
            "image_folder": img_full_path,  # physical folder on disk
        }
        if self.ocr_enabled_var.get():
            params["ocr_language"] = self.ocr_lang_var.get()

        return pymupdf4llm.to_markdown(path, **params)

    def _extract_searchable_pdf_with_ocr(self, path):
        if fitz is None or Image is None or pytesseract is None:
            raise RuntimeError("OCR PDF není dostupné (chybí závislosti).")

        doc = fitz.open(path)
        out = fitz.open()
        try:
            for page in doc:
                pix = page.get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72))
                pdf_b = pytesseract.image_to_pdf_or_hocr(
                    Image.open(io.BytesIO(pix.tobytes())),
                    lang=self.ocr_lang_var.get(),
                    config=self._get_tesseract_config(),
                )
                out.insert_pdf(fitz.open(stream=pdf_b, filetype="pdf"))
        finally:
            doc.close()
        return out

    # -------------------- IMAGE SAVING (KREUZBERG) --------------------
    def _save_kreuzberg_images(self, output_file: pathlib.Path, markdown_text: str, result, img_rel_path: str, img_full_path: str):
        """Persist images provided by Kreuzberg result (if any) into /images.

        NOTE: Kreuzberg result markdown may already contain image references.
        This function focuses on preserving the previous capability of exporting
        image binaries to a subfolder.
        """
        images = getattr(result, "images", None)
        if not images:
            return markdown_text

        os.makedirs(img_full_path, exist_ok=True)

        for idx, img in enumerate(images):
            data = None
            ext = "png"
            name = None

            if isinstance(img, dict):
                data = img.get("data")
                name = img.get("name") or img.get("filename")
                # naive extension detection
                if name and "." in name:
                    ext = name.rsplit(".", 1)[-1].lower() or ext
            else:
                # unknown type - best effort
                data = getattr(img, "data", None)
                name = getattr(img, "name", None) or getattr(img, "filename", None)
                if name and "." in name:
                    ext = name.rsplit(".", 1)[-1].lower() or ext

            if not data:
                continue

            safe_name = name
            if safe_name:
                # keep only basename, avoid path traversal
                safe_name = os.path.basename(str(safe_name))
            else:
                safe_name = f"kb_image_{idx}.{ext}"

            out_path = os.path.join(img_full_path, safe_name)
            with open(out_path, "wb") as f:
                f.write(data)

        return markdown_text


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFToMarkdownApp(root)
    root.mainloop()
