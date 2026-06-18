"""
pdf_extractor.py

Job of this module: take an uploaded PDF file and return clean plain text.
No LLM calls here, no web calls. Just file -> text.
Keeping this separate means if we ever swap PDF libraries, nothing else
in the app needs to change.
"""

from pypdf import PdfReader


def extract_text_from_pdf(uploaded_file) -> str:
    """
    Reads a PDF (file-like object, e.g. from Streamlit's file_uploader)
    and returns all the text inside it as one big string.

    Args:
        uploaded_file: a file-like object (has .read() / supports PdfReader)

    Returns:
        str: all text from the PDF, pages joined by newlines.
    """
    reader = PdfReader(uploaded_file)

    all_text = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:  # some pages can be empty/images-only
            all_text.append(page_text)

    full_text = "\n".join(all_text)
    return full_text


def chunk_text_if_too_long(text: str, max_chars: int = 12000) -> str:
    """
    Groq's LLM has a context limit. Most marketing PDFs are short,
    but just in case someone uploads something huge, we cut it down
    so the claim-extraction step doesn't fail.

    Args:
        text: full extracted text
        max_chars: rough safety limit (characters, not tokens)

    Returns:
        str: text, trimmed if it was too long
    """
    if len(text) <= max_chars:
        return text
    return text[:max_chars]