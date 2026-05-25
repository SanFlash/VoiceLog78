import json
import os
import numpy as np

def detect_speakers(wav_path: str, segments: list) -> dict:
    """
    Detect speakers using energy/pitch analysis with librosa.
    Falls back to pyannote if available and HF token is set.
    """
    hf_token = os.environ.get('HUGGINGFACE_TOKEN')
    if hf_token:
        try:
            return _pyannote_diarization(wav_path, segments, hf_token)
        except Exception as e:
            print(f"Pyannote failed, using energy-based fallback: {e}")

    return _energy_based_diarization(wav_path, segments)

def _energy_based_diarization(wav_path: str, segments: list) -> dict:
    """
    Energy + pitch-based speaker segmentation using librosa.
    Groups segments by similar vocal characteristics.
    """
    try:
        import librosa
        y, sr = librosa.load(wav_path, sr=16000)
        
        seg_features = []
        for seg in segments:
            start_sample = int(seg['start'] * sr)
            end_sample = int(seg['end'] * sr)
            chunk = y[start_sample:end_sample]
            
            if len(chunk) < 100:
                seg_features.append({'segment': seg, 'pitch_mean': 0, 'energy': 0})
                continue

            # Extract pitch using librosa
            pitches, magnitudes = librosa.piptrack(y=chunk, sr=sr, threshold=0.1)
            pitch_vals = pitches[pitches > 0]
            pitch_mean = float(np.mean(pitch_vals)) if len(pitch_vals) > 0 else 0

            # Extract RMS energy
            rms = librosa.feature.rms(y=chunk)
            energy = float(np.mean(rms))

            seg_features.append({
                'segment': seg,
                'pitch_mean': pitch_mean,
                'energy': energy
            })

        # Cluster into speakers using pitch ranges
        labeled = _assign_speakers_by_pitch(seg_features)
        speaker_count = len(set(s['speaker'] for s in labeled))

        transcript_data = []
        for item in labeled:
            transcript_data.append({
                'speaker': item['speaker'],
                'text': item['segment']['text'],
                'start': item['segment']['start'],
                'end': item['segment']['end']
            })

        return {
            'speaker_count': speaker_count,
            'transcript_json': json.dumps(transcript_data)
        }

    except ImportError:
        print("librosa not available, using simple alternating speaker assignment")
        return _simple_alternating(segments)
    except Exception as e:
        print(f"Energy-based diarization failed: {e}, using simple alternating")
        return _simple_alternating(segments)

def _assign_speakers_by_pitch(seg_features: list) -> list:
    """Assign speakers based on pitch clustering."""
    if not seg_features:
        return []

    pitches = [f['pitch_mean'] for f in seg_features if f['pitch_mean'] > 0]
    
    if not pitches or len(pitches) < 2:
        # All same speaker
        for f in seg_features:
            f['speaker'] = 'Person 1'
        return seg_features

    median_pitch = float(np.median(pitches))
    std_pitch = float(np.std(pitches))

    # Detect if there's meaningful pitch variation (multiple speakers)
    if std_pitch < 30:
        for f in seg_features:
            f['speaker'] = 'Person 1'
        return seg_features

    # Cluster into 2-3 speakers using pitch ranges
    low_thresh = median_pitch - std_pitch * 0.3
    high_thresh = median_pitch + std_pitch * 0.3
    
    speaker_map = {}
    speaker_counter = 1

    for f in seg_features:
        p = f['pitch_mean']
        if p == 0:
            bucket = 'mid'
        elif p < low_thresh:
            bucket = 'low'
        elif p > high_thresh:
            bucket = 'high'
        else:
            bucket = 'mid'

        if bucket not in speaker_map:
            speaker_map[bucket] = f'Person {speaker_counter}'
            speaker_counter += 1

        f['speaker'] = speaker_map[bucket]

    return seg_features

def _simple_alternating(segments: list) -> dict:
    """Simple fallback: alternate between Person 1 and Person 2 at pauses."""
    transcript_data = []
    current_speaker = 1
    prev_end = 0

    for seg in segments:
        gap = seg['start'] - prev_end
        # Switch speaker on gaps > 1.5s
        if gap > 1.5 and prev_end > 0:
            current_speaker = 2 if current_speaker == 1 else 1

        transcript_data.append({
            'speaker': f'Person {current_speaker}',
            'text': seg['text'],
            'start': seg['start'],
            'end': seg['end']
        })
        prev_end = seg['end']

    speaker_count = len(set(s['speaker'] for s in transcript_data))
    return {
        'speaker_count': speaker_count,
        'transcript_json': json.dumps(transcript_data)
    }

def _pyannote_diarization(wav_path: str, segments: list, hf_token: str) -> dict:
    """Use pyannote.audio for accurate speaker diarization."""
    from pyannote.audio import Pipeline
    import torch

    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        use_auth_token=hf_token
    )
    diarization = pipeline(wav_path)

    # Map Whisper segments to pyannote speakers
    speaker_turns = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        speaker_turns.append({'start': turn.start, 'end': turn.end, 'speaker': speaker})

    transcript_data = []
    for seg in segments:
        seg_mid = (seg['start'] + seg['end']) / 2
        matched_speaker = 'Person 1'
        for turn in speaker_turns:
            if turn['start'] <= seg_mid <= turn['end']:
                # Normalize speaker label to Person N
                speaker_num = int(turn['speaker'].split('_')[-1]) + 1
                matched_speaker = f'Person {speaker_num}'
                break
        transcript_data.append({
            'speaker': matched_speaker,
            'text': seg['text'],
            'start': seg['start'],
            'end': seg['end']
        })

    speaker_count = len(set(s['speaker'] for s in transcript_data))
    return {
        'speaker_count': speaker_count,
        'transcript_json': json.dumps(transcript_data)
    }
