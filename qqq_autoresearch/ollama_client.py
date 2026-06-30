"""Minimal local Ollama HTTP client.

The client intentionally uses only `requests` so the repo does not need an
additional Ollama Python SDK dependency. It calls the local Ollama REST API by
default at http://localhost:11434.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import requests


class OllamaError(RuntimeError):
    """Raised when the local Ollama server or model call fails."""


@dataclass
class OllamaClient:
    base_url: str = "http://localhost:11434"
    model: str = "qwen2.5:7b"
    timeout: int = 600

    def _url(self, path: str) -> str:
        return self.base_url.rstrip("/") + path

    def health_check(self) -> dict[str, Any]:
        try:
            resp = requests.get(self._url("/api/tags"), timeout=20)
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            raise OllamaError(
                "Could not connect to local Ollama. Make sure Ollama is running "
                f"at {self.base_url}. Original error: {exc}"
            ) from exc

    def generate_json(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.2,
        num_ctx: int = 32768,
        keep_alive: str = "10m",
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": temperature,
                "num_ctx": num_ctx,
            },
            "keep_alive": keep_alive,
        }
        if system:
            payload["system"] = system

        try:
            resp = requests.post(self._url("/api/generate"), json=payload, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            raise OllamaError(f"Ollama /api/generate call failed: {exc}") from exc

        text = data.get("response", "")
        if not isinstance(text, str) or not text.strip():
            raise OllamaError("Ollama returned an empty response.")

        return self._parse_json_response(text)

    @staticmethod
    def _parse_json_response(text: str) -> dict[str, Any]:
        text = text.strip()
        try:
            obj = json.loads(text)
        except json.JSONDecodeError:
            # Some models still wrap JSON in prose or fences. Try to recover the
            # largest JSON-looking object.
            start = text.find("{")
            end = text.rfind("}")
            if start == -1 or end == -1 or end <= start:
                raise OllamaError("Model response was not valid JSON and no JSON object could be recovered.")
            try:
                obj = json.loads(text[start : end + 1])
            except json.JSONDecodeError as exc:
                raise OllamaError(f"Model response was not valid JSON: {exc}\nRaw response:\n{text[:2000]}") from exc
        if not isinstance(obj, dict):
            raise OllamaError("Expected top-level JSON object from model.")
        return obj
