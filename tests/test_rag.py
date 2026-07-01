"""Tests for the chunking and retrieval logic.

These do not require ANTHROPIC_API_KEY or network access -- they only
exercise chunking.py, embeddings.py, and vector_store.py. They do download
the sentence-transformers model on first run.
"""

from rag.chunking import chunk_documents, split_into_chunks
from rag.embeddings import embed_texts
from rag.vector_store import InMemoryVectorStore


def test_split_into_chunks_basic():
    text = "word " * 1000
    chunks = split_into_chunks(text, source="doc.txt", chunk_size=100, overlap=20)
    assert len(chunks) > 1
    assert all(c.source == "doc.txt" for c in chunks)
    assert [c.index for c in chunks] == list(range(len(chunks)))


def test_split_into_chunks_overlap():
    words = [f"w{i}" for i in range(50)]
    text = " ".join(words)
    chunks = split_into_chunks(text, source="doc.txt", chunk_size=20, overlap=5)
    first_chunk_words = chunks[0].text.split()
    second_chunk_words = chunks[1].text.split()
    assert first_chunk_words[-5:] == second_chunk_words[:5]


def test_split_into_chunks_empty_text():
    assert split_into_chunks("", source="empty.txt") == []


def test_split_into_chunks_invalid_args():
    try:
        split_into_chunks("hello world", source="doc.txt", chunk_size=10, overlap=10)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_chunk_documents_multiple_sources():
    docs = {"a.txt": "alpha " * 50, "b.txt": "beta " * 50}
    chunks = chunk_documents(docs, chunk_size=20, overlap=5)
    sources = {c.source for c in chunks}
    assert sources == {"a.txt", "b.txt"}


def test_vector_store_retrieves_relevant_chunk():
    docs = {
        "vacation.txt": "Employees accrue fifteen days of paid vacation per year.",
        "passwords.txt": "Reset your password using the self service portal link.",
    }
    chunks = chunk_documents(docs, chunk_size=50, overlap=5)

    store = InMemoryVectorStore()
    store.add(chunks)
    assert len(store) == len(chunks)

    results = store.search("How many vacation days do I get?", top_k=1)
    assert len(results) == 1
    assert results[0].chunk.source == "vacation.txt"
    assert -1.0 <= results[0].score <= 1.0


def test_vector_store_empty_search():
    store = InMemoryVectorStore()
    assert store.search("anything") == []


def test_vector_store_project_chunks_shape():
    docs = {
        "a.txt": "The quick brown fox jumps over the lazy dog.",
        "b.txt": "Paid vacation accrues at one point two five days per month.",
        "c.txt": "Reset your password using the self service portal.",
    }
    chunks = chunk_documents(docs, chunk_size=50, overlap=5)
    store = InMemoryVectorStore()
    store.add(chunks)

    points = store.project_chunks()
    assert points.shape == (len(chunks), 2)


def test_vector_store_project_with_fewer_than_two_chunks():
    docs = {"a.txt": "Just one short document."}
    chunks = chunk_documents(docs, chunk_size=50, overlap=5)
    store = InMemoryVectorStore()
    store.add(chunks)

    # Can't fit 2 principal components from fewer than 2 points -- should
    # degrade gracefully to zeros instead of raising.
    points = store.project_chunks()
    assert points.shape == (len(chunks), 2)
    assert (points == 0).all()


def test_search_by_vector_matches_search():
    docs = {
        "vacation.txt": "Employees accrue fifteen days of paid vacation per year.",
        "passwords.txt": "Reset your password using the self service portal link.",
    }
    chunks = chunk_documents(docs, chunk_size=50, overlap=5)
    store = InMemoryVectorStore()
    store.add(chunks)

    query = "How many vacation days do I get?"
    by_string = store.search(query, top_k=1)
    query_vector = embed_texts([query])[0]
    by_vector = store.search_by_vector(query_vector, top_k=1)

    assert by_string[0].chunk.source == by_vector[0].chunk.source
    assert by_string[0].score == by_vector[0].score


def test_search_by_vector_returns_chunk_vector():
    docs = {"a.txt": "Paid vacation accrues at one point two five days per month."}
    chunks = chunk_documents(docs, chunk_size=50, overlap=5)
    store = InMemoryVectorStore()
    store.add(chunks)

    query_vector = embed_texts(["vacation"])[0]
    results = store.search_by_vector(query_vector, top_k=1)

    assert results[0].vector.shape == query_vector.shape


def test_chunk_vectors_shape():
    docs = {"a.txt": "alpha " * 50, "b.txt": "beta " * 50}
    chunks = chunk_documents(docs, chunk_size=20, overlap=5)
    store = InMemoryVectorStore()
    store.add(chunks)

    vectors = store.chunk_vectors()
    assert vectors.shape[0] == len(chunks)


def test_chunk_vectors_empty_store():
    store = InMemoryVectorStore()
    assert store.chunk_vectors().shape == (0, 0)
