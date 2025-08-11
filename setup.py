from cx_Freeze import setup, Executable
import sys

# Dependensi yang perlu disertakan
build_exe_options = {
    "packages": [
        "pandas", 
        "numpy", 
        "matplotlib", 
        "PyQt6",
        "sys",
        "datetime"
    ],
    "includes": [
        "matplotlib.backends.backend_qt5agg",
        "PyQt6.QtWidgets",
        "PyQt6.QtCore", 
        "PyQt6.QtGui",
        "pandas",
        "numpy"
    ],
    "include_files": [
        # Tambahkan file tambahan jika ada (icon, dll)
    ],
    "excludes": [
        "tkinter",  # Tidak diperlukan untuk PyQt6
        "unittest",
        "pydoc_data"
    ]
}

# Konfigurasi untuk Windows
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # Menghilangkan console window

setup(
    name="Gantt Chart Analyzer",
    version="1.0",
    description="Aplikasi Integrasi Gantt Chart dan Analisis Data",
    options={"build_exe": build_exe_options},
    executables=[Executable(
        "mainrev02.py",
        base=base,
        target_name="GanttChartAnalyzer.exe",
        icon=None  # Tambahkan path icon jika ada
    )]
)