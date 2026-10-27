import os
import time
import pyautogui
from PIL import ImageChops
from pynput.mouse import Controller

# Inicializace ovladače myši pro přesný posun
mouse = Controller()

# ==============================================================================
# NASTAVENÍ VÝŘEZU (v pixelech)
# Nastav si v Adobe Readeru šířku dokumentu na maximum (Ctrl + 2).
# Výřez zaměř tak, aby pokrýval celou šířku textu. Výška výřezu určuje, 
# o kolik pixelů se dokument pokaždé posune dolů.
# ==============================================================================
VYREZ = (476, 129, 906, 902)


def zamerit_vyrez():
    print("--- ZAMĚŘOVÁNÍ VÝŘEZU (REŽIM NA ŠÍŘKU) ---")
    print("Ujisti se, že máš v Adobe Readeru dokument přizpůsobený na šířku (Ctrl+2).")
    print("\n1. Najed myší do LEVÉHO HORNÍHO rohu oblasti, kterou chceš snímat.")
    for i in range(5, 0, -1):
        print(f"Zaměřuji levý horní roh za... {i}")
        time.sleep(1)
    x1, y1 = pyautogui.position()
    print(f"-> Levý horní roh zaměřen: [{x1}, {y1}]\n")

    print("2. Nyní najed myší do PRAVÉHO DOLNÍHO rohu této oblasti.")
    print("(Výška tohoto výřezu určí přesný krok, o který bude script scrolovat!)")
    for i in range(5, 0, -1):
        print(f"Zaměřuji pravý dolní roh za... {i}")
        time.sleep(1)
    x2, y2 = pyautogui.position()
    print(f"-> Pravý dolní roh zaměřen: [{x2}, {y2}]\n")

    sirka = x2 - x1
    vyska = y2 - y1

    if sirka <= 0 or vyska <= 0:
        print("Chyba: Pravý dolní roh musí být níže a více vpravo než levý horní!")
        return None

    print("-" * 40)
    print("Zkopíruj si tyto hodnoty do scriptu (do proměnné VYREZ nahoře):")
    print(f"VYREZ = ({x1}, {y1}, {sirka}, {vyska})")
    print("-" * 40)
    return (x1, y1, sirka, vyska)


def automaticke_snimani_pdf(maximalni_pocet, slozka_ulozeni="pdf_snimky"):
    global VYREZ

    if VYREZ == (0, 0, 0, 0):
        zvoleny_vyrez = zamerit_vyrez()
        if zvoleny_vyrez is None:
            return
        VYREZ = zvoleny_vyrez
        print("\nPokračujeme k samotnému snímání...")

    x_horni, y_horni, sirka_frame, vyska_frame = VYREZ

    if not os.path.exists(slozka_ulozeni):
        os.makedirs(slozka_ulozeni)
        print(f"Vytvořena složka: {slozka_ulozeni}")

    print("\n!!! POZOR !!!")
    print("Máš 5 sekund na to, abys překlikl do Adobe Readeru a najel na úplný začátek.")
    for i in range(5, 0, -1):
        print(f"Začínám za... {i}")
        time.sleep(1)

    print("\nSpouštím automatické snímání s přesným scrolováním...")
    
    # AKTIVACE OKNA BEZ OZNAČENÍ TEXTU:
    # Klikneme na levý horní roh výřezu (často okraj stránky nebo šedé pozadí), ne doprostřed textu
    pyautogui.click(VYREZ[0]-5, VYREZ[1])
    time.sleep(0.2)
    
    # Pro jistotu stiskneme Escape, kdyby se přece jen něco označilo, čímž výběr zrušíme
    pyautogui.press("escape")
    time.sleep(0.2)

    predchozi_snimek = None

    for stranka in range(1, maximalni_pocet + 1):
        nazev_souboru = f"{stranka:03d}.PNG"
        cesta_k_souboru = os.path.join(slozka_ulozeni, nazev_souboru)

        # 1. Vyfotit přesný výřez
        aktualni_snimek = pyautogui.screenshot(region=VYREZ)

        # 2. Kontrola konce dokumentu
        if predchozi_snimek is not None:
            rozdil = ImageChops.difference(aktualni_snimek, predchozi_snimek)
            if rozdil.getbbox() is None:
                print(f"\n[!] Dosažen konec dokumentu. Snímek {stranka} je identický s předchozím.")
                break

        # Uložení snímku
        aktualni_snimek.save(cesta_k_souboru)
        print(f"Uloženo (vysoké rozlišení): {cesta_k_souboru}")

        predchozi_snimek = aktualni_snimek
        time.sleep(0.1)

        # 3. MATEMATICKY PŘESNÝ POSUN
        # Windows používá pro scrollování "detenty" (obvykle 1 krok = 120 jednotek dolů).
        # Přepočítáme výšku našeho výřezu na přesný počet kroků kolečka myši.
        # Směr dolů je v pynput definován jako záporné číslo.
        #skoky = -(vyska_frame / 55)
        
        #skoky = -(vyska_frame)
        #mouse.scroll(0, skoky)
        
        pyautogui.press("space")
        pyautogui.press("down")
        time.sleep(0.1)
        
        # Pauza na plynulé doscrolování a vykreslení textu
        #time.sleep(0.1)

    print(f"\nHotovo! Snímky v plném rozlišení najdeš v: {os.path.abspath(slozka_ulozeni)}")


if __name__ == "__main__":
    MAX_STRANEK_LIMIT = 2000

    automaticke_snimani_pdf(MAX_STRANEK_LIMIT)