import asyncio
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import pathlib
import os
import shutil

try:
    import pytesseract
except ImportError:
    pytesseract = None

try:
    import onnxruntime
except ImportError:
    onnxruntime = None

try:
    from kreuzberg import extract_file, ExtractionConfig, OcrConfig, TesseractConfig
except ImportError:
    extract_file = None
    ExtractionConfig = None
    OcrConfig = None
    TesseractConfig = None

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
        self.root.geometry("520x420")
        self.root.minsize(520, 420)
        self.root.resizable(False, True)
        
        self.selected_file = None
        self.is_converting = False
        self.kreuzberg_installed = extract_file is not None
        self.ocr_installed = pytesseract is not None and shutil.which("tesseract") is not None
        self.ocr_enabled_var = tk.BooleanVar(value=self.ocr_installed)
        
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

        ocr_check = tk.Checkbutton(
            main_frame,
            text="Použít OCR (pokud dostupné)",
            variable=self.ocr_enabled_var,
            onvalue=True,
            offvalue=False,
        )
        self.ocr_check = ocr_check
        ocr_check.pack(pady=5)
        
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

        if not self.kreuzberg_installed:
            self.status_label.config(
                text="Knihovna kreuzberg není nainstalovaná. Nainstalujte ji pomocí `pip install kreuzberg`.",
                fg="#FF9800",
            )
            self.convert_btn.config(state=tk.DISABLED)
        elif not self.ocr_installed:
            self.status_label.config(
                text="OCR není nainstalované nebo není dostupné v PATH. Konverze proběhne bez OCR.",
                fg="#FF9800",
            )
        else:
            self.status_label.config(
                text="Kreuzberg je připraveno. OCR je dostupné a lze ho použít.",
                fg="#4CAF50",
            )

    def _check_ocr_support(self):
        return self.ocr_installed

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
        if self.kreuzberg_installed:
            self.convert_btn.config(state=tk.NORMAL)
        self.status_label.config(text="", fg="#333333")

    def convert_file(self):
        """Spustí převod PDF na pozadí, aby GUI nezamrzlo."""
        if not self.selected_file:
            messagebox.showerror("Chyba", "Nejdříve vyberte soubor!")
            return

        if not self.kreuzberg_installed:
            messagebox.showerror(
                "Chyba",
                "Knihovna kreuzberg není nainstalovaná. Nainstalujte ji pomocí `pip install kreuzberg`."
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

        if not self.ocr_installed and self.ocr_enabled_var.get():
            proceed = messagebox.askyesno(
                "OCR není dostupné",
                "OCR není nainstalované nebo není dostupné v PATH. "
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
            md_text = self._extract_markdown_with_kreuzberg(self.selected_file)
            self.root.after(0, self._post_conversion, md_text, None)
        except Exception as e:
            self.root.after(0, self._post_conversion, None, e)

    def _extract_markdown_with_kreuzberg(self, file_path):
        if extract_file is None:
            raise ImportError("Knihovna kreuzberg není nainstalovaná. Nainstalujte ji pomocí `pip install kreuzberg`.")

        config_kwargs = {}
        if self.ocr_enabled_var.get():
            if OcrConfig is None:
                raise RuntimeError("OCR konfigurace není dostupná v knihovně kreuzberg.")
            ocr_kwargs = {
                "backend": "tesseract",
                "language": "ces",
            }
            if TesseractConfig is not None:
                ocr_kwargs["tesseract_config"] = TesseractConfig()
            config_kwargs["force_ocr"] = True
            config_kwargs["ocr"] = OcrConfig(**ocr_kwargs)

        config = ExtractionConfig(**config_kwargs) if ExtractionConfig is not None else None
        result = asyncio.run(extract_file(file_path, config=config))
        return result.content or ""

    def _post_conversion(self, md_text, error):
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

        pdf_path = pathlib.Path(self.selected_file)
        if result:
            output_file = pdf_path.with_suffix(".md")
        else:
            initial_name = pdf_path.stem + ".md"
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
            output_file = pdf_path.parent / new_name

        output_file.write_bytes(md_text.encode())
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
