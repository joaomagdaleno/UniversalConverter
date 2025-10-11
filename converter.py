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
            # Prepara os parâmetros para salvar o GIF
            save_params = {
                'save_all': True,
                'append_images': [],
                'duration': int(1000 / frame_rate),
                'loop': loop,
                'disposal': 2  # Mantém o fundo transparente
            }

            # Garante que a transparência seja mantida
            if 'transparency' in img.info:
                save_params['transparency'] = img.info['transparency']

            # Adiciona todos os frames se for um .webp animado
            if img.n_frames > 1:
                # O primeiro frame já está carregado, então adicionamos do segundo em diante
                for frame in range(1, img.n_frames):
                    img.seek(frame)
                    save_params['append_images'].append(img.copy())

            # Volta para o primeiro frame para salvar
            img.seek(0)
            img.save(output_path, 'gif', **save_params)

        return output_path
    except Exception as e:
        print(f"Ocorreu um erro ao converter o arquivo {input_path}: {e}")
        return None
