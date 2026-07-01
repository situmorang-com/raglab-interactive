"""Step 3: Retrieval.

The simplest possible vector store: keep every chunk's embedding in one
NumPy matrix in memory, and rank chunks for a query by cosine similarity.
Because embeddings.py already L2-normalizes every vector, cosine
similarity is just a dot product.

This does not scale to millions of chunks -- a production system would use
an approximate-nearest-neighbor index (FAISS, Chroma, Pinecone, pgvector,
...). See docs/EXTENDING.md for how to swap one in.
"""

from dataclasses import dataclass

import numpy as np

from rag.chunking import Chunk
from rag.embeddings import embed_texts


@dataclass
class ScoredChunk:
    chunk: Chunk
    score: float
    vector: np.ndarray


class InMemoryVectorStore:
    def __init__(self) -> None:
        self._chunks: list[Chunk] = []
        self._vectors: np.ndarray | None = None
        self._pca_mean: np.ndarray | None = None
        self._pca_components: np.ndarray | None = None

    def add(self, chunks: list[Chunk]) -> None:
        if not chunks:
            return
        new_vectors = embed_texts([c.text for c in chunks])
        self._chunks.extend(chunks)
        self._vectors = new_vectors if self._vectors is None else np.vstack([self._vectors, new_vectors])
        self._fit_projection()

    def _fit_projection(self) -> None:
        """Fit a 2D PCA projection (via SVD) so chunks/queries can be plotted.

        Manual PCA instead of scikit-learn -- keeps the dependency list small.
        Needs at least 2 chunks to find 2 principal directions.
        """
        if self._vectors is None or len(self._vectors) < 2:
            self._pca_mean = None
            self._pca_components = None
            return
        self._pca_mean = self._vectors.mean(axis=0)
        centered = self._vectors - self._pca_mean
        _, _, vt = np.linalg.svd(centered, full_matrices=False)
        self._pca_components = vt[:2]

    def project(self, vectors: np.ndarray) -> np.ndarray:
        """Project an (N, D) batch of embeddings into (N, 2) plot coordinates."""
        if self._pca_components is None:
            return np.zeros((len(vectors), 2), dtype=np.float32)
        centered = vectors - self._pca_mean
        return centered @ self._pca_components.T

    def project_chunks(self) -> np.ndarray:
        """Project every stored chunk's embedding into 2D, in chunk order."""
        if self._vectors is None:
            return np.zeros((0, 2), dtype=np.float32)
        return self.project(self._vectors)

    def chunk_vectors(self) -> np.ndarray:
        """The full (N, D) matrix of every stored chunk's raw embedding, in chunk order."""
        if self._vectors is None:
            return np.zeros((0, 0), dtype=np.float32)
        return self._vectors

    def search_by_vector(self, vector: np.ndarray, top_k: int = 3) -> list[ScoredChunk]:
        """Rank stored chunks against an already-embedded query vector."""
        if self._vectors is None or len(self._chunks) == 0:
            return []
        scores = self._vectors @ vector  # cosine similarity (vectors are unit-normalized)
        top_k = min(top_k, len(self._chunks))
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [
            ScoredChunk(chunk=self._chunks[i], score=float(scores[i]), vector=self._vectors[i])
            for i in top_indices
        ]

    def search(self, query: str, top_k: int = 3) -> list[ScoredChunk]:
        if self._vectors is None or len(self._chunks) == 0:
            return []
        query_vector = embed_texts([query])[0]
        return self.search_by_vector(query_vector, top_k=top_k)

    def __len__(self) -> int:
        return len(self._chunks)
