import flet as ft
import os
import threading
import requests
import subprocess
import sys
import tempfile
import zipfile
from packaging.version import parse as parse_version
from converter import convert_image

# (Full UpdateManager class code here)

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

    selected_files_ref = ft.Ref[ft.Text]()
    image_preview_ref = ft.Ref[ft.Image]()
    state = AppState()

    def on_file_drop(e: ft.FileDropEvent):
        if state.conversion_mode is None or state.conversion_mode == "dashboard":
            return
        from_format, _ = state.conversion_mode.split('_to_')
        allowed_extensions = [from_format.lower()]
        if from_format == "JPG":
            allowed_extensions.append("jpeg")

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
            image_preview_ref.current.visible = len(state.input_paths) == 1
            if len(state.input_paths) == 1:
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
        # (Dashboard UI with dropdowns)
        pass

    def create_conversion_view(mode):
        # (Full conversion view UI with all controls, file pickers, and logic)
        pass

    def create_settings_controls(mode, page_ref):
        # (Full settings controls logic)
        pass

    page.add(ft.Container(content=main_content_area, expand=True, padding=ft.padding.all(20)))
    show_view("dashboard")

    # (Update manager initialization)
