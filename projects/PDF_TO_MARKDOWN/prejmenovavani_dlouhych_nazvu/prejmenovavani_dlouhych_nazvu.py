import os


def odstran_string_z_nazvu(vychozi_cesta, string_ke_smazani):
    # Kontrola, zda zadaná cesta vůbec existuje
    if not os.path.exists(vychozi_cesta):
        print(f"Chyba: Cesta '{vychozi_cesta}' neexistuje.")
        return

    pocitadlo_souboru = 0
    pocitadlo_slozek = 0

    print("Spouštím přejmenovávání...")
    print("-" * 40)

    # topdown=False je klíčové – prochází strukturu od nejhlubších souborů po kořenovou složku
    for korenovy_adresar, slozky, soubory in os.walk(
        vychozi_cesta, topdown=False
    ):

        # 1. Nejprve zpracujeme soubory
        for soubor in soubory:
            if string_ke_smazani in soubor:
                stara_cesta = os.path.join(korenovy_adresar, soubor)
                novy_nazev = soubor.replace(string_ke_smazani, "")
                nova_cesta = os.path.join(korenovy_adresar, novy_nazev)

                os.rename(stara_cesta, nova_cesta)
                print(f"Přejmenován soubor: {soubor} -> {novy_nazev}")
                pocitadlo_souboru += 1

        # 2. Poté zpracujeme složky
        for slozka in slozky:
            if string_ke_smazani in slozka:
                stara_cesta = os.path.join(korenovy_adresar, slozka)
                novy_nazev = slozka.replace(string_ke_smazani, "")
                nova_cesta = os.path.join(korenovy_adresar, novy_nazev)

                os.rename(stara_cesta, nova_cesta)
                print(f"Přejmenována složka: {slozka} -> {novy_nazev}")
                pocitadlo_slozek += 1

    print("-" * 40)
    print(
        f"Hotovo! Celkem přejmenováno: {pocitadlo_souboru} souborů a {pocitadlo_slozek} složek."
    )


# --- NASTAVENÍ A SPUŠTĚNÍ ---
if __name__ == "__main__":
    # Zde zadej cestu ke složce, kde chceš mazat (může být absolutní i relativní)
    # Rychlý tip: Před cestu dej 'r', aby Python nebral zpětná lomítka ve Windows jako speciální znaky
    CESTA_K_ADRESARI = r"B:\_NORMY\ČSN EN 1993-1-10_Eurokód 3_Navrhování ocelových konstrukcí - Část 1-10"

    # Zde zadej text, který se má z názvů odstranit
    TEXT_KE_SMAZANI = " 1-10_Houževnatost materiálu a vlastnosti napříč tloušťkou"

    odstran_string_z_nazvu(CESTA_K_ADRESARI, TEXT_KE_SMAZANI)