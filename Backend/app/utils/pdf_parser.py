import fitz  # PyMuPDF
import docx
from io import BytesIO
from lxml import etree
from typing import Dict


def parse_pdf_with_formulas(file_bytes: bytes) -> Dict[str, str]:
    """
    Extract text and approximate mathematical formulas from a PDF.
    Note: Real math extraction depends on how the PDF was created.
    """
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text_content = ""
    formulas = []

    for page in doc:
        text = page.get_text("text")
        text_content += text

        # Detect likely math expressions (heuristic)
        lines = text.splitlines()
        for line in lines:
            if any(sym in line for sym in ["∑", "∫", "√", "≈", "≤", "≥", "^", "_", "π", "θ", "∞", "="]):
                formulas.append(line.strip())

    doc.close()
    return {"text": text_content.strip(), "formulas": "\n".join(formulas)}


def parse_docx_with_formulas(file_bytes: bytes) -> Dict[str, str]:
    """
    Extract text and math formulas (OMML/MathML) from DOCX files.
    """
    text_content = ""
    formulas = []

    doc = docx.Document(BytesIO(file_bytes))
    for para in doc.paragraphs:
        text_content += para.text + "\n"

    # Parse raw XML for math content
    zip_stream = BytesIO(file_bytes)
    import zipfile
    with zipfile.ZipFile(zip_stream) as z:
        for name in z.namelist():
            if name.startswith("word/") and name.endswith(".xml"):
                xml = z.read(name)
                tree = etree.fromstring(xml)
                # Search for Office MathML (OMML) nodes
                for math in tree.findall(".//{http://schemas.openxmlformats.org/officeDocument/2006/math}oMath"):
                    formulas.append(etree.tostring(math, encoding="unicode"))

    return {"text": text_content.strip(), "formulas": "\n".join(formulas)}


def extract_text_and_formulas(filename: str, file_bytes: bytes) -> Dict[str, str]:
    """
    Decide which parser to use based on file type.
    """
    if filename.lower().endswith(".pdf"):
        return parse_pdf_with_formulas(file_bytes)
    elif filename.lower().endswith(".docx"):
        return parse_docx_with_formulas(file_bytes)
    else:
        raise ValueError("Unsupported file type. Only PDF and DOCX are supported.")
