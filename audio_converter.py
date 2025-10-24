import os
import sys
from pydub import AudioSegment

def get_ffmpeg_path():
    """Determines the path to the bundled FFmpeg executable."""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    # The executable is expected in an 'assets' subdirectory
    ffmpeg_path = os.path.join(base_path, 'assets', 'ffmpeg.exe')

    # On non-Windows systems, the executable name might not have .exe
    if not os.path.exists(ffmpeg_path) and sys.platform != 'win32':
        ffmpeg_path = os.path.join(base_path, 'assets', 'ffmpeg')

    return ffmpeg_path

def convert_audio(input_path, output_dir, to_format, bitrate):
    """
    Converts an audio file to a specified format using pydub.

    Args:
        input_path (str): The full path to the input audio file.
        output_dir (str): The directory where the converted file will be saved.
        to_format (str): The target audio format (e.g., 'mp3', 'wav', 'flac').
        bitrate (str): The desired bitrate for the output file (e.g., '192k').

    Returns:
        bool: True if conversion was successful, False otherwise.
    """
    try:
        # Explicitly tell pydub where to find FFmpeg
        AudioSegment.converter = get_ffmpeg_path()

        # Load the audio file
        audio = AudioSegment.from_file(input_path)

        # Construct the output path
        file_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(output_dir, f"{file_name}.{to_format.lower()}")

        # Perform the conversion
        audio.export(output_path, format=to_format.lower(), bitrate=bitrate)

        print(f"Successfully converted {input_path} to {output_path}")
        return True
    except Exception as e:
        print(f"Error converting {input_path}: {e}")
        return False
