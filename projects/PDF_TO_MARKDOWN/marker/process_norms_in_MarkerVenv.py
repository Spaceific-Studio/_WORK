import os
import subprocess
import shutil
from pathlib import Path

# Konfigurace cest
BASE_DIR = Path(r"H:/_NORMY/AI_priprava")
# Cesta přímo k EXE souboru markeru ve vašem prostředí
MARKER_EXE = Path(r"C:/MarkerVenv/Scripts/marker_single.exe")

def run_marker(pdf_path, output_dir):
    """Spustí marker_single.exe přímo z Scripts složky venv."""
    print(f"--- Spouštím marker pro: {pdf_path.name} ---")
    
    # Sestavení příkazu přímo pro .exe
    cmd = [
        str(MARKER_EXE), 
        str(pdf_path), 
        "--output_dir", 
        str(output_dir)
    ]
    
    try:
        # shell=True může být v některých konfiguracích Windows nutné pro .exe
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Chyba při zpracování {pdf_path.name}: {e}")
        return False
    except FileNotFoundError:
        print(f"CHYBA: Soubor {MARKER_EXE} nebyl nalezen. Ověřte instalaci v C:/MarkerVenv")
        return False

def process_structure():
    if not BASE_DIR.exists():
        print(f"Adresář {BASE_DIR} neexistuje.")
        return

    for main_dir in BASE_DIR.iterdir():
        if not main_dir.is_dir():
            continue

        pdf_files = list(main_dir.glob("*.pdf"))

        for pdf_file in pdf_files:
            base_name = pdf_file.stem
            md_file_path = main_dir / f"{base_name}.md"
            sub_dir_path = main_dir / base_name
            
            should_run = False

            # 1. MD neexistuje
            if not md_file_path.exists():
                if not sub_dir_path.exists():
                    should_run = True
                else:
                    sub_md = sub_dir_path / f"{base_name}.md"
                    if not sub_md.exists():
                        shutil.rmtree(sub_dir_path)
                        should_run = True
                    else:
                        print(f"Nalezen zapomenutý .md v {sub_dir_path.name}, přesouvám.")
                        shutil.move(str(sub_md), str(md_file_path))
            
            # 2. MD je starší než PDF
            elif md_file_path.exists():
                if md_file_path.stat().st_mtime < pdf_file.stat().st_mtime:
                    print(f"PDF {pdf_file.name} je novější než .md, aktualizuji.")
                    if sub_dir_path.exists():
                        shutil.rmtree(sub_dir_path)
                    should_run = True

            if should_run:
                if run_marker(pdf_file, main_dir):
                    # Po úspěchu marker vytvoří složku se stejným názvem jako PDF
                    # Uvnitř je výsledné .md, které přesuneme o úroveň výš
                    new_md = sub_dir_path / f"{base_name}.md"
                    if new_md.exists():
                        if md_file_path.exists():
                            os.remove(md_file_path)
                        shutil.move(str(new_md), str(md_file_path))
                        print(f"Soubor {base_name}.md byl úspěšně vytvořen a přesunut.")
                    else:
                        print(f"Varování: Marker doběhl, ale soubor {new_md} nebyl nalezen.")

if __name__ == "__main__":
    process_structure()