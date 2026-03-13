"""Unit tests for BatchSession and fetch_many_by_ids."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from warera._batch import BatchSession, fetch_many_by_ids
from warera.exceptions import WareraBatchError, WareraNotFoundError

# ---------------------------------------------------------------------------
# BatchSession
# ---------------------------------------------------------------------------


def _make_http(return_values: list) -> MagicMock:
    http = MagicMock()
    http.post_batch = AsyncMock(return_value=return_values)
    return http


@pytest.mark.asyncio
async def test_batch_session_resolves_items():
    http = _make_http([{"id": "1"}, {"id": "2"}])

    async with BatchSession(http) as batch:
        item_a = batch.add("company.getById", {"companyId": "1"})
        item_b = batch.add("company.getById", {"companyId": "2"})

    assert item_a.result == {"id": "1"}
    assert item_b.result == {"id": "2"}
    assert item_a.ok
    assert item_b.ok


@pytest.mark.asyncio
async def test_batch_session_passes_correct_args_to_http():
    http = _make_http([{}, {}])

    async with BatchSession(http) as batch:
        batch.add("company.getById", {"companyId": "111"})
        batch.add("government.getByCountryId", {"countryId": "7"})

    http.post_batch.assert_called_once_with(
        ["company.getById", "government.getByCountryId"],
        [{"companyId": "111"}, {"countryId": "7"}],
    )


@pytest.mark.asyncio
async def test_batch_session_empty_does_not_call_http():
    http = _make_http([])

    async with BatchSession(http) as _batch:
        pass  # nothing added

    http.post_batch.assert_not_called()


@pytest.mark.asyncio
async def test_batch_session_splits_into_chunks():
    """When queue exceeds batch_size, multiple POST calls are made."""
    # 3 items with batch_size=2 → 2 POST requests
    http = MagicMock()
    http.post_batch = AsyncMock(
        side_effect=[
            [{"id": "1"}, {"id": "2"}],
            [{"id": "3"}],
        ]
    )

    async with BatchSession(http, batch_size=2) as batch:
        a = batch.add("company.getById", {"companyId": "1"})
        b = batch.add("company.getById", {"companyId": "2"})
        c = batch.add("company.getById", {"companyId": "3"})

    assert http.post_batch.call_count == 2
    assert a.result == {"id": "1"}
    assert b.result == {"id": "2"}
    assert c.result == {"id": "3"}


@pytest.mark.asyncio
async def test_batch_session_item_not_resolved_before_flush():
    http = _make_http([{}])
    batch = BatchSession(http)
    item = batch.add("company.getById", {"companyId": "1"})

    with pytest.raises(RuntimeError, match="not been resolved"):
        _ = item.result


@pytest.mark.asyncio
async def test_batch_session_partial_failure():
    """Items that succeed should resolve; failed items should raise on .result."""

    http = MagicMock()
    http.post_batch = AsyncMock(
        side_effect=WareraBatchError(
            errors={1: WareraNotFoundError()},
            results={0: {"id": "1"}},
        )
    )

    async with BatchSession(http) as batch:
        good = batch.add("company.getById", {"companyId": "1"})
        bad = batch.add("company.getById", {"companyId": "missing"})

    assert good.result == {"id": "1"}
    assert bad.ok is False
    with pytest.raises(WareraNotFoundError):
        _ = bad.result


# ---------------------------------------------------------------------------
# fetch_many_by_ids
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_fetch_many_by_ids_single_chunk():
    http = MagicMock()
    http.post_batch = AsyncMock(return_value=[{"id": "1"}, {"id": "2"}])

    results = await fetch_many_by_ids(http, "company.getById", "companyId", ["1", "2"])

    assert results == [{"id": "1"}, {"id": "2"}]
    http.post_batch.assert_called_once_with(
        ["company.getById", "company.getById"],
        [{"companyId": "1"}, {"companyId": "2"}],
    )


@pytest.mark.asyncio
async def test_fetch_many_by_ids_multiple_chunks():
    """IDs exceeding batch_size must be split into concurrent requests."""
    http = MagicMock()
    http.post_batch = AsyncMock(
        side_effect=[
            [{"id": "1"}, {"id": "2"}],
            [{"id": "3"}],
        ]
    )

    results = await fetch_many_by_ids(
        http, "company.getById", "companyId", ["1", "2", "3"], batch_size=2
    )

    assert [r["id"] for r in results] == ["1", "2", "3"]
    assert http.post_batch.call_count == 2


@pytest.mark.asyncio
async def test_fetch_many_by_ids_empty():
    http = MagicMock()
    results = await fetch_many_by_ids(http, "company.getById", "companyId", [])
    assert results == []
    http.post_batch.assert_not_called()
