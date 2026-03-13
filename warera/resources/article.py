from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from .._enums import ArticleType
from .._pagination import collect_all, paginate
from ..models.article import Article, ArticleLite
from ..models.common import CursorPage
from ._base import BaseResource


class ArticleResource(BaseResource):
    """
    Endpoints:
      • article.getArticleById
      • article.getArticleLiteById
      • article.getArticlesPaginated  (cursor-paginated)
    """

    async def get(self, article_id: str) -> Article:
        """Get a full article by ID (includes content body)."""
        raw = await self._get("article.getArticleById", articleId=article_id)
        return Article.model_validate(raw)

    async def get_lite(self, article_id: str) -> ArticleLite:
        """Get a lightweight article by ID (metadata only, no content body)."""
        raw = await self._get("article.getArticleLiteById", articleId=article_id)
        return ArticleLite.model_validate(raw)

    async def get_paginated(
        self,
        type: ArticleType | str,
        *,
        limit: int = 10,
        cursor: str | None = None,
        user_id: str | None = None,
        categories: list[str] | None = None,
        languages: list[str] | None = None,
        positive_score_only: bool | None = None,
    ) -> CursorPage[ArticleLite]:
        """
        Get articles (cursor-paginated).

        Args:
            type:               Article feed type (daily, weekly, top, my, subscriptions, last).
            user_id:            Filter to articles by a specific author.
            categories:         Filter by category list.
            languages:          Filter by language codes (e.g. ["en", "ro"]).
            positive_score_only: When True, exclude downvoted articles.
        """
        raw = await self._get(
            "article.getArticlesPaginated",
            type=type,
            limit=limit,
            cursor=cursor,
            userId=user_id,
            categories=categories,
            languages=languages,
            positiveScoreOnly=positive_score_only,
        )
        return CursorPage.from_raw(raw, ArticleLite)

    async def paginate(self, type: ArticleType | str, **kwargs: Any) -> AsyncIterator[ArticleLite]:
        """Async generator over articles of the given type."""
        async for item in paginate(self.get_paginated, type=type, **kwargs):
            yield item

    async def collect_all(self, type: ArticleType | str, **kwargs: Any) -> list[ArticleLite]:
        """Collect all articles of the given type across all pages."""
        return await collect_all(self.get_paginated, type=type, **kwargs)
