import os
import tkinter as tk
from tkinter import filedialog, messagebox

# Kompletní importy pro správnou strukturu v nejnovějším Doclingu
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import PdfFormatOption  # <--- TOTO JE KLÍČOVÉ

def proved_konverzi():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    cesta_pdf = filedialog.askopenfilename(
        title="Vyberte PDF normu",
        filetypes=[("PDF soubory", "*.pdf")]
    )

    if not cesta_pdf:
        return

    try:
        print(f"Zpracovávám: {os.path.basename(cesta_pdf)}")
        
        # 1. Příprava cest
        adresar = os.path.dirname(cesta_pdf)
        jmeno_bez_pripony = os.path.splitext(os.path.basename(cesta_pdf))[0]
        cesta_md = os.path.join(adresar, f"{jmeno_bez_pripony}.md")

        # 2. Nastavení vnitřní logiky (OCR vypnuto)
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = False
        pipeline_options.do_table_structure = True

        # 3. Zabalení nastavení do formátového objektu (řeší chybu 'backend')
        pdf_format_option = PdfFormatOption(
            pipeline_options=pipeline_options # Zde se definuje backend automaticky
        )

        # 4. Inicializace konvertoru
        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: pdf_format_option
            }
        )
        
        # 5. Převod
        result = converter.convert(cesta_pdf)
        
        # 6. Uložení
        with open(cesta_md, "w", encoding="utf-8") as f:
            f.write(result.document.export_to_markdown())

        print(f"Hotovo: {cesta_md}")
        messagebox.showinfo("Hotovo", "Převod proběhl úspěšně.")

    except Exception as e:
        # Výpis celé chyby do konzole pro jistotu
        import traceback
        traceback.print_exc()
        messagebox.showerror("Chyba", f"Nastala chyba: {e}")
    
    finally:
        root.destroy()

if __name__ == "__main__":
    proved_konverzi()