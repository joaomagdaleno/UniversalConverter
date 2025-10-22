import flet as ft
import os
import threading
from converter import convert_webp_to_gif, convert_gif_to_webp

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

    def show_view(view_name):
        main_content_area.controls.clear()
        if view_name == "dashboard":
            main_content_area.controls.append(create_dashboard_view())
        elif view_name == "webp_to_gif":
            main_content_area.controls.append(create_conversion_view('webp_to_gif'))
        elif view_name == "gif_to_webp":
            main_content_area.controls.append(create_conversion_view('gif_to_webp'))
        page.update()

    def create_dashboard_view():
        return ft.Column(
            [
                ft.Text("Selecione uma Ferramenta de Conversão", size=20, weight=ft.FontWeight.BOLD),
                ft.Row(
                    [
                        ft.ElevatedButton(text="WebP para GIF", on_click=lambda _: show_view('webp_to_gif'), height=80, width=200),
                        ft.ElevatedButton(text="GIF para WebP", on_click=lambda _: show_view('gif_to_webp'), height=80, width=200),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER, spacing=20
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=30
        )

    def create_conversion_view(mode):
        state.conversion_mode = mode
        title = "Conversor WebP para GIF" if mode == 'webp_to_gif' else "Conversor GIF para WebP"
        file_extension = "webp" if mode == 'webp_to_gif' else "gif"

        # --- Controls that need to be referenced later ---
        selected_files_text = ft.Text("Nenhum arquivo selecionado")
        output_dir_text = ft.Text("Nenhuma pasta selecionada")
        progress_bar = ft.ProgressBar(width=400, value=0)
        status_label = ft.Text("")
        convert_button = ft.ElevatedButton("Converter", icon=ft.icons.SWAP_HORIZ)

        # --- Settings controls ---
        settings_controls = create_settings_controls(mode, page)

        # --- Event Handlers and Logic ---
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
            total_files = len(state.input_paths)
            converted_count = 0
            for i, file_path in enumerate(state.input_paths):
                if state.conversion_mode == 'webp_to_gif':
                    fps = int(settings_controls['fps'].value)
                    loop = settings_controls['loop'].value
                    success = convert_webp_to_gif(file_path, state.output_dir, frame_rate=fps, loop=0 if loop else 1)
                else: # gif_to_webp
                    lossless = settings_controls['lossless'].value
                    quality = int(settings_controls['quality'].value)
                    success = convert_gif_to_webp(file_path, state.output_dir, lossless=lossless, quality=quality)

                if success:
                    converted_count += 1

                # Update progress in a thread-safe way
                progress_value = (i + 1) / total_files
                page.run_threadsafe(update_progress, progress_value)

            page.run_threadsafe(finish_conversion, converted_count, total_files)

        def start_conversion(e):
            if not state.input_paths or not state.output_dir:
                # This should be a dialog in a real app
                status_label.value = "Selecione arquivos e uma pasta de destino."
                page.update()
                return

            convert_button.disabled = True
            status_label.value = "Convertendo..."
            progress_bar.value = 0
            page.update()

            # Run conversion in a separate thread
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
                        ft.ElevatedButton("Selecionar Arquivos", icon=ft.icons.UPLOAD_FILE, on_click=lambda _: file_picker.pick_files(allow_multiple=True, allowed_extensions=[file_extension])),
                        ft.ElevatedButton("Selecionar Pasta", icon=ft.icons.FOLDER_OPEN, disabled=True),
                    ]),
                    selected_files_text
                ]),
                padding=10, border=ft.border.all(1, ft.colors.OUTLINE), border_radius=ft.border_radius.all(5)
            ),
            ft.Container(
                ft.Column([
                    ft.Text("2. Escolha o Destino", weight=ft.FontWeight.BOLD),
                    ft.Row([
                        ft.ElevatedButton("Escolher Pasta de Destino", icon=ft.icons.FOLDER_SPECIAL, on_click=lambda _: output_dir_picker.get_directory_path()),
                    ]),
                    output_dir_text
                ]),
                padding=10, border=ft.border.all(1, ft.colors.OUTLINE), border_radius=ft.border_radius.all(5)
            ),
            ft.Container(
                ft.Column(settings_controls["controls"]),
                padding=10, border=ft.border.all(1, ft.colors.OUTLINE), border_radius=ft.border_radius.all(5)
            ),
            ft.Container(
                ft.Column([
                    ft.Text("4. Execute a Conversão", weight=ft.FontWeight.BOLD),
                    ft.Row([
                        ft.ElevatedButton("Pré-visualizar", icon=ft.icons.VISIBILITY, disabled=True),
                        convert_button,
                    ]),
                    progress_bar,
                    status_label
                ]),
                padding=10, border=ft.border.all(1, ft.colors.OUTLINE), border_radius=ft.border_radius.all(5)
            ),
            ft.ElevatedButton("Voltar para o Dashboard", on_click=lambda _: show_view("dashboard"))
        ], spacing=15)

    def create_settings_controls(mode, page_ref):
        if mode == 'webp_to_gif':
            fps_input = ft.TextField(label="Taxa de Quadros (FPS)", value="10", width=150)
            loop_checkbox = ft.Checkbox(label="GIF em Loop (Repetir Infinitamente)", value=True)
            return {
                "controls": [ft.Text("3. Ajuste as Configurações", weight=ft.FontWeight.BOLD), fps_input, loop_checkbox],
                "fps": fps_input,
                "loop": loop_checkbox
            }
        else: # gif_to_webp
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

    navigation_rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=400,
        leading=ft.Text("Menu", size=16, weight=ft.FontWeight.BOLD),
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(icon=ft.icons.DASHBOARD_OUTLINED, selected_icon=ft.icons.DASHBOARD, label="Dashboard"),
            ft.NavigationRailDestination(icon=ft.icons.SETTINGS_OUTLINED, selected_icon=ft.icons.SETTINGS, label="Configurações"),
            ft.NavigationRailDestination(icon_content=ft.Icon(ft.icons.INFO_OUTLINE), selected_icon_content=ft.Icon(ft.icons.INFO), label="Sobre"),
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
