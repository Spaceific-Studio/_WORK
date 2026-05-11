import asyncio
import threading
import re
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import pathlib
import os
import shutil
import io
from unittest import result

from kreuzberg import HierarchyConfig
 
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
    from kreuzberg import extract_file, extract_bytes, HierarchyConfig, ExtractionConfig, PageConfig, ImageExtractionConfig, PdfConfig, OcrConfig, LayoutDetectionConfig, TesseractConfig, OutputFormat
except ImportError:
    extract_file = None
    extract_bytes = None
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
        self.root.geometry("700x720")
        self.root.minsize(520, 680)
        self.root.resizable(False, True)
       
        self.selected_file = None
        self.is_converting = False
        self.btn_font = ("Calibri", 11, "bold")
        
        # Inicializace stavu systému
        self.kreuzberg_installed = extract_file is not None
        self.pymupdf_installed = pymupdf4llm is not None
        self.tesseract_path = self._find_tesseract_cmd()
        self.tessdata_dir = self._find_tessdata_dir(self.tesseract_path)
        self._update_tesseract_environment()
        self.ocr_installed = pytesseract is not None and self.tesseract_path is not None
        self.ocr_supported = self._check_ocr_support()
        self.ocr_pdf_available = (fitz is not None and Image is not None and self.ocr_installed)
        
        self.ocr_enabled_var = tk.BooleanVar(value=None)
        self.ocr_lang_var = tk.StringVar(value="ces")
        self.ocr_lang_var.trace_add("write", lambda *args: self._refresh_tesseract_info())
        self.mode_var = tk.StringVar(value="markdown")
        self.engine_var = tk.StringVar(
            value="kreuzberg" if self.kreuzberg_installed else ("pymupdf" if self.pymupdf_installed else "kreuzberg")
        )
       
# Hlavní kontejner
        main_container = tk.Frame(root, padx=30, pady=10)
        main_container.pack(fill=tk.BOTH, expand=True)

        tk.Label(main_container, text="PDF to Markdown Converter", font=("Calibri", 18, "bold")).pack(pady=(0, 20))

        # --- SEKCE 1: VÝBĚR SOUBORU ---
        file_frame = tk.Frame(main_container, pady=10)
        file_frame.pack(fill=tk.X)
        tk.Label(file_frame, text="1. VÝBĚR SOUBORU", font=("Calibri", 10, "bold"), fg="#333333").pack(anchor="w")
       
        self.select_btn = tk.Button(file_frame, text="VYBRAT PDF SOUBOR", command=self.select_file,
                                   height=2, bg="#4CAF50", fg="white", 
                                   font=self.btn_font, relief="flat")
        self.select_btn.pack(fill=tk.X, pady=5)
 
        self.file_label = tk.Label(file_frame, text="Žádný soubor vybrán", wraplength=500, fg="#666666", font=("Calibri", 9))
        self.file_label.pack(pady=5, anchor="w")

        # --- SEKCE 2: NASTAVENÍ ---
        settings_frame = tk.Frame(main_container, pady=10)
        settings_frame.pack(fill=tk.X)
        tk.Label(settings_frame, text="2. REŽIM A ENGINE", font=("Calibri", 10, "bold"), fg="#333333").pack(anchor="w")
 
        mode_sub = tk.Frame(settings_frame)
        mode_sub.pack(fill=tk.X, pady=5)
        tk.Label(mode_sub, text="Výstup:", font=("Calibri", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        tk.Radiobutton(mode_sub, text="Markdown", variable=self.mode_var, value="markdown", command=self._update_ui_state, font=("Calibri", 10)).pack(side=tk.LEFT)
        tk.Radiobutton(mode_sub, text="OCR PDF", variable=self.mode_var, value="ocr_pdf", command=self._update_ui_state, font=("Calibri", 10)).pack(side=tk.LEFT, padx=(10, 0))
 
        engine_sub = tk.Frame(settings_frame)
        engine_sub.pack(fill=tk.X, pady=5)
        tk.Label(engine_sub, text="Engine:", font=("Calibri", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        kr_radio = tk.Radiobutton(engine_sub, text="Kreuzberg", variable=self.engine_var, value="kreuzberg", command=self._update_ui_state, font=("Calibri", 10))
        py_radio = tk.Radiobutton(engine_sub, text="PyMuPDF", variable=self.engine_var, value="pymupdf", command=self._update_ui_state, font=("Calibri", 10))
        kr_radio.pack(side=tk.LEFT)
        py_radio.pack(side=tk.LEFT, padx=(10, 0))
        self.engine_radios = [kr_radio, py_radio]

        self.ocr_check = tk.Checkbutton(settings_frame, text="Aktivovat OCR vrstvu", variable=self.ocr_enabled_var, font=("Calibri", 10))
        self.ocr_check.pack(anchor="w", pady=5)

 
        # --- SEKCE 3: AKCE ---
        action_frame = tk.Frame(main_container, pady=20)
        action_frame.pack(fill=tk.X)
       
        self.convert_btn = tk.Button(action_frame, text="SPUSTIT PŘEVOD",
                               command=self.convert_file, height=2, bg="#2196F3",
                               fg="white", font=self.btn_font, relief="flat", state=tk.DISABLED)
        self.convert_btn.pack(fill=tk.X)
       
        self.status_label = tk.Label(action_frame, text="", wraplength=500, font=("Calibri", 10, "italic"))
        self.status_label.pack(pady=10)
 
        # --- STAVOVÝ ŘÁDEK ---
        status_bar = tk.Frame(root, bd=1, relief=tk.SUNKEN, bg="#f0f0f0")
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
 
        self.tesseract_info_label = tk.Label(status_bar, text=self._build_tesseract_info_text(),
                                           justify=tk.LEFT, font=("Consolas", 8), bg="#f0f0f0", anchor="w")
        self.tesseract_info_label.pack(side=tk.LEFT, padx=10, pady=5)
 
        self.path_btn = tk.Button(status_bar, text="ZMĚNIT CESTU", command=self.ask_tesseract_path,
                                 bg="#9E9E9E", fg="white", font=("Calibri", 8, "bold"), 
                                 relief="flat", padx=8)
        self.path_btn.pack(side=tk.LEFT, padx=10)

        lang_frame = tk.Frame(status_bar, bg="#f0f0f0")
        lang_frame.pack(side=tk.RIGHT, padx=10)
        tk.Label(lang_frame, text="Jazyk:", font=("Calibri", 8, "bold"), bg="#f0f0f0").pack(side=tk.LEFT)
        lang_menu = tk.OptionMenu(lang_frame, self.ocr_lang_var, "ces", "eng", "deu", "spa")
        lang_menu.config(font=("Calibri", 8), width=5, relief="flat") 
        lang_menu.pack(side=tk.LEFT, padx=5)
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
        # Zeptáme se na cestu uložení dříve, abychom mohli nastavit cestu pro obrázky[cite: 5]
        #ext = ".pdf" if self.mode_var.get() == "ocr_pdf" else ".md"
        #save_path = filedialog.asksaveasfilename(defaultextension=ext, filetypes=[("Cílový soubor", f"*{ext}")])
        save_path = pathlib.Path(self.selected_file)
        #if not save_path:
        #    return

        self.is_converting = True
        self.convert_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Zpracovávám dokument a extrahuji obrázky...", fg="#FF9800")
        
        threading.Thread(target=self._convert_file_thread, args=(save_path,), daemon=True).start()

    def _save_extracted_images(self, output_file, result):
        #if result and getattr(result, "images", None):
        img_dir = output_file.parent / output_file.stem
        img_dir.mkdir(exist_ok=True) 
        for idx, img in enumerate(result.images):
            if isinstance(img, dict) and img.get("data"):
                (img_dir / f"image_{idx}.png").write_bytes(img["data"])

    """   
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
    """
    def _convert_file_thread(self, save_path):
        try:
            mode = self.mode_var.get()
            save_dir = os.path.dirname(save_path)
            # Definujeme složku pro obrázky relativně k MD souboru[cite: 5]

            path = pathlib.Path(self.selected_file)
            ext = ".pdf" if self.mode_var.get() == "ocr_pdf" else ".md"
            out = filedialog.asksaveasfilename(defaultextension=ext, initialfile=path.stem + ("_ocr" if self.mode_var.get() == "ocr_pdf" else "") + ext)
            out_path = pathlib.Path(out)
            img_rel_path = "images"
            img_full_path = (out_path.parent / img_rel_path).resolve()
            img_full_path.mkdir(parents=True, exist_ok=True)
            
            if mode == "ocr_pdf":
                res = self._extract_searchable_pdf_with_ocr(self.selected_file)
                res.save(out)
                self.root.after(0, lambda: messagebox.showinfo("Hotovo", "OCR PDF bylo vytvořeno."))
            elif self.engine_var.get() == "kreuzberg":
                # Kreuzberg primárně vrací text, obrázky v MD odkazuje, ale fyzicky je neukládá tak přímo jako PyMuPDF
                res = asyncio.run(self._extract_kreuzberg(self.selected_file))
                content = (res.content or "").encode("utf-8")         
                pathlib.Path(out).write_bytes(content)
                if out:
                    if ext == ".pdf": res.save(out)
                    else:
                        self._save_extracted_images(pathlib.Path(out), res)
                        #pathlib.Path(out).write_text(md_text, encoding="utf-8")
                        #messagebox.showinfo("Hotovo", f"Uloženo do: {out}")
                self.root.after(0, self._save_extracted_images, img_full_path, res)
                self.root.after(0, lambda: messagebox.showinfo("Hotovo", "Markdown byl uložen (Kreuzberg)."))
            else:
                # PyMuPDF engine – engine vytvoří složku "images" v CWD běžícího programu.
                # Po konverzi ji postprocessingem přesuneme vedle výstupního .md souboru.
                cwd_images_src = pathlib.Path(os.getcwd()) / "images"
                target_images_dir = out_path.parent / "images"

                params = {
                    "show_progress": False,
                    "use_ocr": self.ocr_enabled_var.get() and self.ocr_supported,
                    "force_ocr": self.ocr_enabled_var.get() and self.ocr_supported,
                    "write_images": True,       # povolení zápisu obrázků
                    "image_path": "images",     # relativní odkaz na obrázky v MD souboru
                    "page_separators": True,
                }
                if self.ocr_enabled_var.get():
                    params["ocr_language"] = self.ocr_lang_var.get()

                txt = pymupdf4llm.to_markdown(self.selected_file, **params)

                # --- Postprocessing: přesun vygenerovaných obrázků ---
                # Engine uloží obrázky do CWD/images; přesuneme je vedle výstupního .md.
                if cwd_images_src.exists() and cwd_images_src.is_dir():
                    if target_images_dir.exists():
                        shutil.rmtree(target_images_dir)
                    shutil.move(str(cwd_images_src), str(target_images_dir))

                self.root.after(0, self._post_conversion, txt, out, None)
        
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: messagebox.showerror("Chyba", error_msg))
        finally:
            self.root.after(0, self._cleanup_after_conversion)

    def _post_conversion(self, md_text, output_file, error):
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

        result = messagebox.askyesnocancel(
            "Uložit soubor",
            f"Chcete uložit soubor pod stejným názvem?\n\n"
            f"YES = Stejný název\n"
            f"NO = Přejmenovat soubor\n"
            f"CANCEL = Zrušit"
        )

        if result is None:
            self.status_label.config(text="Konverze zrušena", fg="#F44336")
            return

        #pdf_path = pathlib.Path(self.selected_file)
        """
        if result:
            out = output_file.with_suffix(".md")
        else:
            initial_name = out.stem + ".md"
            new_name = simpledialog.askstring(
                "Nový název",
                "Zadejte nový název souboru (bez cesty):",
                initialvalue=initial_name
            )
            if not new_name:
                self.status_label.config(text="Konverze zrušena", fg="#F44336")
                return
            if not new_name.endswith(".md"):
                new_name += ".md"
            output_file = out.parent / new_name
        """
        pathlib.Path(output_file).write_text(md_text, encoding="utf-8")
        self.status_label.config(
            text=f"✓ Úspěšně uloženo: {output_file}",
            fg="#4CAF50"
        )
        
        messagebox.showinfo(
            "Úspěch",
            f"Soubor byl úspěšně převeden a uložen:\n\n{output_file}"
        )

    def _cleanup_after_conversion(self):
        self.is_converting = False
        self.status_label.config(text="")
        self._update_ui_state()
 
    async def _extract_kreuzberg(self, file):
        cfg = ExtractionConfig(output_format=OutputFormat.MARKDOWN, \
                                pdf_options=PdfConfig( \
                                                        extract_images=True, \
                                                        hierarchy = HierarchyConfig(ocr_coverage_threshold=0.5, \
                                                            include_bbox=True) \
                                                        ), \
                                force_ocr=self.ocr_enabled_var.get(), \
                                include_document_structure=True, \
                                images = ImageExtractionConfig( \
                                                                extract_images = True \
                                                                ), \
                                ocr=OcrConfig( \
                                                backend="tesseract", \
                                                language=self.ocr_lang_var.get(), \
                                                tesseract_config=TesseractConfig( \
                                                                                psm=3, \
                                                                                enable_table_detection=False \
                                                                                ) \
                                                ), \
                                pages = PageConfig(insert_page_markers=True) \
                                ) \
                                
                                
        return await extract_file(file, config=cfg)
 
    def _extract_searchable_pdf_with_ocr(self, path):
        doc = fitz.open(path)
        out = fitz.open()
        for page in doc:
            pix = page.get_pixmap(dpi=300)
            pdf_b = pytesseract.image_to_pdf_or_hocr(Image.open(io.BytesIO(pix.tobytes())), lang=self.ocr_lang_var.get())
            out.insert_pdf(fitz.open(stream=pdf_b, filetype="pdf"))
        return out
if __name__ == "__main__":
    root = tk.Tk()
    app = PDFToMarkdownApp(root)
    root.mainloop()