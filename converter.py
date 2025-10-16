import os
from PIL import Image

def convert_webp_to_gif(input_path, output_dir, frame_rate=10, loop=0):
    """
    Converte uma imagem .webp para .gif.

    Args:
        input_path (str): O caminho para a imagem .webp de entrada.
        output_dir (str): O diretório para salvar a imagem .gif de saída.
        frame_rate (int): A taxa de quadros para o .gif (quadros por segundo).
        loop (int): O número de vezes que o GIF deve repetir (0 para sempre).

    Returns:
        str: O caminho para o arquivo .gif de saída, ou None se a conversão falhar.
    """
    try:
        # Garante que o diretório de saída exista
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Define o nome do arquivo de saída
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(output_dir, f"{base_name}.gif")

        # Verifica se um arquivo com o mesmo nome já existe e adiciona um número se necessário
        i = 1
        while os.path.exists(output_path):
            output_path = os.path.join(output_dir, f"{base_name}-{i}.gif")
            i += 1

        # Abre a imagem .webp com o Pillow
        with Image.open(input_path) as img:
            # Processa cada frame para aplicar dithering e otimizar a paleta
            frames = []
            for i in range(img.n_frames):
                img.seek(i)
                # Converte para RGBA e aplica quantização com dithering Floyd-Steinberg
                quantized_frame = img.convert("RGBA").quantize(colors=256, dither=Image.Dither.FLOYDSTEINBERG)
                frames.append(quantized_frame)

            # Salva os frames processados como um GIF animado
            if frames:
                frames[0].save(
                    output_path,
                    'gif',
                    save_all=True,
                    append_images=frames[1:],
                    duration=int(1000 / frame_rate),
                    loop=loop,
                    disposal=2,
                    # Garante que a transparência seja preservada corretamente
                    transparency=img.info.get('transparency')
                )

        return output_path
    except Exception as e:
        print(f"Ocorreu um erro ao converter o arquivo {input_path}: {e}")
        return None


def convert_gif_to_webp(input_path, output_dir, lossless=False, quality=80):
    """
    Converte uma imagem .gif para .webp.

    Args:
        input_path (str): O caminho para a imagem .gif de entrada.
        output_dir (str): O diretório para salvar a imagem .webp de saída.
        lossless (bool): Se verdadeiro, usa compressão sem perdas.
        quality (int): A qualidade da compressão com perdas (1-100).

    Returns:
        str: O caminho para o arquivo .webp de saída, ou None se a conversão falhar.
    """
    try:
        # Garante que o diretório de saída exista
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Define o nome do arquivo de saída
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(output_dir, f"{base_name}.webp")

        # Verifica se um arquivo com o mesmo nome já existe e adiciona um número se necessário
        i = 1
        while os.path.exists(output_path):
            output_path = os.path.join(output_dir, f"{base_name}-{i}.webp")
            i += 1

        # Abre a imagem .gif com o Pillow
        with Image.open(input_path) as img:
            # Prepara os parâmetros para salvar o WebP animado
            save_params = {
                'lossless': lossless,
                'quality': quality,
                'method': 6,  # Usa o método de compressão mais lento para a melhor qualidade
                'duration': img.info.get('duration', 100),
                'loop': img.info.get('loop', 0)
            }

            # O Pillow lida com os frames automaticamente ao usar save_all=True
            img.save(output_path, 'webp', save_all=True, **save_params)

        return output_path
    except Exception as e:
        print(f"Ocorreu um erro ao converter o arquivo {input_path}: {e}")
        return None
