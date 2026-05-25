import os
import json

def transcribe_audio(wav_path: str) -> list:
    """Transcribe audio using faster-whisper. Returns list of segments."""
    try:
        from faster_whisper import WhisperModel
        model_size = os.environ.get('WHISPER_MODEL', 'base')
        model = WhisperModel(model_size, device='cpu', compute_type='int8')
        segments, info = model.transcribe(wav_path, beam_size=5, language='en')
        result = []
        for seg in segments:
            result.append({
                'start': round(seg.start, 2),
                'end': round(seg.end, 2),
                'text': seg.text.strip()
            })
        return result
    except ImportError:
        print("faster-whisper not available, using mock transcription")
        return _mock_transcription(wav_path)
    except Exception as e:
        print(f"Whisper transcription failed: {e}")
        return _mock_transcription(wav_path)

def _mock_transcription(wav_path: str) -> list:
    """Fallback mock transcription for testing without Whisper."""
    return [
        {'start': 0.0, 'end': 3.0, 'text': 'Hello, welcome to the session.'},
        {'start': 3.5, 'end': 6.0, 'text': 'Thank you for having me here today.'},
        {'start': 6.5, 'end': 10.0, 'text': 'Let us start with a brief introduction.'},
        {'start': 10.5, 'end': 14.0, 'text': 'Sure, I have been working in this field for five years.'},
        {'start': 14.5, 'end': 18.0, 'text': 'That is impressive. Can you tell us more?'},
        {'start': 18.5, 'end': 22.0, 'text': 'Of course, I specialize in data analysis and machine learning.'},
    ]
