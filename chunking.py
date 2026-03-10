import re

def split_into_sentences(text):
    """Splits text into sentences using regex."""
    # Split by period, question mark, or exclamation mark followed by whitespace
    # Using lookbehind to keep the punctuation
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]

def chunk_text(text, max_len=400):
    """Chunks text into segments of manageable length (sentences)."""
    sentences = split_into_sentences(text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        # If adding the sentence exceeds max_len and chunk is not empty
        if len(current_chunk) + len(sentence) + 1 > max_len and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            if current_chunk:
                current_chunk += " " + sentence
            else:
                current_chunk = sentence
    
    # Don't forget the last chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
        
    return chunks
