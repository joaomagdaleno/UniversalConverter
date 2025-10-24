import os
import sys
import subprocess

def get_ffmpeg_path():
    """Determines the path to the bundled FFmpeg executable."""
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    ffmpeg_path = os.path.join(base_path, 'assets', 'ffmpeg.exe')
    if not os.path.exists(ffmpeg_path) and sys.platform != 'win32':
        ffmpeg_path = os.path.join(base_path, 'assets', 'ffmpeg')
    return ffmpeg_path

def convert_video(input_path, output_dir, to_format, resolution, quality):
    """
    Converts a video file to a specified format using FFmpeg.

    Args:
        input_path (str): The full path to the input video file.
        output_dir (str): The directory where the converted file will be saved.
        to_format (str): The target video format (e.g., 'mp4', 'webm').
        resolution (str): The target resolution (e.g., '1280x720', '_').
        quality (str): The quality preset (e.g., 'Low', 'Medium', 'High').

    Returns:
        bool: True if conversion was successful, False otherwise.
    """
    try:
        ffmpeg_path = get_ffmpeg_path()
        file_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(output_dir, f"{file_name}.{to_format.lower()}")

        # Base FFmpeg command
        command = [
            ffmpeg_path,
            '-i', input_path,
        ]

        # --- Add conversion settings ---

        # Resolution scaling
        if resolution != '_':
            command.extend(['-vf', f'scale={resolution}'])

        # Quality setting (using CRF - Constant Rate Factor)
        # Lower CRF is higher quality. 23 is default for x264.
        crf_value = '28' # Default to 'Low' quality
        if quality == 'Medium':
            crf_value = '23'
        elif quality == 'High':
            crf_value = '18'

        # Codec-specific quality flags
        if to_format.lower() == 'mp4':
            command.extend(['-c:v', 'libx264', '-crf', crf_value])
        elif to_format.lower() == 'webm':
            # For VP9, CRF values are in a different range (0-63). Higher is lower quality.
            # Mapping Low/Medium/High to VP9 CRF values
            crf_value = '35' # Low
            if quality == 'Medium':
                crf_value = '31'
            elif quality == 'High':
                crf_value = '25'
            command.extend(['-c:v', 'libvpx-vp9', '-crf', crf_value, '-b:v', '0'])

        # Always copy the audio stream without re-encoding
        command.extend(['-c:a', 'copy'])

        # Output path and overwrite flag
        command.extend([output_path, '-y'])

        print(f"Executing FFmpeg command: {' '.join(command)}")

        # Execute the command
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        print(f"Successfully converted {input_path} to {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error converting {input_path}:")
        print(f"FFmpeg stdout: {e.stdout.decode()}")
        print(f"FFmpeg stderr: {e.stderr.decode()}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False
