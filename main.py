import argparse
import os
import tempfile
import time
from text_extraction import extract_text
from chunking import chunk_text
from tts_engine import TTSEngine
from audio_utils import concatenate_wavs, cleanup_files, get_chunk_cache_path

"""
doc2voice - Convert documents to personalized speech using Coqui XTTS-v2.

Licensing:
XTTS-v2 is under the Coqui Public Model License (CPML). 
This tool is intended for strictly personal/non-commercial use.
Commercial users must verify licensing.
"""

def main():
    parser = argparse.ArgumentParser(description="Convert PDF/TXT/DOCX to personalized speech.")
    parser.add_argument("--input", required=True, help="Path to PDF, TXT, or DOCX file.")
    parser.add_argument("--voice", required=True, help="Path to reference speaker WAV.")
    parser.add_argument("--lang", default="en", help="Language code (e.g., 'en', 'de', 'fr').")
    parser.add_argument("--out", default="output.wav", help="Path to output audio file.")
    parser.add_argument("--chunk-max-len", type=int, default=400, help="Max length per text chunk.")
    parser.add_argument("--format", default="wav", choices=["wav", "mp3"], help="Output audio format.")
    parser.add_argument("--temperature", type=float, default=0.75, help="TTS temperature (higher = expressive, lower = stable).")
    parser.add_argument("--top-p", type=float, default=0.85, help="TTS top_p sampling.")

    args = parser.parse_args()

    # 1. Extraction
    print(f"[*] Extracting text from {args.input}...")
    try:
        raw_text = extract_text(args.input)
    except Exception as e:
        print(f"Error extracting text: {e}")
        return

    print(f"[*] Extracted {len(raw_text)} characters.")

    # 2. Chunking
    print(f"[*] Splitting text into chunks (max_chars={args.chunk_max_len})...")
    chunks = chunk_text(raw_text, max_chars=args.chunk_max_len)
    num_chunks = len(chunks)
    print(f"[*] Created {num_chunks} chunks.")

    if not chunks:
        print("No text found after extraction.")
        return

    # 3. TTS Generation
    print("[*] Initializing TTS engine...")
    try:
        engine = TTSEngine()
    except Exception as e:
        print(f"Error initializing TTS engine: {e}")
        return

    tmp_files = [] # Will store list of {"path": ..., "type": ...}
    print("[*] Starting TTS generation...")
    
    start_time = time.time()
    for i, chunk_data in enumerate(chunks):
        text = chunk_data["text"]
        chunk_type = chunk_data["type"]
        
        # Support multiple voices (comma separated in CLI)
        voice_paths = [v.strip() for v in args.voice.split(",")] if "," in args.voice else args.voice
        
        # Caching logic
        cache_path = get_chunk_cache_path(
            text=text,
            voice_path=str(voice_paths),
            language=args.lang,
            temperature=args.temperature,
            top_p=args.top_p
        )
        
        if os.path.exists(cache_path):
            print(f"    [Chunk {i+1}/{num_chunks}] Using cached audio...")
            tmp_files.append({"path": cache_path, "type": chunk_type})
            continue

        print(f"    [Chunk {i+1}/{num_chunks}] Generating speech...")
        try:
            engine.generate_speech(
                text=text, 
                speaker_wav=voice_paths, 
                language=args.lang, 
                output_path=cache_path,
                temperature=args.temperature,
                top_p=args.top_p
            )
            tmp_files.append({"path": cache_path, "type": chunk_type})
        except Exception as e:
            print(f"    Error generating chunk {i+1}: {e}")
    
    # 4. Audio Merging
    if tmp_files:
        print(f"[*] Concatenating {len(tmp_files)} audio chunks into {args.out}...")
        try:
            concatenate_wavs(tmp_files, args.out, format=args.format)
        except Exception as e:
            print(f"Error merging audio: {e}")
        finally:
            print("[*] Cleaning up temporary files...")
            cleanup_files([f["path"] for f in tmp_files])
    
    end_time = time.time()
    elapsed = end_time - start_time
    print(f"\n[+] Processing complete!")
    print(f"    Output: {args.out}")
    print(f"    Elapsed time: {elapsed:.2f}s")

if __name__ == "__main__":
    main()
