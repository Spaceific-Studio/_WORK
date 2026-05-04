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
    from pymupdf4llm.helpers.document_layout import select_ocr_function
except Exception:
    select_ocr_function = None

if onnxruntime is not None:
    # Workaround for ONNXRuntime requiring int64 inputs when the model produces int32.
    original_run = onnxruntime.InferenceSession.run
    def patched_run(self, output_names, input_feed, run_options=None):
        input_feed = {k: v.astype('int64') if hasattr(v, 'dtype') and v.dtype == 'int32' else v for k, v in input_feed.items()}
        return original_run(self, output_names, input_feed, run_options)
    onnxruntime.InferenceSession.run = patched_run

import pymupdf4llm


class PDFToMarkdownApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF to Markdown Converter")
        self.root.geometry("520x420")
        self.root.minsize(520, 420)
        self.root.resizable(False, True)
        
        self.selected_file = None
        self.is_converting = False
        self.ocr_installed = pytesseract is not None and shutil.which("tesseract") is not None
        self.ocr_supported = self._check_ocr_support()
        self.ocr_enabled_var = tk.BooleanVar(value=self.ocr_supported)
        
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

        if not self.ocr_installed:
            self.status_label.config(
                text="Pozor: OCR není nainstalované nebo není dostupné v PATH.",
                fg="#FF9800",
            )
        elif not self.ocr_supported:
            self.status_label.config(
                text="Pozor: OCR je nainstalované, ale není plně podporováno tímto modulem.",
                fg="#FF9800",
            )
        else:
            self.status_label.config(
                text="OCR je dostupné a lze ho použít při konverzi.",
                fg="#4CAF50",
            )

    def _check_ocr_support(self):
        if select_ocr_function is None:
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
        self.convert_btn.config(state=tk.NORMAL)
        self.status_label.config(text="", fg="#333333")

    def convert_file(self):
        """Spustí převod PDF na pozadí, aby GUI nezamrzlo."""
        if not self.selected_file:
            messagebox.showerror("Chyba", "Nejdříve vyberte soubor!")
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
        elif not self.ocr_supported and self.ocr_enabled_var.get():
            proceed = messagebox.askyesno(
                "OCR není plně podporováno",
                "OCR není plně podporováno tímto modulem. Zkusit převést bez OCR?"
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
            params = {
                "show_progress": False,
                "use_ocr": self.ocr_enabled_var.get() and self.ocr_supported,
                "force_ocr": self.ocr_enabled_var.get() and self.ocr_supported,
            }
            if self.ocr_enabled_var.get() and self.ocr_supported:
                params["ocr_language"] = "ces"
                if getattr(self, "ocr_function", None) is not None:
                    params["ocr_function"] = self.ocr_function

            md_text = pymupdf4llm.to_markdown(self.selected_file, **params)
            self.root.after(0, self._post_conversion, md_text, None)
        except Exception as e:
            self.root.after(0, self._post_conversion, None, e)

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
