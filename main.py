import argparse
import os
import tempfile
import time
from text_extraction import extract_text
from chunking import chunk_text
from tts_engine import TTSEngine
from audio_utils import concatenate_wavs, cleanup_files

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
    print(f"[*] Splitting text into chunks (max_len={args.chunk_max_len})...")
    chunks = chunk_text(raw_text, max_len=args.chunk_max_len)
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

    tmp_files = []
    print("[*] Starting TTS generation...")
    
    start_time = time.time()
    for i, text in enumerate(chunks):
        suffix = f".chunk_{i}.wav"
        # We use a temporary file for each chunk
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp_path = tmp.name
        
        print(f"    [Chunk {i+1}/{num_chunks}] Generating speech...")
        try:
            engine.generate_speech(
                text=text, 
                speaker_wav=args.voice, 
                language=args.lang, 
                output_path=tmp_path,
                temperature=args.temperature,
                top_p=args.top_p
            )
            tmp_files.append(tmp_path)
        except Exception as e:
            print(f"    Error generating chunk {i+1}: {e}")
            # Continue with others if possible or fail?
    
    # 4. Audio Merging
    if tmp_files:
        print(f"[*] Concatenating {len(tmp_files)} audio chunks into {args.out}...")
        try:
            concatenate_wavs(tmp_files, args.out, format=args.format)
        except Exception as e:
            print(f"Error merging audio: {e}")
        finally:
            print("[*] Cleaning up temporary files...")
            cleanup_files(tmp_files)
    
    end_time = time.time()
    elapsed = end_time - start_time
    print(f"\n[+] Processing complete!")
    print(f"    Output: {args.out}")
    print(f"    Elapsed time: {elapsed:.2f}s")

if __name__ == "__main__":
    main()
