from pathlib import Path

import fitz  # PyMuPDF


def load_pdf(path: Path) -> str:
    doc = fitz.open(path)
    try:
        pages = [page.get_text() for page in doc]
    finally:
        doc.close()
    return "\n\n".join(p.strip() for p in pages if p.strip())
