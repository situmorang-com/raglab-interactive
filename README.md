# RAG Lab Interactive

A from-scratch, step-by-step Retrieval-Augmented Generation (RAG) demo
built for teaching. Ask a question in the browser and watch every stage
of the pipeline run live: **chunking → embedding → retrieval →
generation**.

No vector database, no orchestration framework, no magic — just ~300
lines of readable Python so you can see exactly how RAG works, then fork
it and extend it yourself.

![pipeline](https://img.shields.io/badge/stages-chunk%20%E2%86%92%20embed%20%E2%86%92%20retrieve%20%E2%86%92%20generate-blueviolet)

## Quickstart

```bash
git clone <your-fork-url> raglab-interactive
cd raglab-interactive

python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# edit .env and add your ANTHROPIC_API_KEY (get one at console.anthropic.com)

python3 check_setup.py           # verifies everything above is actually working
python3 app.py
```

Open **http://localhost:5000**, type a question (e.g. *"How many vacation
days do I get?"*), and watch the four pipeline stages render.

The first run downloads a small (~80MB) local embedding model
(`all-MiniLM-L6-v2`) — this takes a minute and only happens once.

Stuck? See [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) for the
most common setup issues and their fixes.

Run the tests (no API key needed — these only exercise chunking and
retrieval):

```bash
pytest tests/
```

## How RAG works (matches the four panels in the UI)

RAG answers a question by **retrieving** relevant text from your own
documents and then **augmenting** the LLM's prompt with that text before
**generating** an answer. This grounds the model's answer in your data
instead of relying purely on what it memorized during training.

1. **Chunking** ([`rag/chunking.py`](rag/chunking.py)) — Documents are too
   big to search or feed to an LLM all at once, so we split them into
   overlapping ~400-word chunks. Overlap means a sentence cut off at a
   chunk boundary still appears whole in the next chunk.

2. **Embedding** ([`rag/embeddings.py`](rag/embeddings.py)) — Each chunk
   (and later, each question) is converted into a vector of numbers by a
   local embedding model, such that semantically similar text produces
   similar vectors.

3. **Retrieval** ([`rag/vector_store.py`](rag/vector_store.py)) — When you
   ask a question, it's embedded the same way, then compared against
   every chunk's vector using cosine similarity. The top-k highest-scoring
   chunks are pulled out.

4. **Generation** ([`rag/generation.py`](rag/generation.py)) — The
   retrieved chunks are inserted into a prompt template along with your
   question, and sent to Claude. The model is instructed to answer using
   only that context.

The whole pipeline is orchestrated in [`app.py`](app.py), and the index
over `data/sample_docs/` is built once when the server starts.

Want to write the whole pipeline yourself, by hand, in a blank file before
reading any of the code above? See
[`docs/BUILD_YOUR_OWN.md`](docs/BUILD_YOUR_OWN.md) — a ~20 minute,
copy-pasteable tutorial that has you print the real embedding vectors and
similarity scores yourself, then compare your file to `rag/*.py`.

## Project layout

```
app.py                  Flask routes + pipeline orchestration
check_setup.py          Run before class -- verifies Python, deps, .env, and port 5000
rag/
  chunking.py            Step 1
  embeddings.py          Step 2
  vector_store.py        Step 3
  generation.py          Step 4
data/sample_docs/        Sample "company handbook" docs to query against
templates/, static/      Frontend (plain HTML/CSS/JS, no build step)
tests/test_rag.py        Tests for chunking + retrieval (no API key needed)
docs/BUILD_YOUR_OWN.md   Write a mini RAG pipeline yourself from a blank file
docs/LAB_WORKSHEET.md    Predict-then-reveal exercises using the app's live knobs
docs/TROUBLESHOOTING.md  Fixes for the most common setup problems
docs/EXTENDING.md        Exercises for going from this toy app to something production-style
```

## Extending it with Claude Code or Codex

This repo is meant to be a starting point you modify with an AI coding
assistant. Once you've got it running, try prompting your assistant
(Claude Code, Codex, etc.) with something like:

- *"Add support for ingesting PDF files into `data/sample_docs/`."*
- *"Add a `/api/chunks/<source>` endpoint that returns chunks for just one document."*
- *"Replace the in-memory vector store with Chroma, keeping the same `InMemoryVectorStore` interface."*
- *"Add streaming so the answer appears token-by-token instead of all at once."*

Because every stage lives in its own small file, an AI assistant (or you)
can read and modify one piece without needing to understand the whole
system. See [`docs/EXTENDING.md`](docs/EXTENDING.md) for a structured list
of exercises, roughly ordered from easiest to most "production-style."

## Troubleshooting

- **"ANTHROPIC_API_KEY is not set"** — copy `.env.example` to `.env` and
  add a real key from [console.anthropic.com](https://console.anthropic.com).
  The retrieval stage still works without a key; only the final answer
  step needs it.
- **First request is slow** — the embedding model downloads on first use
  and the index is rebuilt on every server restart. Subsequent requests
  are fast.

## License

MIT — see [LICENSE](LICENSE). Fork it, teach with it, break it, fix it.
