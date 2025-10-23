import os
from PIL import Image

def convert_image(input_path, output_dir, to_format, settings=None):
    if settings is None:
        settings = {}
    to_format_lower = to_format.lower()

    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(output_dir, f"{base_name}.{to_format_lower}")

        i = 1
        while os.path.exists(output_path):
            output_path = os.path.join(output_dir, f"{base_name}-{i}.{to_format_lower}")
            i += 1

        with Image.open(input_path) as img:
            # --- Resize Logic ---
            width = settings.get('width')
            height = settings.get('height')
            if width and height:
                w, h = int(width), int(height)
                if settings.get('keep_aspect_ratio', True):
                    img.thumbnail((w, h))
                else:
                    img = img.resize((w, h))

            save_params = {}

            # Handle animated formats
            is_animated = hasattr(img, 'n_frames') and img.n_frames > 1

            if to_format_lower == 'gif' and is_animated:
                frames = []
                for i in range(img.n_frames):
                    img.seek(i)
                    quantized_frame = img.convert("RGBA").quantize(colors=256, dither=Image.Dither.FLOYDSTEINBERG)
                    frames.append(quantized_frame)

                if frames:
                    frames[0].save(
                        output_path, 'gif', save_all=True, append_images=frames[1:],
                        duration=int(1000 / settings.get('frame_rate', 10)),
                        loop=0 if settings.get('loop', True) else 1,
                        disposal=2, transparency=img.info.get('transparency')
                    )
                return output_path

            elif to_format_lower == 'webp' and is_animated:
                save_params.update({
                    'lossless': settings.get('lossless', False),
                    'quality': int(settings.get('quality', 80)),
                    'method': 6,
                    'duration': img.info.get('duration', 100),
                    'loop': img.info.get('loop', 0),
                    'save_all': True,
                })

            # Handle static images and single-frame conversions
            if to_format_lower in ['jpeg', 'jpg', 'bmp'] and img.mode == 'RGBA':
                img = img.convert('RGB')

            if to_format_lower in ['jpeg', 'jpg', 'webp']:
                save_params['quality'] = int(settings.get('quality', 95))

            img.save(output_path, format=to_format, **save_params)

        return output_path
    except Exception as e:
        print(f"Erro ao converter {input_path} para {to_format}: {e}")
        return None
