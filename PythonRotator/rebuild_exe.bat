@echo off
setlocal
echo ==============================================
echo Przebudowywanie bota WoWRotator.exe (APB Edition)
echo ==============================================
echo.

:: Ensure Python is in path for this script
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [!] Blad: Python nie jest zainstalowany lub nie ma go w PATH.
    pause
    exit /b 1
)

:: Rebuild using python
python -m PyInstaller --onefile --noconsole --uac-admin --name "WoWRotator" bot.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [+] Budowanie zakonczone sukcesem!
    if exist dist\WoWRotator.exe (
        move /y dist\WoWRotator.exe .
    )
    echo [+] Porzadkowanie...
    if exist build rmdir /s /q build
    if exist dist rmdir /s /q dist
    if exist WoWRotator.spec del /q WoWRotator.spec
    echo.
    echo [ GOTOWE! ] Aplikacja WoWRotator.exe zostala zaktualizowana.
) else (
    echo.
    echo [!] BLAD podczas budowania EXE.
)

pause
