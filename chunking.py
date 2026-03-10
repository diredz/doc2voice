import re

def chunk_text(text: str, max_chars: int = 400) -> list[dict]:
    """Chunks text with type tags: 'sentence' or 'paragraph'"""
    chunks = []
    # Using \r?\n\r?\n to handle different line endings
    paragraphs = re.split(r'\n\s*\n', text)
    
    for para in paragraphs:
        if not para.strip():
            continue
            
        # Split by period, question mark, or exclamation mark followed by whitespace
        sentences = re.split(r'(?<=[.!?])\s+', para.strip())
        buffer = ""
        for sent in sentences:
            if not sent.strip():
                continue
            if len(buffer) + len(sent) < max_chars:
                if buffer:
                    buffer += " " + sent
                else:
                    buffer = sent
            else:
                if buffer:
                    chunks.append({"text": buffer.strip(), "type": "sentence"})
                buffer = sent
        
        # The end of a paragraph is tagged as 'paragraph'
        if buffer:
            chunks.append({"text": buffer.strip(), "type": "paragraph"})
    
    return chunks
