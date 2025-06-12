from .pdf_reader import read_pdf
from .docx_reader import read_docx
from .excel_reader import read_excel

READERS = {
    '.pdf': read_pdf,
    '.docx': read_docx,
    '.xlsx': read_excel,
}

def load_file(path: str) -> str:
    for ext, reader in READERS.items():
        if path.lower().endswith(ext):
            return reader(path)
    raise ValueError(f"Unsupported file type: {path}")
