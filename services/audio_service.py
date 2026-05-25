import subprocess
import os

def convert_to_wav(input_path: str, output_path: str) -> bool:
    """Convert audio file to WAV using FFmpeg."""
    try:
        cmd = [
            'ffmpeg', '-y',
            '-i', input_path,
            '-ar', '16000',   # 16kHz sample rate for Whisper
            '-ac', '1',       # Mono
            '-f', 'wav',
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=120)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        print(f"FFmpeg conversion failed: {e}")
        # Try with pydub as fallback
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(input_path)
            audio = audio.set_frame_rate(16000).set_channels(1)
            audio.export(output_path, format='wav')
            return True
        except Exception as e2:
            print(f"Pydub fallback also failed: {e2}")
            return False
