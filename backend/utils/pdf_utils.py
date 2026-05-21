import io
import os
import PyPDF2
from pdf2image import convert_from_bytes
import pytesseract


def extract_text_from_pdf(file_bytes: bytes) -> tuple[str, bool]:
    """Extract text from PDF with a fallback to OCR for scanned/image-based pages."""
    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"

    if text.strip():
        return text, False

    # If no text could be extracted, fallback to OCR
    ocr_text = ""
    poppler_path = os.getenv('POPPLER_PATH')
    convert_kwargs = {'dpi': 300}
    if poppler_path:
        convert_kwargs['poppler_path'] = poppler_path

    pages = convert_from_bytes(file_bytes, **convert_kwargs)
    for page_image in pages:
        ocr_text += pytesseract.image_to_string(page_image, lang='eng') + "\n"

    return ocr_text, True
