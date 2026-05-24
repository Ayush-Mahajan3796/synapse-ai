import io
import os
import pypdf
from pdf2image import convert_from_bytes
import pytesseract


def extract_text_from_pdf(file_bytes: bytes) -> tuple[str, bool]:
    """Extract text from PDF with a fallback to OCR for scanned/image-based pages."""
    text = ""
    pdf_read_success = False
    
    try:
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        pdf_read_success = True
    except Exception as e:
        # If pypdf fails completely, we will log it and try OCR fallback
        print(f"pypdf failed to parse PDF: {e}")


    if pdf_read_success and text.strip():
        return text, False

    # If no text could be extracted or PyPDF2 failed, fallback to OCR
    ocr_text = ""
    try:
        tesseract_cmd = os.getenv('TESSERACT_CMD')
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

        poppler_path = os.getenv('POPPLER_PATH')
        convert_kwargs = {'dpi': 300}
        if poppler_path:
            convert_kwargs['poppler_path'] = poppler_path

        pages = convert_from_bytes(file_bytes, **convert_kwargs)
        for page_image in pages:
            ocr_text += pytesseract.image_to_string(page_image, lang='eng') + "\n"
        
        if ocr_text.strip():
            return ocr_text, True
    except Exception as ocr_err:
        print(f"OCR Fallback failed: {ocr_err}")
        # If both normal extraction and OCR failed/are unavailable, raise a clear error
        raise ValueError(
            "Could not extract text from the PDF. The document may be scanned or image-only, "
            "and OCR dependencies (Tesseract or Poppler) are not fully configured on the server. "
            "Please upload a standard PDF containing selectable text."
        )

    raise ValueError(
        "The uploaded PDF appears to be empty or contains no readable text. "
        "Please upload a valid PDF document with selectable text."
    )

