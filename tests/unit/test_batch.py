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


# ---------------------------------------------------------------------------
# Hard batch limit enforcement
# ---------------------------------------------------------------------------


def test_max_batch_size_constant_is_50():
    """The hard-cap constant must match the server's limit."""
    from warera._batch import MAX_BATCH_SIZE
    assert MAX_BATCH_SIZE == 50


def test_batch_session_clamps_to_max():
    """BatchSession silently clamps any batch_size > 50 to 50."""
    from warera._batch import BatchSession, MAX_BATCH_SIZE
    from unittest.mock import MagicMock

    # Even if the caller passes a huge number, the session caps it.
    session = BatchSession(http=MagicMock(), batch_size=999)
    assert session._batch_size == MAX_BATCH_SIZE


def test_batch_session_default_is_50():
    """Default batch_size should be the server hard limit."""
    from warera._batch import BatchSession, MAX_BATCH_SIZE
    from unittest.mock import MagicMock

    session = BatchSession(http=MagicMock())
    assert session._batch_size == MAX_BATCH_SIZE


@pytest.mark.asyncio
async def test_batch_session_splits_large_queue():
    """
    Queuing more than 50 items must produce multiple flush chunks,
    each no larger than MAX_BATCH_SIZE.
    """
    from warera._batch import BatchSession, MAX_BATCH_SIZE

    chunk_sizes: list[int] = []

    async def mock_post_batch(procedures, inputs):
        chunk_sizes.append(len(procedures))
        return [{"result": {"data": i}} for i in range(len(procedures))]

    http = MagicMock()
    http.post_batch = mock_post_batch

    session = BatchSession(http=http, batch_size=MAX_BATCH_SIZE)
    for i in range(120):
        session.add("test.proc", {"id": str(i)})

    await session.flush()

    # Every chunk must respect the hard limit.
    assert all(s <= MAX_BATCH_SIZE for s in chunk_sizes), f"Oversized chunk: {chunk_sizes}"
    # 120 items → at least 3 chunks of ≤ 50
    assert len(chunk_sizes) >= 3
    assert sum(chunk_sizes) == 120


@pytest.mark.asyncio
async def test_http_post_batch_auto_splits_over_50():
    """post_batch() must auto-split > 50 procedures into chunks of ≤ 50."""
    import respx
    import httpx
    from warera._http import HttpSession

    BASE = "https://api2.warera.io/trpc"

    call_sizes: list[int] = []

    with respx.mock:
        def handler(request):
            # Count how many procedures are in this request's path.
            path = request.url.path
            procs = path.lstrip("/").split(",")
            call_sizes.append(len(procs))
            body = [{"result": {"data": i}} for i in range(len(procs))]
            return httpx.Response(200, json=body)

        respx.post(url__startswith=BASE).mock(side_effect=handler)

        async with HttpSession(base_url=BASE) as session:
            results = await session.post_batch(
                ["test.proc"] * 120,
                [{}] * 120,
            )

    assert len(results) == 120
    assert all(s <= 50 for s in call_sizes), f"Oversized chunk: {call_sizes}"
    assert len(call_sizes) == 3  # 50 + 50 + 20


@pytest.mark.asyncio
async def test_http_post_batch_accepts_exactly_50():
    """post_batch() must not raise for exactly 50 procedures."""
    import respx
    import httpx
    from warera._http import HttpSession

    BASE = "https://api2.warera.io/trpc"
    ok_response = [{"result": {"data": i}} for i in range(50)]

    with respx.mock:
        respx.post(url__startswith=BASE).mock(
            return_value=httpx.Response(200, json=ok_response)
        )
        async with HttpSession(base_url=BASE) as session:
            results = await session.post_batch(
                ["test.proc"] * 50,
                [{}] * 50,
            )
    assert len(results) == 50
