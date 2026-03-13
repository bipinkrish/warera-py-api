"""Unit tests for cursor pagination helpers."""

from __future__ import annotations

import pytest

from warera._pagination import collect_all, paginate
from warera.models.common import CursorPage
from warera.models.user import User


def _make_page(items: list, next_cursor: str | None = None) -> CursorPage[User]:
    return CursorPage(
        items=[User(_id=str(i), username=f"user{i}") for i in items],
        next_cursor=next_cursor,
        has_more=next_cursor is not None,
    )


@pytest.mark.asyncio
async def test_paginate_single_page():
    async def fetch(**kwargs) -> CursorPage[User]:
        return _make_page([1, 2, 3])

    items = [item async for item in paginate(fetch)]
    assert len(items) == 3
    assert items[0].username == "user1"


@pytest.mark.asyncio
async def test_paginate_multiple_pages():
    pages = {
        None: _make_page([1, 2], next_cursor="cur1"),
        "cur1": _make_page([3, 4], next_cursor="cur2"),
        "cur2": _make_page([5], next_cursor=None),
    }

    async def fetch(cursor=None, **kwargs) -> CursorPage[User]:
        return pages[cursor]

    items = [item async for item in paginate(fetch)]
    assert len(items) == 5
    assert [u.id for u in items] == ["1", "2", "3", "4", "5"]


@pytest.mark.asyncio
async def test_collect_all_returns_flat_list():
    pages = {
        None: _make_page([1, 2], next_cursor="c1"),
        "c1": _make_page([3], next_cursor=None),
    }

    async def fetch(cursor=None, **kwargs) -> CursorPage[User]:
        return pages[cursor]

    result = await collect_all(fetch)
    assert len(result) == 3
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_paginate_forwards_kwargs():
    received_kwargs: list[dict] = []

    async def fetch(cursor=None, **kwargs) -> CursorPage[User]:
        received_kwargs.append({"cursor": cursor, **kwargs})
        return _make_page([1])

    async for _ in paginate(fetch, country_id="7", limit=50):
        break

    assert received_kwargs[0]["country_id"] == "7"
    assert received_kwargs[0]["limit"] == 50


@pytest.mark.asyncio
async def test_paginate_stops_when_no_more():
    call_count = 0

    async def fetch(cursor=None, **_) -> CursorPage[User]:
        nonlocal call_count
        call_count += 1
        return _make_page([1], next_cursor=None)  # has_more=False

    items = [item async for item in paginate(fetch)]
    assert call_count == 1
    assert len(items) == 1
