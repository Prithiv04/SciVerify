from __future__ import annotations

import json
import logging
import os
from abc import ABC, abstractmethod
from typing import Any, TypeVar

import httpx
from pydantic import BaseModel, ValidationError

from app.config import LLM_BASE_URL, LLM_MODEL, LLM_REQUEST_TIMEOUT

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class LLMProviderError(Exception):
    """Raised when an LLM provider fails."""


class LLMUnavailableError(LLMProviderError):
    """Raised when no LLM provider is configured or available."""


class LLMResponseError(LLMProviderError):
    """Raised when an LLM response cannot be parsed or validated."""


class LLMProvider(ABC):
    @abstractmethod
    def generate(
        self,
        prompt: str,
        *,
        system: str | None = None,
        response_model: type[T] | None = None,
    ) -> T | str:
        """Generate a response from the configured LLM provider."""


class UnavailableLLMProvider(LLMProvider):
    def generate(
        self,
        prompt: str,
        *,
        system: str | None = None,
        response_model: type[T] | None = None,
    ) -> T | str:
        raise LLMUnavailableError(
            "LLM provider is not configured. Set LLM_PROVIDER and LLM_API_KEY to enable verification agents."
        )


class OpenAICompatibleLLMProvider(LLMProvider):
    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        base_url: str,
        timeout: float = LLM_REQUEST_TIMEOUT,
        client: httpx.Client | None = None,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client = client

    def generate(
        self,
        prompt: str,
        *,
        system: str | None = None,
        response_model: type[T] | None = None,
    ) -> T | str:
        owns_client = self._client is None
        client = self._client or httpx.Client(timeout=self.timeout)

        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.1,
        }
        if response_model is not None:
            payload["response_format"] = {"type": "json_object"}

        try:
            response = client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
        except httpx.TimeoutException as exc:
            raise LLMProviderError("LLM request timed out.") from exc
        except httpx.RequestError as exc:
            raise LLMProviderError("LLM request failed.") from exc
        finally:
            if owns_client:
                client.close()

        if response.status_code >= 500:
            raise LLMProviderError("LLM provider is unavailable.")
        if response.status_code >= 400:
            raise LLMProviderError("LLM provider rejected the request.")

        try:
            body = response.json()
            content = body["choices"][0]["message"]["content"]
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise LLMResponseError("LLM returned an unexpected response format.") from exc

        if response_model is None:
            return content

        try:
            parsed = json.loads(content)
            return response_model.model_validate(parsed)
        except (json.JSONDecodeError, ValidationError) as exc:
            raise LLMResponseError("LLM returned invalid structured output.") from exc


def get_llm_provider() -> LLMProvider:
    provider = os.getenv("LLM_PROVIDER", "none").strip().lower()
    api_key = os.getenv("LLM_API_KEY", "").strip()
    model = os.getenv("LLM_MODEL", LLM_MODEL).strip()
    base_url = os.getenv("LLM_BASE_URL", LLM_BASE_URL).strip().rstrip("/")

    if provider in {"", "none", "disabled"} or not api_key:
        return UnavailableLLMProvider()

    if provider in {"openai", "openai-compatible", "compatible"}:
        return OpenAICompatibleLLMProvider(
            api_key=api_key,
            model=model,
            base_url=base_url,
        )

    raise LLMUnavailableError(f"Unsupported LLM provider: {provider}")
