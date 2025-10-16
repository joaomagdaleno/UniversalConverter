import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from preview import PreviewWindow
from converter import convert_webp_to_gif, convert_gif_to_webp
import threading

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Conversor de Mídia Universal")
        self.geometry("800x600")
        self.minsize(700, 500)

        style = ttk.Style(self)
        style.configure("Sidebar.TFrame", background="#e7e7e7")
        style.configure("Widget.TButton", font=("Arial", 12), padding=20)
        style.configure("Header.TLabel", font=("Arial", 20, "bold"))

        self.input_paths = []
        self.output_dir = ""
        self.conversion_mode = None

        self.create_main_layout()
        self.create_sidebar()
        self.show_dashboard()

    def create_main_layout(self):
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True)
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=1)

        self.sidebar_frame = ttk.Frame(main_container, width=200, style="Sidebar.TFrame")
        self.sidebar_frame.grid(row=0, column=0, sticky="ns")
        self.sidebar_frame.pack_propagate(False)

        self.main_content_frame = ttk.Frame(main_container, padding="20")
        self.main_content_frame.grid(row=0, column=1, sticky="nsew")

    def create_sidebar(self):
        sidebar_title = ttk.Label(self.sidebar_frame, text="Menu", font=("Arial", 16, "bold"), background="#e7e7e7")
        sidebar_title.pack(pady=20, padx=10)

        btn_dashboard = ttk.Button(self.sidebar_frame, text="Dashboard", command=self.show_dashboard)
        btn_dashboard.pack(fill=tk.X, pady=5, padx=10)

        btn_settings = ttk.Button(self.sidebar_frame, text="Configurações", state="disabled")
        btn_settings.pack(fill=tk.X, pady=5, padx=10)

        btn_about = ttk.Button(self.sidebar_frame, text="Sobre", state="disabled")
        btn_about.pack(fill=tk.X, pady=5, padx=10)

    def clear_main_content(self):
        for widget in self.main_content_frame.winfo_children():
            widget.destroy()
        self.input_paths = []
        self.output_dir = ""

    def show_dashboard(self):
        self.clear_main_content()
        self.conversion_mode = None

        dashboard_title = ttk.Label(self.main_content_frame, text="Selecione uma Ferramenta de Conversão", style="Header.TLabel")
        dashboard_title.pack(pady=20)

        widget_frame = ttk.Frame(self.main_content_frame)
        widget_frame.pack(expand=True)

        btn_webp_to_gif = ttk.Button(widget_frame, text="WebP para GIF", style="Widget.TButton", command=lambda: self.show_conversion_screen('webp_to_gif'))
        btn_webp_to_gif.grid(row=0, column=0, padx=20, pady=20)

        btn_gif_to_webp = ttk.Button(widget_frame, text="GIF para WebP", style="Widget.TButton", command=lambda: self.show_conversion_screen('gif_to_webp'))
        btn_gif_to_webp.grid(row=0, column=1, padx=20, pady=20)

    def show_conversion_screen(self, mode):
        self.clear_main_content()
        self.conversion_mode = mode

        title = "Conversor WebP para GIF" if mode == 'webp_to_gif' else "Conversor GIF para WebP"
        ttk.Label(self.main_content_frame, text=title, style="Header.TLabel").pack(pady=10)

        # --- Frames de Seção ---
        files_frame = ttk.LabelFrame(self.main_content_frame, text="1. Selecione os Arquivos", padding="10")
        files_frame.pack(fill=tk.X, pady=5)

        output_frame = ttk.LabelFrame(self.main_content_frame, text="2. Escolha o Destino", padding="10")
        output_frame.pack(fill=tk.X, pady=5)

        settings_frame = ttk.LabelFrame(self.main_content_frame, text="3. Ajuste as Configurações", padding="10")
        settings_frame.pack(fill=tk.X, pady=5)

        action_frame = ttk.LabelFrame(self.main_content_frame, text="4. Execute a Conversão", padding="10")
        action_frame.pack(fill=tk.X, pady=10)

        # --- Widgets de Seleção de Arquivos ---
        self.btn_select_files = ttk.Button(files_frame, text="Selecionar Arquivos", command=self.select_files)
        self.btn_select_files.pack(side=tk.LEFT, padx=5)
        self.btn_select_folder = ttk.Button(files_frame, text="Selecionar Pasta", command=self.select_folder)
        self.btn_select_folder.pack(side=tk.LEFT, padx=5)
        self.selected_files_label = ttk.Label(files_frame, text="Nenhum arquivo selecionado")
        self.selected_files_label.pack(side=tk.LEFT, padx=10, expand=True)

        # --- Widgets de Destino ---
        self.btn_output_dir = ttk.Button(output_frame, text="Escolher Pasta de Destino", command=self.select_output_dir)
        self.btn_output_dir.pack(side=tk.LEFT, padx=5)
        self.output_dir_label = ttk.Label(output_frame, text="Nenhuma pasta selecionada")
        self.output_dir_label.pack(side=tk.LEFT, padx=10)

        # --- Widgets de Configurações (Dinâmico) ---
        if mode == 'webp_to_gif':
            self.create_webp_to_gif_settings(settings_frame)
        else: # gif_to_webp
            self.create_gif_to_webp_settings(settings_frame)

        # --- Widgets de Ação ---
        self.btn_preview = ttk.Button(action_frame, text="Pré-visualizar", state="disabled", command=self.open_preview_window)
        self.btn_preview.pack(side=tk.LEFT, padx=10)
        self.btn_convert = ttk.Button(action_frame, text="Converter", state="disabled", command=self.start_conversion_thread)
        self.btn_convert.pack(side=tk.LEFT, padx=10)

        self.progress_bar = ttk.Progressbar(action_frame, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)
        self.status_label = ttk.Label(action_frame, text="")
        self.status_label.pack(side=tk.LEFT)

    def create_webp_to_gif_settings(self, parent):
        ttk.Label(parent, text="Taxa de Quadros (FPS):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.fps_var = tk.IntVar(value=10)
        ttk.Spinbox(parent, from_=1, to=60, textvariable=self.fps_var, width=5).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        self.loop_var = tk.IntVar(value=0)
        ttk.Checkbutton(parent, text="GIF em Loop (Repetir Infinitamente)", variable=self.loop_var, onvalue=0, offvalue=1).grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)

    def create_gif_to_webp_settings(self, parent):
        self.lossless_var = tk.BooleanVar()
        ttk.Checkbutton(parent, text="Compressão sem Perdas (Qualidade Máxima)", variable=self.lossless_var, command=self.toggle_quality_slider).grid(row=0, column=0, columnspan=2, sticky=tk.W)

        self.quality_label = ttk.Label(parent, text="Qualidade (1-100):")
        self.quality_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        self.quality_var = tk.IntVar(value=80)
        self.quality_slider = ttk.Scale(parent, from_=1, to=100, orient=tk.HORIZONTAL, variable=self.quality_var, length=200)
        self.quality_slider.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

    def toggle_quality_slider(self):
        if self.lossless_var.get():
            self.quality_slider.config(state="disabled")
            self.quality_label.config(state="disabled")
        else:
            self.quality_slider.config(state="normal")
            self.quality_label.config(state="normal")

    def update_button_states(self):
        """Atualiza o estado dos botões 'Pré-visualizar' e 'Converter'."""
        files_selected = bool(self.input_paths)
        output_selected = bool(self.output_dir)

        self.btn_convert.config(state="normal" if files_selected and output_selected else "disabled")
        self.btn_preview.config(state="normal" if files_selected and output_selected and len(self.input_paths) == 1 else "disabled")

    def select_files(self):
        filetypes = [("Arquivos WebP", "*.webp")] if self.conversion_mode == 'webp_to_gif' else [("Arquivos GIF", "*.gif")]
        title = "Selecione os arquivos WebP" if self.conversion_mode == 'webp_to_gif' else "Selecione os arquivos GIF"

        self.input_paths = filedialog.askopenfilenames(title=title, filetypes=filetypes)
        if self.input_paths:
            self.selected_files_label.config(text=f"{len(self.input_paths)} arquivo(s) selecionado(s)")
        else:
            self.selected_files_label.config(text="Nenhum arquivo selecionado")
        self.update_button_states()

    def select_folder(self):
        title = "Selecione uma pasta com arquivos WebP" if self.conversion_mode == 'webp_to_gif' else "Selecione uma pasta com arquivos GIF"
        folder_path = filedialog.askdirectory(title=title)
        if folder_path:
            extension = ".webp" if self.conversion_mode == 'webp_to_gif' else ".gif"
            self.input_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(extension)]
            if self.input_paths:
                self.selected_files_label.config(text=f"{len(self.input_paths)} arquivo(s) na pasta")
            else:
                self.selected_files_label.config(text=f"Nenhum arquivo {extension} encontrado")
        self.update_button_states()

    def select_output_dir(self):
        self.output_dir = filedialog.askdirectory(title="Selecione a pasta de destino")
        if self.output_dir:
            self.output_dir_label.config(text=self.output_dir)
        else:
            self.output_dir_label.config(text="Nenhuma pasta selecionada")
        self.update_button_states()


    def open_preview_window(self):
        if self.input_paths:
            # A janela de preview só funciona para o primeiro arquivo da lista
            preview_win = PreviewWindow(self, self.input_paths[0], self.output_dir)
            preview_win.grab_set() # Torna a janela de preview modal

    def start_conversion_thread(self):
        self.btn_convert.config(state=tk.DISABLED)
        self.btn_preview.config(state=tk.DISABLED)
        self.status_label.config(text="Convertendo...")
        self.progress_bar["value"] = 0
        self.progress_bar["maximum"] = len(self.input_paths)

        conversion_thread = threading.Thread(target=self.run_conversion, daemon=True)
        conversion_thread.start()

    def run_conversion(self):
        converted_count = 0
        for i, file_path in enumerate(self.input_paths):
            if self.conversion_mode == 'webp_to_gif':
                success = convert_webp_to_gif(
                    file_path, self.output_dir,
                    frame_rate=self.fps_var.get(),
                    loop=self.loop_var.get()
                )
            else: # gif_to_webp
                success = convert_gif_to_webp(
                    file_path, self.output_dir,
                    lossless=self.lossless_var.get(),
                    quality=self.quality_var.get()
                )
            if success:
                converted_count += 1

            self.after(0, self.update_progress, i + 1)

        self.after(0, self.conversion_finished, converted_count)

    def update_progress(self, value):
        self.progress_bar["value"] = value

    def conversion_finished(self, count):
        messagebox.showinfo("Sucesso", f"{count} de {len(self.input_paths)} arquivo(s) convertido(s) com sucesso!")
        self.status_label.config(text="")
        self.progress_bar["value"] = 0
        self.update_button_states()


if __name__ == "__main__":
    app = App()
    app.mainloop()
