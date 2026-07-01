"""Step 1: Chunking.

LLMs and embedding models can't digest a whole document at once, and
retrieval works better over small, focused passages than over giant blobs
of text. So before anything else, we split documents into overlapping
chunks. The overlap means a sentence that gets cut off at a chunk boundary
still appears in full in the next chunk too.
"""

from dataclasses import dataclass


@dataclass
class Chunk:
    text: str
    source: str
    index: int


def split_into_chunks(text: str, source: str, chunk_size: int = 400, overlap: int = 80) -> list[Chunk]:
    """Split `text` into word-based chunks of ~chunk_size words, each
    overlapping the previous one by `overlap` words.

    Word-based (not character-based) chunking keeps things simple and
    readable for teaching purposes -- production systems often chunk by
    tokens or sentences instead.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0
    index = 0
    step = chunk_size - overlap

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunks.append(Chunk(text=" ".join(chunk_words), source=source, index=index))
        index += 1
        if end >= len(words):
            break
        start += step

    return chunks


def chunk_documents(documents: dict[str, str], chunk_size: int = 400, overlap: int = 80) -> list[Chunk]:
    """Chunk a {filename: text} mapping of documents into a flat list of Chunks."""
    all_chunks = []
    for source, text in documents.items():
        all_chunks.extend(split_into_chunks(text, source, chunk_size, overlap))
    return all_chunks
