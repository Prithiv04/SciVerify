from __future__ import annotations

import pytest

from app.services.llm.provider import (
    LLMUnavailableError,
    UnavailableLLMProvider,
    get_llm_provider,
)


class TestLLMProvider:
    def test_unavailable_when_not_configured(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("LLM_PROVIDER", "none")
        monkeypatch.setenv("LLM_API_KEY", "")

        provider = get_llm_provider()
        assert isinstance(provider, UnavailableLLMProvider)

        with pytest.raises(LLMUnavailableError):
            provider.generate("test prompt")

    def test_unsupported_provider(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("LLM_PROVIDER", "unknown-provider")
        monkeypatch.setenv("LLM_API_KEY", "test-key")

        with pytest.raises(LLMUnavailableError):
            get_llm_provider()
