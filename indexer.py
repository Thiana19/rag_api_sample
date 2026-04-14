"""
indexer.py — Chunks scraped content and stores it in ChromaDB.
Run this once after scraper.py to build the vector database.
"""

import json
import chromadb
from chromadb.utils import embedding_functions

from config import (
    SCRAPED_OUTPUT, CHROMA_DIR, COLLECTION_NAME,
    EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP,
)


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list:
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start += size - overlap
    return chunks


def main():
    with open(SCRAPED_OUTPUT, "r", encoding="utf-8") as f:
        pages = json.load(f)

    print(f"Loaded {len(pages)} pages from {SCRAPED_OUTPUT}")

    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )

    client = chromadb.PersistentClient(path=CHROMA_DIR)

    try:
        client.delete_collection(COLLECTION_NAME)
        print("Deleted existing collection")
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,
    )

    documents = []
    metadatas = []
    ids = []
    chunk_id = 0

    for page in pages:
        url = page["url"]
        content = page["content"]
        chunks = chunk_text(content)
        print(f"  {url} -> {len(chunks)} chunks")

        for chunk in chunks:
            if chunk.strip():
                documents.append(chunk)
                metadatas.append({"url": url})
                ids.append(f"chunk_{chunk_id}")
                chunk_id += 1

    batch_size = 100
    for i in range(0, len(documents), batch_size):
        collection.add(
            documents=documents[i:i+batch_size],
            metadatas=metadatas[i:i+batch_size],
            ids=ids[i:i+batch_size],
        )
        print(f"Indexed batch {i//batch_size + 1} ({min(i+batch_size, len(documents))}/{len(documents)} chunks)")

    print(f"\nDone! {len(documents)} chunks indexed into ChromaDB at {CHROMA_DIR}")


if __name__ == "__main__":
    main()
