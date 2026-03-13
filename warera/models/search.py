from __future__ import annotations

from typing import Any

from .common import WareraModel


class SearchResult(WareraModel):
    id: str | None = None
    type: str | None = None  # "user" | "country" | "company" | "mu" | "article"
    name: str | None = None
    image: str | None = None
    extra: dict[str, Any] | None = None


class SearchResults(WareraModel):
    results: list[SearchResult] = []
    total: int | None = None
