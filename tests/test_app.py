"""Tests for the Flask routes in app.py.

Claude API calls are mocked out (no ANTHROPIC_API_KEY or network needed).
Chunking, embedding, and retrieval still run for real against the sample
docs, so these also catch wiring bugs between app.py and rag/.
"""

from unittest.mock import patch

import pytest

import app as app_module


@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as test_client:
        yield test_client


def test_api_chunks_returns_points(client):
    res = client.get("/api/chunks")
    data = res.get_json()
    assert res.status_code == 200
    assert data["chunk_count"] > 0
    assert "x" in data["chunks"][0] and "y" in data["chunks"][0]


def test_api_chunks_returns_vector_preview(client):
    res = client.get("/api/chunks")
    data = res.get_json()
    chunk = data["chunks"][0]
    assert len(chunk["vector_preview"]) == 12
    assert chunk["vector_dim"] > len(chunk["vector_preview"])


@patch("app.generate_answer", return_value=("prompt text", "the answer"))
def test_api_query_use_rag(mock_generate, client):
    res = client.post("/api/query", json={"query": "vacation days?", "use_rag": True})
    data = res.get_json()
    assert res.status_code == 200
    assert data["rag"]["answer"] == "the answer"
    assert data["no_rag"] is None
    mock_generate.assert_called_once()


@patch("app.generate_plain_answer", return_value="general knowledge answer")
def test_api_query_no_rag(mock_generate, client):
    res = client.post("/api/query", json={"query": "vacation days?", "use_rag": False})
    data = res.get_json()
    assert res.status_code == 200
    assert data["no_rag"]["answer"] == "general knowledge answer"
    assert data["rag"] is None


@patch("app.generate_plain_answer", return_value="plain answer")
@patch("app.generate_answer", return_value=("prompt text", "rag answer"))
def test_api_query_compare(mock_rag, mock_plain, client):
    res = client.post("/api/query", json={"query": "vacation days?", "compare": True})
    data = res.get_json()
    assert res.status_code == 200
    assert data["rag"]["answer"] == "rag answer"
    assert data["no_rag"]["answer"] == "plain answer"


def test_api_query_empty_query(client):
    res = client.post("/api/query", json={"query": "  "})
    assert res.status_code == 400


@patch("app.generate_answer", return_value=("prompt text", "the answer"))
def test_api_query_returns_vector_previews(mock_generate, client):
    res = client.post("/api/query", json={"query": "vacation days?"})
    data = res.get_json()
    assert res.status_code == 200
    assert len(data["query_vector_preview"]) == 12
    assert data["embedding_dim"] > len(data["query_vector_preview"])
    assert len(data["retrieved_chunks"][0]["vector_preview"]) == 12


def test_api_reindex_changes_chunk_count(client):
    small = client.post("/api/reindex", json={"chunk_size": 30, "overlap": 5}).get_json()
    large = client.post("/api/reindex", json={"chunk_size": 1000, "overlap": 50}).get_json()

    assert small["chunk_size"] == 30
    assert large["chunk_count"] <= small["chunk_count"]

    # restore defaults so later tests in this module see a known state
    client.post("/api/reindex", json={"chunk_size": 400, "overlap": 80})


def test_api_reindex_rejects_bad_overlap(client):
    res = client.post("/api/reindex", json={"chunk_size": 50, "overlap": 50})
    assert res.status_code == 400


def test_api_documents_adds_and_increases_chunk_count(client):
    before = client.get("/api/chunks").get_json()["chunk_count"]
    res = client.post("/api/documents", json={
        "name": "course_notes",
        "text": "Lecture one covers embeddings and vector search in detail.",
    })
    data = res.get_json()
    assert res.status_code == 200
    assert data["chunk_count"] >= before + 1
    assert data["added_name"] == "course_notes.txt"


def test_api_documents_rejects_empty_text(client):
    res = client.post("/api/documents", json={"name": "empty", "text": "  "})
    assert res.status_code == 400
