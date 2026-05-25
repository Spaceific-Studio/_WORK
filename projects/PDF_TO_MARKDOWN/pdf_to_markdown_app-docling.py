import os

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"
import tkinter as tk
from tkinter import filedialog, messagebox
from docling.document_converter import DocumentConverter

def proved_konverzi():
    # 1. Výběr souboru přes grafické okno
    root = tk.Tk()
    root.withdraw()  # Skryje hlavní prázdné okno
    root.attributes("-topmost", True)

    cesta_pdf = filedialog.askopenfilename(
        title="Vyberte PDF normu pro převod",
        filetypes=[("PDF soubory", "*.pdf")]
    )

    if not cesta_pdf:
        print("Storno: Nebyl vybrán žádný soubor.")
        return

    try:
        print(f"Startuji Docling konverzi pro: {os.path.basename(cesta_pdf)}")
        
        # 2. Nastavení výstupní cesty (stejná složka, stejné jméno .md)
        adresar = os.path.dirname(cesta_pdf)
        jmeno_bez_pripony = os.path.splitext(os.path.basename(cesta_pdf))[0]
        cesta_md = os.path.join(adresar, f"{jmeno_bez_pripony}.md")

        # 3. Inicializace konvertoru a převod
        converter = DocumentConverter()
        result = converter.convert(cesta_pdf)
        
        # 4. Export do Markdownu
        markdown_text = result.document.export_to_markdown()

        # 5. Zápis do souboru
        with open(cesta_md, "w", encoding="utf-8") as f:
            f.write(markdown_text)

        print(f"Hotovo! Soubor vytvořen: {cesta_md}")
        messagebox.showinfo("Hotovo", f"Uloženo do:\n{cesta_md}")

    except Exception as e:
        error_info = f"Chyba při převodu: {str(e)}"
        print(error_info)
        messagebox.showerror("Chyba", error_info)
    
    finally:
        root.destroy()

if __name__ == "__main__":
    proved_konverzi()