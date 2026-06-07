"""
ingest.py
Loads all documents from the documents/ folder.
- .txt files: reads header metadata (SOURCE, URL, CATEGORY) + body text
- .pdf files: extracts text using pdfplumber
Returns a list of dicts, each with: text, source, url, category
"""

import os
import pdfplumber

DOCUMENTS_DIR = "documents"

# Map PDF filenames to their metadata manually
PDF_METADATA = {
    "uc_tag_matrix.pdf": {
        "source": "UC TAG Matrix 2026-27",
        "url": "https://admission.universityofcalifornia.edu/_assets/files/transfer-requirements/uc-tag-matrix_2026-2027.pdf",
        "category": "official",
    },
    "uc_transfer_application_guide.pdf": {
        "source": "UC Transfer Application Guide",
        "url": "https://admission.universityofcalifornia.edu/_assets/files/how-to-apply/application-guide-transfer-applicants.pdf",
        "category": "official",
    },
}


def parse_txt_header(lines):
    """
    Reads the header lines at the top of a .txt file.
    Looks for SOURCE:, URL:, CATEGORY: keys.
    Returns (metadata dict, index where body starts)
    """
    metadata = {"source": "", "url": "", "category": ""}
    body_start = 0

    for i, line in enumerate(lines):
        line_stripped = line.strip()
        if line_stripped.startswith("SOURCE:"):
            metadata["source"] = line_stripped.replace("SOURCE:", "").strip()
        elif line_stripped.startswith("URL:"):
            metadata["url"] = line_stripped.replace("URL:", "").strip()
        elif line_stripped.startswith("CATEGORY:"):
            metadata["category"] = line_stripped.replace("CATEGORY:", "").strip()
        elif line_stripped == "=" * 40:
            # Everything after the === separator is body text
            body_start = i + 1
            break
        # Stop looking for headers after 10 lines
        if i > 10 and not body_start:
            body_start = i
            break

    return metadata, body_start


def load_txt(filepath):
    """Load a .txt file, parse its header, return a document dict."""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    metadata, body_start = parse_txt_header(lines)
    body = "".join(lines[body_start:]).strip()

    return {
        "text": body,
        "source": metadata["source"],
        "url": metadata["url"],
        "category": metadata["category"],
        "filename": os.path.basename(filepath),
    }


def extract_pdf_text(filepath):
    """
    Extract text from a PDF, handling multi-column layouts.
    Splits each page into left and right halves and reads each separately,
    then joins them in reading order.
    Also strips page headers/footers (lines with page numbers).
    """
    import re
    text_parts = []

    # PDFs that use tables/complex layouts — skip column splitting
    table_heavy_pdfs = ["uc_tag_matrix.pdf"]
    use_columns = os.path.basename(filepath) not in table_heavy_pdfs

    with pdfplumber.open(filepath) as pdf:
        print(f"    ({len(pdf.pages)} pages)")
        for page in pdf.pages:
            width = page.width
            height = page.height

            if use_columns:
                # Try splitting into left and right columns
                left = page.crop((0, 0, width / 2, height))
                right = page.crop((width / 2, 0, width, height))

                left_text = left.extract_text() or ""
                right_text = right.extract_text() or ""

                # If one side is empty, fall back to full page extraction
                if not left_text.strip() or not right_text.strip():
                    page_text = page.extract_text() or ""
                else:
                    page_text = left_text + "\n" + right_text
            else:
                page_text = page.extract_text() or ""

            # Remove page header/footer lines (short lines with page numbers)
            lines = page_text.split("\n")
            cleaned_lines = []
            for line in lines:
                stripped = line.strip()
                # Skip lines that look like page headers/footers
                if re.search(r'UNDERGRADUATE ADMISSIONS|APPLICATION GUIDE TRANSFER \d+', stripped):
                    continue
                if re.match(r'^\d+$', stripped):  # lone page numbers
                    continue
                cleaned_lines.append(line)

            page_text = "\n".join(cleaned_lines).strip()
            if page_text:
                text_parts.append(page_text)

    return "\n\n".join(text_parts).strip()


def load_pdf(filepath):
    """Extract text from a PDF using pdfplumber."""
    filename = os.path.basename(filepath)
    metadata = PDF_METADATA.get(filename, {
        "source": filename,
        "url": "",
        "category": "official",
    })

    full_text = extract_pdf_text(filepath)

    return {
        "text": full_text,
        "source": metadata["source"],
        "url": metadata["url"],
        "category": metadata["category"],
        "filename": filename,
    }


def load_all_documents():
    """Load all .txt and .pdf files from the documents/ folder."""
    documents = []

    for filename in os.listdir(DOCUMENTS_DIR):
        filepath = os.path.join(DOCUMENTS_DIR, filename)

        if filename.endswith(".txt"):
            doc = load_txt(filepath)
            documents.append(doc)
            print(f"  Loaded .txt: {filename} ({len(doc['text'])} chars)")

        elif filename.endswith(".pdf"):
            doc = load_pdf(filepath)
            documents.append(doc)
            print(f"  Loaded .pdf: {filename} ({len(doc['text'])} chars)")

    return documents


if __name__ == "__main__":
    print("Loading documents...\n")
    docs = load_all_documents()
    print(f"\nTotal documents loaded: {len(docs)}")
    print("\n--- Preview of each document ---")
    for doc in docs:
        print(f"\nFile:     {doc['filename']}")
        print(f"Source:   {doc['source']}")
        print(f"Category: {doc['category']}")
        print(f"URL:      {doc['url']}")
        print(f"Text preview: {doc['text'][:200]}...")
