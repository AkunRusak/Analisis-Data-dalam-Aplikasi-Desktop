# 🚀 Panduan Build Aplikasi Gantt Chart Analysis

Panduan lengkap untuk mengkonversi aplikasi Python menjadi executable menggunakan PyInstaller.

## 📋 Prerequisites

### 1. Python
Pastikan Python 3.8+ sudah terinstall:
```bash
python --version
# atau
python3 --version
```

### 2. Dependencies
Install semua dependencies yang diperlukan:
```bash
pip install -r requirements.txt
```

### 3. File yang Diperlukan
- `GanttAnalysisApp.py` (file utama aplikasi)
- `requirements.txt` 
- `build_app.py` (script build otomatis)
- `build.bat` (Windows) atau `build.sh` (Linux/Mac)

## 🛠️ Cara Build

### Metode 1: Script Otomatis (Recommended)

#### Windows:
```cmd
# Double-click file build.bat
# atau jalankan dari Command Prompt:
build.bat
```

#### Linux/Mac:
```bash
# Beri permission execute
chmod +x build.sh

# Jalankan script
./build.sh
```

### Metode 2: Python Script
```bash
python build_app.py
```

### Metode 3: Manual PyInstaller

#### Single File (Executable Tunggal):
```bash
pyinstaller --onefile --windowed --clean --noconfirm \
    --name=GanttAnalysisApp \
    --hidden-import=pandas \
    --hidden-import=numpy \
    --hidden-import=matplotlib \
    --hidden-import=PyQt6 \
    --hidden-import=matplotlib.backends.backend_qt5agg \
    GanttAnalysisApp.py
```

#### Directory Mode (Folder dengan Dependencies):
```bash
pyinstaller --onedir --windowed --clean --noconfirm \
    --name=GanttAnalysisApp \
    --hidden-import=pandas \
    --hidden-import=numpy \
    --hidden-import=matplotlib \
    --hidden-import=PyQt6 \
    --hidden-import=matplotlib.backends.backend_qt5agg \
    GanttAnalysisApp.py
```

## 📁 Hasil Build

Setelah build berhasil, file akan tersimpan di folder `dist/`:

### Single File Mode:
```
dist/
└── GanttAnalysisApp.exe      # Windows
└── GanttAnalysisApp          # Linux/Mac
```

### Directory Mode:
```
dist/
└── GanttAnalysisApp/
    ├── GanttAnalysisApp.exe  # Windows
    ├── GanttAnalysisApp      # Linux/Mac
    └── [various dependencies files]
```

## 🔧 Parameter Build

| Parameter | Fungsi |
|-----------|--------|
| `--onefile` | Membuat single executable file |
| `--onedir` | Membuat folder dengan dependencies |
| `--windowed` | Tidak menampilkan console window |
| `--clean` | Membersihkan cache build sebelumnya |
| `--noconfirm` | Tidak meminta konfirmasi overwrite |
| `--name` | Nama file executable |
| `--hidden-import` | Import module yang tidak terdeteksi otomatis |
| `--icon` | Icon untuk executable (optional) |

## 🐛 Troubleshooting

### Error: Module not found
**Solusi**: Tambahkan `--hidden-import=nama_module` ke command PyInstaller

### Error: PyQt6 not working
**Solusi**: Pastikan PyQt6 terinstall dengan benar:
```bash
pip uninstall PyQt6
pip install PyQt6
```

### Error: matplotlib backend
**Solusi**: Tambahkan hidden import:
```bash
--hidden-import=matplotlib.backends.backend_qt5agg
```

### File terlalu besar
**Solusi**: 
1. Gunakan `--onedir` mode
2. Tambahkan `--exclude-module` untuk module yang tidak diperlukan
3. Gunakan virtual environment yang minimal

### Error pada Windows: Missing DLL
**Solusi**: Install Visual C++ Redistributable

### Error pada Linux: Library not found
**Solusi**: Install dependencies sistem:
```bash
# Ubuntu/Debian
sudo apt-get install python3-dev python3-tk

# CentOS/RHEL
sudo yum install python3-devel tkinter
```

## 🎯 Tips Optimasi

### 1. Ukuran File
- Gunakan virtual environment yang minimal
- Exclude module yang tidak diperlukan:
```bash
--exclude-module=tkinter --exclude-module=unittest
```

### 2. Startup Speed
- Directory mode lebih cepat startup daripada single file
- Hindari terlalu banyak import di level module

### 3. Icon dan Metadata (Windows)
Buat file `.ico` dan tambahkan:
```bash
--icon=app_icon.ico
--version-file=version.txt
```

## 📦 Distribution

### Single File Distribution:
✅ Pros:
- Mudah didistribusikan (1 file saja)
- Tidak perlu folder dependencies

❌ Cons:
- File size lebih besar
- Startup lebih lambat
- Temporary extraction setiap run

### Directory Distribution:
✅ Pros:
- Startup lebih cepat
- Ukuran total lebih kecil
- Bisa di-customize dependencies

❌ Cons:
- Banyak file yang perlu didistribusikan
- User bisa accidentally menghapus dependencies

## 🔍 Testing

Setelah build, test aplikasi:

1. **Functionality Test**:
   - Buka file CSV
   - Buat Gantt Chart
   - Test semua fitur analisis
   - Export functionality

2. **Performance Test**:
   - Test dengan file CSV besar
   - Monitor memory usage
   - Check startup time

3. **Compatibility Test**:
   - Test pada sistem yang berbeda
   - Test tanpa Python terinstall
   - Test dengan user privileges terbatas

## 📝 Build Log

Simpan log build untuk debugging:
```bash
pyinstaller [parameters] > build.log 2>&1
```

## 🚀 Advanced Options

### Custom Spec File:
Untuk kontrol yang lebih detail, gunakan file `.spec`:
```bash
pyi-makespec --onefile GanttAnalysisApp.py
# Edit GanttAnalysisApp.spec sesuai kebutuhan
pyinstaller GanttAnalysisApp.spec
```

### Cross-Platform Build:
PyInstaller tidak mendukung cross-platform build. Build harus dilakukan di sistem target.

## 📞 Support

Jika mengalami masalah:

1. Cek [PyInstaller Documentation](https://pyinstaller.readthedocs.io/)
2. Cek [Common Issues](https://github.com/pyinstaller/pyinstaller/wiki)
3. Jalankan dengan `--debug=all` untuk detail error
4. Gunakan virtual environment untuk isolasi dependencies

---

**Happy Building! 🎉**
