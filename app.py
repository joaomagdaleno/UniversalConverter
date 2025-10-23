import flet as ft
import os
import threading
import requests
import subprocess
import sys
import tempfile
import zipfile
from packaging.version import parse as parse_version

# --- Constants ---
REPO_NAME = "joaomagdaleno/UniversalConverter"
VERSION_FILE = "VERSION.txt"

# --- Update Manager ---
class UpdateManager:
    def __init__(self, page: ft.Page):
        self.page = page
        self.current_version = self.get_current_version()
        self.repo_url = f"https://api.github.com/repos/{REPO_NAME}/releases/latest"

        # Dialogs for update flow
        self.update_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Atualização Disponível"),
            content=ft.Text(""),  # Will be filled with the new version info
            actions=[
                ft.TextButton("Agora não", on_click=self.close_dialog),
                ft.FilledButton("Atualizar", on_click=self.start_download),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.progress_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Baixando Atualização..."),
            content=ft.Column([
                ft.Text("Por favor, aguarde."),
                ft.ProgressBar(width=400, value=None) # Indeterminate progress
            ], tight=True, spacing=10),
        )
        self.restart_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Atualização Pronta"),
            content=ft.Text("A nova versão está pronta. O aplicativo será fechado para iniciar o instalador."),
            actions=[
                ft.FilledButton("OK", on_click=self.close_and_launch_updater),
            ],
        )

    def get_current_version(self):
        try:
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            version_path = os.path.join(base_path, VERSION_FILE)
            with open(version_path, 'r') as f:
                return f.read().strip()
        except FileNotFoundError:
            return "0.0.0"

    def check_for_updates_thread(self):
        if not self.current_version or self.current_version == "0.0.0":
            return

        try:
            response = requests.get(self.repo_url, timeout=10)
            response.raise_for_status()
            latest_release = response.json()
            latest_version_str = latest_release.get("tag_name", "").lstrip('v')

            if not latest_version_str:
                return

            current_v = parse_version(self.current_version)
            latest_v = parse_version(latest_version_str)

            if latest_v > current_v:
                assets = latest_release.get("assets", [])
                zip_asset = next((asset for asset in assets if asset['name'].endswith('.zip')), None)
                if zip_asset:
                    self.latest_version_info = {
                        "version": latest_version_str,
                        "url": zip_asset['browser_download_url'],
                        "name": zip_asset['name']
                    }
                    self.page.run_threadsafe(self.show_update_dialog)

        except (requests.RequestException, ValueError) as e:
            print(f"Update check failed: {e}")

    def show_update_dialog(self):
        self.update_dialog.content.value = f"Uma nova versão ({self.latest_version_info['version']}) está disponível. Deseja baixar e instalar?"
        self.page.dialog = self.update_dialog
        self.update_dialog.open = True
        self.page.update()

    def close_dialog(self, e):
        self.page.dialog.open = False
        self.page.update()

    def start_download(self, e):
        self.close_dialog(e)
        self.page.dialog = self.progress_dialog
        self.progress_dialog.open = True
        self.page.update()

        download_thread = threading.Thread(target=self.download_and_install_thread, daemon=True)
        download_thread.start()

    def download_and_install_thread(self):
        try:
            url = self.latest_version_info['url']
            file_name = self.latest_version_info['name']
            temp_dir = tempfile.gettempdir()
            zip_path = os.path.join(temp_dir, file_name)
            extract_path = os.path.join(temp_dir, "UniversalConverterUpdate")

            # Download the zip file
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(zip_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

            # Extract the zip file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)

            # Find the executable
            executable_path = None
            for root, _, files in os.walk(extract_path):
                for file in files:
                    if file.lower() == "universalconverter.exe":
                        executable_path = os.path.join(root, file)
                        break
                if executable_path:
                    break

            if executable_path:
                self.updater_exe_path = executable_path
                self.page.run_threadsafe(self.show_restart_dialog)
            else:
                 self.page.run_threadsafe(self.show_download_error)

        except (requests.RequestException, zipfile.BadZipFile) as e:
            print(f"Download/Extraction failed: {e}")
            self.page.run_threadsafe(self.show_download_error)

    def show_restart_dialog(self):
        self.progress_dialog.open = False
        self.page.dialog = self.restart_dialog
        self.restart_dialog.open = True
        self.page.update()

    def close_and_launch_updater(self, e):
        # This will run the new executable and close the current one
        subprocess.Popen([self.updater_exe_path])
        self.page.window_close()

    def show_download_error(self):
        self.progress_dialog.title = ft.Text("Erro na Atualização")
        self.progress_dialog.content = ft.Text("Não foi possível baixar ou extrair a nova versão.")
        # No actions, user must close the dialog manually or you can add a button
        self.page.update()


# --- Main App ---
from converter import convert_image

class AppState:
    def __init__(self):
        self.input_paths = []
        self.output_dir = ""
        self.conversion_mode = None

def main(page: ft.Page):
    page.title = "Conversor de Mídia Universal"
    page.window_width = 800
    page.window_height = 600
    page.window_min_width = 700
    page.window_min_height = 500
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.START
    state = AppState()
    main_content_area = ft.Column(expand=True, spacing=20)

    def show_view(mode):
        main_content_area.controls.clear()
        if mode == "dashboard":
            main_content_area.controls.append(create_dashboard_view())
        else:
            main_content_area.controls.append(create_conversion_view(mode))
        page.update()

    def create_dashboard_view():
        from_format = ft.Dropdown(
            label="Converter de",
            options=[
                ft.dropdown.Option("WEBP"),
                ft.dropdown.Option("GIF"),
                ft.dropdown.Option("PNG"),
                ft.dropdown.Option("JPG"),
                ft.dropdown.Option("BMP"),
            ],
            width=200,
        )
        to_format = ft.Dropdown(
            label="Para",
            options=[
                ft.dropdown.Option("WEBP"),
                ft.dropdown.Option("GIF"),
                ft.dropdown.Option("PNG"),
                ft.dropdown.Option("JPG"),
                ft.dropdown.Option("BMP"),
            ],
            width=200,
        )

        def start_conversion_setup(e):
            if from_format.value and to_format.value:
                mode = f"{from_format.value}_to_{to_format.value}"
                show_view(mode)

        return ft.Column(
            controls=[
                ft.Text("Selecione o Formato da Conversão", size=20, weight=ft.FontWeight.BOLD),
                ft.Row(
                    controls=[
                        from_format,
                        ft.Icon(ft.Icons.SWAP_HORIZ),
                        to_format,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,
                ),
                ft.ElevatedButton("Iniciar", on_click=start_conversion_setup, height=50, width=200),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=30,
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
        )

    def create_conversion_view(mode):
        state.conversion_mode = mode
        from_format, to_format = mode.split('_to_')
        title = f"Conversor {from_format} para {to_format}"

        # Define allowed extensions, treating JPG and JPEG as the same
        allowed_extensions = [from_format.lower()]
        if from_format == "JPG":
            allowed_extensions.append("jpeg")

        selected_files_text = ft.Text("Nenhum arquivo selecionado")
        output_dir_text = ft.Text("Nenhuma pasta selecionada")
        progress_bar = ft.ProgressBar(width=400, value=0)
        status_label = ft.Text("")
        convert_button = ft.ElevatedButton("Converter", icon=ft.Icons.SWAP_HORIZ)
        settings_controls = create_settings_controls(mode, page)

        def on_files_selected(e: ft.FilePickerResultEvent):
            if e.files:
                state.input_paths = [f.path for f in e.files]
                selected_files_text.value = f"{len(state.input_paths)} arquivo(s) selecionado(s)"
            else:
                state.input_paths = []
                selected_files_text.value = "Nenhum arquivo selecionado"
            page.update()

        def on_output_dir_selected(e: ft.FilePickerResultEvent):
            if e.path:
                state.output_dir = e.path
                output_dir_text.value = f"Destino: {state.output_dir}"
            else:
                state.output_dir = ""
                output_dir_text.value = "Nenhuma pasta selecionada"
            page.update()

        file_picker = ft.FilePicker(on_result=on_files_selected)
        output_dir_picker = ft.FilePicker(on_result=on_output_dir_selected)
        page.overlay.extend([file_picker, output_dir_picker])

        def run_conversion_thread():
            from_format, to_format = state.conversion_mode.split('_to_')
            total_files = len(state.input_paths)
            converted_count = 0

            for i, file_path in enumerate(state.input_paths):
                settings = {}
                if state.conversion_mode == 'WEBP_to_GIF':
                    settings['frame_rate'] = int(settings_controls['fps'].value)
                    settings['loop'] = settings_controls['loop'].value
                elif state.conversion_mode == 'GIF_to_WEBP':
                    settings['lossless'] = settings_controls['lossless'].value
                    settings['quality'] = int(settings_controls['quality'].value)

                success = convert_image(file_path, state.output_dir, to_format, settings)

                if success:
                    converted_count += 1

                progress_value = (i + 1) / total_files
                page.run_threadsafe(update_progress, progress_value)

            page.run_threadsafe(finish_conversion, converted_count, total_files)

        def start_conversion(e):
            if not state.input_paths or not state.output_dir:
                status_label.value = "Selecione arquivos e uma pasta de destino."
                page.update()
                return
            convert_button.disabled = True
            status_label.value = "Convertendo..."
            progress_bar.value = 0
            page.update()
            thread = threading.Thread(target=run_conversion_thread, daemon=True)
            thread.start()

        def update_progress(value):
            progress_bar.value = value
            page.update()

        def finish_conversion(count, total):
            convert_button.disabled = False
            status_label.value = f"{count} de {total} arquivo(s) convertido(s) com sucesso!"
            progress_bar.value = 1.0
            page.update()

        convert_button.on_click = start_conversion

        return ft.Column([
            ft.Text(title, size=20, weight=ft.FontWeight.BOLD),
            ft.Container(
                ft.Column([
                    ft.Text("1. Selecione os Arquivos", weight=ft.FontWeight.BOLD),
                    ft.Row([
                        ft.ElevatedButton("Selecionar Arquivos", icon=ft.Icons.UPLOAD_FILE, on_click=lambda _: file_picker.pick_files(allow_multiple=True, allowed_extensions=allowed_extensions)),
                    ]),
                    selected_files_text
                ]),
                padding=10, border=ft.border.all(1, ft.Colors.OUTLINE), border_radius=ft.border_radius.all(5)
            ),
            ft.Container(
                ft.Column([
                    ft.Text("2. Escolha o Destino", weight=ft.FontWeight.BOLD),
                    ft.Row([
                        ft.ElevatedButton("Escolher Pasta de Destino", icon=ft.Icons.FOLDER_SPECIAL, on_click=lambda _: output_dir_picker.get_directory_path()),
                    ]),
                    output_dir_text
                ]),
                padding=10, border=ft.border.all(1, ft.Colors.OUTLINE), border_radius=ft.border_radius.all(5)
            ),
            ft.Container(
                ft.Column(settings_controls["controls"]),
                padding=10, border=ft.border.all(1, ft.Colors.OUTLINE), border_radius=ft.border_radius.all(5)
            ),
            ft.Container(
                ft.Column([
                    ft.Text("4. Execute a Conversão", weight=ft.FontWeight.BOLD),
                    ft.Row([
                        convert_button,
                    ]),
                    progress_bar,
                    status_label
                ]),
                padding=10, border=ft.border.all(1, ft.Colors.OUTLINE), border_radius=ft.border_radius.all(5)
            ),
            ft.ElevatedButton("Voltar para o Dashboard", on_click=lambda _: show_view("dashboard"))
        ], spacing=15)

    def create_settings_controls(mode, page_ref):
        if mode == 'WEBP_to_GIF':
            fps_input = ft.TextField(label="Taxa de Quadros (FPS)", value="10", width=150)
            loop_checkbox = ft.Checkbox(label="GIF em Loop (Repetir Infinitamente)", value=True)
            return {
                "controls": [ft.Text("3. Ajuste as Configurações", weight=ft.FontWeight.BOLD), fps_input, loop_checkbox],
                "fps": fps_input,
                "loop": loop_checkbox
            }
        elif mode == 'GIF_to_WEBP':
            quality_slider = ft.Slider(min=1, max=100, divisions=99, value=80, label="Qualidade: {value}")

            def toggle_quality(e):
                quality_slider.disabled = e.control.value
                page_ref.update()
            lossless_checkbox = ft.Checkbox(label="Compressão sem Perdas (Qualidade Máxima)", value=False, on_change=toggle_quality)
            return {
                "controls": [ft.Text("3. Ajuste as Configurações", weight=ft.FontWeight.BOLD), lossless_checkbox, quality_slider],
                "lossless": lossless_checkbox,
                "quality": quality_slider
            }
        else:
            return {}

    navigation_rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=400,
        leading=ft.Text("Menu", size=16, weight=ft.FontWeight.BOLD),
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD_OUTLINED, selected_icon=ft.Icons.DASHBOARD, label="Dashboard"),
            ft.NavigationRailDestination(icon=ft.Icons.SETTINGS_OUTLINED, selected_icon=ft.Icons.SETTINGS, label="Configurações"),
            ft.NavigationRailDestination(icon=ft.Icons.INFO_OUTLINE, selected_icon=ft.Icons.INFO, label="Sobre"),
        ],
        on_change=lambda e: show_view("dashboard") if e.control.selected_index == 0 else None,
    )

    page.add(
        ft.Row(
            [
                navigation_rail,
                ft.VerticalDivider(width=1),
                ft.Container(content=main_content_area, expand=True, padding=ft.padding.all(20)),
            ],
            expand=True,
        )
    )

    show_view("dashboard")

    # --- Start Update Check ---
    update_manager = UpdateManager(page)
    update_thread = threading.Thread(target=update_manager.check_for_updates_thread, daemon=True)
    update_thread.start()
