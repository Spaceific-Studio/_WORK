import os
import time
import pyautogui
from PIL import ImageChops

# ==============================================================================
# NASTAVENÍ VÝREZU (v pixelech)
# Spusť script s (0, 0, 0, 0) a zaměř čistě VNITŘNÍ plochu dokumentu.
# ==============================================================================
VYREZ = (476, 129, 906, 902)


def zamerit_vyrez():
    print("--- ZAMĚŘOVÁNÍ VNITŘNÍHO OKNA ---")
    print("V Adobe Readeru nastav zobrazení na ŠÍŘKU (Ctrl + 2).")
    print("\n1. Najed myší do LEVÉHO HORNÍHO rohu vnitřní plochy.")
    for i in range(5, 0, -1):
        print(f"Zaměřuji levý horní roh za... {i}")
        time.sleep(1)
    x1, y1 = pyautogui.position()
    print(f"-> Levý horní roh zaměřen: [{x1}, {y1}]\n")

    print("2. Nyní najed myší do PRAVÉHO DOLNÍHO rohu vnitřní plochy.")
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

    print("-" * 50)
    print("Zkopíruj si tyto hodnoty do scriptu (do proměnné VYREZ nahoře):")
    print(f"VYREZ = ({x1}, {y1}, {sirka}, {vyska})")
    print("-" * 50)
    return (x1, y1, sirka, vyska)


def automaticke_snimani_pdf(maximalni_pocet, slozka_ulozeni="pdf_snimky"):
    global VYREZ

    if VYREZ == (0, 0, 0, 0):
        zvoleny_vyrez = zamerit_vyrez()
        if zvoleny_vyrez is None:
            return
        VYREZ = zvoleny_vyrez
        print("\nPokračujeme k samotnému snímání...")

    x, y, w, h = VYREZ

    if not os.path.exists(slozka_ulozeni):
        os.makedirs(slozka_ulozeni)

    print("\n!!! POZOR !!!")
    print("Máš 5 sekund na to, abys překlikl do Adobe Readeru a vyjel na ÚPLNÝ ZAČÁTEK dokumentu.")
    for i in range(5, 0, -1):
        print(f"Začínám za... {i}")
        time.sleep(1)

    print("\nSpouštím snímání přes Mezerník + Šipku dolů...")
    
    # Aktivace okna
    pyautogui.click(x + (w // 2), y + (h // 2))
    time.sleep(0.2)
    pyautogui.press("escape")
    time.sleep(0.5)

    predchozi_snimek = None

    for stranka in range(1, maximalni_pocet + 1):
        nazev_souboru = f"{stranka:03d}.PNG"
        cesta_k_souboru = os.path.join(slozka_ulozeni, nazev_souboru)

        # 1. Vyfotit
        aktualni_snimek = pyautogui.screenshot(region=VYREZ)

        # 2. Kontrola konce dokumentu
        if predchozi_snimek is not None:
            rozdil = ImageChops.difference(aktualni_snimek, predchozi_snimek)
            if rozdil.getbbox() is None:
                print(f"\n[!] Dosažen konec dokumentu. Snímek {stranka} je stejný jako předchozí.")
                break

        # Uložení snímku
        aktualni_snimek.save(cesta_k_souboru)
        print(f"Uloženo: {cesta_k_souboru}")

        predchozi_snimek = aktualni_snimek
        time.sleep(0.1)

        # 3. KOMBINOVANÝ POSUN (Mezerník + Šipka dolů)
        # Skočíme o jedno okno dolů
        pyautogui.press("space")
        time.sleep(0.1)
        
        # Dotlačíme dokument o kousek dál, abychom odrolovali ten otravný překryv
        # Pokud by ti tam ještě kousek překryvu zbyl, stačí řádek níže duplikovat 
        # a poslat šipku dolů dvakrát: pyautogui.press("down")
        pyautogui.press("down")

        # Pauza na plynulé dokrolování a vykreslení
        time.sleep(1.2)

    print(f"\nHotovo! Snímky najdeš v: {os.path.abspath(slozka_ulozeni)}")


if __name__ == "__main__":
    MAX_STRANEK_LIMIT = 1000

    automaticke_snimani_pdf(MAX_STRANEK_LIMIT)