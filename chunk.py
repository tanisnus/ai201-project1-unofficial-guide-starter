"""
chunk.py
Splits documents into chunks based on category.
Chunk sizes from planning.md:
  - official: 2000 chars
  - faq:      2800 chars
  - thread:   1200 chars
  - overlap:   300 chars for all categories
Each chunk keeps metadata: source, url, category, filename.
"""

import re
from ingest import load_all_documents

# Chunk sizes per category (in characters)
CHUNK_SIZES = {
    "official": 2000,
    "faq": 2800,
    "thread": 1200,
}
DEFAULT_CHUNK_SIZE = 1500
OVERLAP = 300


def clean_text(text):
    """
    Basic cleaning:
    - Remove invisible/zero-width characters (like the edvisorly filler)
    - Collapse multiple blank lines into one
    - Strip leading/trailing whitespace
    """
    # Remove zero-width and invisible unicode characters
    text = re.sub(r'[​‌‍﻿­]', '', text)
    # Collapse 3+ newlines into 2
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Strip
    text = text.strip()
    return text


def chunk_text(text, category):
    """
    Splits text into overlapping chunks based on category chunk size.
    Returns a list of chunk strings.
    """
    chunk_size = CHUNK_SIZES.get(category, DEFAULT_CHUNK_SIZE)
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size

        # If we're not at the end, try to break at a paragraph or sentence
        if end < text_length:
            # Prefer to break at a double newline (paragraph boundary)
            paragraph_break = text.rfind('\n\n', start, end)
            if paragraph_break != -1 and paragraph_break > start:
                end = paragraph_break
            else:
                # Fall back to breaking at a sentence (period + space)
                sentence_break = text.rfind('. ', start, end)
                if sentence_break != -1 and sentence_break > start:
                    end = sentence_break + 1  # include the period

        chunk = text[start:end].strip()
        if len(chunk) > 0:
            chunks.append(chunk)

        # Move forward by chunk_size minus overlap
        start = end - OVERLAP
        if start <= 0:
            break

    return chunks


def chunk_all_documents(documents):
    """
    Takes a list of document dicts from ingest.py.
    Returns a list of chunk dicts with text + metadata.
    """
    all_chunks = []

    for doc in documents:
        cleaned = clean_text(doc["text"])
        chunks = chunk_text(cleaned, doc["category"])

        for i, chunk_text_str in enumerate(chunks):
            all_chunks.append({
                "text": chunk_text_str,
                "source": doc["source"],
                "url": doc["url"],
                "category": doc["category"],
                "filename": doc["filename"],
                "chunk_index": i,
            })

    return all_chunks


if __name__ == "__main__":
    print("Loading documents...")
    docs = load_all_documents()

    print("\nChunking documents...")
    chunks = chunk_all_documents(docs)

    # Summary by category
    print(f"\nTotal chunks: {len(chunks)}")
    print("\nChunks per file:")
    from collections import Counter
    counts = Counter(c["filename"] for c in chunks)
    for filename, count in sorted(counts.items()):
        print(f"  {filename}: {count} chunks")

    # Print 5 sample chunks for inspection
    print("\n--- 5 Sample Chunks ---")
    import random
    samples = random.sample(chunks, min(5, len(chunks)))
    for i, chunk in enumerate(samples):
        print(f"\n[Chunk {i+1}]")
        print(f"Source:   {chunk['source']}")
        print(f"Category: {chunk['category']}")
        print(f"Length:   {len(chunk['text'])} chars")
        print(f"Text:\n{chunk['text'][:400]}...")
        print("-" * 50)
