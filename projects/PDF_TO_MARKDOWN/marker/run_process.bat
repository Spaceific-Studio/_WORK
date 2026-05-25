@echo off
:: Nastavení cesty k Python instalaci
set PATH=C:\Users\GercakD\AppData\Local\Programs\Python\Python310;%PATH%

:: Přesun do pracovního adresáře (volitelné)
::cd /d "H:\_NORMY"

:: Spuštění skriptu
python C:\DANO\_WORK\PYTHON\projects\PDF_TO_MARKDOWN\marker\process_norms_in_MarkerVenv.py

pause