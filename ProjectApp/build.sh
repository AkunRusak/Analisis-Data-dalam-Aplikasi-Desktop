#!/bin/bash
# Linux/Mac Shell Script untuk build aplikasi Gantt Chart

echo "================================================"
echo "     BUILD SCRIPT - GANTT CHART APPLICATION"
echo "================================================"
echo

# Fungsi untuk cek command
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "ERROR: $1 tidak ditemukan!"
        return 1
    fi
    return 0
}

# Cek apakah Python terinstall
if ! check_command python3; then
    if ! check_command python; then
        echo "Silakan install Python terlebih dahulu."
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "Python ditemukan: $($PYTHON_CMD --version)"
echo

# Cek apakah file utama ada
if [ ! -f "GanttAnalysisApp.py" ]; then
    echo "ERROR: File GanttAnalysisApp.py tidak ditemukan!"
    echo "Pastikan file ini ada di directory yang sama."
    exit 1
fi

echo "File utama ditemukan."
echo

# Install dependencies
echo "Installing dependencies..."
$PYTHON_CMD -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "WARNING: Ada masalah saat install dependencies."
    echo "Melanjutkan proses build..."
fi
echo

# Install PyInstaller jika belum ada
$PYTHON_CMD -m pip install pyinstaller
echo

# Pilihan build
echo "Pilih mode build:"
echo "1. Single File (executable tunggal)"
echo "2. Directory (folder dengan dependencies)"
echo "3. Keduanya"
echo
read -p "Masukkan pilihan (1-3): " choice

case $choice in
    1)
        echo
        echo "Building single file executable..."
        pyinstaller --onefile --windowed --clean --noconfirm \
            --name=GanttAnalysisApp \
            --hidden-import=pandas \
            --hidden-import=numpy \
            --hidden-import=matplotlib \
            --hidden-import=PyQt6 \
            --hidden-import=matplotlib.backends.backend_qt5agg \
            GanttAnalysisApp.py
        
        if [ $? -eq 0 ]; then
            echo
            echo "SUCCESS: Single file executable berhasil dibuat!"
            echo "File: dist/GanttAnalysisApp"
        else
            echo
            echo "ERROR: Build gagal!"
        fi
        ;;
    
    2)
        echo
        echo "Building directory executable..."
        pyinstaller --onedir --windowed --clean --noconfirm \
            --name=GanttAnalysisApp \
            --hidden-import=pandas \
            --hidden-import=numpy \
            --hidden-import=matplotlib \
            --hidden-import=PyQt6 \
            --hidden-import=matplotlib.backends.backend_qt5agg \
            GanttAnalysisApp.py
        
        if [ $? -eq 0 ]; then
            echo
            echo "SUCCESS: Directory executable berhasil dibuat!"
            echo "Folder: dist/GanttAnalysisApp/"
            echo "Jalankan: ./dist/GanttAnalysisApp/GanttAnalysisApp"
        else
            echo
            echo "ERROR: Build gagal!"
        fi
        ;;
    
    3)
        echo
        echo "Building both versions..."
        
        echo "1/2: Building single file..."
        pyinstaller --onefile --windowed --clean --noconfirm \
            --name=GanttAnalysisApp-SingleFile \
            --distpath=dist/single \
            --hidden-import=pandas \
            --hidden-import=numpy \
            --hidden-import=matplotlib \
            --hidden-import=PyQt6 \
            --hidden-import=matplotlib.backends.backend_qt5agg \
            GanttAnalysisApp.py
        
        echo "2/2: Building directory..."
        pyinstaller --onedir --windowed --clean --noconfirm \
            --name=GanttAnalysisApp-Directory \
            --distpath=dist/directory \
            --hidden-import=pandas \
            --hidden-import=numpy \
            --hidden-import=matplotlib \
            --hidden-import=PyQt6 \
            --hidden-import=matplotlib.backends.backend_qt5agg \
            GanttAnalysisApp.py
        
        echo
        echo "SUCCESS: Kedua versi berhasil dibuat!"
        echo "Single file: dist/single/GanttAnalysisApp-SingleFile"
        echo "Directory: dist/directory/GanttAnalysisApp-Directory/"
        ;;
    
    *)
        echo "ERROR: Pilihan tidak valid!"
        exit 1
        ;;
esac

echo
echo "Build process selesai."

# Buat file executable (untuk Linux/Mac)
if [ -f "dist/GanttAnalysisApp" ]; then
    chmod +x dist/GanttAnalysisApp
fi

if [ -f "dist/GanttAnalysisApp/GanttAnalysisApp" ]; then
    chmod +x dist/GanttAnalysisApp/GanttAnalysisApp
fi

echo