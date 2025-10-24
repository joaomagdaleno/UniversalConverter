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
            width = settings.get('width')
            height = settings.get('height')
            if width and height:
                try:
                    w, h = int(width), int(height)
                    if settings.get('keep_aspect_ratio', True):
                        img.thumbnail((w, h))
                    else:
                        img = img.resize((w, h))
                except (ValueError, TypeError):
                    pass

            save_params = {}
            is_animated = hasattr(img, 'n_frames') and img.n_frames > 1

            if to_format_lower == 'gif' and is_animated:
                frames = [frame.copy().convert("RGBA").quantize(colors=256, dither=Image.Dither.FLOYDSTEINBERG) for frame in Image.ImageSequence.Iterator(img)]
                if frames:
                    frames[0].save(
                        output_path, 'gif', save_all=True, append_images=frames[1:],
                        duration=img.info.get('duration', 100), loop=img.info.get('loop', 0),
                        disposal=2, transparency=img.info.get('transparency', -1)
                    )
                return True

            elif to_format_lower == 'webp' and is_animated:
                save_params.update({
                    'lossless': settings.get('lossless', False),
                    'quality': int(settings.get('quality', 80)),
                    'method': 6,
                    'duration': img.info.get('duration', 100),
                    'loop': img.info.get('loop', 0),
                })
                img.save(output_path, 'webp', save_all=True, **save_params)
                return True

            if to_format_lower in ['jpeg', 'jpg', 'bmp'] and img.mode == 'RGBA':
                img = img.convert('RGB')

            if to_format_lower in ['jpeg', 'jpg', 'webp']:
                save_params['quality'] = int(settings.get('quality', 95))

            img.save(output_path, format=to_format, **save_params)

        return True
    except Exception as e:
        print(f"Error converting {input_path} to {to_format}: {e}")
        return False
