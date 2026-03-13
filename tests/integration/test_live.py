"""
Integration tests against the live WarEra API.

Run with:
    pytest tests/integration/ -v

An API key is optional but gives higher rate limits:
    WARERA_API_KEY=your_key pytest tests/integration/ -v
"""

from __future__ import annotations

import pytest

from warera import WareraClient
from warera._enums import RankingType
from warera.models import Country


@pytest.fixture(scope="module")
async def client():
    async with WareraClient() as c:
        yield c


# ---------------------------------------------------------------------------
# country
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_get_all_countries(client):
    countries = await client.country.get_all()
    assert isinstance(countries, dict)
    assert len(countries) > 0
    first = next(iter(countries.values()))
    assert isinstance(first, Country)


@pytest.mark.anyio
async def test_find_country_by_name(client):
    countries = await client.country.get_all()
    # find any country and verify round-trip by name
    first = next(iter(countries.values()))
    if first.name:
        found = await client.country.find_by_name(first.name)
        assert found is not None
        assert found.id == first.id


# ---------------------------------------------------------------------------
# game_config
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_get_game_dates(client):
    dates = await client.game_config.get_dates()
    assert dates is not None


@pytest.mark.anyio
async def test_get_game_config(client):
    config = await client.game_config.get()
    assert config is not None


# ---------------------------------------------------------------------------
# item_trading
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_get_item_prices(client):
    prices = await client.item_trading.get_prices()
    assert isinstance(prices, dict)


# ---------------------------------------------------------------------------
# region
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_get_all_regions(client):
    regions = await client.region.get_all()
    assert isinstance(regions, dict)
    assert len(regions) > 0


# ---------------------------------------------------------------------------
# battle
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_get_battles_paginated(client):
    page = await client.battle.get_many(is_active=True, limit=5)
    assert isinstance(page.items, list)


# ---------------------------------------------------------------------------
# ranking
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_get_user_wealth_ranking(client):
    entries = await client.ranking.get(RankingType.USER_WEALTH)
    assert isinstance(entries, list)


# ---------------------------------------------------------------------------
# search
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_search_returns_results(client):
    results = await client.search.query("a")
    assert results is not None
    assert isinstance(results.results, list)


# ---------------------------------------------------------------------------
# Batch
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_batch_gets_all_countries_and_prices(client):
    """Verify that a batch request with mixed procedures resolves correctly."""
    async with client.batch() as batch:
        prices_item = batch.add("itemTrading.getPrices", {})
        config_item = batch.add("gameConfig.getDates", {})

    assert prices_item.ok
    assert config_item.ok


@pytest.mark.anyio
async def test_get_many_countries_batch(client):
    """Verify get_all + batch ID fetch round-trip."""
    all_countries = await client.country.get_all()
    ids = list(all_countries.keys())[:5]

    async with client.batch() as batch:
        items = [batch.add("country.getCountryById", {"countryId": cid}) for cid in ids]

    for item in items:
        assert item.ok
