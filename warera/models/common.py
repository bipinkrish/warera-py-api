"""
Shared Pydantic base types used across all models.
"""

from __future__ import annotations

from typing import Any, Generic, TypeVar, cast

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

T = TypeVar("T")


def _base_config() -> ConfigDict:
    """
    Standard model config applied to every WarEra model:
      • camelCase aliases (API returns camelCase, Python uses snake_case)
      • extra fields allowed (forward-compatible with schema additions)
      • populate_by_name lets you use either the alias or field name
    """
    return ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="allow",
    )


class WareraModel(BaseModel):
    """Base class for all response models."""

    model_config = _base_config()
    id: str | None = Field(default=None, alias="_id")


class CursorPage(WareraModel, Generic[T]):
    """
    Generic cursor-paginated page returned by all paginated endpoints.

    Usage:
        page: CursorPage[User] = await client.user.get_by_country("7")
        for user in page.items:
            print(user.username)
        if page.has_more:
            next_page = await client.user.get_by_country("7", cursor=page.next_cursor)
    """

    items: list[T]
    next_cursor: str | None = None
    has_more: bool = False

    @classmethod
    def from_raw(cls, raw: Any, item_type: type[T]) -> CursorPage[T]:
        """
        Parse a raw API response dict into a typed CursorPage.
        Handles both wrapped `{items, nextCursor}` and plain list responses.
        """
        if isinstance(raw, list):
            items = []
            for r in raw:
                if isinstance(r, dict) and hasattr(item_type, "model_validate"):
                    items.append(cast(Any, item_type).model_validate(r))
                else:
                    items.append(r)
            return cls(items=items, next_cursor=None, has_more=False)

        if isinstance(raw, dict):
            raw_items = raw.get("items", raw.get("data", []))
            items = []
            if isinstance(raw_items, list):
                for r in raw_items:
                    if isinstance(r, dict) and hasattr(item_type, "model_validate"):
                        items.append(cast(Any, item_type).model_validate(r))
                    else:
                        items.append(r)

            next_cursor = raw.get("nextCursor") or raw.get("next_cursor")
            has_more = bool(raw.get("hasMore", raw.get("has_more", bool(next_cursor))))
            return cls(items=items, next_cursor=next_cursor, has_more=has_more)

        return cls(items=[], next_cursor=None, has_more=False)
