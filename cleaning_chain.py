import librosa, soundfile as sf, numpy as np

def clean_vocals(path):
    y, sr = librosa.load(path)

    # Basic de-noise (spectral gating simulation)
    y_smooth = librosa.decompose.nn_filter(y, aggregate=np.median, metric="cosine")

    # Normalize
    y_norm = librosa.util.normalize(y_smooth)

    out = path.replace(".wav", "_clean.wav")
    sf.write(out, y_norm, sr)
    return out
