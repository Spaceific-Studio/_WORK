import os
import torch
import logging
from marker.converters.pdf import PdfConverter
from marker.config.parser import ConfigParser
from marker.models import create_model_dict

logging.basicConfig(level=logging.INFO)

print("--- Start diagnostiky v11 ---")

try:
    fname = r"H:\_NORMY\AI_priprava\73 0540-1_Tepelná ochrana budov - 1_Terminologie\73 0540-1_Tepelná ochrana budov - 1_Terminologie.pdf"
    out_dir = r"H:\TempOutput"

    # 1. Musíme vytvořit konfiguraci, která vypadá jako slovník, ale chová se jako objekt
    config_dict = {
        "output_format": "markdown",
        "device": "cpu",
        "dtype": torch.float32
    }
    
    # 2. Inicializujeme parser
    parser = ConfigParser(config_dict)
    
    # 3. ZÍSKÁME ARTIFACTS - Tady byl minule ten "to(dict)" error. 
    # Musíme zajistit, aby device byl string "cpu"
    config_for_models = parser.generate_config_dict()
    if hasattr(config_for_models, "get") and isinstance(config_for_models.get("device"), dict):
        config_for_models["device"] = "cpu"
    
    print("Krok 1: Načítám artefakty (modely)...")
    # Toto vytvoří ten chybějící artifact_dict
    artifacts = create_model_dict(config_for_models)

    print("Krok 2: Inicializace konvertoru...")
    # Teď mu dáme VŠECHNO, co chce
    converter = PdfConverter(
        config=config_obj if 'config_obj' in locals() else config_for_models,
        artifact_dict=artifacts,
        processor_list=parser.get_processors(artifacts)
    )
    
    print("Krok 3: Konverze (teď se to rozjede)...")
    rendered = converter(fname)
    
    if not os.path.exists(out_dir): os.makedirs(out_dir)
    with open(os.path.join(out_dir, "vystup.md"), "w", encoding="utf-8") as f:
        f.write(rendered.markdown)

    print(f"HOTOVO! Výsledek je v {out_dir}")

except Exception as e:
    print(f"\n!!! CHYBA: {e}")
    import traceback
    traceback.print_exc()