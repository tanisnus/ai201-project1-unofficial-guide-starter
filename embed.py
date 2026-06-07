"""
embed.py
Embeds all chunks using all-MiniLM-L6-v2 and stores them in ChromaDB.
Run this once (or after document changes) to build or rebuild the vector store.
Use retrieve.py to query without re-embedding.
"""

import chromadb
from sentence_transformers import SentenceTransformer
from chunk import chunk_all_documents
from ingest import load_all_documents
from retrieve import CHROMA_DIR, COLLECTION_NAME, MODEL_NAME


def build_vector_store():
    print("Loading documents...")
    docs: list[dict] = load_all_documents()

    print("Chunking documents...")
    chunks: list[dict] = chunk_all_documents(docs)
    print(f"Total chunks to embed: {len(chunks)}")

    print(f"\nLoading embedding model ({MODEL_NAME})...")
    model = SentenceTransformer(MODEL_NAME)

    print("Setting up ChromaDB...")
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    try:
        client.delete_collection(COLLECTION_NAME)
        print("Deleted existing collection.")
    except Exception:
        pass

    collection = client.create_collection(
        COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    print("Embedding and storing chunks...")
    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)

    collection.add(
        ids=[f"chunk_{i}" for i in range(len(chunks))],
        embeddings=embeddings.tolist(),
        documents=texts,
        metadatas=[{
            "source": chunk["source"],
            "url": chunk["url"],
            "category": chunk["category"],
            "filename": chunk["filename"],
            "chunk_index": chunk["chunk_index"],
        } for chunk in chunks],
    )

    print(f"\nDone! {len(chunks)} chunks stored in ChromaDB at '{CHROMA_DIR}/'")
    print("Run 'python retrieve.py' to test queries without re-embedding.")
    return collection, model


if __name__ == "__main__":
    build_vector_store()
