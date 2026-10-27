@echo off
chcp 65001 >nul
echo ============================================================================
echo   AGROZICA v2.6 - Compilador Automatizado de Executavel (.EXE) PyInstaller
echo   Desafio Oficial AGROHACK 2026/2 - IFRO Campus Ariquemes
echo ============================================================================

cd /d "%~dp0"

echo [1/3] Garantindo geracao da base simulada inicial de 500ha...
python generator_seed.py

echo [2/3] Compilando AgroZica.exe com CustomTkinter, Matplotlib e Configuracoes...
pyinstaller --noconfirm --onedir --windowed ^
    --name "AgroZica" ^
    --collect-all customtkinter ^
    --add-data "config;config" ^
    --add-data "data;data" ^
    main.py

echo [3/3] Copiando pastas config/ e data/ editaveis para junto do executavel...
xcopy /E /I /Y "config" "dist\AgroZica\config" >nul
xcopy /E /I /Y "data" "dist\AgroZica\data" >nul

echo ============================================================================
echo   Compilacao concluida com sucesso!
echo   Executavel disponivel em: dist\AgroZica\AgroZica.exe
echo ============================================================================
pause

