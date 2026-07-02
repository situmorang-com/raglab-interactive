"""RAG Lab Interactive -- an interactive teaching demo of Retrieval-Augmented Generation.

Run with:
    python3 app.py

Then open http://localhost:5000. Every /api/query request runs the full
pipeline (chunk -> embed -> retrieve -> generate) and returns every
intermediate stage so the UI can render it live. Students can also:
  - rebuild the index with a different chunk size/overlap (/api/reindex)
  - add their own document to the corpus (/api/documents)
  - compare a RAG answer against a no-context baseline answer in one request
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

from rag.chunking import chunk_documents
from rag.embeddings import embed_texts
from rag.generation import PROVIDERS, GenerationError, MissingAPIKeyError, generate_answer, generate_plain_answer
from rag.vector_store import InMemoryVectorStore

load_dotenv()

CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", 400))
CHUNK_OVERLAP = int(os.environ.get("CHUNK_OVERLAP", 80))
TOP_K = int(os.environ.get("TOP_K", 3))

MIN_CHUNK_SIZE, MAX_CHUNK_SIZE = 20, 2000
MIN_TOP_K, MAX_TOP_K = 1, 10
VECTOR_PREVIEW_DIMS = 12

DATA_DIR = Path(__file__).parent / "data" / "sample_docs"

app = Flask(__name__)

# All mutable pipeline state lives in these globals. The app assumes a
# single student running their own local instance (per the README), not a
# shared multi-tenant deployment, so plain module state is fine -- no
# per-session handling needed.
_documents: dict[str, str] = {}
_all_chunks = []
_vector_store = InMemoryVectorStore()


def _load_sample_documents() -> dict[str, str]:
    documents = {}
    for path in sorted(DATA_DIR.glob("*.txt")):
        documents[path.name] = path.read_text(encoding="utf-8")
    return documents


def rebuild_index(chunk_size: int, overlap: int) -> None:
    """Re-chunk every document in _documents and rebuild the vector store.

    Chunking is treated as an ingestion-time decision (you have to
    explicitly rebuild), unlike top-k which is just a per-query parameter --
    that split mirrors how real RAG systems are structured.
    """
    global _all_chunks, _vector_store, CHUNK_SIZE, CHUNK_OVERLAP
    CHUNK_SIZE, CHUNK_OVERLAP = chunk_size, overlap
    _all_chunks = chunk_documents(_documents, chunk_size, overlap)
    _vector_store = InMemoryVectorStore()
    _vector_store.add(_all_chunks)
    print(f"[index] {len(_documents)} document(s) -> {len(_all_chunks)} chunk(s) "
          f"(chunk_size={chunk_size}, overlap={overlap}).")


def chunks_response() -> dict:
    """Shared payload for any endpoint that changes or reports the chunk set."""
    points = _vector_store.project_chunks()
    vectors = _vector_store.chunk_vectors()
    chunks = []
    for c, point, vector in zip(_all_chunks, points, vectors):
        chunks.append({
            "source": c.source,
            "index": c.index,
            "text": c.text,
            "x": float(point[0]),
            "y": float(point[1]),
            "vector_preview": vector[:VECTOR_PREVIEW_DIMS].tolist(),
            "vector_dim": int(vector.shape[0]),
        })
    return {
        "chunk_count": len(_all_chunks),
        "chunk_size": CHUNK_SIZE,
        "overlap": CHUNK_OVERLAP,
        "chunks": chunks,
    }


def _env_file_path() -> Path:
    return Path(__file__).parent / ".env"


def _write_env_value(key: str, value: str) -> None:
    """Upsert a single KEY=value line into .env, preserving everything else.

    If the key already exists (commented out or not, e.g. the optional
    provider blocks in .env.example), that line is replaced in place so
    configuring a provider through the UI "activates" it the same way
    manually uncommenting the line would.
    """
    path = _env_file_path()
    lines = path.read_text().splitlines() if path.exists() else []
    new_line = f"{key}={value}"
    for i, line in enumerate(lines):
        stripped = line.strip().lstrip("#").strip()
        if stripped.startswith(f"{key}="):
            lines[i] = new_line
            break
    else:
        lines.append(new_line)
    path.write_text("\n".join(lines) + "\n")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/config")
def api_config_get():
    """Reports which provider is active and whether it has a key configured.

    Never returns the key itself -- only a boolean -- even though this is a
    local single-student app, echoing a secret back once it's been entered
    is needless exposure.
    """
    provider = os.environ.get("LLM_PROVIDER", "anthropic").lower()
    if provider not in PROVIDERS:
        provider = "anthropic"
    config = PROVIDERS[provider]
    key_configured = bool(os.environ.get(config["api_key_env"])) if config["key_required"] else True
    return jsonify({
        "provider": provider,
        "key_required": config["key_required"],
        "key_configured": key_configured,
        "model": os.environ.get(config["model_env"], config["model_default"]),
        # Every provider's static metadata, so the frontend can build the
        # picker/placeholders without duplicating these defaults in JS.
        "all_providers": {
            name: {
                "key_required": p["key_required"],
                "model_default": p["model_default"],
                "model_choices": p["model_choices"],
            }
            for name, p in PROVIDERS.items()
        },
    })


@app.route("/api/config", methods=["POST"])
def api_config_set():
    """Sets the active provider/key/model for this run *and* persists it to
    .env so it survives a restart -- the next query picks it up immediately
    since rag/generation.py reads os.environ at call time, not just at
    startup.
    """
    body = request.get_json(silent=True) or {}
    provider = (body.get("provider") or "").strip().lower()
    api_key = (body.get("api_key") or "").strip()
    model = (body.get("model") or "").strip()

    if provider not in PROVIDERS:
        return jsonify({"error": f"Unknown provider '{provider}'. Valid options: {', '.join(PROVIDERS.keys())}."}), 400

    config = PROVIDERS[provider]
    already_has_key = bool(os.environ.get(config["api_key_env"]))
    if config["key_required"] and not api_key and not already_has_key:
        return jsonify({"error": f"Please provide an API key for {provider}."}), 400

    os.environ["LLM_PROVIDER"] = provider
    _write_env_value("LLM_PROVIDER", provider)

    if api_key:
        os.environ[config["api_key_env"]] = api_key
        _write_env_value(config["api_key_env"], api_key)

    if model:
        os.environ[config["model_env"]] = model
        _write_env_value(config["model_env"], model)

    return jsonify({"ok": True, "provider": provider})


@app.route("/api/chunks")
def api_chunks():
    """Lets the UI show the full chunk set (and plot) up front, before any query."""
    return jsonify(chunks_response())


@app.route("/api/reindex", methods=["POST"])
def api_reindex():
    body = request.get_json(silent=True) or {}
    try:
        chunk_size = int(body.get("chunk_size", CHUNK_SIZE))
        overlap = int(body.get("overlap", CHUNK_OVERLAP))
    except (TypeError, ValueError):
        return jsonify({"error": "chunk_size and overlap must be integers."}), 400

    if not (MIN_CHUNK_SIZE <= chunk_size <= MAX_CHUNK_SIZE):
        return jsonify({"error": f"chunk_size must be between {MIN_CHUNK_SIZE} and {MAX_CHUNK_SIZE}."}), 400
    if not (0 <= overlap < chunk_size):
        return jsonify({"error": "overlap must be >= 0 and less than chunk_size."}), 400

    rebuild_index(chunk_size, overlap)
    return jsonify(chunks_response())


@app.route("/api/documents", methods=["POST"])
def api_documents():
    body = request.get_json(silent=True) or {}
    name = (body.get("name") or "custom_doc").strip()
    text = (body.get("text") or "").strip()
    if not text:
        return jsonify({"error": "Please provide non-empty 'text'."}), 400

    if not name.endswith(".txt"):
        name += ".txt"
    base_name = name
    suffix = 1
    while name in _documents:
        suffix += 1
        name = f"{base_name.removesuffix('.txt')}_{suffix}.txt"

    _documents[name] = text
    rebuild_index(CHUNK_SIZE, CHUNK_OVERLAP)
    response = chunks_response()
    response["added_name"] = name
    return jsonify(response)


@app.route("/api/query", methods=["POST"])
def api_query():
    body = request.get_json(silent=True) or {}
    query = (body.get("query") or "").strip()
    if not query:
        return jsonify({"error": "Please provide a non-empty 'query'."}), 400

    try:
        top_k = int(body.get("top_k", TOP_K))
    except (TypeError, ValueError):
        top_k = TOP_K
    top_k = max(MIN_TOP_K, min(MAX_TOP_K, top_k))

    use_rag = body.get("use_rag", True)
    compare = bool(body.get("compare", False))

    # Embed the query once and reuse it for retrieval, the plot point, and
    # the vector preview -- avoids re-running the embedding model 3x per request.
    query_vector = embed_texts([query])[0]

    # Retrieval is local and free, so always run it -- it powers the plot
    # and the retrieved-chunks panel regardless of which answer mode is used.
    scored_chunks = _vector_store.search_by_vector(query_vector, top_k=top_k)
    retrieved = [
        {
            "source": sc.chunk.source,
            "index": sc.chunk.index,
            "text": sc.chunk.text,
            "score": sc.score,
            "vector_preview": sc.vector[:VECTOR_PREVIEW_DIMS].tolist(),
        }
        for sc in scored_chunks
    ]

    point = _vector_store.project(query_vector[None, :])[0] if _all_chunks else None
    query_point_dict = {"x": float(point[0]), "y": float(point[1])} if point is not None else None

    rag_result = None
    no_rag_result = None

    if compare or use_rag:
        try:
            prompt_sent, answer = generate_answer(query, scored_chunks)
            rag_result = {"prompt_sent": prompt_sent, "answer": answer, "error": None, "needs_config": False}
        except (MissingAPIKeyError, GenerationError) as exc:
            rag_result = {
                "prompt_sent": None, "answer": None, "error": str(exc),
                "needs_config": isinstance(exc, MissingAPIKeyError),
            }

    if compare or not use_rag:
        try:
            answer = generate_plain_answer(query)
            no_rag_result = {"answer": answer, "error": None, "needs_config": False}
        except (MissingAPIKeyError, GenerationError) as exc:
            no_rag_result = {
                "answer": None, "error": str(exc),
                "needs_config": isinstance(exc, MissingAPIKeyError),
            }

    return jsonify({
        "query": query,
        "retrieved_chunks": retrieved,
        "query_point": query_point_dict,
        "query_vector_preview": query_vector[:VECTOR_PREVIEW_DIMS].tolist(),
        "embedding_dim": int(query_vector.shape[0]),
        "rag": rag_result,
        "no_rag": no_rag_result,
    })


_documents = _load_sample_documents()
rebuild_index(CHUNK_SIZE, CHUNK_OVERLAP)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
