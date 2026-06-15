@echo off
setlocal EnableDelayedExpansion

echo ========================================
echo  M5PaperS3 Calculator Uploader (Windows)
echo ========================================
echo.
echo  Copies boot.py and main.py to a M5PaperS3
echo  already running UIFlow2 / MicroPython.
echo  (No firmware .bin - this is a file upload.)
echo.

:: Check Python
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install from https://www.python.org/
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do set PY_VER=%%v
echo [OK] !PY_VER! found.
echo.

:: Check / install mpremote (MicroPython file transfer tool)
python -c "import mpremote" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing mpremote...
    python -m pip install mpremote --quiet || python -m pip install --user mpremote --quiet
    if errorlevel 1 (
        echo [ERROR] Failed to install mpremote.
        pause
        exit /b 1
    )
    echo [OK] mpremote installed.
) else (
    echo [OK] mpremote found.
)
echo.

:: Locate the files to upload (next to this script)
set "BOOT=%~dp0boot.py"
set "MAIN=%~dp0main.py"
if not exist "!BOOT!" (
    echo [ERROR] boot.py not found next to this script.
    pause
    exit /b 1
)
if not exist "!MAIN!" (
    echo [ERROR] main.py not found next to this script.
    pause
    exit /b 1
)
echo [OK] Found: boot.py, main.py
echo.

:: Auto-detect COM port
echo [INFO] Scanning for connected devices...
set "CWPORTS_TMP=%TEMP%\cwports_%RANDOM%_%RANDOM%.tmp"
reg query "HKLM\HARDWARE\DEVICEMAP\SERIALCOMM" 2>nul | findstr "REG_SZ" > "!CWPORTS_TMP!"
set PORT_COUNT=0
if exist "!CWPORTS_TMP!" (
    for /f "usebackq tokens=3" %%P in ("!CWPORTS_TMP!") do (
        set /a PORT_COUNT+=1
        set "PORT_VAL_!PORT_COUNT!=%%P"
    )
    del "!CWPORTS_TMP!" 2>nul
)

if !PORT_COUNT!==0 (
    echo [WARN] No COM port found. Connect M5PaperS3 via USB-C and check Device Manager.
    echo.
    set /p PORT="Enter COM port manually (e.g. COM3): "
) else if !PORT_COUNT!==1 (
    echo [OK] Auto-detected: !PORT_VAL_1!
    set PORT=!PORT_VAL_1!
) else (
    echo Found multiple devices:
    for /l %%i in (1,1,!PORT_COUNT!) do (
        echo   [%%i] !PORT_VAL_%%i!
    )
    echo.
    set /p CHOICE="Select device number [1-!PORT_COUNT!]: "
    set "PORT="
    for /l %%i in (1,1,!PORT_COUNT!) do (
        if "%%i"=="!CHOICE!" set "PORT=!PORT_VAL_%%i!"
    )
    if "!PORT!"=="" (
        echo [WARN] Invalid choice - enter COM port manually.
        set /p PORT="COM port (e.g. COM3): "
    )
)

:: Normalize PORT
set "PORT=%PORT:^"=%"
set "PORT=%PORT: =%"

:: Validate PORT
echo(!PORT!| findstr /r /i "^COM[0-9][0-9]*$" >nul
if errorlevel 1 (
    echo [ERROR] "!PORT!" does not look like a valid COM port.
    pause
    exit /b 1
)
echo.

:: Upload
echo [INFO] Uploading to !PORT! ...
echo        Close UIFlow2 / any serial monitor first, or the port will be busy.
echo.
python -m mpremote connect "!PORT!" fs cp "!BOOT!" :boot.py + fs cp "!MAIN!" :main.py
if errorlevel 1 (
    echo.
    echo [ERROR] Upload failed.
    echo         - Make sure no other program holds the COM port (UIFlow2, Thonny, serial monitor)
    echo         - Try a different USB cable or replug the device
    echo         - Confirm the COM port is correct
    pause
    exit /b 1
)

:: Reset so the calculator starts fresh
python -m mpremote connect "!PORT!" reset >nul 2>&1

echo.
echo ========================================
echo  Done^! The calculator should start on the device.
echo ========================================
pause
