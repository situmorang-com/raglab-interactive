# Extending RAG Lab Interactive

This app is intentionally minimal. Below are exercises, roughly ordered
from easiest to most "production-style," that take it further. Each one
is a good prompt to hand to an AI coding assistant (Claude Code, Codex,
etc.) once you understand what the current code does.

## Easy — extend within the existing architecture

1. **Add more sample documents.** Drop more `.txt` files into
   `data/sample_docs/` and restart the server — no code changes needed.
   Try documents from your own course material.

2. **Tune chunk size and overlap.** Edit `CHUNK_SIZE` / `CHUNK_OVERLAP` in
   `.env` and observe how it changes which chunks get retrieved for the
   same question. Smaller chunks are more precise but lose surrounding
   context; larger chunks have more context but dilute relevance.

3. **Change `TOP_K`.** Retrieve more or fewer chunks per query and see how
   it affects answer quality and the size of the prompt sent to Claude.

4. **Show similarity scores as percentages or a bar chart** in the UI
   (`static/app.js` + `static/style.css`) instead of raw cosine scores.

## Medium — change how documents get in

5. **PDF / Markdown ingestion.** Add a loader (e.g. `pypdf`) so
   `data/sample_docs/` can contain PDFs and Markdown, not just `.txt`.
   This only touches `load_documents()` in `app.py`.

6. **Per-document chunk viewer.** Add a `/api/chunks/<source>` route and a
   UI dropdown to inspect chunks for a single document.

7. **Highlight which words triggered retrieval.** After getting the top-k
   chunks, do a simple keyword overlap check between the query and each
   chunk and bold the overlapping words in the UI.

## Harder — move toward production-style architecture

8. **Swap the vector store.** Replace `InMemoryVectorStore` in
   `rag/vector_store.py` with [Chroma](https://www.trychroma.com/) or
   [FAISS](https://github.com/facebookresearch/faiss), keeping the same
   `add()` / `search()` interface so the rest of the app doesn't need to
   change. This is the standard next step for real-sized document sets.

9. **Persist the index.** Right now the index is rebuilt from scratch on
   every restart. Persist embeddings to disk (or a real vector DB) so
   restarts are instant and documents can be added incrementally.

10. **Streaming answers.** Use the Anthropic SDK's streaming API
    (`client.messages.stream(...)`) and Server-Sent Events or a streaming
    `fetch()` response so the answer appears token-by-token.

11. **Conversation memory.** Let students ask follow-up questions that
    reference earlier turns, by keeping a short conversation history and
    including it in the prompt (watch out for prompt size growth).

12. **Re-ranking.** After retrieving top-k chunks by embedding similarity,
    add a second pass that re-ranks them with a cross-encoder model or an
    LLM call, and compare answer quality before/after.

13. **Evaluation.** Build a small set of question/expected-answer pairs
    and a script that scores retrieval (did the right chunk get
    retrieved?) and generation (does the answer match, using exact match,
    keyword match, or an LLM-as-judge prompt) quality over time as you
    change the pipeline.

14. **Guardrails.** Add a check that refuses to answer (or asks for
    clarification) when retrieval similarity scores are all below a
    threshold, instead of letting Claude guess from weak context.

## A note on scope

Don't add everything at once. The point of starting from a deliberately
simple app is that each exercise is a clean, reviewable diff against a
codebase you already understand. Pick one, implement it, run
`pytest tests/`, and try it in the browser before moving to the next.
