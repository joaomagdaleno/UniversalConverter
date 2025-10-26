import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QComboBox, QPushButton,
                               QStackedWidget, QSlider, QLineEdit, QCheckBox,
                               QFrame, QFileDialog, QProgressBar)
from PySide6.QtCore import Qt, QThread, Signal
from converter import convert_image
from audio_converter import convert_audio
from video_converter import convert_video

class DashboardWidget(QWidget):
    def __init__(self, start_conversion_callback):
        super().__init__()
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        title_label = QLabel("Selecione os formatos de conversão:")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title_label)

        self.image_formats = ["WEBP", "GIF", "PNG", "JPG", "BMP"]
        self.audio_formats = ["MP3", "WAV", "FLAC"]
        self.video_formats_from = ["MP4", "MKV", "MOV"]
        self.video_formats_to = ["MP4", "WEBM"]

        all_from_formats = self.image_formats + self.audio_formats + self.video_formats_from
        all_to_formats = self.image_formats + self.audio_formats + self.video_formats_to

        dropdown_layout = QHBoxLayout()
        self.from_dropdown = QComboBox()
        self.from_dropdown.addItems(all_from_formats)

        self.to_dropdown = QComboBox()
        self.to_dropdown.addItems(all_to_formats)

        dropdown_layout.addWidget(self.from_dropdown)
        dropdown_layout.addWidget(QLabel("para"))
        dropdown_layout.addWidget(self.to_dropdown)

        main_layout.addLayout(dropdown_layout)

        self.start_button = QPushButton("Iniciar Conversão")
        self.start_button.setMinimumHeight(40)
        main_layout.addWidget(self.start_button)

        self.start_button.clicked.connect(lambda: start_conversion_callback(
            self.from_dropdown.currentText(),
            self.to_dropdown.currentText()
        ))

class Worker(QThread):
    progress = Signal(int, int)
    finished = Signal()

    def __init__(self, conversion_function, files, output_dir, to_format, settings):
        super().__init__()
        self.conversion_function = conversion_function
        self.files = files
        self.output_dir = output_dir
        self.to_format = to_format
        self.settings = settings

    def run(self):
        total = len(self.files)
        for i, file_path in enumerate(self.files):
            self.conversion_function(file_path, self.output_dir, self.to_format, self.settings)
            self.progress.emit(i + 1, total)
        self.finished.emit()

class ImageConversionWidget(QWidget):
    def __init__(self, back_callback):
        super().__init__()
        self.input_paths = []
        self.setAcceptDrops(True)

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        self.title = QLabel()
        self.title.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(self.title)

        drop_area = QLabel("Arraste e solte os arquivos aqui ou clique para selecionar")
        drop_area.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        drop_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_area.setMinimumHeight(200)
        drop_area.mousePressEvent = self.open_file_dialog
        main_layout.addWidget(drop_area)

        self.selected_files_label = QLabel("Nenhum arquivo selecionado.")
        main_layout.addWidget(self.selected_files_label)

        # Image settings
        settings_layout = QVBoxLayout()
        settings_layout.addWidget(QLabel("Qualidade"))
        self.quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.quality_slider.setRange(1, 100)
        self.quality_slider.setValue(95)
        settings_layout.addWidget(self.quality_slider)

        size_layout = QHBoxLayout()
        self.width_input = QLineEdit()
        self.width_input.setPlaceholderText("Largura")
        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("Altura")
        size_layout.addWidget(self.width_input)
        size_layout.addWidget(self.height_input)
        settings_layout.addLayout(size_layout)

        self.aspect_ratio_checkbox = QCheckBox("Manter proporção")
        self.aspect_ratio_checkbox.setChecked(True)
        settings_layout.addWidget(self.aspect_ratio_checkbox)

        main_layout.addLayout(settings_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_label = QLabel()
        self.status_label.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.status_label)

        # Action buttons
        button_layout = QHBoxLayout()
        self.convert_button = QPushButton("Converter")
        self.convert_button.setMinimumHeight(40)
        self.back_button = QPushButton("Voltar")
        self.back_button.setMinimumHeight(40)
        button_layout.addWidget(self.convert_button)
        button_layout.addWidget(self.back_button)
        main_layout.addLayout(button_layout)

        self.back_button.clicked.connect(back_callback)
        self.convert_button.clicked.connect(self.start_conversion)

    def open_file_dialog(self, event):
        files, _ = QFileDialog.getOpenFileNames(self, "Selecionar Arquivos")
        if files:
            self.input_paths.extend(files)
            self.update_selected_files_label()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        for url in urls:
            if url.isLocalFile():
                self.input_paths.append(url.toLocalFile())
        self.update_selected_files_label()

    def update_selected_files_label(self):
        self.selected_files_label.setText(f"{len(self.input_paths)} arquivo(s) selecionado(s).")

    def set_conversion_mode(self, from_format, to_format):
        self.title.setText(f"Conversão: {from_format} para {to_format}")
        self.input_paths = []
        self.update_selected_files_label()

    def start_conversion(self):
        if not self.input_paths:
            return

        output_dir = QFileDialog.getExistingDirectory(self, "Selecionar Pasta de Saída")
        if not output_dir:
            return

        settings = {
            'quality': self.quality_slider.value(),
            'width': self.width_input.text(),
            'height': self.height_input.text(),
            'keep_aspect_ratio': self.aspect_ratio_checkbox.isChecked(),
        }

        title_text = self.title.text()
        to_format = title_text.split(" para ")[-1]

        self.worker = Worker(convert_image, self.input_paths, output_dir, to_format, settings)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.conversion_finished)

        self.progress_bar.setVisible(True)
        self.status_label.setVisible(True)
        self.status_label.setText("Iniciando conversão...")
        self.worker.start()

    def update_progress(self, current, total):
        self.progress_bar.setValue(int((current / total) * 100))
        self.status_label.setText(f"Convertendo: {current}/{total}")

    def conversion_finished(self):
        self.status_label.setText("Conversão concluída!")
        self.progress_bar.setVisible(False)
        self.input_paths = []
        self.update_selected_files_label()

class AudioConversionWidget(QWidget):
    def __init__(self, back_callback):
        super().__init__()
        self.input_paths = []
        self.setAcceptDrops(True)

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        self.title = QLabel()
        self.title.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(self.title)

        drop_area = QLabel("Arraste e solte os arquivos aqui ou clique para selecionar")
        drop_area.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        drop_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_area.setMinimumHeight(200)
        drop_area.mousePressEvent = self.open_file_dialog
        main_layout.addWidget(drop_area)

        self.selected_files_label = QLabel("Nenhum arquivo selecionado.")
        main_layout.addWidget(self.selected_files_label)

        # Audio settings
        settings_layout = QVBoxLayout()
        settings_layout.addWidget(QLabel("Bitrate (kbps)"))
        self.bitrate_combo = QComboBox()
        self.bitrate_combo.addItems(["96", "128", "192", "256", "320"])
        self.bitrate_combo.setCurrentText("192")
        settings_layout.addWidget(self.bitrate_combo)
        main_layout.addLayout(settings_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_label = QLabel()
        self.status_label.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.status_label)

        # Action buttons
        button_layout = QHBoxLayout()
        self.convert_button = QPushButton("Converter")
        self.convert_button.setMinimumHeight(40)
        self.back_button = QPushButton("Voltar")
        self.back_button.setMinimumHeight(40)
        button_layout.addWidget(self.convert_button)
        button_layout.addWidget(self.back_button)
        main_layout.addLayout(button_layout)

        self.back_button.clicked.connect(back_callback)
        self.convert_button.clicked.connect(self.start_conversion)

    def open_file_dialog(self, event):
        files, _ = QFileDialog.getOpenFileNames(self, "Selecionar Arquivos")
        if files:
            self.input_paths.extend(files)
            self.update_selected_files_label()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls(): event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        for url in urls:
            if url.isLocalFile():
                self.input_paths.append(url.toLocalFile())
        self.update_selected_files_label()

    def update_selected_files_label(self):
        self.selected_files_label.setText(f"{len(self.input_paths)} arquivo(s) selecionado(s).")

    def set_conversion_mode(self, from_format, to_format):
        self.title.setText(f"Conversão: {from_format} para {to_format}")
        self.input_paths = []
        self.update_selected_files_label()

    def start_conversion(self):
        if not self.input_paths:
            return

        output_dir = QFileDialog.getExistingDirectory(self, "Selecionar Pasta de Saída")
        if not output_dir:
            return

        settings = {
            'bitrate': self.bitrate_combo.currentText(),
        }

        title_text = self.title.text()
        to_format = title_text.split(" para ")[-1]

        self.worker = Worker(convert_audio, self.input_paths, output_dir, to_format, settings)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.conversion_finished)

        self.progress_bar.setVisible(True)
        self.status_label.setVisible(True)
        self.status_label.setText("Iniciando conversão...")
        self.worker.start()

    def update_progress(self, current, total):
        self.progress_bar.setValue(int((current / total) * 100))
        self.status_label.setText(f"Convertendo: {current}/{total}")

    def conversion_finished(self):
        self.status_label.setText("Conversão concluída!")
        self.progress_bar.setVisible(False)
        self.input_paths = []
        self.update_selected_files_label()

class VideoConversionWidget(QWidget):
    def __init__(self, back_callback):
        super().__init__()
        self.input_paths = []
        self.setAcceptDrops(True)

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        self.title = QLabel()
        self.title.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(self.title)

        drop_area = QLabel("Arraste e solte os arquivos aqui ou clique para selecionar")
        drop_area.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        drop_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_area.setMinimumHeight(200)
        drop_area.mousePressEvent = self.open_file_dialog
        main_layout.addWidget(drop_area)

        self.selected_files_label = QLabel("Nenhum arquivo selecionado.")
        main_layout.addWidget(self.selected_files_label)

        # Video settings
        settings_layout = QVBoxLayout()
        settings_layout.addWidget(QLabel("Resolução"))
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["Manter original", "1080p", "720p", "480p"])
        settings_layout.addWidget(self.resolution_combo)

        settings_layout.addWidget(QLabel("Qualidade"))
        self.quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.quality_slider.setRange(0, 2)
        self.quality_slider.setValue(1)
        settings_layout.addWidget(self.quality_slider)
        main_layout.addLayout(settings_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_label = QLabel()
        self.status_label.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.status_label)

        # Action buttons
        button_layout = QHBoxLayout()
        self.convert_button = QPushButton("Converter")
        self.convert_button.setMinimumHeight(40)
        self.back_button = QPushButton("Voltar")
        self.back_button.setMinimumHeight(40)
        button_layout.addWidget(self.convert_button)
        button_layout.addWidget(self.back_button)
        main_layout.addLayout(button_layout)

        self.back_button.clicked.connect(back_callback)
        self.convert_button.clicked.connect(self.start_conversion)

    def open_file_dialog(self, event):
        files, _ = QFileDialog.getOpenFileNames(self, "Selecionar Arquivos")
        if files:
            self.input_paths.extend(files)
            self.update_selected_files_label()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls(): event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        for url in urls:
            if url.isLocalFile():
                self.input_paths.append(url.toLocalFile())
        self.update_selected_files_label()

    def update_selected_files_label(self):
        self.selected_files_label.setText(f"{len(self.input_paths)} arquivo(s) selecionado(s).")

    def set_conversion_mode(self, from_format, to_format):
        self.title.setText(f"Conversão: {from_format} para {to_format}")
        self.input_paths = []
        self.update_selected_files_label()

    def start_conversion(self):
        if not self.input_paths:
            return

        output_dir = QFileDialog.getExistingDirectory(self, "Selecionar Pasta de Saída")
        if not output_dir:
            return

        quality_map = {0: "Baixa", 1: "Média", 2: "Alta"}
        settings = {
            'resolution': self.resolution_combo.currentText(),
            'quality': quality_map[self.quality_slider.value()],
        }

        title_text = self.title.text()
        to_format = title_text.split(" para ")[-1]

        self.worker = Worker(convert_video, self.input_paths, output_dir, to_format, settings)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.conversion_finished)

        self.progress_bar.setVisible(True)
        self.status_label.setVisible(True)
        self.status_label.setText("Iniciando conversão...")
        self.worker.start()

    def update_progress(self, current, total):
        self.progress_bar.setValue(int((current / total) * 100))
        self.status_label.setText(f"Convertendo: {current}/{total}")

    def conversion_finished(self):
        self.status_label.setText("Conversão concluída!")
        self.progress_bar.setVisible(False)
        self.input_paths = []
        self.update_selected_files_label()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Conversor de Mídia Universal")
        self.resize(800, 600)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.dashboard = DashboardWidget(self.navigate_to_conversion)
        self.image_conversion_screen = ImageConversionWidget(self.go_to_dashboard)
        self.audio_conversion_screen = AudioConversionWidget(self.go_to_dashboard)
        self.video_conversion_screen = VideoConversionWidget(self.go_to_dashboard)

        self.stacked_widget.addWidget(self.dashboard)
        self.stacked_widget.addWidget(self.image_conversion_screen)
        self.stacked_widget.addWidget(self.audio_conversion_screen)
        self.stacked_widget.addWidget(self.video_conversion_screen)

    def navigate_to_conversion(self, from_format, to_format):
        is_image_conversion = from_format in self.dashboard.image_formats and to_format in self.dashboard.image_formats
        is_audio_conversion = from_format in self.dashboard.audio_formats and to_format in self.dashboard.audio_formats
        is_video_conversion = from_format in self.dashboard.video_formats_from and to_format in self.dashboard.video_formats_to

        if is_image_conversion:
            self.image_conversion_screen.set_conversion_mode(from_format, to_format)
            self.stacked_widget.setCurrentWidget(self.image_conversion_screen)
        elif is_audio_conversion:
            self.audio_conversion_screen.set_conversion_mode(from_format, to_format)
            self.stacked_widget.setCurrentWidget(self.audio_conversion_screen)
        elif is_video_conversion:
            self.video_conversion_screen.set_conversion_mode(from_format, to_format)
            self.stacked_widget.setCurrentWidget(self.video_conversion_screen)
        else:
            print(f"Navegação para {from_format} para {to_format} ainda não implementada ou inválida.")

    def go_to_dashboard(self):
        self.stacked_widget.setCurrentWidget(self.dashboard)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
