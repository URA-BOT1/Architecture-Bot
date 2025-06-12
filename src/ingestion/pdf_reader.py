import fitz
from pdf2image import convert_from_path
import pytesseract
from pathlib import Path
from typing import List

def read_pdf(path: str) -> str:
    doc = fitz.open(path)
    text = []
    for page in doc:
        text.append(page.get_text())
    if any(text):
        return "\n".join(text)
    # fallback OCR for scanned PDFs
    pages = convert_from_path(path, dpi=300)
    ocr_text = []
    for p in pages:
        ocr_text.append(pytesseract.image_to_string(p, lang="fra"))
    return "\n".join(ocr_text)
