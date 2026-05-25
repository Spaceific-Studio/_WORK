import os
import re
import fitz  # PyMuPDF
import gc    # Garbage Collector pro čištění paměti

def images_to_pdf(image_folder, output_pdf_path):
    """
    Vysoce optimalizované generování PDF z obrázků.
    Vkládá obrázky přímo na stránky a průběžně čistí paměť.
    """
    if not os.path.exists(image_folder):
        print(f"   [Chyba] Složka s obrázky neexistuje: {image_folder}")
        return False
    
    # Načtení a seřazení PNG obrázků
    images = sorted([f for f in os.listdir(image_folder) if f.lower().endswith('.png')])
    
    if not images:
        print(f"   [Upozornění] Ve složce {image_folder} nebyly nalezeny žádné PNG obrázky.")
        return False
    
    total_images = len(images)
    print(f"   -> Nalezeno {total_images} obrázků. Spouštím rychlé streamované spojování...")
    
    try:
        doc = fitz.open()  # Vytvoření nového PDF dokumentu
        
        for idx, img_name in enumerate(images, start=1):
            img_path = os.path.join(image_folder, img_name)
            
            # Informace o průběhu
            if idx % 10 == 0 or idx == total_images:
                print(f"      Zpracováno: {idx}/{total_images} obrázků...", end="\r", flush=True)
            
            try:
                # Otevřeme obrázek pouze jako bitmapu, abychom zjistili rozměry
                img = fitz.Pixmap(img_path)
                
                # Vytvoříme novou stránku v PDF přesně podle rozměrů obrázku
                page = doc.new_page(width=img.width, height=img.height)
                
                # Vykreslíme obrázek přímo na celou plochu stránky (nejrychlejší metoda)
                page.insert_image(page.rect, pixmap=img)
                
                # Okamžité uvolnění paměti bitmapy
                img = None
                
            except Exception as img_err:
                print(f"\n   [Chyba souboru] Nelze vložit obrázek {img_name}: {img_err}")
                continue
            
            # Každých 50 obrázků uvolníme nepoužívanou paměť v Pythonu
            if idx % 50 == 0:
                gc.collect()
            
        print(f"\n   -> Ukládám hotové PDF (ukládání může chvíli trvat)...")
        
        # Použijeme kompresi a linearizaci pro rychlé uložení velkých souborů
        doc.save(output_pdf_path, garbage=3, deflate=True)
        doc.close()
        
        # Finální vyčištění paměti po uzavření dokumentu
        gc.collect()
        
        print(f"   [Úspěch] PDF úspěšně vygenerováno: {output_pdf_path}")
        return True
    except Exception as e:
        print(f"\n   [Kritická Chyba] Nepodařilo se uložit PDF {output_pdf_path}. Důvod: {e}")
        return False

def zpracuj_normy(root_path):
    if not os.path.exists(root_path):
        print(f"Kořenový adresář {root_path} neexistuje!")
        return

    print(f"Prohledávám adresář: {root_path}\n" + "-"*50)

    # Procházení složek v kořenovém adresáři
    for folder_name in os.listdir(root_path):
        folder_path = os.path.join(root_path, folder_name)
        
        # Krok 1: Kontrola, zda jde o složku normy (obsahuje podtržítko oddělující Číslo_Název)
        if not os.path.isdir(folder_path) or "_" not in folder_name:
            continue
            
        print(f"\nZpracovávám normu: {folder_name}")
        
        # Definice cest pro hlavní PDF
        main_pdf_name = f"{folder_name}.pdf"
        main_pdf_path = os.path.join(folder_path, main_pdf_name)
        
        # Krok 2: Detekce podsložek (Kapitálky NEBO výjimka jako Za, Za1 apod.)
        subfolders = []
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            
            if os.path.isdir(item_path):
                if re.match(r"^[A-Z0-9]+$", item) or re.match(r"^Z[a-z][0-9]*$", item):
                    subfolders.append(item)

        # Krok 3 & 4 & 5: Rozhodování a generování
        
        # 1. Zpracování HLAVNÍHO PDF (ze složky PNG)
        if not os.path.exists(main_pdf_path):
            print(f" > Hlavní PDF neexistuje. Pokus o vygenerování ze složky 'PNG'.")
            if "PNG" in subfolders:
                png_folder_path = os.path.join(folder_path, "PNG")
                images_to_pdf(png_folder_path, main_pdf_path)
            else:
                print(f"   [Chyba] Chybí složka 'PNG' pro vygenerování hlavního PDF!")
        else:
            print(f" > Hlavní PDF existuje.")

        # 2. Zpracování OSTATNÍCH podsložek (Opravy, Změny...)
        for subfolder in subfolders:
            if subfolder == "PNG":
                continue
                
            suffix_pdf_name = f"{folder_name}_{subfolder}.pdf"
            suffix_pdf_path = os.path.join(folder_path, suffix_pdf_name)
            
            if not os.path.exists(suffix_pdf_path):
                print(f" > Chybí PDF pro složku '{subfolder}'. Generuji {suffix_pdf_name}...")
                source_folder = os.path.join(folder_path, subfolder)
                images_to_pdf(source_folder, suffix_pdf_path)
            else:
                print(f" > PDF pro složku '{subfolder}' již existuje v pořádku.")

if __name__ == "__main__":
    VÝCHOZÍ_CESTA = r"H:\_NORMY\AI_priprava"
    zpracuj_normy(VÝCHOZÍ_CESTA)