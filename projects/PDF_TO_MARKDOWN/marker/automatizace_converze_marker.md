Napíš script v python, který načte struktúru adresaře "H:/_NORMY/AI_priprava", kde jsou adresáře norem i s podsložkami a na základě následujících kritérii spusti skript marker:
marker_single "H:/_NORMY/AI_priprava/{<main_dir> ve formátu: "číslo normy"_"název normy"}/{<název_souboru> pdf ve formátu: "číslo normy"_"název normy".pdf}" --output_dir "H:/_NORMY/AI_priprava/{<main_dir> ve formátu: "číslo normy"_"název normy"}"

kromě samotného python scriptu napíš i sadu příkazu do .bat souboru pro spuštění daného scriptu z přikazového řádku
-   musíš nejprve nastavit adresář pro python - "C:\Users\GercakD\AppData\Local\Programs\Python\Python310"

-   před spuštěním marker_single příkazu z pythonu musíš aktivovat v konzole oddělené prostředí "C:\MarkerVenv" a zněho ten script spustit

rozhodovací logika (pseudo kód):

if <main_dir>.files() contains ".pdf" files:
    pdf_files = filter(".pdf", <main_dir>.files())
    for pdf_file in pdf_files:
    dir.name = pdf_file.name                                        #file name (without extension)
        if <main_dir>.files() not contains pdf_file.name + ".md"    #file name (without extension) + extension .md:
            if <main_dir>.dirs() not contains dir.name:
                #run in console 
                marker_single "H:/_NORMY/AI_priprava/<main_dir>/<pdf_file.name>.pdf" --output_dir "H:/_NORMY/AI_priprava/<main_dir>"
            else:
                sub_dir_files = <sub_dir>.files()
                if <sub_dir>.files() not contains pdf_file.name + ".md"   #file name (without extension) + extension .md:
                    delete(<sub_dir>)
                    #run in console 
                    marker_single "H:/_NORMY/AI_priprava/<main_dir>/<pdf_file.name>.pdf" --output_dir "H:/_NORMY/AI_priprava/<main_dir>"
                    #after marker finished
                    md_file = <sub_dir>[pdf_file.name + ".md"]
                    move md_file from <sub_dir> to <main_dir>
                else:
                    md_file = <sub_dir>[pdf_file.name + ".md"]
                    move md_file from <sub_dir> to <main_dir>
        elif <main_dir>.files()[pdf_file.name + ".md"].date_of_creation < pdf_file.date_of_creation:
            if <main_dir>.dirs() not contains dir.name:
                #run in console 
                marker_single "H:/_NORMY/AI_priprava/<main_dir>/<pdf_file.name>.pdf" --output_dir "H:/_NORMY/AI_priprava/<main_dir>"
                #after marker finished
                md_file = <sub_dir>[pdf_file.name + ".md"]
                move md_file from <sub_dir> to <main_dir>
            else:
                delete(<sub_dir>)
                #run in console 
                marker_single "H:/_NORMY/AI_priprava/<main_dir>/<pdf_file.name>.pdf" --output_dir "H:/_NORMY/AI_priprava/<main_dir>"
                #after marker finished
                md_file = <sub_dir>[pdf_file.name + ".md"]
                move md_file from <sub_dir> to <main_dir>
            
