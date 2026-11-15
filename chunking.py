from typing import Any


# Character Based Chunker
def chunk_text(text: str, chunk_size: int = 12000, overlap: int = 500) -> dict[str, Any]:
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        chunk = text[start:end]
        chunks.append(chunk)

        start = end - overlap
    return {
        "chunks": chunks,
        "total_chunks": f"{len(chunks)} Chunks"
    }
