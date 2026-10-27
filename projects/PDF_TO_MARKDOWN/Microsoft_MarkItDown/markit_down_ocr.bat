@echo off
chcp 65001 > nul

:: Definice cest do proměnných pro lepší přehlednost
set VENV_PATH=C:\MarkItDown\Scripts\Activate.ps1
set SCRIPT_PATH=C:\DANO\_WORK\PYTHON\projects\PDF_TO_MARKDOWN\Microsoft_MarkItDown\markItDown_OCR.py
set INPUT_FILE=H:\_NORMY\AI_priprava\ČSN EN ISO 23387_Informační modelování staveb BIM - Datové šablony pro stavební objekty\ČSN EN ISO 23387_Informační modelování staveb BIM - Datové šablony pro stavební objekty.pdf
set OUTPUT_FILE=H:\_NORMY\AI_priprava\ČSN EN ISO 23387_Informační modelování staveb BIM - Datové šablony pro stavební objekty\output.md

echo Spoustim konverzi PDF do Markdown...
echo Prosim cekejte, proces muze chvili trvat (vyuziva se LLM)...
echo.

:: Spuštění PowerShellu, aktivace venv, spuštění skriptu s předáním argumentů
powershell -NoProfile -ExecutionPolicy Bypass -Command "& '%VENV_PATH%'; python '%SCRIPT_PATH%' '%INPUT_FILE%' '%OUTPUT_FILE%'"

echo.
echo Proces byl dokoncen. Praci zdar!
pause