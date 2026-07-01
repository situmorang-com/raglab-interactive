"""Step 2: Embeddings.

An embedding model turns text into a vector of numbers such that
semantically similar text ends up with similar vectors. This is what lets
us find relevant chunks for a question later by comparing vectors instead
of matching keywords.

We use a small local model (sentence-transformers/all-MiniLM-L6-v2) so the
whole pipeline runs offline and free -- no API key needed for this stage.
The model is downloaded once (~80MB) the first time it's used and then
cached locally.
"""

from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


def embed_texts(texts: list[str]) -> np.ndarray:
    """Embed a list of strings into an (N, D) array of unit-normalized vectors.

    Normalizing the vectors up front means cosine similarity reduces to a
    plain dot product later in vector_store.py.
    """
    if not texts:
        return np.empty((0, 384), dtype=np.float32)
    model = _get_model()
    embeddings = model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)
    return embeddings.astype(np.float32)
