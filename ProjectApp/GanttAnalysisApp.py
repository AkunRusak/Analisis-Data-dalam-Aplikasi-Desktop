# Import semua library yang diperlukan untuk aplikasi
import sys  # Untuk mengakses sistem operasi dan keluar dari aplikasi
import pandas as pd  # Untuk manipulasi dan analisis data dalam bentuk DataFrame
import numpy as np  # Untuk operasi matematika dan array numerik
import matplotlib.pyplot as plt  # Untuk membuat plot dan visualisasi
import matplotlib.dates as mdates  # Untuk format tanggal pada plot matplotlib
from datetime import datetime, timedelta  # Untuk manipulasi tanggal dan waktu
# Import komponen PyQt6 untuk membuat GUI
from PyQt6.QtWidgets import (QApplication, QMainWindow, QFileDialog, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QLabel, QTableView, QTabWidget, 
                             QComboBox, QMessageBox, QSplitter, QGroupBox, QFormLayout)
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex, QSize  # Core components PyQt6
from PyQt6.QtGui import QAction, QIcon, QPalette, QColor  # GUI components untuk actions dan styling
# Import untuk integrasi matplotlib dengan PyQt6
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar


class PandasModel(QAbstractTableModel):
    """Model untuk menampilkan DataFrame pandas di QTableView PyQt6"""
    
    def __init__(self, data):
        super().__init__()  # Memanggil constructor parent class
        self._data = data  # Menyimpan DataFrame sebagai data internal

    def rowCount(self, parent=QModelIndex()):
        """Mengembalikan jumlah baris dalam DataFrame"""
        return self._data.shape[0]  # shape[0] memberikan jumlah baris

    def columnCount(self, parent=QModelIndex()):
        """Mengembalikan jumlah kolom dalam DataFrame"""
        return self._data.shape[1]  # shape[1] memberikan jumlah kolom

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        """Mengembalikan data untuk ditampilkan di cell tertentu"""
        if role == Qt.ItemDataRole.DisplayRole:  # Hanya untuk role display
            # Mengambil nilai dari DataFrame berdasarkan baris dan kolom
            value = self._data.iloc[index.row(), index.column()]
            return str(value)  # Konversi ke string untuk ditampilkan
        return None  # Kembalikan None untuk role lainnya

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        """Mengembalikan data header untuk baris dan kolom"""
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:  # Header kolom
                return str(self._data.columns[section])  # Nama kolom DataFrame
            if orientation == Qt.Orientation.Vertical:  # Header baris
                return str(section + 1)  # Nomor baris (dimulai dari 1)
        return None


class GanttChartCanvas(FigureCanvas):
    """Widget untuk menampilkan Gantt Chart menggunakan matplotlib"""
    
    def __init__(self, parent=None, width=10, height=8, dpi=100):
        # Membuat figure dan axis matplotlib
        self.fig, self.ax = plt.subplots(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)  # Initialize FigureCanvas dengan figure
        self.setParent(parent)  # Set parent widget
        self.fig.tight_layout()  # Atur layout agar rapi
        
    def plot_gantt(self, df, task_col, start_col, end_col, progress_col=None):
        """Membuat Gantt chart dari DataFrame"""
        if df.empty:  # Cek apakah DataFrame kosong
            return
            
        # Konversi kolom tanggal jika belum dalam format datetime
        for col in [start_col, end_col]:
            if df[col].dtype != 'datetime64[ns]':  # Cek tipe data
                df[col] = pd.to_datetime(df[col])  # Konversi ke datetime
                
        # Urutkan DataFrame berdasarkan tanggal mulai
        df = df.sort_values(by=start_col)
        
        # Siapkan data untuk plotting
        tasks = df[task_col].tolist()  # List nama tugas
        starts = df[start_col].tolist()  # List tanggal mulai
        ends = df[end_col].tolist()  # List tanggal selesai
        
        # Hitung durasi dalam hari untuk setiap tugas
        durations = [(end - start).days + 1 for start, end in zip(starts, ends)]
        
        # Bersihkan plot sebelumnya
        self.ax.clear()
        
        # Atur posisi y-axis untuk setiap tugas
        y_positions = range(len(tasks))
        self.ax.set_yticks(y_positions)  # Set posisi tick
        self.ax.set_yticklabels(tasks)  # Set label untuk setiap tick
        
        # Buat palet warna menggunakan colormap viridis
        colors = plt.cm.viridis(np.linspace(0, 1, len(tasks)))
        
        # Plot horizontal bar untuk setiap tugas
        for i, (task, start, duration) in enumerate(zip(tasks, starts, durations)):
            # Buat horizontal bar dengan:
            # - Posisi y: i (indeks tugas)
            # - Lebar: duration (durasi dalam hari)
            # - Posisi x awal: tanggal mulai (dikonversi ke number)
            self.ax.barh(i, duration, left=mdates.date2num(start), height=0.5, 
                         color=colors[i], edgecolor='black', alpha=0.8)
                         
            # Tambahkan teks durasi di tengah bar
            self.ax.text(mdates.date2num(start) + duration/2, i, f"{duration} hari", 
                         ha='center', va='center', color='white', fontweight='bold')
        
        # Format x-axis sebagai tanggal
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        self.ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        
        # Atur batasan x-axis berdasarkan rentang tanggal
        if starts and ends:
            min_date = min(starts) - timedelta(days=1)  # Tambah buffer 1 hari
            max_date = max(ends) + timedelta(days=1)    # Tambah buffer 1 hari
            self.ax.set_xlim(min_date, max_date)
        
        # Tambahkan label dan judul
        self.ax.set_xlabel('Tanggal')
        self.ax.set_ylabel('Tugas')
        self.ax.set_title('Gantt Chart')
        
        # Rotasi label tanggal untuk keterbacaan
        plt.xticks(rotation=45)
        
        # Format grid hanya pada sumbu x
        self.ax.grid(True, axis='x', linestyle='--', alpha=0.7)
        
        self.fig.tight_layout()  # Atur layout
        self.draw()  # Refresh canvas


class AnalysisCanvas(FigureCanvas):
    """Widget untuk menampilkan visualisasi analisis data"""
    
    def __init__(self, parent=None, width=10, height=8, dpi=100):
        # Membuat figure dan axis matplotlib
        self.fig, self.ax = plt.subplots(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)  # Initialize FigureCanvas
        self.setParent(parent)  # Set parent widget
        self.fig.tight_layout()  # Atur layout

    def plot_task_duration(self, df, task_col, start_col, end_col):
        """Membuat grafik durasi tugas"""
        if df.empty:  # Cek DataFrame kosong
            return
            
        # Konversi kolom tanggal jika perlu
        for col in [start_col, end_col]:
            if df[col].dtype != 'datetime64[ns]':
                df[col] = pd.to_datetime(df[col])
        
        # Hitung durasi dalam hari dan tambahkan sebagai kolom baru
        df['duration'] = (df[end_col] - df[start_col]).dt.days + 1
        
        # Urutkan berdasarkan durasi (terpanjang ke terpendek)
        df = df.sort_values(by='duration', ascending=False)
        
        # Ambil top 10 tugas dengan durasi terpanjang
        plot_df = df.head(10)
        
        # Bersihkan plot sebelumnya
        self.ax.clear()
        
        # Plot horizontal bar chart
        bars = self.ax.barh(plot_df[task_col], plot_df['duration'], color='skyblue')
        
        # Tambahkan nilai durasi di ujung setiap bar
        for bar in bars:
            width = bar.get_width()  # Dapatkan lebar bar (nilai durasi)
            # Tambahkan text di ujung bar
            self.ax.text(width + 0.5, bar.get_y() + bar.get_height()/2, 
                         f"{int(width)} hari", va='center')
        
        # Tambahkan label dan judul
        self.ax.set_xlabel('Durasi (hari)')
        self.ax.set_ylabel('Tugas')
        self.ax.set_title('10 Tugas dengan Durasi Terpanjang')
        
        # Format grid hanya pada sumbu x
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
        
        # Plot histogram untuk tanggal mulai dan selesai
        # Menggunakan list berisi dua series data
        self.ax.hist([df[start_col], df[end_col]], 
                     label=['Tanggal Mulai', 'Tanggal Selesai'],
                     alpha=0.7, bins=10)  # 10 bins untuk distribusi
        
        # Format x-axis sebagai tanggal
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        self.ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        
        # Tambahkan label dan judul
        self.ax.set_xlabel('Tanggal')
        self.ax.set_ylabel('Jumlah Tugas')
        self.ax.set_title('Distribusi Tanggal Mulai dan Selesai')
        self.ax.legend()  # Tampilkan legend
        
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
        project_start = df[start_col].min()  # Tanggal mulai paling awal
        project_end = df[end_col].max()      # Tanggal selesai paling akhir
        
        # Buat rentang tanggal harian dari awal hingga akhir proyek
        date_range = pd.date_range(start=project_start, end=project_end)
        
        # Hitung jumlah tugas aktif per hari
        active_tasks = []
        for date in date_range:
            # Hitung berapa tugas yang aktif pada tanggal ini
            # Tugas aktif jika: tanggal_mulai <= date <= tanggal_selesai
            count = sum((df[start_col] <= date) & (df[end_col] >= date))
            active_tasks.append(count)
        
        # Bersihkan plot sebelumnya
        self.ax.clear()
        
        # Plot line chart untuk jumlah tugas aktif
        self.ax.plot(date_range, active_tasks, 'b-', linewidth=2)
        # Tambahkan area terisi di bawah garis
        self.ax.fill_between(date_range, active_tasks, alpha=0.3)
        
        # Format x-axis sebagai tanggal
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        self.ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        
        # Tandai titik dengan overlap tertinggi
        max_overlap = max(active_tasks)          # Nilai maksimum overlap
        max_index = active_tasks.index(max_overlap)  # Indeks nilai maksimum
        max_date = date_range[max_index]         # Tanggal dengan overlap maksimum
        
        # Tambahkan marker merah di titik maksimum
        self.ax.plot(max_date, max_overlap, 'ro')
        # Tambahkan annotasi dengan panah
        self.ax.annotate(f'Puncak: {max_overlap} tugas\n{max_date.strftime("%Y-%m-%d")}',
                         xy=(max_date, max_overlap),  # Posisi titik yang ditunjuk
                         xytext=(max_date + timedelta(days=2), max_overlap + 1),  # Posisi teks
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
        super().__init__()  # Memanggil constructor parent class
        
        # Properti data - untuk menyimpan DataFrame yang dimuat
        self.df = None
        
        # Setup UI dan tema
        self.setWindowTitle("Aplikasi Integrasi Gantt Chart dan Analisis Data")
        self.setGeometry(100, 100, 1200, 600)  # x, y, width, height
        self.setup_ui()      # Inisialisasi antarmuka pengguna
        self.setup_themes()  # Inisialisasi tema dark/light
        
    def setup_ui(self):
        # Buat menu bar
        self.create_menus()
        
        # Widget utama sebagai central widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Layout utama menggunakan vertical layout
        main_layout = QVBoxLayout(main_widget)
        
        # Tab widget untuk tampilan yang berbeda (Data, Gantt, Analisis)
        self.tab_widget = QTabWidget()
        
        # === TAB DATA ===
        data_tab = QWidget()
        data_layout = QVBoxLayout(data_tab)
        # Table view untuk menampilkan DataFrame
        self.table_view = QTableView()
        data_layout.addWidget(QLabel("Preview Data:"))
        data_layout.addWidget(self.table_view)
        self.tab_widget.addTab(data_tab, "Data")
        
        # === TAB GANTT CHART ===
        gantt_tab = QWidget()
        gantt_layout = QHBoxLayout(gantt_tab)  # Horizontal layout

        # Widget untuk form konfigurasi dengan ukuran terbatas
        config_widget = QWidget()
        config_widget.setMaximumWidth(200)  # Batas lebar maksimum
        config_widget.setMinimumWidth(150)  # Batas lebar minimum
        config_main_layout = QVBoxLayout(config_widget)

        # Group box untuk konfigurasi Gantt
        gantt_config = QGroupBox("Konfigurasi Gantt Chart")
        config_layout = QVBoxLayout(gantt_config)

        # ComboBox untuk pemilihan kolom tugas
        task_label = QLabel("Kolom Tugas:")
        self.task_col_combo = QComboBox()
        self.task_col_combo.setMaximumWidth(150)
        config_layout.addWidget(task_label)
        config_layout.addWidget(self.task_col_combo)

        # ComboBox untuk pemilihan kolom tanggal mulai
        start_label = QLabel("Kolom Tanggal Mulai:")
        self.start_col_combo = QComboBox()
        self.start_col_combo.setMaximumWidth(150)
        config_layout.addWidget(start_label)
        config_layout.addWidget(self.start_col_combo)

        # ComboBox untuk pemilihan kolom tanggal selesai
        end_label = QLabel("Kolom Tanggal Selesai:")
        self.end_col_combo = QComboBox()
        self.end_col_combo.setMaximumWidth(150)
        config_layout.addWidget(end_label)
        config_layout.addWidget(self.end_col_combo)

        # ComboBox untuk pemilihan kolom progress (opsional)
        progress_label = QLabel("Kolom Progress (opsional):")
        self.progress_col_combo = QComboBox()
        self.progress_col_combo.setMaximumWidth(150)
        config_layout.addWidget(progress_label)
        config_layout.addWidget(self.progress_col_combo)

        # Tambahkan sedikit jarak sebelum tombol
        config_layout.addSpacing(10)

        # Tombol untuk memperbarui Gantt chart
        update_gantt_button = QPushButton("Perbarui")
        update_gantt_button.setMaximumWidth(150)
        update_gantt_button.setMinimumHeight(35)
        update_gantt_button.setMaximumHeight(45)
        # Hubungkan tombol dengan fungsi update
        update_gantt_button.clicked.connect(self.update_gantt_chart)
        config_layout.addWidget(update_gantt_button)

        config_main_layout.addWidget(gantt_config)
        config_main_layout.addStretch()  # Mendorong form ke atas

        # Widget untuk canvas dan toolbar
        canvas_widget = QWidget()
        canvas_layout = QVBoxLayout(canvas_widget)

        # Canvas untuk Gantt Chart dengan toolbar navigasi
        self.gantt_canvas = GanttChartCanvas()
        gantt_toolbar = NavigationToolbar(self.gantt_canvas, self)

        canvas_layout.addWidget(gantt_toolbar)
        canvas_layout.addWidget(self.gantt_canvas)

        # Susun secara horizontal: form di kiri, canvas di kanan
        gantt_layout.addWidget(config_widget)      # Form di kiri
        gantt_layout.addWidget(canvas_widget, 1)   # Canvas di kanan dengan stretch

        self.tab_widget.addTab(gantt_tab, "Gantt Chart")
        
        # === TAB ANALISIS ===
        analysis_tab = QWidget()
        analysis_layout = QVBoxLayout(analysis_tab)
        
        # Form untuk konfigurasi analisis
        analysis_config = QGroupBox("Konfigurasi Analisis")
        analysis_form = QFormLayout(analysis_config)
        
        # ComboBox untuk memilih jenis analisis
        self.analysis_type_combo = QComboBox()
        self.analysis_type_combo.addItems(["Durasi Tugas", "Distribusi Timeline", "Overlap Tugas"])
        
        analysis_form.addRow("Jenis Analisis:", self.analysis_type_combo)
        
        # Tombol untuk menjalankan analisis
        update_analysis_button = QPushButton("Jalankan Analisis")
        update_analysis_button.clicked.connect(self.update_analysis)
        analysis_form.addRow(update_analysis_button)
        
        analysis_layout.addWidget(analysis_config)
        
        # Canvas untuk analisis dengan toolbar navigasi
        self.analysis_canvas = AnalysisCanvas()
        analysis_toolbar = NavigationToolbar(self.analysis_canvas, self)
        
        analysis_layout.addWidget(analysis_toolbar)
        analysis_layout.addWidget(self.analysis_canvas)
        
        self.tab_widget.addTab(analysis_tab, "Analisis Data")
        
        # Tambahkan tab widget ke layout utama
        main_layout.addWidget(self.tab_widget)

    def create_menus(self):
        """Membuat menu bar dan menu items"""
        # Menu bar utama
        menu_bar = self.menuBar()
        
        # === MENU FILE ===
        file_menu = menu_bar.addMenu("File")
        
        # Action untuk membuka file CSV
        open_action = QAction("Buka CSV", self)
        open_action.setShortcut("Ctrl+O")  # Keyboard shortcut
        open_action.triggered.connect(self.load_csv)  # Connect ke fungsi
        
        # Action untuk ekspor Gantt chart
        export_gantt_action = QAction("Ekspor Gantt Chart", self)
        export_gantt_action.triggered.connect(self.export_gantt)
        
        # Action untuk ekspor analisis
        export_analysis_action = QAction("Ekspor Analisis", self)
        export_analysis_action.triggered.connect(self.export_analysis)
        
        # Action untuk keluar dari aplikasi
        exit_action = QAction("Keluar", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        
        # Tambahkan action ke menu file
        file_menu.addAction(open_action)
        file_menu.addAction(export_gantt_action)
        file_menu.addAction(export_analysis_action)
        file_menu.addSeparator()  # Garis pemisah
        file_menu.addAction(exit_action)
        
        # === MENU BANTUAN ===
        help_menu = menu_bar.addMenu("Bantuan")
        
        # Action untuk menampilkan info aplikasi
        about_action = QAction("Tentang Aplikasi", self)
        about_action.triggered.connect(self.show_about)
        
        help_menu.addAction(about_action)

        # === MENU TAMPILAN ===
        view_menu = menu_bar.addMenu("Tampilan")

        # Action untuk toggle dark/light mode
        theme_action = QAction("Dark/Light Mode", self)
        theme_action.setShortcut("Ctrl+T")
        theme_action.triggered.connect(self.toggle_theme)

        view_menu.addAction(theme_action)
    
    def load_csv(self):
        """Memuat dan memproses file CSV"""
        # Buka dialog file untuk memilih CSV
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Pilih File CSV", "", "CSV Files (*.csv)")
        
        if file_path:  # Jika user memilih file
            try:
                # Baca file CSV menggunakan pandas
                self.df = pd.read_csv(file_path)
                
                # Tampilkan data di tabel menggunakan custom model
                model = PandasModel(self.df)
                self.table_view.setModel(model)
                
                # Perbarui combo box dengan nama kolom dari CSV
                self.update_column_combos()
                
                # Beralih ke tab data untuk menampilkan hasil
                self.tab_widget.setCurrentIndex(0)
                
                # Tampilkan pesan sukses
                QMessageBox.information(self, "Berhasil", f"File CSV berhasil dimuat: {file_path}")
            
            except Exception as e:  # Tangani error jika gagal membaca file
                QMessageBox.critical(self, "Error", f"Gagal memuat file CSV: {str(e)}")
    
    def update_column_combos(self):
        """Memperbarui combo box dengan nama kolom dari DataFrame"""
        if self.df is not None:
            columns = self.df.columns.tolist()  # Dapatkan list nama kolom
            
            # Simpan pilihan saat ini jika ada (untuk restore setelah update)
            current_task = self.task_col_combo.currentText()
            current_start = self.start_col_combo.currentText()
            current_end = self.end_col_combo.currentText()
            current_progress = self.progress_col_combo.currentText()
            
            # Kosongkan semua combo box
            self.task_col_combo.clear()
            self.start_col_combo.clear()
            self.end_col_combo.clear()
            self.progress_col_combo.clear()
            
            # Tambahkan opsi kosong untuk kolom progress (karena opsional)
            self.progress_col_combo.addItem("")
            
            # Isi combo box dengan nama kolom
            self.task_col_combo.addItems(columns)
            self.start_col_combo.addItems(columns)
            self.end_col_combo.addItems(columns)
            self.progress_col_combo.addItems(columns)
            
            # Coba kembalikan pilihan sebelumnya jika masih tersedia
            for combo, current_text in [
                (self.task_col_combo, current_task),
                (self.start_col_combo, current_start),
                (self.end_col_combo, current_end),
                (self.progress_col_combo, current_progress)
            ]:
                if current_text in columns:
                    index = combo.findText(current_text)  # Cari indeks teks
                    if index >= 0:
                        combo.setCurrentIndex(index)  # Set pilihan
            
            # Coba tebak kolom yang mungkin untuk Gantt Chart
            self.guess_gantt_columns()
    
    def guess_gantt_columns(self):
        """Menebak kolom yang mungkin untuk Gantt Chart berdasarkan nama atau tipe data"""
        if self.df is None:
            return

        # ----------------------------------------------------------------------------------------    
        # Kata kunci untuk menebak kolom berdasarkan nama
        task_keywords = ['task', 'tugas', 'aktivitas', 'kegiatan', 'nama']
        start_keywords = ['start', 'mulai', 'begin', 'awal']
        end_keywords = ['end', 'finish', 'selesai', 'akhir']
        progress_keywords = ['progress', 'kemajuan', 'persen', 'percent', '%']
        # ----------------------------------------------------------------------------------------

        # Fungsi helper untuk menemukan kolom berdasarkan kata kunci
        def find_column_by_keywords(keywords):
            for col in self.df.columns:
                col_lower = col.lower()  # Konversi ke lowercase untuk pencocokan
                # Cek apakah ada kata kunci yang terdapat dalam nama kolom
                if any(keyword in col_lower for keyword in keywords):
                    return col
            return None
        
        # Tebak kolom tugas
        task_col = find_column_by_keywords(task_keywords)
        if task_col:
            index = self.task_col_combo.findText(task_col)
            if index >= 0:
                self.task_col_combo.setCurrentIndex(index)
        
        # Cari kolom yang bisa dikonversi ke datetime (untuk tanggal)
        date_columns = []
        for col in self.df.columns:
            try:
                # Coba konversi sample data ke datetime
                pd.to_datetime(self.df[col])
                date_columns.append(col)
            except:
                pass  # Abaikan jika tidak bisa dikonversi
        
        # Jika ada minimal 2 kolom tanggal
        if len(date_columns) >= 2:
            # Prioritaskan berdasarkan kata kunci, jika tidak ada gunakan urutan
            start_col = find_column_by_keywords(start_keywords) or date_columns[0]
            end_col = find_column_by_keywords(end_keywords) or date_columns[1]
            
            # Set combo box untuk tanggal mulai
            if start_col:
                index = self.start_col_combo.findText(start_col)
                if index >= 0:
                    self.start_col_combo.setCurrentIndex(index)
            
            # Set combo box untuk tanggal selesai
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
        """Perbarui tampilan Gantt Chart berdasarkan konfigurasi yang dipilih"""
        if self.df is None:  # Cek apakah ada data yang dimuat
            QMessageBox.warning(self, "Peringatan", "Tidak ada data yang dimuat")
            return
        
        # Ambil konfigurasi dari combo box
        task_col = self.task_col_combo.currentText()      # Kolom tugas
        start_col = self.start_col_combo.currentText()    # Kolom tanggal mulai
        end_col = self.end_col_combo.currentText()        # Kolom tanggal selesai
        # Kolom progress (bisa kosong)
        progress_col = self.progress_col_combo.currentText() if self.progress_col_combo.currentText() else None
        
        # Validasi konfigurasi - pastikan kolom wajib sudah dipilih
        if not task_col or not start_col or not end_col:
            QMessageBox.warning(self, "Peringatan", "Pilih kolom untuk tugas, tanggal mulai, dan tanggal selesai")
            return
        
        try:
            # Plot Gantt Chart dengan parameter yang sudah dikonfigurasi
            self.gantt_canvas.plot_gantt(self.df, task_col, start_col, end_col, progress_col)
            
            # Beralih ke tab Gantt untuk menampilkan hasil
            self.tab_widget.setCurrentIndex(1)
            
        except Exception as e:  # Tangani error jika gagal membuat chart
            QMessageBox.critical(self, "Error", f"Gagal membuat Gantt Chart: {str(e)}")
    
    def update_analysis(self):
        """Perbarui tampilan analisis berdasarkan jenis yang dipilih"""
        if self.df is None:  # Cek apakah ada data yang dimuat
            QMessageBox.warning(self, "Peringatan", "Tidak ada data yang dimuat")
            return
        
        # Ambil konfigurasi
        analysis_type = self.analysis_type_combo.currentText()  # Jenis analisis
        task_col = self.task_col_combo.currentText()           # Kolom tugas
        start_col = self.start_col_combo.currentText()         # Kolom tanggal mulai
        end_col = self.end_col_combo.currentText()             # Kolom tanggal selesai
        
        # Validasi konfigurasi - pastikan kolom wajib sudah dipilih
        if not task_col or not start_col or not end_col:
            QMessageBox.warning(self, "Peringatan", "Pilih kolom untuk tugas, tanggal mulai, dan tanggal selesai")
            return
        
        try:
            # Jalankan analisis berdasarkan jenis yang dipilih
            if analysis_type == "Durasi Tugas":
                # Analisis durasi tugas terpanjang
                self.analysis_canvas.plot_task_duration(self.df, task_col, start_col, end_col)
            elif analysis_type == "Distribusi Timeline":
                # Analisis distribusi tanggal mulai dan selesai
                self.analysis_canvas.plot_timeline_histogram(self.df, start_col, end_col)
            elif analysis_type == "Overlap Tugas":
                # Analisis overlap/tumpang tindih tugas
                self.analysis_canvas.plot_task_overlap(self.df, task_col, start_col, end_col)
            
            # Beralih ke tab Analisis untuk menampilkan hasil
            self.tab_widget.setCurrentIndex(2)
            
        except Exception as e:  # Tangani error jika gagal melakukan analisis
            QMessageBox.critical(self, "Error", f"Gagal melakukan analisis: {str(e)}")
    
    def export_gantt(self):
        """Ekspor Gantt Chart sebagai file gambar"""
        # Cek apakah ada Gantt Chart yang ditampilkan
        if self.df is None or self.tab_widget.currentIndex() != 1:
            QMessageBox.warning(self, "Peringatan", "Tidak ada Gantt Chart yang ditampilkan")
            return
        
        # Dialog untuk memilih lokasi dan format file
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(self, "Simpan Gantt Chart", "", "PNG Files (*.png);;PDF Files (*.pdf)")
        
        if file_path:  # Jika user memilih lokasi file
            try:
                # Simpan figure matplotlib sebagai file
                # bbox_inches='tight' : memotong whitespace yang tidak perlu
                # dpi=300 : resolusi tinggi untuk kualitas cetak yang baik
                self.gantt_canvas.fig.savefig(file_path, bbox_inches='tight', dpi=300)
                QMessageBox.information(self, "Berhasil", f"Gantt Chart disimpan ke: {file_path}")
            except Exception as e:  # Tangani error jika gagal menyimpan
                QMessageBox.critical(self, "Error", f"Gagal menyimpan Gantt Chart: {str(e)}")
    
    def export_analysis(self):
        """Ekspor hasil analisis sebagai file gambar"""
        # Cek apakah ada analisis yang ditampilkan
        if self.df is None or self.tab_widget.currentIndex() != 2:
            QMessageBox.warning(self, "Peringatan", "Tidak ada analisis yang ditampilkan")
            return
        
        # Dialog untuk memilih lokasi dan format file
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(self, "Simpan Hasil Analisis", "", "PNG Files (*.png);;PDF Files (*.pdf)")
        
        if file_path:  # Jika user memilih lokasi file
            try:
                # Simpan figure matplotlib sebagai file
                self.analysis_canvas.fig.savefig(file_path, bbox_inches='tight', dpi=300)
                QMessageBox.information(self, "Berhasil", f"Hasil analisis disimpan ke: {file_path}")
            except Exception as e:  # Tangani error jika gagal menyimpan
                QMessageBox.critical(self, "Error", f"Gagal menyimpan hasil analisis: {str(e)}")
    
    def show_about(self):
        """Tampilkan dialog informasi tentang aplikasi"""
        QMessageBox.about(self, "Tentang Aplikasi", 
                         "Aplikasi Integrasi Gantt Chart dan Analisis Data\n\n"
                         "Aplikasi ini memungkinkan pengguna untuk membuat Integrasi Gantt Chart "
                         "dan melakukan analisis data dari file CSV.\n\n"
                         "Dibuat dengan Python dan PyQt6.")

    # === SISTEM DARK/LIGHT MODE ===
    def setup_themes(self):
        """Setup tema untuk aplikasi (dark dan light mode)"""
        # Style CSS untuk light mode
        self.light_style = """
    QMainWindow {
        background-color: #f5f5f5;  /* Latar belakang abu-abu terang */
        color: #333333;             /* Teks hitam */
    }
    
    QTabWidget::pane {
        border: 1px solid #c0c0c0;   /* Border abu-abu */
        background-color: #ffffff;   /* Latar belakang putih */
    }
    
    QTabWidget::tab-bar {
        alignment: center;           /* Tab di tengah */
    }
    
    QTabBar::tab {
        background-color: #e1e1e1;   /* Tab tidak aktif abu-abu terang */
        color: #333333;              /* Teks hitam */
        padding: 8px 16px;           /* Padding dalam tab */
        margin-right: 2px;           /* Jarak antar tab */
        border-top-left-radius: 4px; /* Rounded corner */
        border-top-right-radius: 4px;
    }
    
    QTabBar::tab:selected {
        background-color: #ffffff;   /* Tab aktif putih */
        border-bottom: 2px solid #0078d4; /* Garis biru di bawah tab aktif */
    }
    
    QTabBar::tab:hover {
        background-color: #d0d0d0;   /* Efek hover abu-abu */
    }
    
    QPushButton {
        background-color: #0078d4;   /* Tombol biru */
        color: white;                /* Teks putih */
        border: none;                /* Tanpa border */
        padding: 8px 16px;           /* Padding dalam tombol */
        border-radius: 4px;          /* Rounded corner */
        font-weight: bold;           /* Teks tebal */
    }
    
    QPushButton:hover {
        background-color: #106ebe;   /* Warna hover lebih gelap */
    }
    
    QPushButton:pressed {
        background-color: #005a9e;   /* Warna saat ditekan */
    }
    
    QComboBox {
        background-color: #ffffff;   /* Latar belakang putih */
        border: 1px solid #c0c0c0;   /* Border abu-abu */
        padding: 4px 8px;            /* Padding */
        border-radius: 4px;          /* Rounded corner */
        color: #333333;              /* Teks hitam */
    }
    
    QComboBox:hover {
        border-color: #0078d4;       /* Border biru saat hover */
    }
    
    QComboBox::drop-down {
        border: none;                /* Tanpa border pada dropdown */
        width: 20px;                 /* Lebar area dropdown */
    }
    
    QComboBox::down-arrow {
        image: url(down_arrow_light.png); /* Icon panah (jika ada) */
        width: 12px;
        height: 12px;
    }
    
    QTableView {
        background-color: #ffffff;              /* Latar belakang putih */
        alternate-background-color: #f8f8f8;    /* Baris bergantian abu-abu terang */
        color: #333333;                         /* Teks hitam */
        gridline-color: #d0d0d0;               /* Warna garis grid */
        selection-background-color: #0078d4;    /* Latar belakang sel terpilih */
        selection-color: white;                 /* Teks sel terpilih */
    }
    
    QHeaderView::section {
        background-color: #e1e1e1;   /* Header abu-abu terang */
        color: #333333;              /* Teks hitam */
        padding: 8px;                /* Padding header */
        border: 1px solid #c0c0c0;   /* Border header */
        font-weight: bold;           /* Teks tebal */
    }
    
    QGroupBox {
        font-weight: bold;           /* Judul group tebal */
        border: 2px solid #c0c0c0;   /* Border group */
        border-radius: 8px;          /* Rounded corner */
        margin: 8px 0px;            /* Margin atas bawah */
        padding-top: 8px;           /* Padding atas */
        color: #333333;             /* Teks hitam */
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;   /* Posisi judul */
        left: 10px;                 /* Jarak dari kiri */
        padding: 0 5px 0 5px;       /* Padding judul */
        color: #0078d4;             /* Warna judul biru */
    }
    
    QLabel {
        color: #333333;             /* Teks label hitam */
    }
    
    QMenuBar {
        background-color: #f5f5f5;   /* Latar belakang menu bar */
        color: #333333;              /* Teks hitam */
        border-bottom: 1px solid #c0c0c0; /* Border bawah */
    }
    
    QMenuBar::item {
        background-color: transparent; /* Latar belakang transparan */
        padding: 4px 8px;             /* Padding item menu */
    }
    
    QMenuBar::item:selected {
        background-color: #e1e1e1;    /* Item terpilih abu-abu terang */
    }
    
    QMenu {
        background-color: #ffffff;    /* Latar belakang menu putih */
        color: #333333;               /* Teks hitam */
        border: 1px solid #c0c0c0;    /* Border menu */
    }
    
    QMenu::item:selected {
        background-color: #0078d4;    /* Item terpilih biru */
        color: white;                 /* Teks putih */
    }
    """
    
        # Style CSS untuk dark mode
        self.dark_style = """
    QMainWindow {
        background-color: #2b2b2b;  /* Latar belakang gelap */
        color: #ffffff;             /* Teks putih */
    }
    
    QTabWidget::pane {
        border: 1px solid #555555;   /* Border abu-abu gelap */
        background-color: #3c3c3c;   /* Latar belakang abu-abu gelap */
    }
    
    QTabWidget::tab-bar {
        alignment: center;           /* Tab di tengah */
    }
    
    QTabBar::tab {
        background-color: #404040;   /* Tab tidak aktif abu-abu gelap */
        color: #ffffff;              /* Teks putih */
        padding: 8px 16px;           /* Padding dalam tab */
        margin-right: 2px;           /* Jarak antar tab */
        border-top-left-radius: 4px; /* Rounded corner */
        border-top-right-radius: 4px;
    }
    
    QTabBar::tab:selected {
        background-color: #3c3c3c;   /* Tab aktif sedikit lebih terang */
        border-bottom: 2px solid #0078d4; /* Garis biru di bawah tab aktif */
    }
    
    QTabBar::tab:hover {
        background-color: #4a4a4a;   /* Efek hover lebih terang */
    }
    
    QPushButton {
        background-color: #0078d4;   /* Tombol biru (sama seperti light mode) */
        color: white;                /* Teks putih */
        border: none;                /* Tanpa border */
        padding: 8px 16px;           /* Padding dalam tombol */
        border-radius: 4px;          /* Rounded corner */
        font-weight: bold;           /* Teks tebal */
    }
    
    QPushButton:hover {
        background-color: #106ebe;   /* Warna hover lebih gelap */
    }
    
    QPushButton:pressed {
        background-color: #005a9e;   /* Warna saat ditekan */
    }
    
    QComboBox {
        background-color: #404040;   /* Latar belakang gelap */
        border: 1px solid #555555;   /* Border abu-abu gelap */
        padding: 4px 8px;            /* Padding */
        border-radius: 4px;          /* Rounded corner */
        color: #ffffff;              /* Teks putih */
    }
    
    QComboBox:hover {
        border-color: #0078d4;       /* Border biru saat hover */
    }
    
    QComboBox::drop-down {
        border: none;                /* Tanpa border pada dropdown */
        width: 20px;                 /* Lebar area dropdown */
    }
    
    QComboBox::down-arrow {
        image: url(down_arrow_dark.png); /* Icon panah untuk dark mode */
        width: 12px;
        height: 12px;
    }
    
    QComboBox QAbstractItemView {
        background-color: #404040;            /* Latar belakang dropdown */
        color: #ffffff;                       /* Teks putih */
        selection-background-color: #0078d4;  /* Item terpilih biru */
    }
    
    QTableView {
        background-color: #3c3c3c;              /* Latar belakang gelap */
        alternate-background-color: #404040;     /* Baris bergantian sedikit terang */
        color: #ffffff;                         /* Teks putih */
        gridline-color: #555555;               /* Warna garis grid gelap */
        selection-background-color: #0078d4;    /* Latar belakang sel terpilih */
        selection-color: white;                 /* Teks sel terpilih */
    }
    
    QHeaderView::section {
        background-color: #404040;   /* Header gelap */
        color: #ffffff;              /* Teks putih */
        padding: 8px;                /* Padding header */
        border: 1px solid #555555;   /* Border header gelap */
        font-weight: bold;           /* Teks tebal */
    }
    
    QGroupBox {
        font-weight: bold;           /* Judul group tebal */
        border: 2px solid #555555;   /* Border group gelap */
        border-radius: 8px;          /* Rounded corner */
        margin: 8px 0px;            /* Margin atas bawah */
        padding-top: 8px;           /* Padding atas */
        color: #ffffff;             /* Teks putih */
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;   /* Posisi judul */
        left: 10px;                 /* Jarak dari kiri */
        padding: 0 5px 0 5px;       /* Padding judul */
        color: #0078d4;             /* Warna judul biru (tetap sama) */
    }
    
    QLabel {
        color: #ffffff;             /* Teks label putih */
    }
    
    QMenuBar {
        background-color: #2b2b2b;   /* Latar belakang menu bar gelap */
        color: #ffffff;              /* Teks putih */
        border-bottom: 1px solid #555555; /* Border bawah gelap */
    }
    
    QMenuBar::item {
        background-color: transparent; /* Latar belakang transparan */
        padding: 4px 8px;             /* Padding item menu */
    }
    
    QMenuBar::item:selected {
        background-color: #404040;    /* Item terpilih gelap */
    }
    
    QMenu {
        background-color: #3c3c3c;    /* Latar belakang menu gelap */
        color: #ffffff;               /* Teks putih */
        border: 1px solid #555555;    /* Border menu gelap */
    }
    
    QMenu::item:selected {
        background-color: #0078d4;    /* Item terpilih biru */
        color: white;                 /* Teks putih */
    }
    """
    
        # Set default theme sebagai light mode
        self.is_dark_mode = False
        self.setStyleSheet(self.light_style)

    def toggle_theme(self):
        """Toggle antara dark dan light mode"""
        self.is_dark_mode = not self.is_dark_mode  # Flip status mode
    
        if self.is_dark_mode:
            # Beralih ke dark mode
            self.setStyleSheet(self.dark_style)
            # Update matplotlib style untuk dark mode
            plt.style.use('dark_background')
        
            # Update existing plots untuk dark mode
            self.update_plot_colors_for_dark_mode()
        
        else:
            # Beralih ke light mode
            self.setStyleSheet(self.light_style)
            # Update matplotlib style untuk light mode
            plt.style.use('default')
        
            # Update existing plots untuk light mode
            self.update_plot_colors_for_light_mode()
    
        # Refresh canvas jika ada data yang sedang ditampilkan
        if self.df is not None:
            try:
                # Refresh Gantt chart jika sedang ditampilkan (tab index 1)
                if self.tab_widget.currentIndex() == 1:
                    self.update_gantt_chart()
                
                # Refresh analysis jika sedang ditampilkan (tab index 2)
                elif self.tab_widget.currentIndex() == 2:
                    self.update_analysis()
            except:
                pass  # Abaikan error jika terjadi masalah saat refresh

    def update_plot_colors_for_dark_mode(self):
        """Update warna plot untuk dark mode"""
        # Update Gantt canvas
        if hasattr(self, 'gantt_canvas'):
            self.gantt_canvas.fig.patch.set_facecolor('#2b2b2b')  # Latar belakang figure
            if hasattr(self.gantt_canvas, 'ax') and self.gantt_canvas.ax:
                self.gantt_canvas.ax.set_facecolor('#3c3c3c')     # Latar belakang plot
                self.gantt_canvas.ax.tick_params(colors='white')   # Warna tick marks
                self.gantt_canvas.ax.xaxis.label.set_color('white') # Label sumbu x
                self.gantt_canvas.ax.yaxis.label.set_color('white') # Label sumbu y
                self.gantt_canvas.ax.title.set_color('white')      # Warna judul
        
        # Update Analysis canvas
        if hasattr(self, 'analysis_canvas'):
            self.analysis_canvas.fig.patch.set_facecolor('#2b2b2b')  # Latar belakang figure
            if hasattr(self.analysis_canvas, 'ax') and self.analysis_canvas.ax:
                self.analysis_canvas.ax.set_facecolor('#3c3c3c')     # Latar belakang plot
                self.analysis_canvas.ax.tick_params(colors='white')   # Warna tick marks
                self.analysis_canvas.ax.xaxis.label.set_color('white') # Label sumbu x
                self.analysis_canvas.ax.yaxis.label.set_color('white') # Label sumbu y
                self.analysis_canvas.ax.title.set_color('white')      # Warna judul

    def update_plot_colors_for_light_mode(self):
        """Update warna plot untuk light mode"""
        # Update Gantt canvas
        if hasattr(self, 'gantt_canvas'):
            self.gantt_canvas.fig.patch.set_facecolor('white')    # Latar belakang figure putih
            if hasattr(self.gantt_canvas, 'ax') and self.gantt_canvas.ax:
                self.gantt_canvas.ax.set_facecolor('white')       # Latar belakang plot putih
                self.gantt_canvas.ax.tick_params(colors='black')   # Warna tick marks hitam
                self.gantt_canvas.ax.xaxis.label.set_color('black') # Label sumbu x hitam
                self.gantt_canvas.ax.yaxis.label.set_color('black') # Label sumbu y hitam
                self.gantt_canvas.ax.title.set_color('black')      # Warna judul hitam
        
        # Update Analysis canvas
        if hasattr(self, 'analysis_canvas'):
            self.analysis_canvas.fig.patch.set_facecolor('white')    # Latar belakang figure putih
            if hasattr(self.analysis_canvas, 'ax') and self.analysis_canvas.ax:
                self.analysis_canvas.ax.set_facecolor('white')       # Latar belakang plot putih
                self.analysis_canvas.ax.tick_params(colors='black')   # Warna tick marks hitam
                self.analysis_canvas.ax.xaxis.label.set_color('black') # Label sumbu x hitam
                self.analysis_canvas.ax.yaxis.label.set_color('black') # Label sumbu y hitam
                self.analysis_canvas.ax.title.set_color('black')      # Warna judul hitam
        

def main():
    """Fungsi utama untuk menjalankan aplikasi"""
    # Buat instance QApplication (diperlukan untuk semua aplikasi PyQt6)
    app = QApplication(sys.argv)
    
    # Buat instance jendela utama
    window = MainWindow()
    
    # Tampilkan jendela
    window.show()
    
    # Jalankan event loop aplikasi dan keluar dengan status code yang dikembalikan
    sys.exit(app.exec())


# Entry point program - hanya dijalankan jika file ini dieksekusi langsung
if __name__ == "__main__":
    main()