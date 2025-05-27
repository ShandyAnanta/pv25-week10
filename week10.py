import sys
import csv
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QFileDialog
)
from PyQt5.QtCore import Qt

class BookManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manajemen Buku")
        self.setGeometry(300, 100, 600, 400)
        self.conn = sqlite3.connect("books.db")
        self.create_table()
        self.initUI()

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            judul TEXT NOT NULL,
            pengarang TEXT NOT NULL,
            tahun INTEGER NOT NULL
        )
        """
        self.conn.execute(query)
        self.conn.commit()

    def initUI(self):
        layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setTabShape(QTabWidget.Rounded)
        self.tabs.setStyleSheet("QTabBar::tab { width: 100px; }")

        self.tab_data = QWidget()
        self.tabs.addTab(self.tab_data, "Data Buku")
        self.init_tab_data()

        self.tab_export = QWidget()
        self.tabs.addTab(self.tab_export, "Ekspor")
        self.init_tab_export()

        layout.addWidget(self.tabs)

        self.label_identity = QLabel("Nama: Tri Shandy Ananta Axell Saputra | NIM: F1D022099")
        self.label_identity.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_identity)

        self.setLayout(layout)

    def init_tab_data(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        form_layout = QVBoxLayout()
        form_layout.setAlignment(Qt.AlignCenter)

        row_judul = QHBoxLayout()
        label_judul = QLabel("Judul:")
        label_judul.setFixedWidth(70) 
        row_judul.addWidget(label_judul)
        self.input_judul = QLineEdit()
        row_judul.addWidget(self.input_judul, 3) 
        form_layout.addLayout(row_judul)

        row_pengarang = QHBoxLayout()
        label_pengarang = QLabel("Pengarang:")
        label_pengarang.setFixedWidth(70)
        row_pengarang.addWidget(label_pengarang)
        self.input_pengarang = QLineEdit()
        row_pengarang.addWidget(self.input_pengarang, 3)
        form_layout.addLayout(row_pengarang)

        row_tahun = QHBoxLayout()
        label_tahun = QLabel("Tahun:")
        label_tahun.setFixedWidth(70)
        row_tahun.addWidget(label_tahun)
        self.input_tahun = QLineEdit()
        row_tahun.addWidget(self.input_tahun, 3)
        form_layout.addLayout(row_tahun)

        self.btn_simpan = QPushButton("Simpan")
        self.btn_simpan.clicked.connect(self.save_data)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_simpan)
        btn_layout.addStretch()

        form_layout.addLayout(btn_layout)
        layout.addLayout(form_layout)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Cari judul...")
        self.search_box.textChanged.connect(self.search_data)
        layout.addWidget(self.search_box)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Judul", "Pengarang", "Tahun"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self.edit_data)
        layout.addWidget(self.table)

        self.btn_hapus = QPushButton("Hapus Data")
        self.btn_hapus.setStyleSheet("background-color: orange;")
        self.btn_hapus.clicked.connect(self.delete_data)
        layout.addWidget(self.btn_hapus, alignment=Qt.AlignLeft)

        self.tab_data.setLayout(layout)
        self.load_data()


    def init_tab_export(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        self.btn_export = QPushButton("Ekspor ke CSV")
        self.btn_export.clicked.connect(self.export_csv)
        layout.addWidget(self.btn_export)

        self.tab_export.setLayout(layout)

    def save_data(self):
        judul = self.input_judul.text().strip()
        pengarang = self.input_pengarang.text().strip()
        tahun = self.input_tahun.text().strip()

        if not judul or not pengarang or not tahun:
            QMessageBox.warning(self, "Peringatan", "Semua field harus diisi!")
            return

        if not tahun.isdigit():
            QMessageBox.warning(self, "Peringatan", "Tahun harus berupa angka!")
            return

        if hasattr(self, 'edit_id'):
            query = "UPDATE books SET judul=?, pengarang=?, tahun=? WHERE id=?"
            self.conn.execute(query, (judul, pengarang, int(tahun), self.edit_id))
            self.conn.commit()
            del self.edit_id
        else:
            query = "INSERT INTO books (judul, pengarang, tahun) VALUES (?, ?, ?)"
            self.conn.execute(query, (judul, pengarang, int(tahun)))
            self.conn.commit()

        self.clear_form()
        self.load_data()

    def load_data(self):
        self.table.setRowCount(0)
        cursor = self.conn.execute("SELECT * FROM books")
        for row_data in cursor:
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, data in enumerate(row_data):
                self.table.setItem(row, col, QTableWidgetItem(str(data)))

    def search_data(self, text):
        text = text.lower()
        self.table.setRowCount(0)
        cursor = self.conn.execute("SELECT * FROM books WHERE LOWER(judul) LIKE ?", ('%' + text + '%',))
        for row_data in cursor:
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, data in enumerate(row_data):
                self.table.setItem(row, col, QTableWidgetItem(str(data)))

    def edit_data(self, row, column):
        self.edit_id = int(self.table.item(row, 0).text())
        judul = self.table.item(row, 1).text()
        pengarang = self.table.item(row, 2).text()
        tahun = self.table.item(row, 3).text()

        self.input_judul.setText(judul)
        self.input_pengarang.setText(pengarang)
        self.input_tahun.setText(tahun)

    def delete_data(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Peringatan", "Pilih data yang ingin dihapus!")
            return

        confirm = QMessageBox.question(self, "Konfirmasi", "Yakin ingin menghapus data yang dipilih?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            for index in selected_rows:
                row = index.row()
                id_ = int(self.table.item(row, 0).text())
                self.conn.execute("DELETE FROM books WHERE id=?", (id_,))
            self.conn.commit()
            self.load_data()

    def clear_form(self):
        self.input_judul.clear()
        self.input_pengarang.clear()
        self.input_tahun.clear()

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Simpan File CSV", "", "CSV Files (*.csv)")
        if path:
            cursor = self.conn.execute("SELECT * FROM books")
            with open(path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Judul", "Pengarang", "Tahun"])
                for row in cursor:
                    writer.writerow(row)
            QMessageBox.information(self, "Sukses", f"Data berhasil diekspor ke {path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BookManager()
    window.show()
    sys.exit(app.exec_())