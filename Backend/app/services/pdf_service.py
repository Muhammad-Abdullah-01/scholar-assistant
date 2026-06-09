import fitz  # PyMuPDF
from typing import List

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file using PyMuPDF.
    """
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            page_text = page.get_text()
            text += page_text + "\n"
        return text.strip()
    except Exception as e:
        return f"Error extracting text: {e}"

def extract_texts_from_multiple_pdfs(file_paths: List[str]) -> List[str]:
    """
    Extract text from multiple PDFs.
    Returns a list of texts corresponding to each PDF.
    """
    texts = []
    for path in file_paths:
        texts.append(extract_text_from_pdf(path))
    return texts
