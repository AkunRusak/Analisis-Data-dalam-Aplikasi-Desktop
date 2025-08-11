@echo off
echo ================================================
echo   Gantt Chart Analyzer - Fix Missing Dependencies
echo ================================================
echo.

echo [1/6] Creating new clean environment...
if exist "gantt_fixed" rmdir /s /q gantt_fixed
python -m venv gantt_fixed
call gantt_fixed\Scripts\activate

echo.
echo [2/6] Installing Python standard libraries support...
pip install --upgrade pip setuptools wheel

echo.
echo [3/6] Installing core dependencies...
pip install PyQt6==6.6.0
pip install pandas==2.1.0  
pip install numpy==1.24.0
pip install matplotlib==3.7.0

echo.
echo [4/6] Installing XML and parsing libraries...
pip install lxml
pip install defusedxml
pip install openpyxl

echo.
echo [5/6] Installing PyInstaller...
pip install pyinstaller==5.13.0

echo.
echo [6/6] Building with comprehensive includes...
pyinstaller ^
  --onefile ^
  --console ^
  --name="GanttChartAnalyzer" ^
  --exclude-module=PyQt5 ^
  --exclude-module=PySide2 ^
  --exclude-module=PySide6 ^
  --exclude-module=tkinter ^
  --hidden-import="xml" ^
  --hidden-import="xml.etree.ElementTree" ^
  --hidden-import="xml.parsers.expat" ^
  --hidden-import="lxml" ^
  --hidden-import="lxml.etree" ^
  --hidden-import="PyQt6.QtWidgets" ^
  --hidden-import="PyQt6.QtCore" ^
  --hidden-import="PyQt6.QtGui" ^
  --hidden-import="PyQt6.QtPrintSupport" ^
  --hidden-import="matplotlib.backends.backend_qt5agg" ^
  --hidden-import="pandas._libs.tslibs.timedeltas" ^
  --hidden-import="pandas.plotting._matplotlib" ^
  mainrev02.py

echo.
deactivate

echo.
echo ================================================
echo Build completed!
echo.
if exist "dist\GanttChartAnalyzer.exe" (
    echo SUCCESS: File .exe berhasil dibuat dengan fix dependencies!
    echo Location: dist\GanttChartAnalyzer.exe
    echo.
    echo Testing executable...
    echo Note: Console window akan muncul untuk debugging
    echo Jika berjalan normal, jalankan ulang dengan --windowed
) else (
    echo ERROR: Build gagal!
)
echo.
pause