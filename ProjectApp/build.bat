@echo off
REM Windows Batch Script untuk build aplikasi Gantt Chart
REM Jalankan dengan double-click atau dari Command Prompt

echo ================================================
echo     BUILD SCRIPT - GANTT CHART APPLICATION
echo ================================================
echo.

REM Cek apakah Python terinstall
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python tidak ditemukan!
    echo Silakan install Python terlebih dahulu.
    pause
    exit /b 1
)

echo Python ditemukan.
echo.

REM Cek apakah file utama ada
if not exist "GanttAnalysisApp.py" (
    echo ERROR: File GanttAnalysisApp.py tidak ditemukan!
    echo Pastikan file ini ada di directory yang sama.
    pause
    exit /b 1
)

echo File utama ditemukan.
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo WARNING: Ada masalah saat install dependencies.
    echo Melanjutkan proses build...
)
echo.

REM Install PyInstaller jika belum ada
pip install pyinstaller
echo.

REM Pilihan build
echo Pilih mode build:
echo 1. Single File (executable tunggal)
echo 2. Directory (folder dengan dependencies)
echo 3. Keduanya
echo.
set /p choice="Masukkan pilihan (1-3): "

if "%choice%"=="1" goto single_file
if "%choice%"=="2" goto directory
if "%choice%"=="3" goto both
goto invalid_choice

:single_file
echo.
echo Building single file executable...
pyinstaller --onefile --windowed --clean --noconfirm ^
    --name=GanttAnalysisApp ^
    --hidden-import=pandas ^
    --hidden-import=numpy ^
    --hidden-import=matplotlib ^
    --hidden-import=PyQt6 ^
    --hidden-import=matplotlib.backends.backend_qt5agg ^
    GanttAnalysisApp.py

if %errorlevel% equ 0 (
    echo.
    echo SUCCESS: Single file executable berhasil dibuat!
    echo File: dist\GanttAnalysisApp.exe
) else (
    echo.
    echo ERROR: Build gagal!
)
goto end

:directory
echo.
echo Building directory executable...
pyinstaller --onedir --windowed --clean --noconfirm ^
    --name=GanttAnalysisApp ^
    --hidden-import=pandas ^
    --hidden-import=numpy ^
    --hidden-import=matplotlib ^
    --hidden-import=PyQt6 ^
    --hidden-import=matplotlib.backends.backend_qt5agg ^
    GanttAnalysisApp.py

if %errorlevel% equ 0 (
    echo.
    echo SUCCESS: Directory executable berhasil dibuat!
    echo Folder: dist\GanttAnalysisApp\
    echo Jalankan: dist\GanttAnalysisApp\GanttAnalysisApp.exe
) else (
    echo.
    echo ERROR: Build gagal!
)
goto end

:both
echo.
echo Building both versions...

echo 1/2: Building single file...
pyinstaller --onefile --windowed --clean --noconfirm ^
    --name=GanttAnalysisApp-SingleFile ^
    --distpath=dist/single ^
    --hidden-import=pandas ^
    --hidden-import=numpy ^
    --hidden-import=matplotlib ^
    --hidden-import=PyQt6 ^
    --hidden-import=matplotlib.backends.backend_qt5agg ^
    GanttAnalysisApp.py

echo 2/2: Building directory...
pyinstaller --onedir --windowed --clean --noconfirm ^
    --name=GanttAnalysisApp-Directory ^
    --distpath=dist/directory ^
    --hidden-import=pandas ^
    --hidden-import=numpy ^
    --hidden-import=matplotlib ^
    --hidden-import=PyQt6 ^
    --hidden-import=matplotlib.backends.backend_qt5agg ^
    GanttAnalysisApp.py

echo.
echo SUCCESS: Kedua versi berhasil dibuat!
echo Single file: dist\single\GanttAnalysisApp-SingleFile.exe
echo Directory: dist\directory\GanttAnalysisApp-Directory\
goto end

:invalid_choice
echo ERROR: Pilihan tidak valid!
goto end

:end
echo.
echo Build process selesai.
echo.
pause