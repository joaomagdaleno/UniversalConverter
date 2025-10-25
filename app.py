import flet as ft
import os
import threading
from packaging.version import parse as parse_version
from converter import convert_image
from audio_converter import convert_audio
from video_converter import convert_video

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

    # Refs for UI elements
    selected_files_ref = ft.Ref[ft.Text]()
    image_preview_ref = ft.Ref[ft.Image]()

    # Refs for image conversion settings
    quality_slider_ref = ft.Ref[ft.Slider]()
    width_input_ref = ft.Ref[ft.TextField]()
    height_input_ref = ft.Ref[ft.TextField]()
    keep_aspect_ratio_ref = ft.Ref[ft.Checkbox]()

    # Ref for audio conversion settings
    bitrate_dropdown_ref = ft.Ref[ft.Dropdown]()

    # Refs for video conversion settings
    resolution_dropdown_ref = ft.Ref[ft.Dropdown]()
    quality_slider_ref_video = ft.Ref[ft.Slider]()

    state = AppState()

    def on_file_drop(e: ft.FileDropEvent):
        if state.conversion_mode is None or state.conversion_mode == "dashboard":
            return
        from_format, _ = state.conversion_mode.split('_to_')

        image_formats = ["WEBP", "GIF", "PNG", "JPG", "BMP"]
        audio_formats = ["MP3", "WAV", "FLAC"]
        video_formats = ["MP4", "MKV", "MOV"]

        allowed_extensions = [from_format.lower()]
        if from_format == "JPG":
            allowed_extensions.append("jpeg")
        if from_format in audio_formats:
             allowed_extensions.extend(["mp3", "wav", "flac"])
        if from_format in video_formats:
            allowed_extensions.extend(["mp4", "mkv", "mov"])

        found_files = []
        for f in e.files:
            if os.path.isdir(f.path):
                for root, _, files in os.walk(f.path):
                    for file in files:
                        if any(file.lower().endswith(ext) for ext in allowed_extensions):
                            found_files.append(os.path.join(root, file))
            else:
                if any(f.path.lower().endswith(ext) for ext in allowed_extensions):
                    found_files.append(f.path)

        if found_files:
            state.input_paths.extend(found_files)
            selected_files_ref.current.value = f"{len(state.input_paths)} arquivo(s) selecionado(s)."
            image_preview_ref.current.visible = len(state.input_paths) == 1 and from_format in image_formats
            if image_preview_ref.current.visible:
                image_preview_ref.current.src = state.input_paths[0]
            page.update()

    page.on_file_drop = on_file_drop
    main_content_area = ft.Column(expand=True, spacing=20)

    def show_view(mode):
        main_content_area.controls.clear()
        if mode == "dashboard":
            main_content_area.controls.append(create_dashboard_view())
        else:
            main_content_area.controls.append(create_conversion_view(mode))
        page.update()

    def create_dashboard_view():
        image_formats = ["WEBP", "GIF", "PNG", "JPG", "BMP"]
        audio_formats = ["MP3", "WAV", "FLAC"]
        video_formats_from = ["MP4", "MKV", "MOV"]
        video_formats_to = ["MP4", "WEBM"]

        all_from_formats = image_formats + audio_formats + video_formats_from
        all_to_formats = image_formats + audio_formats + video_formats_to

        from_dropdown = ft.Dropdown(options=[ft.dropdown.Option(f) for f in all_from_formats])
        to_dropdown = ft.Dropdown(options=[ft.dropdown.Option(f) for f in all_to_formats])

        def start_conversion_clicked(e):
            if from_dropdown.value and to_dropdown.value:
                mode = f"{from_dropdown.value}_to_{to_dropdown.value}"
                show_view(mode)

        return ft.Column(
            controls=[
                ft.Text("Selecione os formatos de conversão:", style=ft.TextThemeStyle.HEADLINE_SMALL),
                ft.Row([from_dropdown, ft.Text("para"), to_dropdown]),
                ft.ElevatedButton("Iniciar Conversão", on_click=start_conversion_clicked)
            ]
        )

    def create_conversion_view(mode):
        state.conversion_mode = mode
        from_format, to_format = mode.split('_to_')

        def pick_files_result(e: ft.FilePickResultEvent):
            if e.files:
                state.input_paths.extend([f.path for f in e.files])
                selected_files_ref.current.value = f"{len(state.input_paths)} arquivo(s) selecionado(s)."
                image_preview_ref.current.visible = len(state.input_paths) == 1 and from_format in ["WEBP", "GIF", "PNG", "JPG", "BMP"]
                if image_preview_ref.current.visible:
                    image_preview_ref.current.src = state.input_paths[0]
                page.update()

        pick_files_dialog = ft.FilePicker(on_result=pick_files_result)
        get_directory_dialog = ft.FilePicker(on_result=lambda e: setattr(state, 'output_dir', e.path) or start_conversion(e))
        page.overlay.extend([pick_files_dialog, get_directory_dialog])

        def start_conversion(e):
            if not state.input_paths:
                return
            if not state.output_dir:
                get_directory_dialog.get_directory_path()
                return

            image_formats = ["WEBP", "GIF", "PNG", "JPG", "BMP"]
            audio_formats = ["MP3", "WAV", "FLAC"]
            video_formats = ["MP4", "MKV", "MOV", "WEBM"]

            is_image_conversion = from_format in image_formats and to_format in image_formats
            is_audio_conversion = from_format in audio_formats and to_format in audio_formats
            is_video_conversion = from_format in video_formats and to_format in video_formats

            settings = {}
            if is_image_conversion:
                settings = {
                    'quality': quality_slider_ref.current.value,
                    'width': width_input_ref.current.value,
                    'height': height_input_ref.current.value,
                    'keep_aspect_ratio': keep_aspect_ratio_ref.current.value,
                }
            elif is_audio_conversion:
                settings['bitrate'] = bitrate_dropdown_ref.current.value
            elif is_video_conversion:
                quality_map = {0.0: "Baixa", 1.0: "Média", 2.0: "Alta"}
                settings = {
                    'resolution': resolution_dropdown_ref.current.value,
                    'quality': quality_map[quality_slider_ref_video.current.value],
                }

            # Move progress bar and status text creation here
            progress_bar = ft.ProgressBar(width=400, visible=False)
            status_text = ft.Text("")
            # Add them to the main content area's controls, not the page
            main_content_area.controls.append(progress_bar)
            main_content_area.controls.append(status_text)
            page.update()

            def convert_all_files():
                progress_bar.visible = True
                status_text.value = "Iniciando conversão..."
                page.update()

                total_files = len(state.input_paths)
                for i, file_path in enumerate(state.input_paths):
                    if is_image_conversion:
                        convert_image(file_path, state.output_dir, to_format, settings)
                    elif is_audio_conversion:
                        convert_audio(file_path, state.output_dir, to_format, settings)
                    elif is_video_conversion:
                        convert_video(file_path, state.output_dir, to_format, settings)

                    progress = (i + 1) / total_files
                    progress_bar.value = progress
                    status_text.value = f"Convertendo: {i+1}/{total_files}"
                    page.update()

                status_text.value = "Conversão concluída!"
                progress_bar.visible = False
                page.update()
                state.input_paths = []
                state.output_dir = ""
                selected_files_ref.current.value = ""
                page.update()


            conversion_thread = threading.Thread(target=convert_all_files)
            conversion_thread.start()

        image_formats = ["WEBP", "GIF", "PNG", "JPG", "BMP"]
        is_image_conversion = from_format in image_formats

        quality_slider = ft.Slider(ref=quality_slider_ref, min=1, max=100, divisions=99, value=95, label="Qualidade ({value})")
        width_input = ft.TextField(ref=width_input_ref, label="Largura", width=100)
        height_input = ft.TextField(ref=height_input_ref, label="Altura", width=100)
        keep_aspect_ratio_checkbox = ft.Checkbox(ref=keep_aspect_ratio_ref, label="Manter proporção", value=True)

        image_settings = ft.Column(
            visible=is_image_conversion,
            controls=[
                ft.Text("Opções de Imagem", style=ft.TextThemeStyle.TITLE_MEDIUM),
                quality_slider,
                ft.Row([width_input, height_input]),
                keep_aspect_ratio_checkbox,
            ]
        )

        audio_formats = ["MP3", "WAV", "FLAC"]
        is_audio_conversion = from_format in audio_formats
        bitrate_options = ["96", "128", "192", "256", "320"]
        bitrate_dropdown = ft.Dropdown(
            ref=bitrate_dropdown_ref,
            label="Bitrate (kbps)",
            options=[ft.dropdown.Option(b) for b in bitrate_options],
            value="192"
        )
        audio_settings = ft.Column(
            visible=is_audio_conversion,
            controls=[
                ft.Text("Opções de Áudio", style=ft.TextThemeStyle.TITLE_MEDIUM),
                bitrate_dropdown,
            ]
        )

        video_formats = ["MP4", "MKV", "MOV", "WEBM"]
        is_video_conversion = from_format in video_formats and to_format in video_formats
        resolution_options = ["Manter original", "1080p", "720p", "480p"]
        resolution_dropdown = ft.Dropdown(
            ref=resolution_dropdown_ref,
            label="Resolução",
            options=[ft.dropdown.Option(r) for r in resolution_options],
            value="Manter original"
        )
        quality_slider_video = ft.Slider(
            ref=quality_slider_ref_video,
            min=0, max=2, divisions=2,
            label="{value}",
            value=1,
            on_change=lambda e: setattr(e.control, 'label', ["Baixa", "Média", "Alta"][int(e.control.value)])
        )
        quality_slider_video.label = "Média"

        video_settings = ft.Column(
            visible=is_video_conversion,
            controls=[
                ft.Text("Opções de Vídeo", style=ft.TextThemeStyle.TITLE_MEDIUM),
                resolution_dropdown,
                ft.Text("Qualidade"),
                quality_slider_video,
            ]
        )

        return ft.Column(
            controls=[
                ft.Text(f"Conversão: {from_format} para {to_format}", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.Container(
                    content=ft.Column([
                        ft.Icon(name=ft.icons.UPLOAD_FILE, size=50),
                        ft.Text("Arraste e solte os arquivos aqui ou clique para selecionar.")
                    ]),
                    width=float('inf'),
                    height=200,
                    border=ft.border.all(2, color=ft.colors.GREY_400),
                    border_radius=ft.border_radius.all(10),
                    alignment=ft.alignment.center,
                    on_click=lambda _: pick_files_dialog.pick_files(allow_multiple=True),
                ),
                ft.Text("", ref=selected_files_ref),
                ft.Image(ref=image_preview_ref, visible=False, height=150),
                image_settings,
                audio_settings,
                video_settings,
                ft.ElevatedButton("Converter", on_click=start_conversion),
                ft.TextButton("Voltar", on_click=lambda _: show_view("dashboard"))
            ],
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

    page.add(ft.Container(content=main_content_area, expand=True, padding=ft.padding.all(20)))
    show_view("dashboard")
