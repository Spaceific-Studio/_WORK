import asyncio
import threading
import re
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import pathlib
import os
import shutil
import io

# --- Imports a Overrides (Zachováno z obou verzí) ---

try:
    import fitz # PyMuPDF
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
    # Workaround pro ONNXRuntime (zachováno z obou verzí)
    original_run = onnxruntime.InferenceSession.run
    def patched_run(self, output_names, input_feed, run_options=None):
        input_feed = {k: v.astype('int64') if hasattr(v, 'dtype') and v.dtype == 'int32' else v for k, v in input_feed.items()}
        return original_run(self, output_names, input_feed, run_options)
    onnxruntime.InferenceSession.run = patched_run


class PDFToMarkdownApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF to Markdown Converter")
        # ZVÝŠENÁ VÝŠKA OKNA (z druhé verze)
        self.root.geometry("520x720")
        self.root.minsize(520, 680)
        self.root.resizable(False, True)

        self.selected_file = None
        self.is_converting = False
        # Inicializace systémových stavů
        self.kreuzberg_installed = extract_file is not None
        self.pymupdf_installed = pymupdf4llm is not None
        
        # Tesseract/OCR setup (z druhé verze - robustnější)
        self.tesseract_path = self._find_tesseract_cmd()
        self.tessdata_dir = self._find_tessdata_dir(self.tesseract_path)
        self._update_tesseract_environment()
        self.ocr_installed = pytesseract is not None and self.tesseract_path is not None
        self.ocr_supported = self._check_ocr_support()
        self.ocr_pdf_available = (
            fitz is not None and Image is not None and self.ocr_installed
        )

        # Kontrolní proměnné UI
        self.ocr_enabled_var = tk.BooleanVar(value=self.ocr_installed and self.ocr_supported)
        self.ocr_lang_var = tk.StringVar(value="ces")
        self.ocr_lang_var.trace_add("write", lambda *args: self._refresh_tesseract_info())
        self.mode_var = tk.StringVar(value="markdown")
        self.engine_var = tk.StringVar(
            value="kreuzberg"
            if self.kreuzberg_installed
            else ("pymupdf" if self.pymupdf_installed else "kreuzberg")
        )

        # Main frame (struktura z druhé verze)
        main_frame = tk.Frame(root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title = tk.Label(main_frame, text="PDF to Markdown Converter",
                        font=("Arial", 16, "bold"))
        title.pack(pady=10)

        # --- Sekce výběru souboru (vylepšené UI z druhé verze) ---
        self.select_btn = tk.Button(main_frame, text="Vybrat PDF soubor",
                                     command=self.select_file,
                                     width=30, height=2, bg="#4CAF50",
                                     fg="white", font=("Arial", 10))
        self.select_btn.pack(pady=10)

        # Knoflík pro ruční zadání cesty (z druhé verze)
        manual_btn = tk.Button(main_frame, text="Zadat cestu k PDF",
                               command=self.enter_file_path,
                               width=30, height=2, bg="#FFC107",
                               fg="white", font=("Arial", 10))
        manual_btn.pack(pady=5)

        # --- Sekce Nastavení Režimu a Engine (z druhé verze) ---
        mode_frame = tk.Frame(main_frame)
        mode_label = tk.Label(mode_frame, text="Výstupní režim:", font=("Arial", 10, "bold"))
        mode_label.pack(side=tk.LEFT, padx=(0, 10))
        markdown_radio = tk.Radiobutton(
            mode_frame, text="Markdown", variable=self.mode_var, value="markdown", command=self._update_ui_state,
            font=("Arial", 10)
        )
        ocr_pdf_radio = tk.Radiobutton(
            mode_frame, text="OCR PDF", variable=self.mode_var, value="ocr_pdf", command=self._update_ui_state,
            font=("Arial", 10)
        )
        markdown_radio.pack(side=tk.LEFT)
        ocr_pdf_radio.pack(side=tk.LEFT, padx=(10, 0))
        mode_frame.pack(pady=5)

        engine_frame = tk.Frame(main_frame)
        engine_label = tk.Label(engine_frame, text="Engine:", font=("Arial", 10, "bold"))
        engine_label.pack(side=tk.LEFT, padx=(0, 10))
        kreuzberg_radio = tk.Radiobutton(
            engine_frame, text="Kreuzberg", variable=self.engine_var, value="kreuzberg", command=self._update_ui_state,
            font=("Arial", 10)
        )
        pymupdf_radio = tk.Radiobutton(
            engine_frame, text="PyMuPDF", variable=self.engine_var, value="pymupdf", command=self._update_ui_state,
            font=("Arial", 10)
        )
        kreuzberg_radio.pack(side=tk.LEFT)
        pymupdf_radio.pack(side=tk.LEFT, padx=(10, 0))
        engine_frame.pack(pady=5)

        # --- Sekce OCR a Tesseract (z druhé verze) ---
        ocr_check = tk.Checkbutton(
            main_frame, text="Použít OCR (pokud dostupné)",
            variable=self.ocr_enabled_var, onvalue=True, offvalue=False,
            font=("Arial", 10)
        )
        self.ocr_check = ocr_check
        # Původní funkčnost: Pokud je mode "ocr_pdf", OCR musí být vždy zapnuté
        self.ocr_check.bind("<<ComboboxSelected>>", self._update_ui_state) 

        self.tesseract_button = tk.Button(
            main_frame, text="Zadat cestu k Tesseract", command=self.ask_tesseract_path,
            width=30, height=1, bg="#9E9E9E", fg="white", font=("Arial", 9)
        )
        self.tesseract_button.pack(pady=2)

        # OCR Jazyk (z druhé verze)
        lang_frame = tk.Frame(main_frame)
        lang_label = tk.Label(lang_frame, text="OCR jazyk:", font=("Arial", 10, "bold"))
        lang_label.pack(side=tk.LEFT, padx=(0, 10))
        # Zde se používá OptionMenu z druhé verze s kompletní sadou jazyků
        self.ocr_lang_menu = tk.OptionMenu(
            lang_frame, self.ocr_lang_var, "ces", "eng", "deu", "spa"
        )
        self.ocr_lang_menu.config(width=10)
        self.ocr_lang_menu.pack(side=tk.LEFT)
        lang_frame.pack(pady=5)

        # Tesseract Info Label
        self.tesseract_info_label = tk.Label(
            main_frame, text=self._build_tesseract_info_text(), wraplength=400, justify=tk.LEFT,
            fg="#555555", font=("Arial", 8)
        )
        self.tesseract_info_label.pack(pady=(2, 8))

        # Selected file label
        self.file_label = tk.Label(main_frame, text="Žádný soubor vybrán", wraplength=400, justify=tk.LEFT,
                                   fg="#666666")
        self.file_label.pack(pady=10)

        # Convert button
        self.convert_btn = tk.Button(main_frame, text="Převést PDF na Markdown",
                               command=self.convert_file, width=30, height=2, bg="#2196F3",
                               fg="white", font=("Arial", 10), state=tk.DISABLED)
        self.convert_btn.pack(pady=10)

        # Status label
        self.status_label = tk.Label(main_frame, text="", wraplength=400, justify=tk.LEFT,
                                    fg="#333333", font=("Arial", 9))
        self.status_label.pack(pady=10)

        self._update_ui_state(initial=True)

    # ==============================================
    #                         OCR/PATH HELPERS
    # ==============================================

    def _find_tesseract_cmd(self):
        """Zkuste najít tesseract.exe z různých cest."""
        candidates = []
        if pytesseract is not None:
            try:
                cmd = pytesseract.pytesseract.tesseract_cmd
                if cmd: candidates.append(cmd)
            except Exception: pass
        candidates.append(shutil.which("tesseract"))
        # Klasické cesty pro Windows (z obou verzí)
        candidates.extend([
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"C:\Users\%USERNAME%\AppData\Local\Programs\Tesseract-OCR\tesseract.exe",
        ])
        for candidate in candidates:
            if not candidate: continue
            candidate = os.path.expandvars(candidate)
            # Zkusíme najít první funkční cestu
            if os.path.isfile(candidate): return candidate
        return None

    def _find_tessdata_dir(self, tesseract_path):
        """Robustní hledání složky tessdata (z druhé verze)."""
        if not tesseract_path: return None
        base = pathlib.Path(tesseract_path).resolve().parent
        # Zkusíme základní struktury
        candidates = [
            base / "tessdata",
            base / "share" / "tessdata",
            base.parent / "tessdata",
            base / "../tessdata",
        ]
        for candidate in candidates:
            candidate_str = str(candidate) # Zabraňme, že se změní os.path při použití glob/resolve
            if pathlib.Path(candidate_str).is_dir(): return str(candidate)
        # Globální hledání (z druhé verze)
        for candidate in base.glob("**/tessdata"):
            if candidate.is_dir():
                return str(candidate)
        return None

    def _update_tesseract_environment(self):
        """Nastaví globalní prostředí buat pyatesseract a os."""
        if pytesseract is None: return
        if self.tesseract_path: pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
        if self.tessdata_dir: os.environ["TESSDATA_PREFIX"] = self.tessdata_dir
        else:
             os.environ.pop("TESSDATA_PREFIX", None)

    def _build_tesseract_info_text(self):
        """Generuje informaci o Tesseractu a tessdata."""
        path_text = self.tesseract_path or "Nenalezen"
        tessdata_text = self.tessdata_dir or "Nenalezen"
        return f"Tesseract: {path_text}\nTessdata: {tessdata_text}\nJazyk: {self.ocr_lang_var.get()}"

    def _refresh_tesseract_info(self):
        if hasattr(self, 'tesseract_info_label'):
            self.tesseract_info_label.config(text=self._build_tesseract_info_text())

    # ==============================================
    #                         UI HANDLERY
    # ==============================================

    def select_file(self):
        """Standardní výběr souboru (zachováno)."""
        file_path = filedialog.askopenfilename(title="Vyberte PDF soubor", filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self._set_selected_file(file_path)

    def enter_file_path(self):
        """Manuální zadání cesty k souboru (zachováno z druhé verze)."""
        file_path = simpledialog.askstring("Zadat cestu", "Zadejte úplnou cestu k PDF:", parent=self.root)
        if file_path:
            clean_path = file_path.strip()
            if os.path.isfile(clean_path):
                self._set_selected_file(clean_path)

    def _set_selected_file(self, file_path):
        """Uaktualní zobrazený soubor."""
        self.selected_file = file_path
        display_path = file_path if len(file_path) <= 50 else "..." + file_path[-47:]
        self.file_label.config(text=f"Vybrán: {display_path}")
        self._update_ui_state()

    def ask_tesseract_path(self):
        """Uživatel ručně zadá cestu k Tesseractovi."""
        if pytesseract is None:
            messagebox.showerror("Chyba", "Knihovna pytesseract není nainstalovaná.")
            return
        # Používáme simpledialog z druhé verze pro lepší UX
        path = simpledialog.askstring(
            "Cesta k Tesseract",
            "Zadejte úplnou cestu k tesseract.exe:",
            initialvalue=self.tesseract_path or "",
            parent=self.root,
        )
        if not path: return
        
        path = os.path.expandvars(path.strip())
        if not os.path.isfile(path):
            messagebox.showerror("Chyba", "Tesseract nebyl nalezen.")
            return

        self.tesseract_path = path
        self.tessdata_dir = self._find_tessdata_dir(path)
        self._update_tesseract_environment()
        self.ocr_installed = True # Předpokládáme, že pokud našli cestu, je OCR funkční
        self.ocr_supported = self._check_ocr_support()
        self.ocr_pdf_available = fitz is not None and Image is not None and self.ocr_installed
        self._update_ui_state(initial=True)


    def _update_ui_state(self, initial=False):
        """Aktualizuje stav tlačítek na základě zvoleného režimu."""
        mode = self.mode_var.get()

        # 1. Text tlačítka a logika OCR mode switchu
        if mode == "ocr_pdf":
            self.convert_btn.config(text="SPUSTIT OCR PDF")
            state = tk.NORMAL if self.selected_file and self.ocr_pdf_available else tk.DISABLED
            # V ocr_pdf režimu jsou engine a OCR check zablokovány (V2 logika)
            for widget in self.engine_radios: widget.config(state=tk.DISABLED)
            self.ocr_check.config(state=tk.DISABLED)
        else:
            self.convert_btn.config(text="PŘEVÉST NA MARKDOWN")
            # V normálním režimu jsou všechny ovládací prvky aktivní
            for widget in self.engine_radios: widget.config(state=tk.NORMAL)
            self.ocr_check.config(state=tk.NORMAL)
            state = tk.NORMAL if self.selected_file else tk.DISABLED

        self.convert_btn.config(state=state)
        self._refresh_tesseract_info()


    # ==============================================
    #                         KONVERZE (CORE LOGIC)
    # ==============================================

    def convert_file(self):
        """Spustí konverzi v samostatném vlákně."""
        if not self.selected_file: return
        
        # Použijeme z druhé verze, aby se minimalizoval rizikový kód při zadávání cesty pro dialogy
        ext = ".pdf" if self.mode_var.get() == "ocr_pdf" else ".md"
        save_path = filedialog.asksaveasfilename(
            defaultextension=f"*{ext}", filetypes=[("Cílový soubor", f"*{ext}")], initialfile="konverz_output")

        if not save_path:
            return

        self.is_converting = True
        self.convert_btn.config(state=tk.DISABLED)
        # Status z druhé verze, lépe popírává
        self.status_label.config(text="Zpracovávám dokument a extrahuji obsah...", fg="#FF9800")

        threading.Thread(target=self._convert_file_thread, args=(save_path,), daemon=True).start()


    def _convert_file_thread(self, save_path):
        """Hlavní logika konverze v vlákně."""
        try:
            mode = self.mode_var.get()
            save_dir = os.path.dirname(save_path)

            # --- ZÁZNAM IMAGE FOLDER (Klíčový k požadované funkci) ---
            img_rel_path = "images" 
            img_full_path = os.path.join(save_dir, img_rel_path)
            
            if mode == "ocr_pdf":
                # OCR PDF režim - V1 logika zachována
                res = self._extract_searchable_pdf_with_ocr(self.selected_file)
                res.save(save_path)
                self.root.after(0, lambda: messagebox.showinfo("Hotovo", "OCR PDF bylo vytvořeno."))
            elif self.engine_var.get() == "kreuzberg":
                # Kreuzberg engine - V1 logika zachována (pouze text/MD)
                res = asyncio.run(self._extract_kreuzberg(self.selected_file))
                pathlib.Path(save_path).write_text(res.content, encoding="utf-8")
                # Poznámka: Kreuzberg v tomto případě nezajímá se o systémové obrázky pro MD
                self.root.after(0, lambda: messagebox.showinfo("Hotovo", "Markdown byl uložen (Kreuzberg)."))
            else: # PyMuPDF engine - Kombinace V1 image saving + V2 UI/state management
                # Zde je implementován krytý mechanismus zachovávající uložení obrázků do složky 'images'
                txt = pymupdf4llm.to_markdown(
                    self.selected_file, 
                    use_ocr=self.ocr_enabled_var.get(),
                    write_images=True,           # Povolení zápisu obrázků (Klíčový bod)
                    image_path=img_rel_path,     # Relativní cesta v MD souboru (Zachováno z V1)
                    image_folder=img_full_path   # Fyzická cílová složka pro obrázky (Zachováno z V1)
                )
                pathlib.Path(save_path).write_text(txt, encoding="utf-8")
                self.root.after(0, lambda: messagebox.showinfo("Hotovo", f"Markdown a obrázky (ve složce /{img_rel_path}) byly uloženy."))

        except Exception as e:
            # Přesměrování chyby na GUI vlákno z druhé verze
            self.root.after(0, lambda: messagebox.showerror("Chyba", f"Došlo k chybě při konverzi: {str(e)}"))
        finally:
            self.root.after(0, self._cleanup_after_conversion)

    def _cleanup_after_conversion(self):
        """Četní stav po dokončení operace."""
        self.is_converting = False
        self.status_label.config(text="")
        self._update_ui_state()


    # --- Specializované Konverzní Metody (Zachováno z V1) ---

    async def _extract_kreuzberg(self, path):
        """Konverze pomocí Kreuzberg API."""
        cfg = ExtractionConfig(output_format=OutputFormat.MARKDOWN, force_ocr=self.ocr_enabled_var.get(),
                               ocr=OcrConfig(backend="tesseract", language=self.ocr_lang_var.get()))
        return await extract_file(path, config=cfg)

    def _extract_searchable_pdf_with_ocr(self, path):
        """Konverze na vyhledávatelný PDF pomocí OCR (zachováno z V1)."""
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
