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


def load_pdf(filepath):
    """Extract text from a PDF using pdfplumber."""
    filename = os.path.basename(filepath)
    metadata = PDF_METADATA.get(filename, {
        "source": filename,
        "url": "",
        "category": "official",
    })

    text_parts = []
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

    full_text = "\n".join(text_parts).strip()

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
