# Build Your Own Mini RAG From Scratch

The app in this repo is ~300 lines across 4 small files. This tutorial has
you write a much smaller version of it yourself, by hand, in a single
empty file — no Flask, no web UI, just the core idea running in your
terminal. By the end you'll have watched real numbers move through every
stage, and you'll be able to compare your file line-for-line against
`rag/chunking.py`, `rag/embeddings.py`, `rag/vector_store.py`, and
`rag/generation.py` to see that you built the same thing.

**Time**: ~20 minutes. **Prerequisite**: Python installed, and the same
`.venv` you set up for the main app (it already has everything you need).

Create a new file in this repo's root called `my_first_rag.py` and build
it up section by section.

## Step 0: Setup

```python
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")
```

Run it (`python3 my_first_rag.py`). The first run downloads the model
(~80MB) — that's the same model `rag/embeddings.py` uses.

## Step 1: Chunks (hardcoded, no real chunking algorithm yet)

Real documents need to be split up (see `rag/chunking.py` for the real
version with overlap). For now, just hardcode 3 short "documents" as a
list of strings:

```python
chunks = [
    "The office is open Monday to Friday, 9am to 6pm.",
    "Employees get 15 paid vacation days per year.",
    "Free coffee and snacks are available in the kitchen.",
]
```

## Step 2: Turn each chunk into a vector

This is the whole point of this exercise — see it with your own eyes:

```python
vectors = model.encode(chunks, normalize_embeddings=True)

print("Shape of the vectors matrix:", vectors.shape)
print("First chunk's vector (first 10 of many numbers):")
print(vectors[0][:10])
print("Length of that vector:", np.linalg.norm(vectors[0]))
```

Run it. You should see something like `Shape: (3, 384)` — 3 chunks, each
turned into 384 numbers — and the length should print as almost exactly
`1.0`. That's not an accident: `normalize_embeddings=True` scales every
vector to unit length, which is what makes the next step's math work as
plain multiplication instead of needing a separate "divide by length"
step. This is exactly what `rag/embeddings.py`'s `embed_texts()` does.

**Stop and look at the numbers.** They mean nothing to a human individually
— there's no dimension that means "is about vacation." But the *pattern*
across all 384 of them is what encodes meaning, and two chunks about
similar topics will have similar patterns. You can't see that from 10
numbers, but the app's embedding-space plot (stage 2) shows you the
*shape* of that similarity by compressing all 384 dimensions down to 2.

## Step 3: This *is* the database

```python
print("The whole 'index' is just this array in memory:")
print(vectors.shape, vectors.dtype)
```

There's no separate database process. `vectors` is a NumPy array sitting
in your Python process's RAM. When you close the script, it's gone. This
is exactly what `InMemoryVectorStore` in `rag/vector_store.py` wraps — a
few convenience methods around one matrix, nothing more. A production
system swaps this matrix for a real vector database (Pinecone, Chroma,
pgvector) so it persists to disk and scales past what fits in RAM — but
the core operation you're about to do in Step 4 stays identical.

## Step 4: Embed a question and rank the chunks

```python
question = "How many vacation days do I get?"
question_vector = model.encode([question], normalize_embeddings=True)[0]

scores = vectors @ question_vector  # dot product of every row with the question

for chunk, score in sorted(zip(chunks, scores), key=lambda pair: -pair[1]):
    print(f"{score:.4f}  {chunk}")
```

Run it. The vacation chunk should score highest. `vectors @ question_vector`
is matrix-vector multiplication — one line computes the similarity between
your question and *every* chunk at once. Because everything is
unit-length (Step 2), this dot product **is** cosine similarity — no
extra normalization needed. This one line is the entire "retrieval"
algorithm in `rag/vector_store.py`'s `search_by_vector()`.

## Step 5 (optional): Generate a grounded answer

If you have `ANTHROPIC_API_KEY` set in your `.env`:

```python
import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

best_chunk = chunks[int(np.argmax(scores))]

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
response = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=200,
    messages=[{
        "role": "user",
        "content": f"Context: {best_chunk}\n\nQuestion: {question}\n\nAnswer using only the context.",
    }],
)
print(response.content[0].text)
```

That's it — chunk, embed, store, retrieve, generate, in about 30 lines.

## Now compare

Open these four files side by side with what you just wrote:

- [`rag/chunking.py`](../rag/chunking.py) — Step 1, but splitting real documents with overlap instead of hardcoding 3 strings.
- [`rag/embeddings.py`](../rag/embeddings.py) — Step 2, wrapped in one function.
- [`rag/vector_store.py`](../rag/vector_store.py) — Steps 3 and 4, wrapped in a small class so it can hold multiple batches of chunks and also do the 2D plotting the UI shows you.
- [`rag/generation.py`](../rag/generation.py) — Step 5, with error handling for a missing/invalid API key and a "no-RAG baseline" variant.

You didn't just read about RAG — you built it. The running app
(`python3 app.py`) is this same pipeline with a web UI wrapped around it,
plus the extra knobs described in [LAB_WORKSHEET.md](LAB_WORKSHEET.md).
That's the natural next step: use those knobs to explore *why* each
design decision here (chunk size, top-k, overlap) matters, using the
intuition you just built by hand.
