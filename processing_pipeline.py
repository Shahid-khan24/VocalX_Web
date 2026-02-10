# processing_pipeline.py
import os
from demucs_runner import separate_stems
from export_manager import export_outputs
from pitch_correction import apply_pitch

def process_file(path, output_type, pitch_mode):
    stems = separate_stems(path)

    vocals = stems["vocals"]
    instrumental = stems["instrumental"]

    # Pitch correction
    corrected = apply_pitch(vocals, pitch_mode)

    return export_outputs(
        vocals,
        instrumental,
        corrected,
        output_type,
        original_video=path
    )
