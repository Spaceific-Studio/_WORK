import sys
from markitdown import MarkItDown
from openai import OpenAI

def main():
    # Kontrola, zda uživatel zadal oba argumenty
    if len(sys.argv) < 3:
        print("Chyba: Musíte zadat vstupní a výstupní soubor.")
        print("Použití: python convert.py <vstupni_soubor> <vystupni_soubor>")
        sys.exit(1)

    # Načtení argumentů z příkazové řádky
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    print(f"Spouštím konverzi souboru: {input_file}...")

    # Inicializace MarkItDown
    md = MarkItDown(
        enable_plugins=True,
        llm_client=OpenAI(),
        llm_model="gpt-4o",
    )

    try:
        # Konverze definovaného vstupu
        result = md.convert(input_file)
        
        # Zápis výsledku do definovaného výstupu s kódováním UTF-8
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result.text_content)
            
        print(f"Hotovo! Výsledek byl uložen do: {output_file}")
        
    except Exception as e:
        print(f"Během konverze došlo k chybě: {e}")

if __name__ == "__main__":
    main()