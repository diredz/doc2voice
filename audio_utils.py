import os
from pydub import AudioSegment
from pydub.silence import detect_leading_silence

def trim_silence(audio_segment, silence_threshold=-50.0, chunk_size=10):
    """Trims leading and trailing silence from an AudioSegment."""
    start_trim = detect_leading_silence(audio_segment, silence_threshold, chunk_size)
    end_trim = detect_leading_silence(audio_segment.reverse(), silence_threshold, chunk_size)
    
    duration = len(audio_segment)
    return audio_segment[start_trim:duration-end_trim]

def concatenate_wavs(wav_files, output_file, format="wav", crossfade_ms=50):
    """Concatenates multiple WAV files with silence trimming and crossfading."""
    if not wav_files:
        raise ValueError("No WAV files to concatenate.")
    
    combined = AudioSegment.empty()
    for i, wav_file in enumerate(wav_files):
        segment = AudioSegment.from_wav(wav_file)
        # Trim silence from the start and end of each chunk
        segment = trim_silence(segment)
        
        if i == 0:
            combined = segment
        else:
            # Apply crossfade to smooth transitions
            # Ensure the segment is long enough for crossfade
            actual_crossfade = min(crossfade_ms, len(combined), len(segment))
            if actual_crossfade > 0:
                combined = combined.append(segment, crossfade=actual_crossfade)
            else:
                combined += segment
    
    combined.export(output_file, format=format)
    print(f"Exported optimized combined audio to: {output_file}")

def cleanup_files(file_list):
    """Deletes temporary files."""
    for file in file_list:
        if os.path.exists(file):
            os.remove(file)
