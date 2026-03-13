from __future__ import annotations

from .common import WareraModel


class Article(WareraModel):
    id: str | None = None
    title: str | None = None
    content: str | None = None
    author_id: str | None = None
    country_id: str | None = None
    type: str | None = None
    category: str | None = None
    language: str | None = None
    score: int | None = None
    views: int | None = None
    comments: int | None = None
    image: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class ArticleLite(WareraModel):
    id: str | None = None
    title: str | None = None
    author_id: str | None = None
    country_id: str | None = None
    type: str | None = None
    category: str | None = None
    language: str | None = None
    score: int | None = None
    views: int | None = None
    image: str | None = None
    created_at: str | None = None
