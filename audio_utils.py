import os
from pydub import AudioSegment
from pydub.silence import detect_leading_silence

def normalize_loudness(audio, target_dbfs=-20.0):
    """Normalize chunk to consistent volume."""
    delta = target_dbfs - audio.dBFS
    return audio.apply_gain(delta)

def trim_silence(audio_segment, silence_threshold=-40.0, chunk_size=10, padding=50):
    """Trims leading and trailing silence from an AudioSegment with padding."""
    start_trim = detect_leading_silence(audio_segment, silence_threshold, chunk_size)
    end_trim = detect_leading_silence(audio_segment.reverse(), silence_threshold, chunk_size)
    
    duration = len(audio_segment)
    trimmed = audio_segment[start_trim:duration-end_trim]
    
    # Add small padding back
    if padding > 0:
        silence = AudioSegment.silent(duration=padding)
        trimmed = silence + trimmed + silence
    return trimmed

def concatenate_wavs(wav_files, output_file, format="wav", sentence_gap_ms=300):
    """Concatenates multiple WAV files with silence trimming, normalization, and gaps."""
    if not wav_files:
        raise ValueError("No WAV files to concatenate.")
    
    combined = AudioSegment.empty()
    sentence_silence = AudioSegment.silent(duration=sentence_gap_ms)
    
    for i, wav_file in enumerate(wav_files):
        segment = AudioSegment.from_wav(wav_file)
        
        # Normalize each chunk to same loudness level
        segment = normalize_loudness(segment)
        
        # Trim leading/trailing silence with padding
        segment = trim_silence(segment)
        
        if i == 0:
            combined = segment
        else:
            # Add gap
            combined += sentence_silence + segment
    
    combined.export(output_file, format=format)
    print(f"Exported normalized/gap-padded audio to: {output_file}")

def cleanup_files(file_list):
    """Deletes temporary files."""
    for file in file_list:
        if os.path.exists(file):
            os.remove(file)
