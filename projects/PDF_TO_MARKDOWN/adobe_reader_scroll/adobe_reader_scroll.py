import os
import time
import pyautogui
from PIL import ImageChops

# ==============================================================================
# NASTAVENÍ VÝŘEZU (v pixelech)
# Pokud zde máš své zaměřené souřadnice z minula, přepiš je sem:
# Příklad: VYREZ = (200, 120, 1400, 900)
# ==============================================================================
VYREZ = (0, 0, 0, 0)


def zamerit_vyrez():
    print("--- ZAMĚŘOVÁNÍ VÝŘEZU ---")
    print("1. Najed myší do LEVÉHO HORNÍHO rohu oblasti, kterou chceš fotit.")
    for i in range(5, 0, -1):
        print(f"Zaměřuji levý horní roh za... {i}")
        time.sleep(1)
    x1, y1 = pyautogui.position()
    print(f"-> Levý horní roh zaměřen: [{x1}, {y1}]\n")

    print("2. Nyní najed myší do PRAVÉHO DOLNÍHO rohu této oblasti.")
    for i in range(5, 0, -1):
        print(f"Zaměřuji pravý dolní roh za... {i}")
        time.sleep(1)
    x2, y2 = pyautogui.position()
    print(f"-> Pravý dolní roh zaměřen: [{x2}, {y2}]\n")

    sirka = x2 - x1
    vyska = y2 - y1

    if sirka <= 0 or vyska <= 0:
        print(
            "Chyba: Pravý dolní roh musí být níže a více vpravo než levý horní!"
        )
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

    if not os.path.exists(slozka_ulozeni):
        os.makedirs(slozka_ulozeni)
        print(f"Vytvořena složka: {slozka_ulozeni}")

    print("\n!!! POZOR !!!")
    print("Máš 5 sekund na to, abys překlikl do Adobe Readeru.")
    for i in range(5, 0, -1):
        print(f"Začínám za... {i}")
        time.sleep(1)

    print("\nSpouštím automatické snímání dokumentu...")

    predchozi_snimek = None

    for stranka in range(1, maximalni_pocet + 1):
        nazev_souboru = f"{stranka:03d}.PNG"
        cesta_k_souboru = os.path.join(slozka_ulozeni, nazev_souboru)

        # 1. Vyfotit výřez
        aktuandli_snimek = pyautogui.screenshot(region=VYREZ)

        # 2. Kontrola, zda nejsme na konci (porovnání s minulým snímkem)
        if predchozi_snimek is not None:
            # ImageChops.difference najde rozdíly mezi obrázky
            rozdil = ImageChops.difference(aktuandli_snimek, predchozi_snimek)
            if rozdil.getbbox() is None:
                # getbbox() vrátí None, pokud jsou obrázky naprosto identické
                print(
                    f"\n[!] Detekován konec dokumentu na snímku {stranka}. Obrázek je stejný jako předchozí."
                )
                break

        # Uložit snímek, pokud je nový
        aktuandli_snimek.save(cesta_k_souboru)
        print(f"Uloženo (výřez): {cesta_k_souboru}")

        # Uchováme pro příští porovnání
        predchozi_snimek = aktuandli_snimek

        time.sleep(0.5)

        # 3. Posunout dolů
        pyautogui.press("pagedown")

        # Pauza na překreslení stránek
        time.sleep(0.1)

    print(
        f"\nHotovo! Všechny snímky najdeš ve složce: {os.path.abspath(slozka_ulozeni)}"
    )


if __name__ == "__main__":
    # Nastav číslo, které bezpečně PŘEKROČÍ počet stránek tvého PDF.
    # Díky chytré kontrole script sám skončí dřív, jakmile dorazí na konec.
    MAX_STRANEK_LIMIT = 1000

    automaticke_snimani_pdf(MAX_STRANEK_LIMIT)