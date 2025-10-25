import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Conversor de Mídia Universal")
        self.resize(800, 600)

        # Define o widget central e o layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Título
        title_label = QLabel("Selecione os formatos de conversão:")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Listas de formatos
        image_formats = ["WEBP", "GIF", "PNG", "JPG", "BMP"]
        audio_formats = ["MP3", "WAV", "FLAC"]
        video_formats_from = ["MP4", "MKV", "MOV"]
        video_formats_to = ["MP4", "WEBM"]

        all_from_formats = image_formats + audio_formats + video_formats_from
        all_to_formats = image_formats + audio_formats + video_formats_to

        # Layout dos menus suspensos
        dropdown_layout = QHBoxLayout()
        self.from_dropdown = QComboBox()
        self.from_dropdown.addItems(all_from_formats)

        self.to_dropdown = QComboBox()
        self.to_dropdown.addItems(all_to_formats)

        dropdown_layout.addWidget(self.from_dropdown)
        dropdown_layout.addWidget(QLabel("para"))
        dropdown_layout.addWidget(self.to_dropdown)

        main_layout.addLayout(dropdown_layout)

        # Botão de conversão
        self.start_button = QPushButton("Iniciar Conversão")
        self.start_button.setMinimumHeight(40)
        main_layout.addWidget(self.start_button)

        # Conectar sinal (ainda sem ação)
        self.start_button.clicked.connect(self.start_conversion)

    def start_conversion(self):
        # A funcionalidade será implementada nas próximas etapas
        from_format = self.from_dropdown.currentText()
        to_format = self.to_dropdown.currentText()
        print(f"Modo de conversão selecionado: {from_format} para {to_format}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
