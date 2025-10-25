import os
import subprocess

def convert_video(input_path, output_dir, to_format, settings=None):
    """
    Converts a video file to a different format using FFmpeg.

    :param input_path: Path to the input video file.
    :param output_dir: Directory to save the converted file.
    :param to_format: The target video format (e.g., 'mp4', 'webm').
    :param settings: A dictionary of conversion settings. Expected keys: 'resolution', 'quality'.
    """
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

        # Build the FFmpeg command
        command = ['ffmpeg', '-i', input_path]

        # --- Apply settings ---
        resolution = settings.get('resolution')
        if resolution and resolution != "Manter original":
            height = resolution.replace('p', '')
            command.extend(['-vf', f'scale=-2:{height}'])

        quality = settings.get('quality')
        if quality:
            # CRF values: Lower is better quality, higher is smaller size.
            # These are just example values, they can be tuned.
            if quality == "Alta":
                command.extend(['-crf', '18'])
            elif quality == "Média":
                command.extend(['-crf', '23'])
            elif quality == "Baixa":
                command.extend(['-crf', '28'])

        command.append(output_path)

        # Execute the command
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return True
    except subprocess.CalledProcessError as e:
        print(f"Error converting {input_path} to {to_format}:")
        print(f"FFmpeg stderr: {e.stderr.decode('utf-8')}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False
