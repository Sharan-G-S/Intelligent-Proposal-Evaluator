# src/processing/document_parser.py

import fitz  # PyMuPDF
import docx
import os
import re
import json
from datetime import datetime

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

def extract_sections(text: str) -> dict:
    """
    Extracts structured sections from raw text based on common headers using a more flexible regex.
    """
    print("Attempting to extract structured sections...")
    sections = {}
    
    headers = [
        "Abstract", "Introduction & Background", "Introduction", "Background",
        "Proposed Methodology", "Methodology", "System Design",
        "Expected Outcomes & Conclusion", "Conclusion", "References"
    ]
    
    pattern = r"^\s*(?:\d+\.\s*)?(" + "|".join(headers) + r")\b"
    
    parts = re.split(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
    
    if len(parts) <= 1:
        print("No standard headers found. Returning all text as 'unclassified'.")
        return {"unclassified": text.strip()}

    if parts[0].strip():
        sections["preamble"] = parts[0].strip()

    for i in range(1, len(parts), 2):
        header = parts[i].strip().lower().replace(" & ", "_and_").replace(" ", "_")
        content = parts[i+1].strip()
        sections[header] = content

    print(f"Successfully extracted {len(sections)} sections.")
    return sections

def parse_document(file_path: str) -> str:
    """
    Parses a document (PDF or DOCX) and returns its text content.
    """
    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_extension == '.docx':
        return extract_text_from_docx(file_path)
    else:
        print(f"Unsupported file type: {file_extension}.")
        return ""

def process_new_proposal(file_path: str) -> dict:
    """
    The main pipeline function for processing a single new proposal file.
    It reads the file, extracts text, and structures it into a standardized JSON object.
    """
    print(f"\n--- Starting Full Processing Pipeline for: {os.path.basename(file_path)} ---")
    
    # Step 1.1: Get the raw text from the document
    raw_text = parse_document(file_path)
    
    if not raw_text:
        print("Processing failed: could not extract text.")
        return None

    # Step 1.2: Structure the text into sections
    structured_content = extract_sections(raw_text)
    
    # Step 1.3: Create the final standardized JSON object
    final_output = {
        "source_file": os.path.basename(file_path),
        "ingestion_timestamp": datetime.now().isoformat(),
        "content": structured_content
    }
    
    print("--- Successfully processed and structured the document ---")
    return final_output


# --- Main block for testing the complete pipeline ---
if __name__ == '__main__':
    # We can test with either the PDF or the DOCX file
    test_file_to_process = 'data/raw/dummy_proposal.docx'
    
    if os.path.exists(test_file_to_process):
        final_json_object = process_new_proposal(test_file_to_process)
    
        if final_json_object:
            print("\n--- FINAL STANDARDIZED JSON OUTPUT ---")
            print(json.dumps(final_json_object, indent=4))
            print("-" * 40)
    else:
        print(f"\nTest file not found at: {test_file_to_process}")