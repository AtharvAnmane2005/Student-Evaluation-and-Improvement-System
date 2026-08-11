"""
Extracts raw text from a resume PDF. PyMuPDF is tried first (fast, handles
most PDFs well); pdfplumber (built on pdfminer.six, a different parsing
engine) is used as a fallback when PyMuPDF returns suspiciously little
text — some PDFs (unusual encodings, certain export tools) extract better
with one engine than the other, and it's cheap to try both.
"""
import io
import logging

logger = logging.getLogger(__name__)


def _extract_with_pymupdf(file_bytes: bytes) -> str:
    import fitz  # PyMuPDF

    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        return "\n".join(page.get_text() for page in doc)


def _extract_with_pdfplumber(file_bytes: bytes) -> str:
    import pdfplumber

    text_parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text_parts.append(page.extract_text() or "")
    return "\n".join(text_parts)


MIN_ACCEPTABLE_TEXT_LENGTH = 20


def extract_text(file_bytes: bytes) -> str:
    try:
        text = _extract_with_pymupdf(file_bytes)
    except Exception:
        logger.warning("PyMuPDF failed to extract text, trying pdfplumber.", exc_info=True)
        text = ""

    if len(text.strip()) < MIN_ACCEPTABLE_TEXT_LENGTH:
        try:
            fallback_text = _extract_with_pdfplumber(file_bytes)
            if len(fallback_text.strip()) > len(text.strip()):
                return fallback_text
        except Exception:
            logger.warning("pdfplumber fallback also failed to extract text.", exc_info=True)

    return text
