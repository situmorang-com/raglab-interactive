"""Tests for the Flask routes in app.py.

Claude API calls are mocked out (no ANTHROPIC_API_KEY or network needed).
Chunking, embedding, and retrieval still run for real against the sample
docs, so these also catch wiring bugs between app.py and rag/.
"""

import os
from unittest.mock import patch

import pytest

import app as app_module


@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as test_client:
        yield test_client


@pytest.fixture
def isolated_env(monkeypatch, tmp_path):
    """Redirects .env to a temp file and fully restores os.environ after the
    test -- POST /api/config mutates os.environ directly (not via
    monkeypatch), so a plain monkeypatch.setenv wouldn't clean it up.
    """
    monkeypatch.setattr(app_module, "_env_file_path", lambda: tmp_path / ".env")
    original_environ = dict(os.environ)
    yield tmp_path / ".env"
    os.environ.clear()
    os.environ.update(original_environ)


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


# --- /api/config -------------------------------------------------------------

def test_api_config_get_never_returns_the_key(client, isolated_env):
    os.environ["LLM_PROVIDER"] = "anthropic"
    os.environ["ANTHROPIC_API_KEY"] = "sk-ant-super-secret"
    res = client.get("/api/config")
    data = res.get_json()
    assert res.status_code == 200
    assert data["provider"] == "anthropic"
    assert data["key_configured"] is True
    assert "sk-ant-super-secret" not in str(data)  # the raw key must never round-trip to the client


def test_api_config_get_reports_no_key_configured(client, isolated_env):
    os.environ["LLM_PROVIDER"] = "nvidia"
    os.environ.pop("NVIDIA_API_KEY", None)
    res = client.get("/api/config")
    data = res.get_json()
    assert data["key_configured"] is False
    assert data["key_required"] is True


def test_api_config_get_includes_all_providers_metadata(client, isolated_env):
    res = client.get("/api/config")
    data = res.get_json()
    assert set(data["all_providers"].keys()) == {"anthropic", "openai", "nvidia", "ollama"}
    assert data["all_providers"]["ollama"]["key_required"] is False


def test_api_config_get_includes_model_choices_per_provider(client, isolated_env):
    res = client.get("/api/config")
    data = res.get_json()
    for name, info in data["all_providers"].items():
        assert info["model_default"] in info["model_choices"], f"{name}'s default model isn't in its own choices"
    assert "gpt-4o-mini" in data["all_providers"]["openai"]["model_choices"]


def test_api_config_post_sets_env_and_persists_to_file(client, isolated_env):
    env_path = isolated_env
    res = client.post("/api/config", json={
        "provider": "nvidia",
        "api_key": "nvapi-test-key",
        "model": "minimaxai/minimax-m3",
    })
    data = res.get_json()
    assert res.status_code == 200
    assert data["ok"] is True

    assert os.environ["LLM_PROVIDER"] == "nvidia"
    assert os.environ["NVIDIA_API_KEY"] == "nvapi-test-key"
    assert os.environ["NVIDIA_MODEL"] == "minimaxai/minimax-m3"

    saved = env_path.read_text()
    assert "LLM_PROVIDER=nvidia" in saved
    assert "NVIDIA_API_KEY=nvapi-test-key" in saved


def test_api_config_post_updates_existing_line_instead_of_duplicating(client, isolated_env):
    env_path = isolated_env
    env_path.write_text("LLM_PROVIDER=anthropic\nANTHROPIC_API_KEY=sk-ant-old\n")
    client.post("/api/config", json={"provider": "anthropic", "api_key": "sk-ant-new"})
    saved = env_path.read_text()
    assert saved.count("ANTHROPIC_API_KEY=") == 1
    assert "sk-ant-new" in saved
    assert "sk-ant-old" not in saved


def test_api_config_post_allows_updating_model_without_resending_key(client, isolated_env):
    # First call sets the key; a later call that only changes the model
    # (no api_key in the body) must not be rejected -- a student fixing a
    # typo'd model name shouldn't have to re-paste their key every time.
    client.post("/api/config", json={"provider": "openai", "api_key": "sk-real-key"})
    res = client.post("/api/config", json={"provider": "openai", "model": "gpt-4o-mini"})
    assert res.status_code == 200
    assert os.environ["OPENAI_API_KEY"] == "sk-real-key"
    assert os.environ["OPENAI_MODEL"] == "gpt-4o-mini"


def test_api_config_post_rejects_unknown_provider(client, isolated_env):
    res = client.post("/api/config", json={"provider": "cohere", "api_key": "x"})
    assert res.status_code == 400


def test_api_config_post_rejects_missing_required_key(client, isolated_env, monkeypatch):
    # Explicitly guarantee no key is already present -- a real .env loaded
    # at app import time could otherwise leak a real OPENAI_API_KEY in here.
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    res = client.post("/api/config", json={"provider": "openai", "api_key": ""})
    assert res.status_code == 400


def test_api_config_post_ollama_does_not_require_key(client, isolated_env):
    res = client.post("/api/config", json={"provider": "ollama"})
    assert res.status_code == 200
    assert os.environ["LLM_PROVIDER"] == "ollama"
