
import sys
import os
import subprocess
from functools import partial
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QStackedWidget, QFileDialog, QProgressBar, QSlider,
    QComboBox, QGridLayout, QTabWidget, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal, QObject
from PySide6.QtGui import QFont

from converter import convert_image
from audio_converter import convert_audio
from video_converter import convert_video
from updater import check_for_updates, download_update

# --- Worker for background tasks (file conversion) ---
class Worker(QObject):
    progress = Signal(int)
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, target, *args, **kwargs):
        super().__init__()
        self.target = target
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            self.target(*self.args, **self.kwargs, progress_callback=self.progress.emit)
            self.finished.emit("Conversão concluída com sucesso!")
        except Exception as e:
            self.error.emit(f"Erro na conversão: {e}")

# --- Workers for the update process ---
class CheckUpdateWorker(QObject):
    update_found = Signal(str, str)
    no_update_found = Signal()

    def run(self):
        is_available, latest_version, download_url = check_for_updates()
        if is_available and download_url:
            self.update_found.emit(latest_version, download_url)
        else:
            self.no_update_found.emit()

class DownloadWorker(QObject):
    progress = Signal(int)
    finished = Signal(str, str) # Emits version and downloaded file path

    def __init__(self, version, url):
        super().__init__()
        self.version = version
        self.url = url

    def run(self):
        file_path = download_update(self.url, self.progress.emit)
        if file_path:
            self.finished.emit(self.version, file_path)

class BaseConversionWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.files = []
        self.output_dir = ""

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self.title_label = QLabel("", self)
        font = QFont()
        font.setPointSize(16)
        self.title_label.setFont(font)
        layout.addWidget(self.title_label, alignment=Qt.AlignCenter)

        self.options_layout = QVBoxLayout()
        layout.addLayout(self.options_layout)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("", self)
        layout.addWidget(self.status_label, alignment=Qt.AlignCenter)

        button_layout = QHBoxLayout()
        self.select_files_button = QPushButton("Selecionar Arquivos")
        self.select_files_button.clicked.connect(self.select_files)
        button_layout.addWidget(self.select_files_button)

        self.select_folder_button = QPushButton("Selecionar Pasta")
        self.select_folder_button.clicked.connect(self.select_folder)
        button_layout.addWidget(self.select_folder_button)
        layout.addLayout(button_layout)

        self.convert_button = QPushButton("Converter")
        self.convert_button.clicked.connect(self.start_conversion)
        layout.addWidget(self.convert_button)

        self.back_button = QPushButton("Voltar")
        self.back_button.clicked.connect(self.main_window.show_dashboard)
        layout.addWidget(self.back_button)

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Selecionar Arquivos")
        if files:
            self.files = files
            self.status_label.setText(f"{len(self.files)} arquivo(s) selecionado(s).")

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecionar Pasta de Destino")
        if folder:
            self.output_dir = folder
            self.status_label.setText(f"Pasta de destino selecionada. {len(self.files)} arquivo(s) pronto(s) para converter.")

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def on_conversion_finished(self, message):
        self.status_label.setText(message)
        self.progress_bar.setVisible(False)
        self.convert_button.setEnabled(True)

    def on_conversion_error(self, message):
        self.status_label.setText(message)
        self.progress_bar.setVisible(False)
        self.convert_button.setEnabled(True)

    def start_conversion(self):
        raise NotImplementedError

class ImageConversionWidget(BaseConversionWidget):
    def __init__(self, from_format, to_format, parent=None):
        super().__init__(parent)
        self.from_format = from_format
        self.to_format = to_format
        self.title_label.setText(f"Converter {from_format} para {to_format}")

        self.quality_slider = QSlider(Qt.Horizontal)
        self.quality_slider.setRange(1, 100)
        self.quality_slider.setValue(90)
        self.options_layout.addWidget(QLabel("Qualidade:"))
        self.options_layout.addWidget(self.quality_slider)

    def start_conversion(self):
        if not self.files or not self.output_dir:
            self.status_label.setText("Por favor, selecione os arquivos e a pasta de destino.")
            return

        self.convert_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        quality = self.quality_slider.value()

        self.worker = Worker(convert_image, self.files, self.output_dir, self.to_format, quality=quality)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_conversion_finished)
        self.worker.error.connect(self.on_conversion_error)
        self.thread.started.connect(self.worker.run)
        self.thread.start()

class AudioConversionWidget(BaseConversionWidget):
    def __init__(self, from_format, to_format, parent=None):
        super().__init__(parent)
        self.from_format = from_format
        self.to_format = to_format
        self.title_label.setText(f"Converter {from_format} para {to_format}")

        self.bitrate_combo = QComboBox()
        self.bitrate_combo.addItems(["96k", "128k", "192k", "256k", "320k"])
        self.bitrate_combo.setCurrentText("192k")
        self.options_layout.addWidget(QLabel("Bitrate:"))
        self.options_layout.addWidget(self.bitrate_combo)

    def start_conversion(self):
        if not self.files or not self.output_dir:
            self.status_label.setText("Por favor, selecione os arquivos e a pasta de destino.")
            return

        self.convert_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        bitrate = self.bitrate_combo.currentText()

        self.worker = Worker(convert_audio, self.files, self.output_dir, self.to_format, bitrate=bitrate)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_conversion_finished)
        self.worker.error.connect(self.on_conversion_error)
        self.thread.started.connect(self.worker.run)
        self.thread.start()

class VideoConversionWidget(BaseConversionWidget):
    def __init__(self, from_format, to_format, parent=None):
        super().__init__(parent)
        self.from_format = from_format
        self.to_format = to_format
        self.title_label.setText(f"Converter {from_format} para {to_format}")

        self.quality_slider = QSlider(Qt.Horizontal)
        self.quality_slider.setRange(18, 28)
        self.quality_slider.setValue(23)
        self.options_layout.addWidget(QLabel("Qualidade (CRF):"))
        self.options_layout.addWidget(self.quality_slider)

    def start_conversion(self):
        if not self.files or not self.output_dir:
            self.status_label.setText("Por favor, selecione os arquivos e a pasta de destino.")
            return

        self.convert_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        quality = self.quality_slider.value()

        self.worker = Worker(convert_video, self.files, self.output_dir, self.to_format, quality=quality)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_conversion_finished)
        self.worker.error.connect(self.on_conversion_error)
        self.thread.started.connect(self.worker.run)
        self.thread.start()

class DashboardWidget(QWidget):
    def __init__(self, start_conversion_callback, check_for_updates_callback):
        super().__init__()
        main_layout = QVBoxLayout(self)

        top_layout = QHBoxLayout()
        top_layout.addStretch()
        self.update_button = QPushButton("Verificar Atualizações")
        self.update_button.clicked.connect(check_for_updates_callback)
        top_layout.addWidget(self.update_button)
        main_layout.addLayout(top_layout)

        main_layout.setAlignment(Qt.AlignCenter)

        self.tabs = QTabWidget()
        self.image_tab = self.create_image_tab(start_conversion_callback)
        self.audio_tab = self.create_audio_tab(start_conversion_callback)
        self.video_tab = self.create_video_tab(start_conversion_callback)

        self.tabs.addTab(self.image_tab, "Imagem")
        self.tabs.addTab(self.audio_tab, "Áudio")
        self.tabs.addTab(self.video_tab, "Vídeo")

        main_layout.addWidget(self.tabs)

    def create_image_tab(self, callback):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        favorites_layout = QGridLayout()
        favorites = [("JPG", "PNG"), ("PNG", "JPG"), ("WEBP", "PNG"), ("JPG", "WEBP")]

        positions = [(i, j) for i in range(2) for j in range(2)]
        for pos, (f_from, f_to) in zip(positions, favorites):
            card = QPushButton(f"{f_from} para {f_to}")
            card.setMinimumSize(150, 80)
            card.clicked.connect(partial(callback, f_from, f_to))
            favorites_layout.addWidget(card, pos[0], pos[1])

        layout.addWidget(QLabel("Favoritos:"))
        layout.addLayout(favorites_layout)
        layout.addStretch()

        other_formats_label = QLabel("Outros:")
        layout.addWidget(other_formats_label)

        other_formats_layout = QGridLayout()
        all_formats = ["WEBP", "GIF", "PNG", "JPG", "BMP"]
        all_combinations = [(f_from, f_to) for f_from in all_formats for f_to in all_formats if f_from != f_to]
        other_combinations = [c for c in all_combinations if c not in favorites]

        row, col = 0, 0
        for f_from, f_to in other_combinations:
            button = QPushButton(f"{f_from} para {f_to}")
            button.clicked.connect(partial(callback, f_from, f_to))
            other_formats_layout.addWidget(button, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1

        layout.addLayout(other_formats_layout)
        return widget

    def create_audio_tab(self, callback):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        favorites_layout = QGridLayout()
        favorites = [("MP3", "WAV"), ("WAV", "MP3"), ("FLAC", "MP3"), ("FLAC", "WAV")]

        positions = [(i, j) for i in range(2) for j in range(2)]
        for pos, (f_from, f_to) in zip(positions, favorites):
            card = QPushButton(f"{f_from} para {f_to}")
            card.setMinimumSize(150, 80)
            card.clicked.connect(partial(callback, f_from, f_to))
            favorites_layout.addWidget(card, pos[0], pos[1])

        layout.addWidget(QLabel("Favoritos:"))
        layout.addLayout(favorites_layout)
        layout.addStretch()

        other_formats_label = QLabel("Outros:")
        layout.addWidget(other_formats_label)

        other_formats_layout = QGridLayout()
        all_formats = ["MP3", "WAV", "FLAC"]
        all_combinations = [(f_from, f_to) for f_from in all_formats for f_to in all_formats if f_from != f_to]
        other_combinations = [c for c in all_combinations if c not in favorites]

        row, col = 0, 0
        for f_from, f_to in other_combinations:
            button = QPushButton(f"{f_from} para {f_to}")
            button.clicked.connect(partial(callback, f_from, f_to))
            other_formats_layout.addWidget(button, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1

        layout.addLayout(other_formats_layout)
        return widget

    def create_video_tab(self, callback):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        favorites_layout = QGridLayout()
        favorites = [("MP4", "WEBM"), ("WEBM", "MP4"), ("MKV", "MP4")]

        card = QPushButton(f"{favorites[0][0]} para {favorites[0][1]}")
        card.setMinimumSize(150, 80)
        card.clicked.connect(partial(callback, favorites[0][0], favorites[0][1]))
        favorites_layout.addWidget(card, 0, 0)

        card = QPushButton(f"{favorites[1][0]} para {favorites[1][1]}")
        card.setMinimumSize(150, 80)
        card.clicked.connect(partial(callback, favorites[1][0], favorites[1][1]))
        favorites_layout.addWidget(card, 0, 1)

        card = QPushButton(f"{favorites[2][0]} para {favorites[2][1]}")
        card.setMinimumSize(150, 80)
        card.clicked.connect(partial(callback, favorites[2][0], favorites[2][1]))
        favorites_layout.addWidget(card, 1, 0)

        layout.addWidget(QLabel("Favoritos:"))
        layout.addLayout(favorites_layout)
        layout.addStretch()

        other_formats_label = QLabel("Outros:")
        layout.addWidget(other_formats_label)

        other_formats_layout = QGridLayout()
        all_formats = ["MP4", "WEBM", "MKV", "MOV"]
        all_combinations = [(f_from, f_to) for f_from in all_formats for f_to in all_formats if f_from != f_to]
        other_combinations = [c for c in all_combinations if c not in favorites]

        row, col = 0, 0
        for f_from, f_to in other_combinations:
            button = QPushButton(f"{f_from} para {f_to}")
            button.clicked.connect(partial(callback, f_from, f_to))
            other_formats_layout.addWidget(button, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1

        layout.addLayout(other_formats_layout)
        return widget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Conversor Universal")
        self.setGeometry(100, 100, 800, 600)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.dashboard = DashboardWidget(self.start_conversion, self.check_for_updates)
        self.stacked_widget.addWidget(self.dashboard)

        self.check_for_updates(is_manual_check=False)

    def start_conversion(self, from_format, to_format):
        image_formats = ["WEBP", "GIF", "PNG", "JPG", "BMP"]
        audio_formats = ["MP3", "WAV", "FLAC"]

        if from_format.upper() in image_formats:
            self.conversion_widget = ImageConversionWidget(from_format, to_format, self)
        elif from_format.upper() in audio_formats:
            self.conversion_widget = AudioConversionWidget(from_format, to_format, self)
        else:
            self.conversion_widget = VideoConversionWidget(from_format, to_format, self)

        self.stacked_widget.addWidget(self.conversion_widget)
        self.stacked_widget.setCurrentWidget(self.conversion_widget)

    def show_dashboard(self):
        self.stacked_widget.setCurrentWidget(self.dashboard)
        if hasattr(self, 'conversion_widget'):
            self.stacked_widget.removeWidget(self.conversion_widget)
            del self.conversion_widget

    def check_for_updates(self, is_manual_check=True):
        self.update_check_thread = QThread()
        self.update_check_worker = CheckUpdateWorker()
        self.update_check_worker.moveToThread(self.update_check_thread)
        self.update_check_worker.update_found.connect(self.start_silent_download)

        if is_manual_check:
            self.update_check_worker.no_update_found.connect(self.show_no_update_dialog)

        self.update_check_thread.started.connect(self.update_check_worker.run)
        self.update_check_thread.start()

    def start_silent_download(self, version, url):
        self.download_thread = QThread()
        self.download_worker = DownloadWorker(version, url)
        self.download_worker.moveToThread(self.download_thread)
        self.download_worker.finished.connect(self.show_restart_dialog)
        # Optional: could connect progress to a status bar item
        self.download_thread.started.connect(self.download_worker.run)
        self.download_thread.start()

    def show_restart_dialog(self, version, file_path):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Atualização Pronta")
        dlg.setText(f"A nova versão ({version}) foi baixada.\n\nDeseja reiniciar agora para instalar a atualização?")
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dlg.setIcon(QMessageBox.Information)

        if dlg.exec() == QMessageBox.Yes:
            self.install_and_restart(file_path)

    def install_and_restart(self, file_path):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
            app_path = sys.executable
        else:
            base_path = os.path.dirname(__file__)
            app_path = os.path.abspath(sys.argv[0])

        installer_script = os.path.join(base_path, "install_update.py")

        subprocess.Popen([sys.executable, installer_script, file_path, app_path, str(os.getpid())])

        QApplication.instance().quit()

    def show_no_update_dialog(self):
        QMessageBox.information(self, "Sem Atualizações", "Você já está usando a versão mais recente.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
