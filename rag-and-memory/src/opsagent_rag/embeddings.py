"""Embeddings opcionales a través del gateway (endpoint ``/v1/embeddings`` compatible con OpenAI).

Anthropic no ofrece embeddings: el gateway enruta el alias configurado (p. ej. un modelo de
Voyage AI) y la aplicación no conoce al proveedor ni guarda su clave.
"""

from __future__ import annotations

from typing import Protocol

import httpx


class Embedder(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...


class OpenAICompatibleEmbedder:
    def __init__(self, base_url: str, api_key: str, model: str, timeout: float = 30.0) -> None:
        self._client = httpx.Client(
            base_url=base_url.rstrip("/"), headers={"Authorization": f"Bearer {api_key}"}, timeout=timeout
        )
        self._model = model

    def embed(self, texts: list[str]) -> list[list[float]]:
        response = self._client.post("/v1/embeddings", json={"model": self._model, "input": texts})
        response.raise_for_status()
        data = sorted(response.json()["data"], key=lambda item: item["index"])
        return [item["embedding"] for item in data]
