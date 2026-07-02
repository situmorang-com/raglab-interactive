"""Tests for the multi-provider LLM dispatch in rag/generation.py.

All SDK clients are mocked -- no real network calls, no real API keys
needed. Exercises the anthropic path plus the shared openai-compatible
path used for openai/nvidia/ollama.
"""

from unittest.mock import MagicMock, patch

import httpx
import openai as openai_sdk
import anthropic as anthropic_sdk
import pytest

from rag.generation import GenerationError, MissingAPIKeyError, generate_plain_answer

DUMMY_REQUEST = httpx.Request("POST", "http://test")
DUMMY_RESPONSE = httpx.Response(401, request=DUMMY_REQUEST)

# Wiped to a known-clean state before every test in this file, then each
# test layers its own monkeypatch.setenv on top. Without this, a real .env
# loaded by app.py earlier in the same pytest session (test_app.py imports
# app, which calls load_dotenv() at module scope) would leak real values
# like a real OPENAI_MODEL into these tests and silently break assertions
# about default values.
ENV_KEYS_TO_ISOLATE = [
    "LLM_PROVIDER",
    "ANTHROPIC_API_KEY", "CLAUDE_MODEL",
    "OPENAI_API_KEY", "OPENAI_MODEL", "OPENAI_BASE_URL",
    "NVIDIA_API_KEY", "NVIDIA_MODEL", "NVIDIA_BASE_URL",
    "OLLAMA_API_KEY", "OLLAMA_MODEL", "OLLAMA_BASE_URL",
]


@pytest.fixture(autouse=True)
def isolated_provider_env(monkeypatch):
    for key in ENV_KEYS_TO_ISOLATE:
        monkeypatch.delenv(key, raising=False)


def _anthropic_response(text="15 days per year."):
    block = MagicMock(type="text", text=text)
    return MagicMock(content=[block])


def _openai_response(text="15 days per year."):
    message = MagicMock(content=text)
    choice = MagicMock(message=message)
    return MagicMock(choices=[choice])


# --- anthropic (default provider) -------------------------------------------

def test_default_provider_is_anthropic(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    with patch("rag.generation.anthropic.Anthropic") as mock_cls:
        mock_cls.return_value.messages.create.return_value = _anthropic_response()
        answer = generate_plain_answer("How many vacation days?")
    assert answer == "15 days per year."
    mock_cls.assert_called_once_with(api_key="sk-ant-test")


def test_anthropic_missing_key_raises(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(MissingAPIKeyError):
        generate_plain_answer("test")


def test_anthropic_auth_error_maps_to_generation_error(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-bad")
    with patch("rag.generation.anthropic.Anthropic") as mock_cls:
        mock_cls.return_value.messages.create.side_effect = anthropic_sdk.AuthenticationError(
            "bad key", response=DUMMY_RESPONSE, body=None
        )
        with pytest.raises(GenerationError, match="console.anthropic.com"):
            generate_plain_answer("test")


# --- openai / nvidia / ollama (shared openai-compatible path) ---------------

def test_openai_provider_uses_default_model_and_base_url(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    with patch("rag.generation.openai.OpenAI") as mock_cls:
        mock_cls.return_value.chat.completions.create.return_value = _openai_response()
        answer = generate_plain_answer("test")
    assert answer == "15 days per year."
    mock_cls.assert_called_once_with(api_key="sk-test", base_url=None)
    _, kwargs = mock_cls.return_value.chat.completions.create.call_args
    assert kwargs["model"] == "gpt-4o-mini"


def test_nvidia_provider_uses_nvidia_base_url_and_model(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "nvidia")
    monkeypatch.setenv("NVIDIA_API_KEY", "nvapi-test")
    with patch("rag.generation.openai.OpenAI") as mock_cls:
        mock_cls.return_value.chat.completions.create.return_value = _openai_response()
        generate_plain_answer("test")
    mock_cls.assert_called_once_with(api_key="nvapi-test", base_url="https://integrate.api.nvidia.com/v1")
    _, kwargs = mock_cls.return_value.chat.completions.create.call_args
    assert kwargs["model"] == "minimaxai/minimax-m3"


def test_ollama_does_not_require_api_key(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.delenv("OLLAMA_API_KEY", raising=False)
    with patch("rag.generation.openai.OpenAI") as mock_cls:
        mock_cls.return_value.chat.completions.create.return_value = _openai_response()
        answer = generate_plain_answer("test")  # should NOT raise MissingAPIKeyError
    assert answer == "15 days per year."
    mock_cls.assert_called_once_with(api_key="not-needed", base_url="http://localhost:11434/v1")


def test_openai_missing_key_raises(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(MissingAPIKeyError, match="platform.openai.com"):
        generate_plain_answer("test")


def test_nvidia_missing_key_raises(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "nvidia")
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)
    with pytest.raises(MissingAPIKeyError, match="build.nvidia.com"):
        generate_plain_answer("test")


def test_openai_compatible_auth_error_maps_to_generation_error(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "nvidia")
    monkeypatch.setenv("NVIDIA_API_KEY", "bad-key")
    with patch("rag.generation.openai.OpenAI") as mock_cls:
        mock_cls.return_value.chat.completions.create.side_effect = openai_sdk.AuthenticationError(
            "bad key", response=DUMMY_RESPONSE, body=None
        )
        with pytest.raises(GenerationError, match="build.nvidia.com"):
            generate_plain_answer("test")


def test_nvidia_permission_denied_maps_to_generation_error(monkeypatch):
    # NVIDIA returns 403 (PermissionDeniedError) for a bad key, not 401
    # (AuthenticationError) -- confirmed against the real API during
    # manual testing, so both must map to the same friendly message.
    monkeypatch.setenv("LLM_PROVIDER", "nvidia")
    monkeypatch.setenv("NVIDIA_API_KEY", "bad-key")
    with patch("rag.generation.openai.OpenAI") as mock_cls:
        mock_cls.return_value.chat.completions.create.side_effect = openai_sdk.PermissionDeniedError(
            "forbidden", response=httpx.Response(403, request=DUMMY_REQUEST), body=None
        )
        with pytest.raises(GenerationError, match="build.nvidia.com"):
            generate_plain_answer("test")


def test_ollama_connection_error_mentions_ollama_serve(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    with patch("rag.generation.openai.OpenAI") as mock_cls:
        mock_cls.return_value.chat.completions.create.side_effect = openai_sdk.APIConnectionError(
            message="connection failed", request=DUMMY_REQUEST
        )
        with pytest.raises(GenerationError, match="ollama serve"):
            generate_plain_answer("test")


def test_unknown_provider_raises_generation_error(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "cohere")
    with pytest.raises(GenerationError, match="Unknown LLM_PROVIDER"):
        generate_plain_answer("test")
