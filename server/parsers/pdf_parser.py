import pdfplumber
import pytesseract
from io import BytesIO

async def parsePdf(file: BytesIO):
    text = ""
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                pageText = page.extract_text()
                if pageText:
                    text += pageText + "\n"

        if not text.strip():
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    pil_img = page.to_image(resolution=300).original
                    text += pytesseract.image_to_string(pil_img) + "\n"

    except Exception as e:
        raise RuntimeError(f"PDF parsing failed: {str(e)}")

    return text