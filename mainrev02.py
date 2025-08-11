import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QApplication, QMainWindow, QFileDialog, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QLabel, QTableView, QTabWidget, 
                             QComboBox, QMessageBox, QSplitter, QGroupBox, QFormLayout)
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex, QSize
from PyQt6.QtGui import QAction, QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt6.QtGui import QAction, QIcon, QPalette, QColor


class PandasModel(QAbstractTableModel):
    """Model untuk menampilkan DataFrame di QTableView"""
    
    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, parent=QModelIndex()):
        return self._data.shape[0]

    def columnCount(self, parent=QModelIndex()):
        return self._data.shape[1]

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[section])
            if orientation == Qt.Orientation.Vertical:
                return str(section + 1)
        return None


class GanttChartCanvas(FigureCanvas):
    """Widget untuk menampilkan Gantt Chart"""
    
    def __init__(self, parent=None, width=10, height=8, dpi=100):
        self.fig, self.ax = plt.subplots(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
        self.fig.tight_layout()
        
    def plot_gantt(self, df, task_col, start_col, end_col, progress_col=None):
        """Membuat Gantt chart dari DataFrame"""
        if df.empty:
            return
            
        # Konversi kolom tanggal jika perlu
        for col in [start_col, end_col]:
            if df[col].dtype != 'datetime64[ns]':
                df[col] = pd.to_datetime(df[col])
                
        # Urutkan berdasarkan tanggal mulai
        df = df.sort_values(by=start_col)
        
        # Siapkan data untuk plotting
        tasks = df[task_col].tolist()
        starts = df[start_col].tolist()
        ends = df[end_col].tolist()
        
        # Hitung durasi
        durations = [(end - start).days + 1 for start, end in zip(starts, ends)]
        
        # Bersihkan plot sebelumnya
        self.ax.clear()
        
        # Atur y-axis
        y_positions = range(len(tasks))
        self.ax.set_yticks(y_positions)
        self.ax.set_yticklabels(tasks)
        
        # Plot bars
        colors = plt.cm.viridis(np.linspace(0, 1, len(tasks)))
        for i, (task, start, duration) in enumerate(zip(tasks, starts, durations)):
            self.ax.barh(i, duration, left=mdates.date2num(start), height=0.5, 
                         color=colors[i], edgecolor='black', alpha=0.8)
                         
            # Tambahkan teks durasi
            self.ax.text(mdates.date2num(start) + duration/2, i, f"{duration} hari", 
                         ha='center', va='center', color='white', fontweight='bold')
        
        # Format x-axis sebagai tanggal
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        self.ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        
        # Atur batasan x-axis
        if starts and ends:
            min_date = min(starts) - timedelta(days=1)
            max_date = max(ends) + timedelta(days=1)
            self.ax.set_xlim(min_date, max_date)
        
        # Tambahkan label dan judul
        self.ax.set_xlabel('Tanggal')
        self.ax.set_ylabel('Tugas')
        self.ax.set_title('Gantt Chart')
        
        # Rotasi label tanggal untuk keterbacaan
        plt.xticks(rotation=45)
        
        # Format grid
        self.ax.grid(True, axis='x', linestyle='--', alpha=0.7)
        
        self.fig.tight_layout()
        self.draw()


class AnalysisCanvas(FigureCanvas):
    """Widget untuk menampilkan visualisasi analisis data"""
    
    def __init__(self, parent=None, width=10, height=8, dpi=100):
        self.fig, self.ax = plt.subplots(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
        self.fig.tight_layout()

    def plot_task_duration(self, df, task_col, start_col, end_col):
        """Membuat grafik durasi tugas"""
        if df.empty:
            return
            
        # Konversi kolom tanggal jika perlu
        for col in [start_col, end_col]:
            if df[col].dtype != 'datetime64[ns]':
                df[col] = pd.to_datetime(df[col])
        
        # Hitung durasi dalam hari
        df['duration'] = (df[end_col] - df[start_col]).dt.days + 1
        
        # Urutkan berdasarkan durasi
        df = df.sort_values(by='duration', ascending=False)
        
        # Ambil top 10 tugas dengan durasi terpanjang
        plot_df = df.head(10)
        
        # Bersihkan plot sebelumnya
        self.ax.clear()
        
        # Plot horizontal bar chart
        bars = self.ax.barh(plot_df[task_col], plot_df['duration'], color='skyblue')
        
        # Tambahkan nilai pada bar
        for bar in bars:
            width = bar.get_width()
            self.ax.text(width + 0.5, bar.get_y() + bar.get_height()/2, 
                         f"{int(width)} hari", va='center')
        
        # Tambahkan label dan judul
        self.ax.set_xlabel('Durasi (hari)')
        self.ax.set_ylabel('Tugas')
        self.ax.set_title('10 Tugas dengan Durasi Terpanjang')
        
        # Format grid
        self.ax.grid(True, axis='x', linestyle='--', alpha=0.7)
        
        self.fig.tight_layout()
        self.draw()
        
    def plot_timeline_histogram(self, df, start_col, end_col):
        """Membuat histogram distribusi waktu mulai dan selesai tugas"""
        if df.empty:
            return
            
        # Konversi kolom tanggal jika perlu
        for col in [start_col, end_col]:
            if df[col].dtype != 'datetime64[ns]':
                df[col] = pd.to_datetime(df[col])
        
        # Bersihkan plot sebelumnya
        self.ax.clear()
        
        # Plot histogram
        self.ax.hist([df[start_col], df[end_col]], 
                     label=['Tanggal Mulai', 'Tanggal Selesai'],
                     alpha=0.7, bins=10)
        
        # Format x-axis sebagai tanggal
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        self.ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        
        # Tambahkan label dan judul
        self.ax.set_xlabel('Tanggal')
        self.ax.set_ylabel('Jumlah Tugas')
        self.ax.set_title('Distribusi Tanggal Mulai dan Selesai')
        self.ax.legend()
        
        # Rotasi label tanggal untuk keterbacaan
        plt.xticks(rotation=45)
        
        self.fig.tight_layout()
        self.draw()
        
    def plot_task_overlap(self, df, task_col, start_col, end_col):
        """Membuat grafik overlap tugas per periode"""
        if df.empty:
            return
            
        # Konversi kolom tanggal jika perlu
        for col in [start_col, end_col]:
            if df[col].dtype != 'datetime64[ns]':
                df[col] = pd.to_datetime(df[col])
        
        # Temukan tanggal awal dan akhir keseluruhan proyek
        project_start = df[start_col].min()
        project_end = df[end_col].max()
        
        # Buat rentang tanggal untuk analisis
        date_range = pd.date_range(start=project_start, end=project_end)
        
        # Hitung jumlah tugas aktif per hari
        active_tasks = []
        for date in date_range:
            # Hitung berapa tugas yang aktif pada tanggal ini
            count = sum((df[start_col] <= date) & (df[end_col] >= date))
            active_tasks.append(count)
        
        # Bersihkan plot sebelumnya
        self.ax.clear()
        
        # Plot line chart
        self.ax.plot(date_range, active_tasks, 'b-', linewidth=2)
        self.ax.fill_between(date_range, active_tasks, alpha=0.3)
        
        # Format x-axis sebagai tanggal
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        self.ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        
        # Tandai nilai tertinggi
        max_overlap = max(active_tasks)
        max_index = active_tasks.index(max_overlap)
        max_date = date_range[max_index]
        
        self.ax.plot(max_date, max_overlap, 'ro')
        self.ax.annotate(f'Puncak: {max_overlap} tugas\n{max_date.strftime("%Y-%m-%d")}',
                         xy=(max_date, max_overlap),
                         xytext=(max_date + timedelta(days=2), max_overlap + 1),
                         arrowprops=dict(facecolor='black', shrink=0.05, width=1.5),
                         fontweight='bold')
        
        # Tambahkan label dan judul
        self.ax.set_xlabel('Tanggal')
        self.ax.set_ylabel('Jumlah Tugas Aktif')
        self.ax.set_title('Jumlah Tugas yang Berjalan Bersamaan')
        
        # Rotasi label tanggal untuk keterbacaan
        plt.xticks(rotation=45)
        
        # Format grid
        self.ax.grid(True, linestyle='--', alpha=0.7)
        
        self.fig.tight_layout()
        self.draw()


class MainWindow(QMainWindow):
    """Jendela utama aplikasi"""
    
    def __init__(self):
        super().__init__()
        
        # Properti data
        self.df = None
        
        # Setup UI
        self.setWindowTitle("Aplikasi Integrasi Gantt Chart dan Analisis Data")
        self.setGeometry(100, 100, 1200, 600)
        self.setup_ui()
        self.setup_themes()
        
    def setup_ui(self):
        # Buat menu
        self.create_menus()
        
        # Widget utama
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Layout utama
        main_layout = QVBoxLayout(main_widget)
        
        # Label Perusahaan
        #upload_button = QPushButton("PT. Krakatau Engineering")
        # upload_button.clicked.connect()
        #upload_button.setMinimumHeight(40)
        #main_layout.addWidget(upload_button)
        
        # Tab widget untuk tampilan yang berbeda
        self.tab_widget = QTabWidget()
        
        # Tab data
        data_tab = QWidget()
        data_layout = QVBoxLayout(data_tab)
        self.table_view = QTableView()
        data_layout.addWidget(QLabel("Preview Data:"))
        data_layout.addWidget(self.table_view)
        self.tab_widget.addTab(data_tab, "Data")
        
                # Perubahan pada method setup_ui() 
        # Ganti bagian Tab Gantt Chart (sekitar line 305-335) dengan code berikut:

        # Tab Gantt Chart
        gantt_tab = QWidget()
        gantt_layout = QHBoxLayout(gantt_tab)  # UBAH: dari QVBoxLayout ke QHBoxLayout

        # TAMBAH: Widget untuk form konfigurasi dengan ukuran terbatas
        config_widget = QWidget()
        config_widget.setMaximumWidth(200)
        config_widget.setMinimumWidth(150)
        config_main_layout = QVBoxLayout(config_widget)

        # Form untuk konfigurasi Gantt
        gantt_config = QGroupBox("Konfigurasi Gantt Chart")
        config_layout = QVBoxLayout(gantt_config)  # Dari QFormLayout

        # Kolom Tugas
        task_label = QLabel("Kolom Tugas:")
        self.task_col_combo = QComboBox()
        self.task_col_combo.setMaximumWidth(150)
        config_layout.addWidget(task_label)
        config_layout.addWidget(self.task_col_combo)

        # Kolom Tanggal Mulai
        start_label = QLabel("Kolom Tanggal Mulai:")
        self.start_col_combo = QComboBox()
        self.start_col_combo.setMaximumWidth(150)
        config_layout.addWidget(start_label)
        config_layout.addWidget(self.start_col_combo)

        # Kolom Tanggal Selesai
        end_label = QLabel("Kolom Tanggal Selesai:")
        self.end_col_combo = QComboBox()
        self.end_col_combo.setMaximumWidth(150)
        config_layout.addWidget(end_label)
        config_layout.addWidget(self.end_col_combo)

        # Kolom Progress
        progress_label = QLabel("Kolom Progress (opsional):")
        self.progress_col_combo = QComboBox()
        self.progress_col_combo.setMaximumWidth(150)
        config_layout.addWidget(progress_label)
        config_layout.addWidget(self.progress_col_combo)

        # Tambahkan sedikit jarak sebelum tombol
        config_layout.addSpacing(10)

        update_gantt_button = QPushButton("Perbarui")
        update_gantt_button.setMaximumWidth(150)
        update_gantt_button.setMinimumHeight(35)
        update_gantt_button.setMaximumHeight(45)
        update_gantt_button.clicked.connect(self.update_gantt_chart)
        config_layout.addWidget(update_gantt_button)

        config_main_layout.addWidget(gantt_config)
        config_main_layout.addStretch()  # TAMBAH: untuk mendorong form ke atas

        # TAMBAH: Widget untuk canvas dan toolbar
        canvas_widget = QWidget()
        canvas_layout = QVBoxLayout(canvas_widget)

        # Canvas untuk Gantt Chart
        self.gantt_canvas = GanttChartCanvas()
        gantt_toolbar = NavigationToolbar(self.gantt_canvas, self)

        canvas_layout.addWidget(gantt_toolbar)
        canvas_layout.addWidget(self.gantt_canvas)

        # UBAH: Susun secara horizontal
        gantt_layout.addWidget(config_widget)      # Form di kiri
        gantt_layout.addWidget(canvas_widget, 1)   # Canvas di kanan dengan stretch

        self.tab_widget.addTab(gantt_tab, "Gantt Chart")

        # HAPUS kode lama yang tidak digunakan:
        # gantt_layout.addWidget(gantt_config)
        # gantt_layout.addWidget(gantt_toolbar) 
        # gantt_layout.addWidget(self.gantt_canvas)
        
        # Tab Analisis
        analysis_tab = QWidget()
        analysis_layout = QVBoxLayout(analysis_tab)
        
        # Form untuk konfigurasi analisis
        analysis_config = QGroupBox("Konfigurasi Analisis")
        analysis_form = QFormLayout(analysis_config)
        
        self.analysis_type_combo = QComboBox()
        self.analysis_type_combo.addItems(["Durasi Tugas", "Distribusi Timeline", "Overlap Tugas"])
        
        analysis_form.addRow("Jenis Analisis:", self.analysis_type_combo)
        
        update_analysis_button = QPushButton("Jalankan Analisis")
        update_analysis_button.clicked.connect(self.update_analysis)
        analysis_form.addRow(update_analysis_button)
        
        analysis_layout.addWidget(analysis_config)
        
        # Canvas untuk analisis
        self.analysis_canvas = AnalysisCanvas()
        analysis_toolbar = NavigationToolbar(self.analysis_canvas, self)
        
        analysis_layout.addWidget(analysis_toolbar)
        analysis_layout.addWidget(self.analysis_canvas)
        
        self.tab_widget.addTab(analysis_tab, "Analisis Data")
        
        main_layout.addWidget(self.tab_widget)

    def create_menus(self):
        # Menu bar
        menu_bar = self.menuBar()
        
        # Menu File
        file_menu = menu_bar.addMenu("File")
        
        # Aksi menu
        open_action = QAction("Buka CSV", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.load_csv)
        
        export_gantt_action = QAction("Ekspor Gantt Chart", self)
        export_gantt_action.triggered.connect(self.export_gantt)
        
        export_analysis_action = QAction("Ekspor Analisis", self)
        export_analysis_action.triggered.connect(self.export_analysis)
        
        exit_action = QAction("Keluar", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        
        # Tambahkan aksi ke menu
        file_menu.addAction(open_action)
        file_menu.addAction(export_gantt_action)
        file_menu.addAction(export_analysis_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        
        # Menu Bantuan
        help_menu = menu_bar.addMenu("Bantuan")
        
        about_action = QAction("Tentang Aplikasi", self)
        about_action.triggered.connect(self.show_about)
        
        help_menu.addAction(about_action)

        # Menu DarkLight Mode
        # Menu View
        view_menu = menu_bar.addMenu("Tampilan")

        theme_action = QAction("Dark/Light Mode", self)
        theme_action.setShortcut("Ctrl+T")
        theme_action.triggered.connect(self.toggle_theme)

        view_menu.addAction(theme_action)
    
    def load_csv(self):
        """Memuat dan memproses file CSV"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Pilih File CSV", "", "CSV Files (*.csv)")
        
        if file_path:
            try:
                # Baca file CSV
                self.df = pd.read_csv(file_path)
                
                # Tampilkan data di tabel
                model = PandasModel(self.df)
                self.table_view.setModel(model)
                
                # Perbarui combo box dengan nama kolom
                self.update_column_combos()
                
                # Beralih ke tab data
                self.tab_widget.setCurrentIndex(0)
                
                QMessageBox.information(self, "Berhasil", f"File CSV berhasil dimuat: {file_path}")
            
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal memuat file CSV: {str(e)}")
    
    def update_column_combos(self):
        """Memperbarui combo box dengan nama kolom dari DataFrame"""
        if self.df is not None:
            columns = self.df.columns.tolist()
            
            # Simpan pilihan saat ini jika ada
            current_task = self.task_col_combo.currentText()
            current_start = self.start_col_combo.currentText()
            current_end = self.end_col_combo.currentText()
            current_progress = self.progress_col_combo.currentText()
            
            # Kosongkan combo box
            self.task_col_combo.clear()
            self.start_col_combo.clear()
            self.end_col_combo.clear()
            self.progress_col_combo.clear()
            
            # Tambahkan opsi kosong untuk kolom progress
            self.progress_col_combo.addItem("")
            
            # Isi dengan kolom dari DataFrame
            self.task_col_combo.addItems(columns)
            self.start_col_combo.addItems(columns)
            self.end_col_combo.addItems(columns)
            self.progress_col_combo.addItems(columns)
            
            # Coba kembalikan pilihan sebelumnya
            for combo, current_text in [
                (self.task_col_combo, current_task),
                (self.start_col_combo, current_start),
                (self.end_col_combo, current_end),
                (self.progress_col_combo, current_progress)
            ]:
                if current_text in columns:
                    index = combo.findText(current_text)
                    if index >= 0:
                        combo.setCurrentIndex(index)
            
            # Coba tebak kolom yang mungkin untuk Gantt Chart
            self.guess_gantt_columns()
    
    def guess_gantt_columns(self):
        """Menebak kolom yang mungkin untuk Gantt Chart berdasarkan nama atau tipe data"""
        if self.df is None:
            return
            
        # Kata kunci untuk menebak kolom
        task_keywords = ['task', 'tugas', 'aktivitas', 'kegiatan', 'nama']
        start_keywords = ['start', 'mulai', 'begin', 'awal']
        end_keywords = ['end', 'finish', 'selesai', 'akhir']
        progress_keywords = ['progress', 'kemajuan', 'persen', 'percent', '%']
        
        # Fungsi untuk menemukan kolom berdasarkan kata kunci
        def find_column_by_keywords(keywords):
            for col in self.df.columns:
                col_lower = col.lower()
                if any(keyword in col_lower for keyword in keywords):
                    return col
            return None
        
        # Tebak kolom tugas
        task_col = find_column_by_keywords(task_keywords)
        if task_col:
            index = self.task_col_combo.findText(task_col)
            if index >= 0:
                self.task_col_combo.setCurrentIndex(index)
        
        # Tebak kolom tanggal mulai dan selesai
        # Prioritaskan kolom dengan tipe data datetime
        date_columns = []
        for col in self.df.columns:
            try:
                # Coba konversi ke datetime
                pd.to_datetime(self.df[col])
                date_columns.append(col)
            except:
                pass
        
        if len(date_columns) >= 2:
            # Jika ada minimal 2 kolom tanggal
            start_col = find_column_by_keywords(start_keywords) or date_columns[0]
            end_col = find_column_by_keywords(end_keywords) or date_columns[1]
            
            # Atur combo box
            if start_col:
                index = self.start_col_combo.findText(start_col)
                if index >= 0:
                    self.start_col_combo.setCurrentIndex(index)
            
            if end_col:
                index = self.end_col_combo.findText(end_col)
                if index >= 0:
                    self.end_col_combo.setCurrentIndex(index)
        
        # Tebak kolom progress
        progress_col = find_column_by_keywords(progress_keywords)
        if progress_col:
            index = self.progress_col_combo.findText(progress_col)
            if index >= 0:
                self.progress_col_combo.setCurrentIndex(index)
    
    def update_gantt_chart(self):
        """Perbarui tampilan Gantt Chart berdasarkan konfigurasi"""
        if self.df is None:
            QMessageBox.warning(self, "Peringatan", "Tidak ada data yang dimuat")
            return
        
        # Ambil konfigurasi
        task_col = self.task_col_combo.currentText()
        start_col = self.start_col_combo.currentText()
        end_col = self.end_col_combo.currentText()
        progress_col = self.progress_col_combo.currentText() if self.progress_col_combo.currentText() else None
        
        # Validasi konfigurasi
        if not task_col or not start_col or not end_col:
            QMessageBox.warning(self, "Peringatan", "Pilih kolom untuk tugas, tanggal mulai, dan tanggal selesai")
            return
        
        try:
            # Plot Gantt Chart
            self.gantt_canvas.plot_gantt(self.df, task_col, start_col, end_col, progress_col)
            
            # Beralih ke tab Gantt
            self.tab_widget.setCurrentIndex(1)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal membuat Gantt Chart: {str(e)}")
    
    def update_analysis(self):
        """Perbarui tampilan analisis berdasarkan jenis yang dipilih"""
        if self.df is None:
            QMessageBox.warning(self, "Peringatan", "Tidak ada data yang dimuat")
            return
        
        # Ambil konfigurasi
        analysis_type = self.analysis_type_combo.currentText()
        task_col = self.task_col_combo.currentText()
        start_col = self.start_col_combo.currentText()
        end_col = self.end_col_combo.currentText()
        
        # Validasi konfigurasi
        if not task_col or not start_col or not end_col:
            QMessageBox.warning(self, "Peringatan", "Pilih kolom untuk tugas, tanggal mulai, dan tanggal selesai")
            return
        
        try:
            # Jalankan analisis yang dipilih
            if analysis_type == "Durasi Tugas":
                self.analysis_canvas.plot_task_duration(self.df, task_col, start_col, end_col)
            elif analysis_type == "Distribusi Timeline":
                self.analysis_canvas.plot_timeline_histogram(self.df, start_col, end_col)
            elif analysis_type == "Overlap Tugas":
                self.analysis_canvas.plot_task_overlap(self.df, task_col, start_col, end_col)
            
            # Beralih ke tab Analisis
            self.tab_widget.setCurrentIndex(2)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal melakukan analisis: {str(e)}")
    
    def export_gantt(self):
        """Ekspor Gantt Chart sebagai gambar"""
        if self.df is None or self.tab_widget.currentIndex() != 1:
            QMessageBox.warning(self, "Peringatan", "Tidak ada Gantt Chart yang ditampilkan")
            return
        
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(self, "Simpan Gantt Chart", "", "PNG Files (*.png);;PDF Files (*.pdf)")
        
        if file_path:
            try:
                self.gantt_canvas.fig.savefig(file_path, bbox_inches='tight', dpi=300)
                QMessageBox.information(self, "Berhasil", f"Gantt Chart disimpan ke: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal menyimpan Gantt Chart: {str(e)}")
    
    def export_analysis(self):
        """Ekspor hasil analisis sebagai gambar"""
        if self.df is None or self.tab_widget.currentIndex() != 2:
            QMessageBox.warning(self, "Peringatan", "Tidak ada analisis yang ditampilkan")
            return
        
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(self, "Simpan Hasil Analisis", "", "PNG Files (*.png);;PDF Files (*.pdf)")
        
        if file_path:
            try:
                self.analysis_canvas.fig.savefig(file_path, bbox_inches='tight', dpi=300)
                QMessageBox.information(self, "Berhasil", f"Hasil analisis disimpan ke: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal menyimpan hasil analisis: {str(e)}")
    
    def show_about(self):
        """Tampilkan informasi tentang aplikasi"""
        QMessageBox.about(self, "Tentang Aplikasi", 
                         "Aplikasi Integrasi Gantt Chart dan Analisis Data\n\n"
                         "Aplikasi ini memungkinkan pengguna untuk membuat Integrasi Gantt Chart "
                         "dan melakukan analisis data dari file CSV.\n\n"
                         "Dibuat dengan Python dan PyQt6.")

# DarkLight Mode
    def setup_themes(self):
        """Setup tema untuk aplikasi"""
        # Style untuk light mode
        self.light_style = """
    QMainWindow {
        background-color: #f5f5f5;
        color: #333333;
    }
    
    QTabWidget::pane {
        border: 1px solid #c0c0c0;
        background-color: #ffffff;
    }
    
    QTabWidget::tab-bar {
        alignment: center;
    }
    
    QTabBar::tab {
        background-color: #e1e1e1;
        color: #333333;
        padding: 8px 16px;
        margin-right: 2px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    
    QTabBar::tab:selected {
        background-color: #ffffff;
        border-bottom: 2px solid #0078d4;
    }
    
    QTabBar::tab:hover {
        background-color: #d0d0d0;
    }
    
    QPushButton {
        background-color: #0078d4;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        font-weight: bold;
    }
    
    QPushButton:hover {
        background-color: #106ebe;
    }
    
    QPushButton:pressed {
        background-color: #005a9e;
    }
    
    QComboBox {
        background-color: #ffffff;
        border: 1px solid #c0c0c0;
        padding: 4px 8px;
        border-radius: 4px;
        color: #333333;
    }
    
    QComboBox:hover {
        border-color: #0078d4;
    }
    
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    
    QComboBox::down-arrow {
        image: url(down_arrow_light.png);
        width: 12px;
        height: 12px;
    }
    
    QTableView {
        background-color: #ffffff;
        alternate-background-color: #f8f8f8;
        color: #333333;
        gridline-color: #d0d0d0;
        selection-background-color: #0078d4;
        selection-color: white;
    }
    
    QHeaderView::section {
        background-color: #e1e1e1;
        color: #333333;
        padding: 8px;
        border: 1px solid #c0c0c0;
        font-weight: bold;
    }
    
    QGroupBox {
        font-weight: bold;
        border: 2px solid #c0c0c0;
        border-radius: 8px;
        margin: 8px 0px;
        padding-top: 8px;
        color: #333333;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px 0 5px;
        color: #0078d4;
    }
    
    QLabel {
        color: #333333;
    }
    
    QMenuBar {
        background-color: #f5f5f5;
        color: #333333;
        border-bottom: 1px solid #c0c0c0;
    }
    
    QMenuBar::item {
        background-color: transparent;
        padding: 4px 8px;
    }
    
    QMenuBar::item:selected {
        background-color: #e1e1e1;
    }
    
    QMenu {
        background-color: #ffffff;
        color: #333333;
        border: 1px solid #c0c0c0;
    }
    
    QMenu::item:selected {
        background-color: #0078d4;
        color: white;
    }
    """
    
    # Style untuk dark mode
        self.dark_style = """
    QMainWindow {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    
    QTabWidget::pane {
        border: 1px solid #555555;
        background-color: #3c3c3c;
    }
    
    QTabWidget::tab-bar {
        alignment: center;
    }
    
    QTabBar::tab {
        background-color: #404040;
        color: #ffffff;
        padding: 8px 16px;
        margin-right: 2px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    
    QTabBar::tab:selected {
        background-color: #3c3c3c;
        border-bottom: 2px solid #0078d4;
    }
    
    QTabBar::tab:hover {
        background-color: #4a4a4a;
    }
    
    QPushButton {
        background-color: #0078d4;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        font-weight: bold;
    }
    
    QPushButton:hover {
        background-color: #106ebe;
    }
    
    QPushButton:pressed {
        background-color: #005a9e;
    }
    
    QComboBox {
        background-color: #404040;
        border: 1px solid #555555;
        padding: 4px 8px;
        border-radius: 4px;
        color: #ffffff;
    }
    
    QComboBox:hover {
        border-color: #0078d4;
    }
    
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    
    QComboBox::down-arrow {
        image: url(down_arrow_dark.png);
        width: 12px;
        height: 12px;
    }
    
    QComboBox QAbstractItemView {
        background-color: #404040;
        color: #ffffff;
        selection-background-color: #0078d4;
    }
    
    QTableView {
        background-color: #3c3c3c;
        alternate-background-color: #404040;
        color: #ffffff;
        gridline-color: #555555;
        selection-background-color: #0078d4;
        selection-color: white;
    }
    
    QHeaderView::section {
        background-color: #404040;
        color: #ffffff;
        padding: 8px;
        border: 1px solid #555555;
        font-weight: bold;
    }
    
    QGroupBox {
        font-weight: bold;
        border: 2px solid #555555;
        border-radius: 8px;
        margin: 8px 0px;
        padding-top: 8px;
        color: #ffffff;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px 0 5px;
        color: #0078d4;
    }
    
    QLabel {
        color: #ffffff;
    }
    
    QMenuBar {
        background-color: #2b2b2b;
        color: #ffffff;
        border-bottom: 1px solid #555555;
    }
    
    QMenuBar::item {
        background-color: transparent;
        padding: 4px 8px;
    }
    
    QMenuBar::item:selected {
        background-color: #404040;
    }
    
    QMenu {
        background-color: #3c3c3c;
        color: #ffffff;
        border: 1px solid #555555;
    }
    
    QMenu::item:selected {
        background-color: #0078d4;
        color: white;
    }
    """
    
    # Set default theme
        self.is_dark_mode = False
        self.setStyleSheet(self.light_style)

    def toggle_theme(self):
        """Toggle antara dark dan light mode"""
        self.is_dark_mode = not self.is_dark_mode
    
        if self.is_dark_mode:
            self.setStyleSheet(self.dark_style)
            # Update matplotlib style untuk dark mode
            plt.style.use('dark_background')
        
            # Update existing plots
            self.update_plot_colors_for_dark_mode()
        
        else:
            self.setStyleSheet(self.light_style)
            # Update matplotlib style untuk light mode
            plt.style.use('default')
        
            # Update existing plots
            self.update_plot_colors_for_light_mode()
    
    # Refresh canvas jika ada data
        if self.df is not None:
            try:
                # Refresh Gantt chart jika sedang ditampilkan
                if self.tab_widget.currentIndex() == 1:
                    self.update_gantt_chart()
                
                # Refresh analysis jika sedang ditampilkan
                elif self.tab_widget.currentIndex() == 2:
                    self.update_analysis()
            except:
                pass

    def update_plot_colors_for_dark_mode(self):
        """Update warna plot untuk dark mode"""
        # Update Gantt canvas
        if hasattr(self, 'gantt_canvas'):
            self.gantt_canvas.fig.patch.set_facecolor('#2b2b2b')
            if hasattr(self.gantt_canvas, 'ax') and self.gantt_canvas.ax:
                self.gantt_canvas.ax.set_facecolor('#3c3c3c')
                self.gantt_canvas.ax.tick_params(colors='white')
                self.gantt_canvas.ax.xaxis.label.set_color('white')
                self.gantt_canvas.ax.yaxis.label.set_color('white')
                self.gantt_canvas.ax.title.set_color('white')
        
        # Update Analysis canvas
        if hasattr(self, 'analysis_canvas'):
            self.analysis_canvas.fig.patch.set_facecolor('#2b2b2b')
            if hasattr(self.analysis_canvas, 'ax') and self.analysis_canvas.ax:
                self.analysis_canvas.ax.set_facecolor('#3c3c3c')
                self.analysis_canvas.ax.tick_params(colors='white')
                self.analysis_canvas.ax.xaxis.label.set_color('white')
                self.analysis_canvas.ax.yaxis.label.set_color('white')
                self.analysis_canvas.ax.title.set_color('white')

    def update_plot_colors_for_light_mode(self):
        """Update warna plot untuk light mode"""
        # Update Gantt canvas
        if hasattr(self, 'gantt_canvas'):
            self.gantt_canvas.fig.patch.set_facecolor('white')
            if hasattr(self.gantt_canvas, 'ax') and self.gantt_canvas.ax:
                self.gantt_canvas.ax.set_facecolor('white')
                self.gantt_canvas.ax.tick_params(colors='black')
                self.gantt_canvas.ax.xaxis.label.set_color('black')
                self.gantt_canvas.ax.yaxis.label.set_color('black')
                self.gantt_canvas.ax.title.set_color('black')
        
        # Update Analysis canvas
        if hasattr(self, 'analysis_canvas'):
            self.analysis_canvas.fig.patch.set_facecolor('white')
            if hasattr(self.analysis_canvas, 'ax') and self.analysis_canvas.ax:
                self.analysis_canvas.ax.set_facecolor('white')
                self.analysis_canvas.ax.tick_params(colors='black')
                self.analysis_canvas.ax.xaxis.label.set_color('black')
                self.analysis_canvas.ax.yaxis.label.set_color('black')
                self.analysis_canvas.ax.title.set_color('black')
        

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()