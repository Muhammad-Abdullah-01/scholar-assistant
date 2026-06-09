import re
import unicodedata

def clean_extracted_text(text: str) -> str:
    """
    Clean and normalize extracted text from PDFs or DOCX files.
    Removes headers, footers, line breaks, special symbols, and redundant spaces.
    """

    # Normalizing unicode characters 
    text = unicodedata.normalize("NFKC", text)

    # Removing common artifacts such as headers/footers, page numbers
    text = re.sub(r"Page\s*\d+(\s*of\s*\d+)?", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\n?\s*\d+\s*\n", " ", text)  # stray numbers (page numbers, footnotes)

    # Removing multiple newlines and replace with one
    text = re.sub(r"\n+", "\n", text)

    # Removing hyphenation across line breaks (e.g., "informa-\ntion" → "information")
    text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)

    # Replacing newlines within paragraphs with spaces
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)

    # Removing unwanted symbols or control characters
    text = re.sub(r"[^\x00-\x7F]+", " ", text)  # non-ASCII chars
    text = re.sub(r"[•·●▪■□▶►]", " ", text)    # bullet symbols

    # Removing excessive whitespace
    text = re.sub(r"\s+", " ", text)

    # Removing references section if not needed (optional)
    text = re.sub(r"(References|Bibliography)[\s\S]*$", "", text, flags=re.IGNORECASE)

    # Strip leading
    text = text.strip()

    return text