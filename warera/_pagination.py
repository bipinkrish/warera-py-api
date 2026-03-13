"""
Pagination helpers for cursor-based WarEra API endpoints.

Provides:
  • paginate()      — async generator that yields individual items across all pages
  • collect_all()   — convenience wrapper that returns a flat list of all items
"""

from __future__ import annotations

from collections.abc import AsyncGenerator, Callable, Coroutine
from typing import Any, TypeVar

from .models.common import CursorPage

T = TypeVar("T")

# A callable that accepts keyword args including an optional `cursor` and
# returns a coroutine that resolves to a CursorPage[T].
PageFetcher = Callable[..., Coroutine[Any, Any, CursorPage[T]]]


async def paginate(
    fetch_fn: PageFetcher[T],
    /,
    **kwargs: Any,
) -> AsyncGenerator[T, None]:
    """
    Async generator that transparently handles cursor pagination.

    Args:
        fetch_fn:  An async callable that accepts `cursor` as a keyword arg
                   and returns a CursorPage[T].
        **kwargs:  Extra keyword arguments forwarded to fetch_fn on every call
                   (filters, limit, etc.). Do NOT include `cursor` — it is
                   managed automatically.

    Yields:
        Individual items of type T across all pages.

    Example:
        async for user in paginate(client.user.get_by_country, country_id="7", limit=50):
            print(user.username)
    """
    cursor: str | None = None

    while True:
        page: CursorPage[T] = await fetch_fn(**kwargs, cursor=cursor)

        for item in page.items:
            yield item

        if not page.has_more or not page.next_cursor:
            break

        cursor = page.next_cursor


async def collect_all(
    fetch_fn: PageFetcher[T],
    /,
    **kwargs: Any,
) -> list[T]:
    """
    Collect every item across all pages into a single flat list.

    ⚠️  Use with care on large datasets — this will keep all items in memory.

    Example:
        all_users = await collect_all(client.user.get_by_country, country_id="7")
    """
    return [item async for item in paginate(fetch_fn, **kwargs)]
