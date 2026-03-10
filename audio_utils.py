import os
import hashlib
from pydub import AudioSegment
from pydub.silence import detect_leading_silence

def get_chunk_cache_path(text, voice_path, language, temperature, top_p, cache_dir=".cache"):
    """Generates a stable cache path for a text chunk based on its content and settings."""
    # Create unique string representing the chunk and its settings
    settings = f"{text}|{voice_path}|{language}|{temperature}|{top_p}"
    h = hashlib.md5(settings.encode()).hexdigest()[:16]
    
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir, exist_ok=True)
        
    return os.path.join(cache_dir, f"chunk_{h}.wav")

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

def concatenate_wavs(wav_data, output_file, format="wav", sentence_gap_ms=300, paragraph_gap_ms=600):
    """
    Concatenates multiple WAV files with variable gaps.
    wav_data: list of dictionaries with {"path": str, "type": "sentence"|"paragraph"}
    """
    if not wav_data:
        raise ValueError("No WAV files to concatenate.")
    
    combined = AudioSegment.empty()
    sentence_silence = AudioSegment.silent(duration=sentence_gap_ms)
    paragraph_silence = AudioSegment.silent(duration=paragraph_gap_ms)
    
    for i, item in enumerate(wav_data):
        wav_file = item["path"]
        
        segment = AudioSegment.from_wav(wav_file)
        
        # Normalize each chunk to same loudness level
        segment = normalize_loudness(segment)
        
        # Trim leading/trailing silence with padding
        segment = trim_silence(segment)
        
        if i == 0:
            combined = segment
        else:
            # Add gap based on the PREVIOUS chunk type
            # (If the previous chunk ended a paragraph, use paragraph gap)
            prev_type = wav_data[i-1].get("type", "sentence")
            gap = paragraph_silence if prev_type == "paragraph" else sentence_silence
            combined += gap + segment
    
    combined.export(output_file, format=format)
    print(f"Exported optimized/cached audio to: {output_file}")

def cleanup_files(file_list):
    """Deletes temporary files."""
    for f in file_list:
        if os.path.exists(f):
            # We don't delete if it's in the .cache directory
            if ".cache" not in f:
                os.remove(f)
