import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from converter import convert_webp_to_gif

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Conversor WebP para GIF")
        self.geometry("600x450")

        # --- Widgets ---
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Seleção de Arquivos
        files_frame = ttk.LabelFrame(main_frame, text="Seleção de Arquivos", padding="10")
        files_frame.pack(fill=tk.X, pady=5)

        self.btn_select_files = ttk.Button(files_frame, text="Selecionar Arquivos", command=self.select_files)
        self.btn_select_files.pack(side=tk.LEFT, padx=5)

        self.btn_select_folder = ttk.Button(files_frame, text="Selecionar Pasta", command=self.select_folder)
        self.btn_select_folder.pack(side=tk.LEFT, padx=5)

        self.selected_files_label = ttk.Label(files_frame, text="Nenhum arquivo selecionado")
        self.selected_files_label.pack(side=tk.LEFT, padx=10)

        # Pasta de Destino
        output_frame = ttk.LabelFrame(main_frame, text="Pasta de Destino", padding="10")
        output_frame.pack(fill=tk.X, pady=5)

        self.btn_output_dir = ttk.Button(output_frame, text="Escolher Destino", command=self.select_output_dir)
        self.btn_output_dir.pack(side=tk.LEFT, padx=5)

        self.output_dir_label = ttk.Label(output_frame, text="Nenhuma pasta de destino selecionada")
        self.output_dir_label.pack(side=tk.LEFT, padx=10)

        # Configurações de Conversão
        settings_frame = ttk.LabelFrame(main_frame, text="Configurações", padding="10")
        settings_frame.pack(fill=tk.X, pady=5)

        ttk.Label(settings_frame, text="Taxa de Quadros (FPS):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.fps_var = tk.IntVar(value=10)
        self.fps_spinbox = ttk.Spinbox(settings_frame, from_=1, to=60, textvariable=self.fps_var, width=5)
        self.fps_spinbox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        self.loop_var = tk.IntVar(value=0)
        self.loop_check = ttk.Checkbutton(settings_frame, text="GIF em Loop (Repetir Infinitamente)", variable=self.loop_var, onvalue=0, offvalue=1)
        self.loop_check.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)

        # Botão de Conversão e Progresso
        action_frame = ttk.Frame(main_frame, padding="10")
        action_frame.pack(fill=tk.X, pady=10)

        self.btn_convert = ttk.Button(action_frame, text="Converter", command=self.start_conversion_thread)
        self.btn_convert.pack(pady=5)

        self.progress_bar = ttk.Progressbar(action_frame, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.pack(pady=5)

        self.status_label = ttk.Label(action_frame, text="")
        self.status_label.pack(pady=5)

        # Variáveis de estado
        self.input_paths = []
        self.output_dir = ""

    def select_files(self):
        self.input_paths = filedialog.askopenfilenames(
            title="Selecione os arquivos WebP",
            filetypes=[("Arquivos WebP", "*.webp")]
        )
        if self.input_paths:
            self.selected_files_label.config(text=f"{len(self.input_paths)} arquivo(s) selecionado(s)")
        else:
            self.selected_files_label.config(text="Nenhum arquivo selecionado")

    def select_folder(self):
        folder_path = filedialog.askdirectory(title="Selecione uma pasta com arquivos WebP")
        if folder_path:
            self.input_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(".webp")]
            if self.input_paths:
                self.selected_files_label.config(text=f"{len(self.input_paths)} arquivo(s) encontrado(s) na pasta")
            else:
                self.selected_files_label.config(text="Nenhum arquivo .webp encontrado na pasta")

    def select_output_dir(self):
        self.output_dir = filedialog.askdirectory(title="Selecione a pasta de destino")
        if self.output_dir:
            self.output_dir_label.config(text=self.output_dir)

    def start_conversion_thread(self):
        if not self.input_paths:
            messagebox.showerror("Erro", "Nenhum arquivo de entrada selecionado.")
            return
        if not self.output_dir:
            messagebox.showerror("Erro", "Nenhuma pasta de destino selecionada.")
            return

        self.btn_convert.config(state=tk.DISABLED)
        self.status_label.config(text="Convertendo...")
        self.progress_bar["value"] = 0
        self.progress_bar["maximum"] = len(self.input_paths)

        # Executa a conversão em uma thread separada para não travar a GUI
        conversion_thread = threading.Thread(target=self.run_conversion)
        conversion_thread.start()

    def run_conversion(self):
        frame_rate = self.fps_var.get()
        loop = self.loop_var.get()

        for i, file_path in enumerate(self.input_paths):
            convert_webp_to_gif(file_path, self.output_dir, frame_rate, loop)
            # Atualiza a GUI a partir da thread principal
            self.after(0, self.update_progress, i + 1)

        self.after(0, self.conversion_finished)

    def update_progress(self, value):
        self.progress_bar["value"] = value

    def conversion_finished(self):
        self.status_label.config(text="Conversão concluída com sucesso!")
        messagebox.showinfo("Sucesso", "Todos os arquivos foram convertidos!")
        self.btn_convert.config(state=tk.NORMAL)
        self.selected_files_label.config(text="Nenhum arquivo selecionado")
        self.input_paths = []

if __name__ == "__main__":
    app = App()
    app.mainloop()
