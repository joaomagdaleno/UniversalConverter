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
from audio_converter import convert_audio

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

    # Refs for UI controls that need to be updated programmatically
    selected_files_ref_img = ft.Ref[ft.Text]()
    selected_files_ref_audio = ft.Ref[ft.Text]()
    image_preview_ref = ft.Ref[ft.Image]()

    def on_file_drop(e: ft.FileDropEvent):
        if state.conversion_mode is None or "dashboard" in state.conversion_mode:
            return

        mode_parts = state.conversion_mode.split('_')
        converter_type = mode_parts[0] # 'audio' or 'image'
        from_format = mode_parts[1]

        allowed_extensions = [from_format.lower()]
        if from_format == "JPG":
            allowed_extensions.append("jpeg")

        dropped_paths = [f.path for f in e.files]
        found_files = []
        for path in dropped_paths:
            if os.path.isdir(path):
                for root, _, files in os.walk(path):
                    for file in files:
                        if any(file.lower().endswith(ext) for ext in allowed_extensions):
                            found_files.append(os.path.join(root, file))
            else:
                if any(path.lower().endswith(ext) for ext in allowed_extensions):
                    found_files.append(path)

        if found_files:
            state.input_paths.extend(found_files)

            # Update the correct UI based on the active converter
            if converter_type == "image":
                if selected_files_ref_img.current:
                    selected_files_ref_img.current.value = f"{len(state.input_paths)} arquivo(s) selecionado(s)."
                if image_preview_ref.current:
                    if len(state.input_paths) == 1:
                        image_preview_ref.current.src = state.input_paths[0]
                        image_preview_ref.current.visible = True
                    else:
                        image_preview_ref.current.visible = False
            elif converter_type == "audio":
                if selected_files_ref_audio.current:
                    selected_files_ref_audio.current.value = f"{len(state.input_paths)} arquivo(s) selecionado(s)."

            page.update()

    page.on_file_drop = on_file_drop
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

        image_preview = ft.Image(ref=image_preview_ref, visible=False, height=150, fit=ft.ImageFit.CONTAIN)
        selected_files_text = ft.Text("Nenhum arquivo selecionado", ref=selected_files_ref)
        output_dir_text = ft.Text("Nenhuma pasta selecionada")
        progress_bar = ft.ProgressBar(width=400, value=0)
        status_label = ft.Text("")
        convert_button = ft.ElevatedButton("Converter", icon=ft.Icons.SWAP_HORIZ)
        settings_controls = create_settings_controls(mode, page)

        def on_files_selected(e: ft.FilePickerResultEvent):
            if e.files:
                state.input_paths = [f.path for f in e.files]
                selected_files_text.value = f"{len(state.input_paths)} arquivo(s) selecionado(s)"
                if len(state.input_paths) == 1:
                    image_preview_ref.current.src = state.input_paths[0]
                    image_preview_ref.current.visible = True
                else:
                    image_preview_ref.current.visible = False
            else:
                state.input_paths = []
                selected_files_text.value = "Nenhum arquivo selecionado"
                image_preview_ref.current.visible = False
            page.update()

        def on_folder_selected(e: ft.FilePickerResultEvent):
            if e.path:
                folder_path = e.path
                found_files = []
                # Use allowed_extensions which is already defined in the view
                for root, _, files in os.walk(folder_path):
                    for file in files:
                        # Check if the file ends with any of the allowed extensions
                        if any(file.lower().endswith(ext) for ext in allowed_extensions):
                            found_files.append(os.path.join(root, file))

                if found_files:
                    state.input_paths = found_files
                    selected_files_text.value = f"{len(found_files)} arquivo(s) encontrado(s) na pasta."
                else:
                    state.input_paths = []
                    selected_files_text.value = f"Nenhum arquivo compatível encontrado na pasta selecionada."
                image_preview_ref.current.visible = False
            else:
                # If no folder is selected, do nothing or clear previous selection
                state.input_paths = []
                selected_files_text.value = "Nenhum arquivo selecionado."
                image_preview_ref.current.visible = False
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
        folder_picker = ft.FilePicker(on_result=on_folder_selected)
        output_dir_picker = ft.FilePicker(on_result=on_output_dir_selected)
        page.overlay.extend([file_picker, folder_picker, output_dir_picker])

        def run_conversion_thread():
            from_format, to_format = state.conversion_mode.split('_to_')
            total_files = len(state.input_paths)
            converted_count = 0

            for i, file_path in enumerate(state.input_paths):
                settings = {
                    'width': settings_controls['width'].value,
                    'height': settings_controls['height'].value,
                    'keep_aspect_ratio': settings_controls['keep_aspect_ratio'].value,
                }
                if 'quality' in settings_controls:
                    settings['quality'] = int(settings_controls['quality'].value)
                if state.conversion_mode == 'WEBP_to_GIF':
                    settings['frame_rate'] = int(settings_controls['fps'].value)
                    settings['loop'] = settings_controls['loop'].value
                elif state.conversion_mode == 'GIF_to_WEBP':
                    settings['lossless'] = settings_controls['lossless'].value

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
                        ft.ElevatedButton("Selecionar Pasta", icon=ft.Icons.FOLDER_OPEN, on_click=lambda _: folder_picker.get_directory_path()),
                    ]),
                    selected_files_text,
                    image_preview,
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
                ft.Column(settings_controls.get("controls", [])),
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
        _, to_format = mode.split('_to_')

        # --- Controles de Redimensionamento (Sempre Visíveis) ---
        width_input = ft.TextField(label="Largura", width=100)
        height_input = ft.TextField(label="Altura", width=100)
        keep_aspect_ratio_checkbox = ft.Checkbox(label="Manter Proporção", value=True)

        resize_controls = [
            ft.Text("Redimensionar (Opcional)", weight=ft.FontWeight.BOLD),
            ft.Row([width_input, height_input, keep_aspect_ratio_checkbox], spacing=10)
        ]

        # --- Controles Específicos do Formato ---
        format_specific_controls = []
        output_controls = {
            "width": width_input,
            "height": height_input,
            "keep_aspect_ratio": keep_aspect_ratio_checkbox,
        }

        if to_format in ['JPG', 'WEBP']:
            quality_slider = ft.Slider(min=1, max=100, divisions=99, value=90, label="Qualidade: {value}")
            format_specific_controls.extend([ft.Text("Qualidade", weight=ft.FontWeight.BOLD), quality_slider])
            output_controls["quality"] = quality_slider

        if mode == 'WEBP_to_GIF':
            fps_input = ft.TextField(label="Taxa de Quadros (FPS)", value="10", width=150)
            loop_checkbox = ft.Checkbox(label="GIF em Loop", value=True)
            format_specific_controls.extend([ft.Text("Animação", weight=ft.FontWeight.BOLD), fps_input, loop_checkbox])
            output_controls.update({"fps": fps_input, "loop": loop_checkbox})

        elif mode == 'GIF_to_WEBP':
            lossless_checkbox = ft.Checkbox(label="Compressão sem Perdas", value=False, on_change=lambda e: setattr(output_controls.get('quality'), 'disabled', e.control.value) or page_ref.update())
            format_specific_controls.append(lossless_checkbox)
            output_controls["lossless"] = lossless_checkbox

        all_controls = resize_controls + format_specific_controls
        if all_controls:
            all_controls.insert(0, ft.Text("3. Ajuste as Configurações", weight=ft.FontWeight.BOLD))

        output_controls["controls"] = all_controls if all_controls else []
        return output_controls

    def create_image_converter_view():
        # This function will now encapsulate the entire UI for the image converter
        # It combines the logic from the old create_dashboard_view and create_conversion_view

        main_image_content_area = ft.Column(expand=True, spacing=20)

        def show_image_view(mode):
            main_image_content_area.controls.clear()
            if mode == "dashboard":
                main_image_content_area.controls.append(create_image_dashboard())
            else:
                main_image_content_area.controls.append(create_image_conversion_view(mode))
            page.update()

        def create_image_dashboard():
            from_format = ft.Dropdown(
                label="Converter de",
                options=[
                    ft.dropdown.Option("WEBP"), ft.dropdown.Option("GIF"),
                    ft.dropdown.Option("PNG"), ft.dropdown.Option("JPG"),
                    ft.dropdown.Option("BMP"),
                ], width=200,
            )
            to_format = ft.Dropdown(
                label="Para",
                options=[
                    ft.dropdown.Option("WEBP"), ft.dropdown.Option("GIF"),
                    ft.dropdown.Option("PNG"), ft.dropdown.Option("JPG"),
                    ft.dropdown.Option("BMP"),
                ], width=200,
            )

            def start_conversion_setup(e):
                if from_format.value and to_format.value:
                    mode = f"{from_format.value}_to_{to_format.value}"
                    show_image_view(mode)

            return ft.Column(
                controls=[
                    ft.Text("Selecione o Formato da Conversão de Imagem", size=20, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        controls=[from_format, ft.Icon(ft.Icons.SWAP_HORIZ), to_format],
                        alignment=ft.MainAxisAlignment.CENTER, spacing=20,
                    ),
                    ft.ElevatedButton("Iniciar", on_click=start_conversion_setup, height=50, width=200),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=30,
                expand=True, alignment=ft.MainAxisAlignment.CENTER,
            )

        def create_image_conversion_view(mode):
            # This is the detailed conversion view, mostly unchanged
            # but calls show_image_view on 'back' button press
            state.conversion_mode = mode
            from_format, to_format = mode.split('_to_')
            title = f"Conversor {from_format} para {to_format}"

            allowed_extensions = [from_format.lower()]
            if from_format == "JPG":
                allowed_extensions.append("jpeg")

            image_preview = ft.Image(ref=image_preview_ref, visible=False, height=150, fit=ft.ImageFit.CONTAIN)
            selected_files_text = ft.Text("Nenhum arquivo selecionado", ref=selected_files_ref_img)
            output_dir_text = ft.Text("Nenhuma pasta selecionada")
            progress_bar = ft.ProgressBar(width=400, value=0)
            status_label = ft.Text("")
            convert_button = ft.ElevatedButton("Converter", icon=ft.Icons.SWAP_HORIZ)
            settings_controls = create_settings_controls(mode, page)

            # ... (on_files_selected, on_folder_selected, etc. remain the same)
            def on_files_selected(e: ft.FilePickerResultEvent):
                if e.files:
                    state.input_paths = [f.path for f in e.files]
                    selected_files_text.value = f"{len(state.input_paths)} arquivo(s) selecionado(s)"
                    if len(state.input_paths) == 1:
                        image_preview_ref.current.src = state.input_paths[0]
                        image_preview_ref.current.visible = True
                    else:
                        image_preview_ref.current.visible = False
                else:
                    state.input_paths = []
                    selected_files_text.value = "Nenhum arquivo selecionado"
                    image_preview_ref.current.visible = False
                page.update()

            def on_folder_selected(e: ft.FilePickerResultEvent):
                if e.path:
                    folder_path = e.path
                    found_files = []
                    for root, _, files in os.walk(folder_path):
                        for file in files:
                            if any(file.lower().endswith(ext) for ext in allowed_extensions):
                                found_files.append(os.path.join(root, file))

                    if found_files:
                        state.input_paths = found_files
                        selected_files_text.value = f"{len(found_files)} arquivo(s) encontrado(s) na pasta."
                    else:
                        state.input_paths = []
                        selected_files_text.value = f"Nenhum arquivo compatível encontrado na pasta selecionada."
                    image_preview_ref.current.visible = False
                else:
                    state.input_paths = []
                    selected_files_text.value = "Nenhum arquivo selecionado."
                    image_preview_ref.current.visible = False
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
            folder_picker = ft.FilePicker(on_result=on_folder_selected)
            output_dir_picker = ft.FilePicker(on_result=on_output_dir_selected)
            page.overlay.extend([file_picker, folder_picker, output_dir_picker])

            def run_conversion_thread():
                # ... (conversion logic remains the same)
                from_format, to_format = state.conversion_mode.split('_to_')
                total_files = len(state.input_paths)
                converted_count = 0

                for i, file_path in enumerate(state.input_paths):
                    settings = {
                        'width': settings_controls['width'].value,
                        'height': settings_controls['height'].value,
                        'keep_aspect_ratio': settings_controls['keep_aspect_ratio'].value,
                    }
                    if 'quality' in settings_controls:
                        settings['quality'] = int(settings_controls['quality'].value)
                    if state.conversion_mode == 'WEBP_to_GIF':
                        settings['frame_rate'] = int(settings_controls['fps'].value)
                        settings['loop'] = settings_controls['loop'].value
                    elif state.conversion_mode == 'GIF_to_WEBP':
                        settings['lossless'] = settings_controls['lossless'].value

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
                            ft.ElevatedButton("Selecionar Pasta", icon=ft.Icons.FOLDER_OPEN, on_click=lambda _: folder_picker.get_directory_path()),
                        ]),
                        selected_files_text,
                        image_preview,
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
                    ft.Column(settings_controls.get("controls", [])),
                    padding=10, border=ft.border.all(1, ft.Colors.OUTLINE), border_radius=ft.border_radius.all(5)
                ),
                ft.Container(
                    ft.Column([
                        ft.Text("4. Execute a Conversão", weight=ft.FontWeight.BOLD),
                        ft.Row([convert_button]),
                        progress_bar,
                        status_label
                    ]),
                    padding=10, border=ft.border.all(1, ft.Colors.OUTLINE), border_radius=ft.border_radius.all(5)
                ),
                ft.ElevatedButton("Voltar para o Início", on_click=lambda _: show_image_view("dashboard"))
            ], spacing=15)

        show_image_view("dashboard")
        return main_image_content_area

    def create_audio_converter_view():
        main_audio_content_area = ft.Column(expand=True, spacing=20)
        bitrate_slider_ref = ft.Ref[ft.Slider]()

        def show_audio_view(mode):
            main_audio_content_area.controls.clear()
            if mode == "dashboard":
                main_audio_content_area.controls.append(create_audio_dashboard())
            else:
                main_audio_content_area.controls.append(create_audio_conversion_view(mode))
            page.update()

        def create_audio_dashboard():
            from_format = ft.Dropdown(
                label="Converter de",
                options=[
                    ft.dropdown.Option("MP3"), ft.dropdown.Option("WAV"), ft.dropdown.Option("FLAC"),
                ], width=200,
            )
            to_format = ft.Dropdown(
                label="Para",
                options=[
                    ft.dropdown.Option("MP3"), ft.dropdown.Option("WAV"), ft.dropdown.Option("FLAC"),
                ], width=200,
            )

            def start_audio_conversion_setup(e):
                if from_format.value and to_format.value:
                    if from_format.value == to_format.value:
                        # Optional: Add user feedback about same format conversion
                        return
                    mode = f"audio_{from_format.value}_to_{to_format.value}"
                    show_audio_view(mode)

            return ft.Column(
                controls=[
                    ft.Text("Selecione o Formato da Conversão de Áudio", size=20, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        controls=[from_format, ft.Icon(ft.Icons.SWAP_HORIZ), to_format],
                        alignment=ft.MainAxisAlignment.CENTER, spacing=20,
                    ),
                    ft.ElevatedButton("Iniciar", on_click=start_audio_conversion_setup, height=50, width=200),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=30,
                expand=True, alignment=ft.MainAxisAlignment.CENTER,
            )

        def create_audio_conversion_view(mode):
            state.conversion_mode = mode
            _, from_format, _, to_format = mode.split('_')
            title = f"Conversor de Áudio: {from_format} para {to_format}"

            allowed_extensions = [from_format.lower()]

            selected_files_text = ft.Text("Nenhum arquivo selecionado", ref=selected_files_ref_audio)
            output_dir_text = ft.Text("Nenhuma pasta selecionada")
            progress_bar = ft.ProgressBar(width=400, value=0)
            status_label = ft.Text("")
            convert_button = ft.ElevatedButton("Converter", icon=ft.Icons.SWAP_HORIZ)

            # --- Audio Specific Settings ---
            bitrate_slider = ft.Slider(
                ref=bitrate_slider_ref,
                min=32, max=320, divisions=9, value=192,
                label="Bitrate: {value} kbps"
            )
            settings_view = ft.Column([
                ft.Text("3. Ajuste as Configurações", weight=ft.FontWeight.BOLD),
                ft.Text("Bitrate (Qualidade de Áudio)", weight=ft.FontWeight.NORMAL),
                bitrate_slider
            ])
            # Hide settings for lossless formats like WAV/FLAC where bitrate isn't applicable
            settings_view.visible = to_format == "MP3"


            def on_files_selected_audio(e: ft.FilePickerResultEvent):
                if e.files:
                    state.input_paths = [f.path for f in e.files]
                    selected_files_text.value = f"{len(state.input_paths)} arquivo(s) selecionado(s)"
                else:
                    state.input_paths = []
                    selected_files_text.value = "Nenhum arquivo selecionado"
                page.update()

            def on_folder_selected_audio(e: ft.FilePickerResultEvent):
                if e.path:
                    folder_path = e.path
                    found_files = []
                    for root, _, files in os.walk(folder_path):
                        for file in files:
                            if any(file.lower().endswith(ext) for ext in allowed_extensions):
                                found_files.append(os.path.join(root, file))

                    if found_files:
                        state.input_paths = found_files
                        selected_files_text.value = f"{len(found_files)} arquivo(s) encontrado(s) na pasta."
                    else:
                        state.input_paths = []
                        selected_files_text.value = "Nenhum arquivo compatível encontrado."
                else:
                    state.input_paths = []
                    selected_files_text.value = "Nenhum arquivo selecionado."
                page.update()

            def on_output_dir_selected_audio(e: ft.FilePickerResultEvent):
                if e.path:
                    state.output_dir = e.path
                    output_dir_text.value = f"Destino: {state.output_dir}"
                else:
                    state.output_dir = ""
                    output_dir_text.value = "Nenhuma pasta selecionada"
                page.update()

            file_picker_audio = ft.FilePicker(on_result=on_files_selected_audio)
            folder_picker_audio = ft.FilePicker(on_result=on_folder_selected_audio)
            output_dir_picker_audio = ft.FilePicker(on_result=on_output_dir_selected_audio)
            page.overlay.extend([file_picker_audio, folder_picker_audio, output_dir_picker_audio])

            def run_audio_conversion_thread():
                _, _, _, to_fmt = state.conversion_mode.split('_')
                total_files = len(state.input_paths)

                for i, file_path in enumerate(state.input_paths):
                    bitrate = f"{int(bitrate_slider_ref.current.value)}k" if bitrate_slider_ref.current else "192k"
                    convert_audio(file_path, state.output_dir, to_fmt, bitrate)
                    page.run_threadsafe(update_progress, (i + 1) / total_files)

                page.run_threadsafe(finish_conversion, total_files, total_files) # Assuming success for now

            def start_audio_conversion(e):
                if not state.input_paths or not state.output_dir:
                    status_label.value = "Selecione arquivos e uma pasta de destino."
                    page.update()
                    return
                convert_button.disabled = True
                status_label.value = "Convertendo..."
                progress_bar.value = 0
                page.update()
                thread = threading.Thread(target=run_audio_conversion_thread, daemon=True)
                thread.start()

            def update_progress(value):
                progress_bar.value = value
                page.update()

            def finish_conversion(count, total):
                convert_button.disabled = False
                status_label.value = f"{count} de {total} arquivo(s) convertido(s) com sucesso!"
                progress_bar.value = 1.0
                page.update()

            convert_button.on_click = start_audio_conversion

            return ft.Column([
                ft.Text(title, size=20, weight=ft.FontWeight.BOLD),
                ft.Container(
                    ft.Column([
                        ft.Text("1. Selecione os Arquivos de Áudio", weight=ft.FontWeight.BOLD),
                        ft.Row([
                            ft.ElevatedButton("Selecionar Arquivos", icon=ft.Icons.UPLOAD_FILE, on_click=lambda _: file_picker_audio.pick_files(allow_multiple=True, allowed_extensions=allowed_extensions)),
                            ft.ElevatedButton("Selecionar Pasta", icon=ft.Icons.FOLDER_OPEN, on_click=lambda _: folder_picker_audio.get_directory_path()),
                        ]),
                        selected_files_text,
                    ]),
                    padding=10, border=ft.border.all(1, ft.Colors.OUTLINE), border_radius=ft.border_radius.all(5)
                ),
                ft.Container(
                    ft.Column([
                        ft.Text("2. Escolha o Destino", weight=ft.FontWeight.BOLD),
                        ft.Row([
                            ft.ElevatedButton("Escolher Pasta de Destino", icon=ft.Icons.FOLDER_SPECIAL, on_click=lambda _: output_dir_picker_audio.get_directory_path()),
                        ]),
                        output_dir_text
                    ]),
                    padding=10, border=ft.border.all(1, ft.Colors.OUTLINE), border_radius=ft.border_radius.all(5)
                ),
                ft.Container(
                    settings_view,
                    padding=10, border=ft.border.all(1, ft.Colors.OUTLINE), border_radius=ft.border_radius.all(5)
                ),
                ft.Container(
                    ft.Column([
                        ft.Text("4. Execute a Conversão", weight=ft.FontWeight.BOLD),
                        ft.Row([convert_button]),
                        progress_bar,
                        status_label
                    ]),
                    padding=10, border=ft.border.all(1, ft.Colors.OUTLINE), border_radius=ft.border_radius.all(5)
                ),
                ft.ElevatedButton("Voltar para o Início", on_click=lambda _: show_audio_view("dashboard"))
            ], spacing=15)

        show_audio_view("dashboard")
        return main_audio_content_area

    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="Imagem",
                icon=ft.Icons.IMAGE,
                content=create_image_converter_view(),
            ),
            ft.Tab(
                text="Áudio",
                icon=ft.Icons.AUDIOTRACK,
                content=create_audio_converter_view(),
            ),
            ft.Tab(
                text="Vídeo",
                icon=ft.Icons.VIDEOCAM,
                content=ft.Text("Funcionalidade de conversão de vídeo em breve!", size=20, text_align=ft.TextAlign.CENTER),
            ),
        ],
        expand=1,
    )

    page.add(tabs)

    # --- Start Update Check ---
    update_manager = UpdateManager(page)
    update_thread = threading.Thread(target=update_manager.check_for_updates_thread, daemon=True)
    update_thread.start()
