"""Step 4: Generation.

Build an "augmented" prompt out of the retrieved chunks plus the user's
question, and ask Claude to answer using only that context. This is the
"Augmented Generation" half of Retrieval-Augmented Generation.

Also exposes generate_plain_answer(), which skips retrieval entirely --
useful as a side-by-side baseline so students can see what the model says
with and without grounding.
"""

import os

import anthropic

from rag.vector_store import ScoredChunk

DEFAULT_MODEL = "claude-sonnet-5"

RAG_SYSTEM_PROMPT = (
    "You are a helpful assistant answering questions using ONLY the provided "
    "context. If the context doesn't contain the answer, say you don't know "
    "rather than making something up. Keep answers concise."
)

PLAIN_SYSTEM_PROMPT = (
    "You are a helpful assistant. Answer the question from your general "
    "knowledge. Keep answers concise."
)


class MissingAPIKeyError(RuntimeError):
    pass


class GenerationError(RuntimeError):
    """Wraps any error from the Claude API call into a message safe to show students."""

    pass


def build_prompt(query: str, scored_chunks: list[ScoredChunk]) -> str:
    """Assemble the literal text that gets sent to Claude as context + question."""
    context_blocks = []
    for sc in scored_chunks:
        context_blocks.append(f"[Source: {sc.chunk.source}]\n{sc.chunk.text}")
    context = "\n\n---\n\n".join(context_blocks) if context_blocks else "(no relevant context found)"

    return (
        f"Context:\n{context}\n\n"
        f"Question: {query}\n\n"
        "Answer the question using only the context above."
    )


def _call_claude(prompt: str, system: str) -> str:
    """Shared Claude API call + error handling for both the RAG and plain paths."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise MissingAPIKeyError(
            "ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add your "
            "Anthropic API key, then restart the app."
        )

    model = os.environ.get("CLAUDE_MODEL", DEFAULT_MODEL)
    client = anthropic.Anthropic(api_key=api_key)

    try:
        response = client.messages.create(
            model=model,
            max_tokens=500,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
    except anthropic.AuthenticationError as exc:
        raise GenerationError(
            "Claude rejected the API key in .env (invalid x-api-key). Double-check "
            "ANTHROPIC_API_KEY against console.anthropic.com and restart the app."
        ) from exc
    except anthropic.APIError as exc:
        raise GenerationError(f"The Claude API call failed: {exc}") from exc

    return "".join(block.text for block in response.content if block.type == "text")


def generate_answer(query: str, scored_chunks: list[ScoredChunk]) -> tuple[str, str]:
    """Call Claude with the retrieved context and return (prompt_sent, answer)."""
    prompt = build_prompt(query, scored_chunks)
    answer = _call_claude(prompt, RAG_SYSTEM_PROMPT)
    return prompt, answer


def generate_plain_answer(query: str) -> str:
    """Call Claude with no retrieved context -- the no-RAG baseline."""
    return _call_claude(query, PLAIN_SYSTEM_PROMPT)
