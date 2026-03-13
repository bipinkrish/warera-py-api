"""Unit tests for resource classes — mock the HTTP layer, test parsing logic."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from warera.resources.battle import BattleResource
from warera.resources.country import CountryResource
from warera.resources.item_trading import ItemTradingResource
from warera.resources.user import UserResource


def _mock_http(return_value) -> MagicMock:
    http = MagicMock()
    http.get = AsyncMock(return_value=return_value)
    return http


# ---------------------------------------------------------------------------
# Country
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_country_get_all_from_dict():
    raw = {
        "7": {"id": "7", "name": "Ukraine", "code": "UA"},
        "8": {"id": "8", "name": "Romania", "code": "RO"},
    }
    resource = CountryResource(_mock_http(raw))
    result = await resource.get_all()

    assert len(result) == 2
    assert result["7"].name == "Ukraine"
    assert result["8"].code == "RO"


@pytest.mark.asyncio
async def test_country_get_all_from_list():
    raw = [
        {"id": "7", "name": "Ukraine", "code": "UA"},
        {"id": "8", "name": "Romania", "code": "RO"},
    ]
    resource = CountryResource(_mock_http(raw))
    result = await resource.get_all()

    assert len(result) == 2
    assert "7" in result


@pytest.mark.asyncio
async def test_country_find_by_name_case_insensitive():
    raw = {"7": {"id": "7", "name": "Ukraine"}}
    resource = CountryResource(_mock_http(raw))
    found = await resource.find_by_name("ukraine")
    assert found is not None
    assert found.id == "7"


@pytest.mark.asyncio
async def test_country_find_by_name_not_found():
    raw = {"7": {"id": "7", "name": "Ukraine"}}
    resource = CountryResource(_mock_http(raw))
    found = await resource.find_by_name("Atlantis")
    assert found is None


# ---------------------------------------------------------------------------
# Battle
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_battle_get_many_returns_cursor_page():
    raw = {
        "items": [
            {"id": "b1", "isActive": True},
            {"id": "b2", "isActive": True},
        ],
        "nextCursor": "next123",
        "hasMore": True,
    }
    resource = BattleResource(_mock_http(raw))
    page = await resource.get_many(is_active=True)

    assert len(page.items) == 2
    assert page.next_cursor == "next123"
    assert page.has_more is True


@pytest.mark.asyncio
async def test_battle_get_active_collects_all_pages():
    """get_active should transparently collect all pages."""
    pages = {
        None: {
            "items": [{"id": "b1", "isActive": True}],
            "nextCursor": "c1",
            "hasMore": True,
        },
        "c1": {
            "items": [{"id": "b2", "isActive": True}],
            "nextCursor": None,
            "hasMore": False,
        },
    }

    call_cursors = []

    async def mock_get(procedure, params):
        cursor = params.get("cursor")
        call_cursors.append(cursor)
        return pages[cursor]

    http = MagicMock()
    http.get = mock_get

    resource = BattleResource(http)
    battles = await resource.get_active()
    assert len(battles) == 2
    assert [b.id for b in battles] == ["b1", "b2"]


# ---------------------------------------------------------------------------
# ItemTrading
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_item_trading_get_prices_from_dict():
    raw = {
        "iron": {"itemCode": "iron", "price": 1.5},
        "wood": {"itemCode": "wood", "price": 0.8},
    }
    resource = ItemTradingResource(_mock_http(raw))
    prices = await resource.get_prices()

    assert prices["iron"].price == 1.5
    assert prices["wood"].price == 0.8


@pytest.mark.asyncio
async def test_item_trading_get_price_single():
    raw = {
        "iron": {"itemCode": "iron", "price": 1.5},
    }
    resource = ItemTradingResource(_mock_http(raw))
    price = await resource.get_price("iron")
    assert price is not None
    assert price.price == 1.5


@pytest.mark.asyncio
async def test_item_trading_get_price_missing_returns_none():
    raw = {}
    resource = ItemTradingResource(_mock_http(raw))
    price = await resource.get_price("unobtainium")
    assert price is None


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_user_get_lite_parses_model():
    raw = {"id": "42", "username": "testplayer", "level": 10, "wealth": 999.5}
    resource = UserResource(_mock_http(raw))
    user = await resource.get_lite("42")

    assert user.id == "42"
    assert user.username == "testplayer"
    assert user.level == 10
    assert user.wealth == 999.5


@pytest.mark.asyncio
async def test_user_get_by_country_cursor_page():
    raw = {
        "items": [{"id": "1", "username": "alice"}, {"id": "2", "username": "bob"}],
        "nextCursor": None,
        "hasMore": False,
    }
    resource = UserResource(_mock_http(raw))
    page = await resource.get_by_country("7")

    assert len(page.items) == 2
    assert page.items[0].username == "alice"
    assert page.has_more is False
