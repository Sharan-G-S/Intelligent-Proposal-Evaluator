# src/processing/document_parser.py

import fitz  # PyMuPDF
import docx
import os

def extract_text_from_pdf(file_path: str) -> str:
    """Extracts all text from a given PDF file."""
    try:
        with fitz.open(file_path) as doc:
            text = ""
            for page in doc:
                text += page.get_text()
            print(f"Successfully extracted text from PDF: {os.path.basename(file_path)}")
            return text
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
        return ""

def extract_text_from_docx(file_path: str) -> str:
    """Extracts all text from a given DOCX file."""
    try:
        doc = docx.Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        print(f"Successfully extracted text from DOCX: {os.path.basename(file_path)}")
        return '\n'.join(full_text)
    except Exception as e:
        print(f"Error reading DOCX {file_path}: {e}")
        return ""

def parse_document(file_path: str) -> str:
    """
    Parses a document (PDF or DOCX) and returns its text content.
    This function acts as a wrapper that calls the correct specific parser.
    """
    # Get the file extension and convert to lowercase
    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_extension == '.docx':
        return extract_text_from_docx(file_path)
    else:
        print(f"Unsupported file type: {file_extension}. Please provide a .pdf or .docx file.")
        return ""

# --- Main block for testing the parser ---
if __name__ == '__main__':
    print("--- Running Document Parser Tests ---")

    # --- Test 1: Parse a PDF document ---
    # We'll use the guideline PDF we already have in our data folder
    pdf_test_path = 'data/raw/S&T-Guidelines-MoC.pdf'
    if os.path.exists(pdf_test_path):
        print(f"\nTesting PDF parsing for: {pdf_test_path}")
        pdf_text = parse_document(pdf_test_path)
        print("--- PDF Content (First 500 characters) ---")
        print(pdf_text[:500])
        print("-" * 40)
    else:
        print(f"\nPDF test file not found at: {pdf_test_path}")


    # --- Test 2: Parse a DOCX document ---
    # We need to create a dummy DOCX file for this test
    docx_test_path = 'data/raw/dummy_proposal.docx'
    if os.path.exists(docx_test_path):
        print(f"\nTesting DOCX parsing for: {docx_test_path}")
        docx_text = parse_document(docx_test_path)
        print("--- DOCX Content ---")
        print(docx_text)
        print("-" * 40)
    else:
        print(f"\nDOCX test file not found at: {docx_test_path}")
        print("Please create a simple .docx file and save it as 'dummy_proposal.docx' in the 'data/raw' folder to run this test.")