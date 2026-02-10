# pitch_correction.py
import librosa
import soundfile as sf

pitch_map = {
    "none": 0,
    "mild": 1,
    "moderate": 2,
    "strong": 3,
    "ultra": 5,
    "deep": -1,
    "lowered": -3,
    "demonic": -5,
}

def apply_pitch(path, mode):
    y, sr = librosa.load(path)

    steps = pitch_map.get(mode, 0)
    corrected = librosa.effects.pitch_shift(y, sr=sr, n_steps=steps)

    out_path = path.replace(".wav", "_corrected.wav")
    sf.write(out_path, corrected, sr)
    return out_path
