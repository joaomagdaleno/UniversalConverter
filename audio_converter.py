import os
from pydub import AudioSegment

def convert_audio(input_path, output_dir, to_format, settings=None):
    """
    Converts an audio file to a different format using pydub.

    :param input_path: Path to the input audio file.
    :param output_dir: Directory to save the converted file.
    :param to_format: The target audio format (e.g., 'mp3', 'wav', 'flac').
    :param settings: A dictionary of conversion settings. Expected keys: 'bitrate'.
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

        audio = AudioSegment.from_file(input_path)

        export_params = {
            'format': to_format_lower
        }
        bitrate = settings.get('bitrate')
        if bitrate and to_format_lower == 'mp3':
            export_params['bitrate'] = f"{bitrate}k"

        audio.export(output_path, **export_params)

        return True
    except Exception as e:
        print(f"Error converting {input_path} to {to_format}: {e}")
        return False
