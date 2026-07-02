"""Step 4: Generation.

Build an "augmented" prompt out of the retrieved chunks plus the user's
question, and ask an LLM to answer using only that context. This is the
"Augmented Generation" half of Retrieval-Augmented Generation.

Also exposes generate_plain_answer(), which skips retrieval entirely --
useful as a side-by-side baseline so students can see what the model says
with and without grounding.

Which LLM answers is controlled by the LLM_PROVIDER env var:
  anthropic (default) | openai | nvidia | ollama
NVIDIA's API Catalog, OpenAI's API, and a local Ollama server are all
OpenAI-compatible (same request/response shape), so those three share one
code path parameterized by the PROVIDERS table below -- only Anthropic
uses a different SDK.
"""

import os

import anthropic
import openai

from rag.vector_store import ScoredChunk

DEFAULT_PROVIDER = "anthropic"
DEFAULT_CLAUDE_MODEL = "claude-sonnet-5"

# Config for every provider, including Anthropic -- one source of truth
# reused by app.py (the /api/config endpoint) and check_setup.py. Anthropic
# still gets its own call path in _call_claude() since its SDK has a
# different shape, but its metadata lives here alongside the rest so
# nothing has to duplicate it. key_help is shown in error messages so
# students know where to get a key; key_prefix is a soft format check.
PROVIDERS = {
    "anthropic": {
        "api_key_env": "ANTHROPIC_API_KEY",
        "base_url_env": None,
        "base_url_default": None,
        "model_env": "CLAUDE_MODEL",
        "model_default": "claude-sonnet-5",
        "model_choices": ["claude-sonnet-5", "claude-opus-4-8", "claude-haiku-4-5-20251001"],
        "key_required": True,
        "key_help": "console.anthropic.com",
        "key_prefix": "sk-ant-",
    },
    "openai": {
        "api_key_env": "OPENAI_API_KEY",
        "base_url_env": "OPENAI_BASE_URL",
        "base_url_default": None,  # None = use the openai SDK's own default
        "model_env": "OPENAI_MODEL",
        "model_default": "gpt-4o-mini",
        "model_choices": ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
        "key_required": True,
        "key_help": "platform.openai.com",
        "key_prefix": "sk-",
    },
    "nvidia": {
        "api_key_env": "NVIDIA_API_KEY",
        "base_url_env": "NVIDIA_BASE_URL",
        "base_url_default": "https://integrate.api.nvidia.com/v1",
        "model_env": "NVIDIA_MODEL",
        "model_default": "minimaxai/minimax-m3",
        "model_choices": [
            "minimaxai/minimax-m3",
            "meta/llama-3.1-70b-instruct",
            "meta/llama-3.1-8b-instruct",
            "mistralai/mixtral-8x7b-instruct-v0.1",
        ],
        "key_required": True,
        "key_help": "build.nvidia.com",
        "key_prefix": "nvapi-",
    },
    "ollama": {
        "api_key_env": "OLLAMA_API_KEY",
        "base_url_env": "OLLAMA_BASE_URL",
        "base_url_default": "http://localhost:11434/v1",
        "model_env": "OLLAMA_MODEL",
        "model_default": "llama3.2",
        "model_choices": ["llama3.2", "llama3.1", "mistral", "qwen2.5", "phi3"],
        "key_required": False,  # Ollama doesn't validate a key at all
        "key_help": None,
        "key_prefix": None,
    },
}

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
    """Wraps any error from the LLM API call into a message safe to show students."""

    pass


def build_prompt(query: str, scored_chunks: list[ScoredChunk]) -> str:
    """Assemble the literal text that gets sent to the LLM as context + question."""
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
    """Anthropic's SDK has a different call shape from the others, so it gets its own path."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise MissingAPIKeyError(
            "ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add your "
            "Anthropic API key (console.anthropic.com), then restart the app."
        )

    model = os.environ.get("CLAUDE_MODEL", DEFAULT_CLAUDE_MODEL)
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


def _call_openai_compatible(prompt: str, system: str, provider: str) -> str:
    """Shared path for openai / nvidia / ollama -- all speak the same chat-completions API."""
    config = PROVIDERS[provider]
    api_key = os.environ.get(config["api_key_env"])

    if config["key_required"] and not api_key:
        raise MissingAPIKeyError(
            f"{config['api_key_env']} is not set. Copy .env.example to .env and add your "
            f"{provider} API key (get one at {config['key_help']}), then restart the app."
        )
    if not api_key:
        api_key = "not-needed"  # Ollama's SDK client requires a non-empty string but never checks it

    base_url = os.environ.get(config["base_url_env"], config["base_url_default"])
    model = os.environ.get(config["model_env"], config["model_default"])
    client = openai.OpenAI(api_key=api_key, base_url=base_url)

    try:
        response = client.chat.completions.create(
            model=model,
            max_tokens=500,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        )
    except (openai.AuthenticationError, openai.PermissionDeniedError) as exc:
        # Some providers (e.g. NVIDIA) return 403 Forbidden for a bad key
        # instead of 401, which the SDK maps to PermissionDeniedError rather
        # than AuthenticationError -- both mean "your key/access is invalid."
        raise GenerationError(
            f"{provider} rejected the API key in .env. Double-check {config['api_key_env']} "
            f"against {config['key_help']}, then restart the app."
        ) from exc
    except openai.APIConnectionError as exc:
        if provider == "ollama":
            raise GenerationError(
                f"Could not reach Ollama at {base_url}. Is `ollama serve` running, and have "
                f"you pulled the model with `ollama pull {model}`?"
            ) from exc
        raise GenerationError(f"Could not reach {provider}'s API: {exc}") from exc
    except openai.APIError as exc:
        raise GenerationError(f"The {provider} API call failed: {exc}") from exc

    return response.choices[0].message.content


def _call_llm(prompt: str, system: str) -> str:
    """Dispatches to whichever provider LLM_PROVIDER selects (default: anthropic)."""
    provider = os.environ.get("LLM_PROVIDER", DEFAULT_PROVIDER).lower()
    if provider == "anthropic":
        return _call_claude(prompt, system)
    if provider in PROVIDERS:
        return _call_openai_compatible(prompt, system, provider)
    raise GenerationError(
        f"Unknown LLM_PROVIDER '{provider}'. Valid options: {', '.join(PROVIDERS.keys())}."
    )


def generate_answer(query: str, scored_chunks: list[ScoredChunk]) -> tuple[str, str]:
    """Call the configured LLM with the retrieved context and return (prompt_sent, answer)."""
    prompt = build_prompt(query, scored_chunks)
    answer = _call_llm(prompt, RAG_SYSTEM_PROMPT)
    return prompt, answer


def generate_plain_answer(query: str) -> str:
    """Call the configured LLM with no retrieved context -- the no-RAG baseline."""
    return _call_llm(query, PLAIN_SYSTEM_PROMPT)
