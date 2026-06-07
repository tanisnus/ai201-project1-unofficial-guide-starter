"""
retrieve.py
Loads an existing ChromaDB vector store and retrieves top-k chunks for a query.
Run embed.py first to build the store. Use this script to test retrieval without re-embedding.
"""

import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_DIR = "chroma_store"
COLLECTION_NAME = "uc_transfer"
MODEL_NAME = "all-MiniLM-L6-v2"
DEFAULT_TOP_K = 5


def load_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


def get_chroma_client() -> chromadb.PersistentClient:
    return chromadb.PersistentClient(path=CHROMA_DIR)


def load_collection():
    """Return the existing collection, or None if embed.py has not been run yet."""
    client = get_chroma_client()
    try:
        return client.get_collection(COLLECTION_NAME)
    except Exception:
        return None


def query_vector_store(query: str, collection, model, top_k: int = DEFAULT_TOP_K) -> dict:
    """Embed a query and return the top-k matching chunks from ChromaDB."""
    query_embedding = model.encode([query])[0]
    return collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=top_k,
    )


def retrieve(query: str, top_k: int = DEFAULT_TOP_K) -> dict:
    """Load model + collection and retrieve top-k chunks for a query."""
    collection = load_collection()
    if collection is None:
        raise RuntimeError(
            f"Vector store not found at '{CHROMA_DIR}/'. Run 'python embed.py' first."
        )
    model = load_embedding_model()
    return query_vector_store(query, collection, model, top_k)


def print_results(query: str, results: dict) -> None:
    for i, (doc, metadata, distance) in enumerate(zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    )):
        print(f"[Result {i+1}] distance: {distance:.3f}")
        print(f"Source:   {metadata['source']}")
        print(f"Category: {metadata['category']}")
        print(f"FULL TEXT:\n{doc}")
        print()


if __name__ == "__main__":
    collection = load_collection()
    if collection is None:
        print(f"No vector store found at '{CHROMA_DIR}/'.")
        print("Run 'python embed.py' to embed your documents first.")
        raise SystemExit(1)

    print(f"Loaded collection '{COLLECTION_NAME}' ({collection.count()} chunks)")
    model = load_embedding_model()

    eval_queries = [
        "What is the minimum GPA a California resident needs to be eligible to transfer to a UC?",
        "Is a UC TAG a 100% guarantee of admission once approved?",
        "How do I find which community college courses satisfy my major prep for a specific UC campus?",
    ]

    for test_query in eval_queries:
        print(f"\n{'='*60}")
        print(f"Query: {test_query}\n")
        results = query_vector_store(test_query, collection, model)
        print_results(test_query, results)
