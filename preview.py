import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox
import os
from converter import convert_gif_to_webp # Assumindo que a lógica de conversão está aqui
import tempfile

class PreviewWindow(ttk.Toplevel):
    def __init__(self, parent, input_path, output_dir):
        super().__init__(parent)
        self.transient(parent)
        self.title("Pré-visualização da Conversão")
        self.geometry("500x400")
        self.resizable(False, False)

        self.parent = parent
        self.input_path = input_path
        self.output_dir = output_dir
        self.temp_output_path = None
        self.final_output_path = None

        self.lossless_var = tk.BooleanVar(value=parent.lossless_var.get())
        self.quality_var = tk.IntVar(value=parent.quality_var.get())

        self.create_widgets()
        self.update_preview()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        info_frame = ttk.LabelFrame(main_frame, text="Informações", padding="10")
        info_frame.pack(fill=tk.X)

        self.original_size = os.path.getsize(self.input_path) / 1024
        ttk.Label(info_frame, text=f"Original: {os.path.basename(self.input_path)}").grid(row=0, column=0, sticky="w")
        ttk.Label(info_frame, text=f"Tamanho: {self.original_size:.2f} KB").grid(row=0, column=1, sticky="e", padx=10)

        self.preview_label = ttk.Label(info_frame, text="Pré-visualização:")
        self.preview_label.grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.preview_size_label = ttk.Label(info_frame, text="Tamanho: ...")
        self.preview_size_label.grid(row=1, column=1, sticky="e", padx=10, pady=(10, 0))

        settings_frame = ttk.LabelFrame(main_frame, text="Ajustar Qualidade", padding="10")
        settings_frame.pack(fill=tk.X, pady=15)

        ttk.Checkbutton(settings_frame, text="Compressão sem Perdas", variable=self.lossless_var, command=self.toggle_quality_slider, bootstyle="primary-round-toggle").grid(row=0, column=0, columnspan=2, sticky="w")

        self.quality_label = ttk.Label(settings_frame, text="Qualidade (1-100):")
        self.quality_label.grid(row=1, column=0, sticky="w", pady=5)

        self.quality_slider = ttk.Scale(settings_frame, from_=1, to=100, orient=tk.HORIZONTAL, variable=self.quality_var, length=250, bootstyle="info")
        self.quality_slider.grid(row=1, column=1, sticky="w", pady=5)
        self.toggle_quality_slider()

        btn_update = ttk.Button(settings_frame, text="Atualizar Pré-visualização", command=self.update_preview, bootstyle="info")
        btn_update.grid(row=2, column=0, columnspan=2, pady=10)

        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, side="bottom", pady=(10,0))

        ttk.Button(action_frame, text="Salvar", command=self.save, bootstyle="success").pack(side="right")
        ttk.Button(action_frame, text="Cancelar", command=self.destroy, bootstyle="secondary").pack(side="right", padx=10)

    def toggle_quality_slider(self):
        state = "disabled" if self.lossless_var.get() else "normal"
        self.quality_slider.config(state=state)
        self.quality_label.config(state=state)

    def update_preview(self):
        lossless = self.lossless_var.get()
        quality = self.quality_var.get()

        temp_dir = tempfile.gettempdir()

        self.temp_output_path = convert_gif_to_webp(self.input_path, temp_dir, lossless=lossless, quality=quality)

        if self.temp_output_path and os.path.exists(self.temp_output_path):
            preview_size = os.path.getsize(self.temp_output_path) / 1024
            reduction = 100 - (preview_size / self.original_size * 100)
            self.preview_size_label.config(text=f"Tamanho: {preview_size:.2f} KB ({reduction:.1f}% menor)")
        else:
            self.preview_size_label.config(text="Falha na conversão.")

    def save(self):
        if self.temp_output_path and os.path.exists(self.temp_output_path):
            base_name = os.path.splitext(os.path.basename(self.input_path))[0]
            output_path = os.path.join(self.output_dir, f"{base_name}.webp")
            i = 1
            while os.path.exists(output_path):
                output_path = os.path.join(self.output_dir, f"{base_name}-{i}.webp")
                i += 1

            os.rename(self.temp_output_path, output_path)
            self.final_output_path = output_path
            messagebox.showinfo("Sucesso", f"Arquivo salvo em:\n{self.final_output_path}", parent=self)
            self.destroy()
        else:
            messagebox.showerror("Erro", "Nenhuma pré-visualização válida para salvar.", parent=self)

    def destroy(self):
        if self.temp_output_path and os.path.exists(self.temp_output_path) and not self.final_output_path:
            os.remove(self.temp_output_path)
        super().destroy()
