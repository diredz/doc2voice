import os
from pypdf import PdfReader
from docx import Document

def extract_from_pdf(file_path):
    """Extracts text from a PDF file."""
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return prepare_text(text)

def extract_from_docx(file_path):
    """Extracts text from a DOCX file."""
    doc = Document(file_path)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return prepare_text(text)

def extract_from_txt(file_path):
    """Extracts text from a TXT file."""
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    return prepare_text(text)

def prepare_text(text):
    """Normalizes whitespace and prepares text for processing."""
    # Normalize whitespace: replace multiple spaces with single space, multiple newlines with double newline (paragraph break)
    import re
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    # Strip leading/trailing whitespace
    return text.strip()

def extract_text(file_path):
    """Dispatches extraction based on file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_from_pdf(file_path)
    elif ext == ".docx":
        return extract_from_docx(file_path)
    elif ext == ".txt":
        return extract_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
