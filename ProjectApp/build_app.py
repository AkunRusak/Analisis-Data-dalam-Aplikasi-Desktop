#!/usr/bin/env python3
"""
Script untuk membangun aplikasi Gantt Chart menjadi executable menggunakan PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_pyinstaller():
    """Cek apakah PyInstaller sudah terinstall"""
    try:
        import PyInstaller
        print("✓ PyInstaller sudah terinstall")
        return True
    except ImportError:
        print("✗ PyInstaller belum terinstall")
        return False

def install_pyinstaller():
    """Install PyInstaller jika belum ada"""
    print("Installing PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller berhasil diinstall")
        return True
    except subprocess.CalledProcessError:
        print("✗ Gagal menginstall PyInstaller")
        return False

def create_spec_file():
    """Membuat file .spec untuk konfigurasi PyInstaller"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Daftar hidden imports yang mungkin diperlukan
hiddenimports = [
    'pandas',
    'numpy',
    'matplotlib',
    'matplotlib.backends.backend_qt5agg',
    'matplotlib.figure',
    'matplotlib.dates',
    'PyQt6',
    'PyQt6.QtWidgets',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'datetime',
    'sys'
]

# Data files yang perlu disertakan (jika ada)
datas = [
    # Contoh: ('path/to/data', 'data_folder_in_exe'),
]

# Binary files yang perlu disertakan
binaries = []

a = Analysis(
    ['GanttAnalysisApp.py'],           # Script utama
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GanttAnalysisApp',              # Nama executable
    debug=False,                          # Set True untuk debugging
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                            # Kompresi UPX (optional)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                       # Set True jika ingin console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'  # Uncomment dan sesuaikan jika ada icon
)
'''
    
    with open('GanttAnalysisApp.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✓ File .spec berhasil dibuat")

def build_application():
    """Build aplikasi menggunakan PyInstaller"""
    print("Memulai proses build...")
    
    try:
        # Build menggunakan file .spec
        subprocess.check_call([
            'pyinstaller',
            '--clean',              # Bersihkan build cache
            '--noconfirm',          # Tidak perlu konfirmasi
            'GanttAnalysisApp.spec'
        ])
        
        print("✓ Build berhasil!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Build gagal: {e}")
        return False

def build_onefile():
    """Build aplikasi sebagai single file executable"""
    print("Memulai proses build (single file)...")
    
    try:
        cmd = [
            'pyinstaller',
            '--onefile',                    # Single file
            '--windowed',                   # Tidak ada console window
            '--clean',                      # Bersihkan build cache
            '--noconfirm',                  # Tidak perlu konfirmasi
            '--name=GanttAnalysisApp',      # Nama executable
            # '--icon=icon.ico',            # Uncomment jika ada icon
            '--add-data=;.',                # Tambahkan data files jika perlu
            '--hidden-import=pandas',
            '--hidden-import=numpy', 
            '--hidden-import=matplotlib',
            '--hidden-import=PyQt6',
            '--hidden-import=matplotlib.backends.backend_qt5agg',
            'GanttAnalysisApp.py'
        ]
        
        subprocess.check_call(cmd)
        print("✓ Build single file berhasil!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Build single file gagal: {e}")
        return False

def build_onedir():
    """Build aplikasi sebagai directory dengan dependencies"""
    print("Memulai proses build (directory)...")
    
    try:
        cmd = [
            'pyinstaller',
            '--onedir',                     # Directory mode
            '--windowed',                   # Tidak ada console window
            '--clean',                      # Bersihkan build cache
            '--noconfirm',                  # Tidak perlu konfirmasi
            '--name=GanttAnalysisApp',      # Nama executable
            # '--icon=icon.ico',            # Uncomment jika ada icon
            '--hidden-import=pandas',
            '--hidden-import=numpy',
            '--hidden-import=matplotlib',
            '--hidden-import=PyQt6',
            '--hidden-import=matplotlib.backends.backend_qt5agg',
            'GanttAnalysisApp.py'
        ]
        
        subprocess.check_call(cmd)
        print("✓ Build directory berhasil!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Build directory gagal: {e}")
        return False

def cleanup():
    """Bersihkan file-file build"""
    folders_to_clean = ['build', '__pycache__']
    files_to_clean = ['*.spec']
    
    print("Membersihkan file build...")
    
    # Hapus folder
    for folder in folders_to_clean:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"✓ Folder {folder} dihapus")
    
    # Hapus file spec (optional)
    # if os.path.exists('GanttAnalysisApp.spec'):
    #     os.remove('GanttAnalysisApp.spec')
    #     print("✓ File .spec dihapus")

def check_requirements():
    """Cek apakah semua dependencies sudah terinstall"""
    required_packages = [
        'pandas', 'numpy', 'matplotlib', 'PyQt6'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} tersedia")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} tidak ditemukan")
    
    if missing_packages:
        print(f"\nPackage yang perlu diinstall: {', '.join(missing_packages)}")
        print("Jalankan: pip install " + " ".join(missing_packages))
        return False
    
    return True

def main():
    """Fungsi utama"""
    print("=" * 60)
    print("    PYINSTALLER BUILD SCRIPT")
    print("    Aplikasi Gantt Chart Analysis")
    print("=" * 60)
    
    # Cek apakah file utama ada
    if not os.path.exists('GanttAnalysisApp.py'):
        print("✗ File GanttAnalysisApp.py tidak ditemukan!")
        print("  Pastikan file ini berada di directory yang sama.")
        return
    
    # Cek requirements
    print("\n1. Mengecek dependencies...")
    if not check_requirements():
        return
    
    # Cek PyInstaller
    print("\n2. Mengecek PyInstaller...")
    if not check_pyinstaller():
        if not install_pyinstaller():
            return
    
    # Pilihan build mode
    print("\n3. Pilih mode build:")
    print("   1. Single File (.exe tunggal)")
    print("   2. Directory (folder dengan dependencies)")
    print("   3. Custom (.spec file)")
    print("   4. Cleanup build files")
    
    choice = input("\nPilihan (1-4): ").strip()
    
    if choice == '1':
        print("\n4. Building single file executable...")
        if build_onefile():
            print("\n✓ Executable berhasil dibuat di folder 'dist'!")
            print("  File: dist/GanttAnalysisApp.exe")
    
    elif choice == '2':
        print("\n4. Building directory executable...")
        if build_onedir():
            print("\n✓ Aplikasi berhasil dibuat di folder 'dist'!")
            print("  Jalankan: dist/GanttAnalysisApp/GanttAnalysisApp.exe")
    
    elif choice == '3':
        print("\n4. Membuat custom .spec file...")
        create_spec_file()
        print("\n5. Building dengan .spec file...")
        if build_application():
            print("\n✓ Aplikasi berhasil dibuat di folder 'dist'!")
    
    elif choice == '4':
        cleanup()
        print("\n✓ Cleanup selesai!")
    
    else:
        print("✗ Pilihan tidak valid!")

if __name__ == "__main__":
    main()