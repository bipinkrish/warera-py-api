"""Unit tests for the HTTP layer — no live network calls."""

from __future__ import annotations

import json
from urllib.parse import parse_qs, unquote, urlparse

import httpx
import pytest
import respx

from warera._http import HttpSession
from warera.exceptions import (
    WareraBatchError,
    WareraNotFoundError,
    WareraUnauthorizedError,
)

BASE = "https://api2.warera.io/trpc"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_trpc_ok(data: object) -> dict:
    return {"result": {"data": data}}


def _make_trpc_error(message: str, http_status: int = 500) -> dict:
    return {"error": {"message": message, "data": {"httpStatus": http_status}}}


# ---------------------------------------------------------------------------
# Single GET
# ---------------------------------------------------------------------------


@respx.mock
@pytest.mark.asyncio
async def test_get_encodes_input_as_query_param():
    """Input params must be JSON-encoded in the ?input= query string."""
    route = respx.get(url__startswith=BASE).mock(
        return_value=httpx.Response(200, json=_make_trpc_ok({"id": "1", "name": "TestCo"}))
    )

    async with HttpSession(base_url=BASE) as session:
        result = await session.get("company.getById", {"companyId": "1"})

    assert result == {"id": "1", "name": "TestCo"}
    request = route.calls[0].request
    parsed = parse_qs(urlparse(str(request.url)).query)
    input_raw = parsed["input"][0]
    assert json.loads(unquote(input_raw)) == {"companyId": "1"}


@respx.mock
@pytest.mark.asyncio
async def test_get_strips_none_params():
    """None values must not appear in the serialised input."""
    route = respx.get(url__startswith=BASE).mock(
        return_value=httpx.Response(200, json=_make_trpc_ok({}))
    )

    async with HttpSession(base_url=BASE) as session:
        await session.get("battle.getBattles", {"isActive": True, "warId": None, "limit": 10})

    request = route.calls[0].request
    parsed = parse_qs(urlparse(str(request.url)).query)
    input_data = json.loads(unquote(parsed["input"][0]))
    assert "warId" not in input_data
    assert input_data["isActive"] is True
    assert input_data["limit"] == 10


@respx.mock
@pytest.mark.asyncio
async def test_get_injects_api_key_header():
    respx.get(url__startswith=BASE).mock(return_value=httpx.Response(200, json=_make_trpc_ok({})))

    async with HttpSession(api_key="secret-key", base_url=BASE) as session:
        await session.get("user.getUserLite", {"userId": "1"})

    request = respx.calls[0].request
    assert request.headers["X-API-Key"] == "secret-key"


@respx.mock
@pytest.mark.asyncio
async def test_get_no_api_key_header_when_not_set():
    respx.get(url__startswith=BASE).mock(return_value=httpx.Response(200, json=_make_trpc_ok({})))

    async with HttpSession(base_url=BASE) as session:  # no key
        await session.get("user.getUserLite", {"userId": "1"})

    request = respx.calls[0].request
    assert "X-API-Key" not in request.headers


@respx.mock
@pytest.mark.asyncio
async def test_get_raises_unauthorized_on_401():
    respx.get(url__startswith=BASE).mock(
        return_value=httpx.Response(401, json={"message": "Unauthorized"})
    )
    async with HttpSession(base_url=BASE) as session:
        with pytest.raises(WareraUnauthorizedError):
            await session.get("user.getUserLite", {"userId": "1"})


@respx.mock
@pytest.mark.asyncio
async def test_get_raises_not_found_on_404():
    respx.get(url__startswith=BASE).mock(
        return_value=httpx.Response(404, json={"message": "Not found"})
    )
    async with HttpSession(base_url=BASE) as session:
        with pytest.raises(WareraNotFoundError):
            await session.get("company.getById", {"companyId": "nonexistent"})


# ---------------------------------------------------------------------------
# Batch POST
# ---------------------------------------------------------------------------


@respx.mock
@pytest.mark.asyncio
async def test_batch_post_builds_correct_url():
    """URL must be comma-joined procedures + ?batch=1."""
    route = respx.post(url__startswith=BASE).mock(
        return_value=httpx.Response(
            200,
            json=[
                _make_trpc_ok({"id": "1"}),
                _make_trpc_ok({"id": "2"}),
            ],
        )
    )

    async with HttpSession(base_url=BASE) as session:
        results = await session.post_batch(
            ["company.getById", "company.getById"],
            [{"companyId": "1"}, {"companyId": "2"}],
        )

    request = route.calls[0].request
    url_str = str(request.url)
    assert "company.getById,company.getById" in url_str
    assert "batch=1" in url_str
    assert results == [{"id": "1"}, {"id": "2"}]


@respx.mock
@pytest.mark.asyncio
async def test_batch_post_body_uses_string_integer_keys():
    """Body keys must be '0', '1', '2' — string integers, not actual ints."""
    route = respx.post(url__startswith=BASE).mock(
        return_value=httpx.Response(
            200,
            json=[
                _make_trpc_ok({"countryId": "7"}),
                _make_trpc_ok({"userId": "42"}),
            ],
        )
    )

    async with HttpSession(base_url=BASE) as session:
        await session.post_batch(
            ["government.getByCountryId", "user.getUserLite"],
            [{"countryId": "7"}, {"userId": "42"}],
        )

    request = route.calls[0].request
    body = json.loads(request.content)
    assert "0" in body
    assert "1" in body
    assert body["0"] == {"countryId": "7"}
    assert body["1"] == {"userId": "42"}


@respx.mock
@pytest.mark.asyncio
async def test_batch_post_mixed_procedures():
    """Different procedures can be mixed in one batch."""
    respx.post(url__startswith=BASE).mock(
        return_value=httpx.Response(
            200,
            json=[
                _make_trpc_ok({"name": "Ukraine"}),
                _make_trpc_ok({"presidentId": "99"}),
                _make_trpc_ok({}),
            ],
        )
    )

    async with HttpSession(base_url=BASE) as session:
        results = await session.post_batch(
            ["country.getCountryById", "government.getByCountryId", "itemTrading.getPrices"],
            [{"countryId": "7"}, {"countryId": "7"}, {}],
        )

    assert len(results) == 3
    assert results[0]["name"] == "Ukraine"
    assert results[1]["presidentId"] == "99"


@respx.mock
@pytest.mark.asyncio
async def test_batch_post_raises_batch_error_on_partial_failure():
    """WareraBatchError must be raised if any item in the batch fails."""
    respx.post(url__startswith=BASE).mock(
        return_value=httpx.Response(
            200,
            json=[
                _make_trpc_ok({"id": "1"}),
                _make_trpc_error("Not found", 404),
            ],
        )
    )

    async with HttpSession(base_url=BASE) as session:
        with pytest.raises(WareraBatchError) as exc_info:
            await session.post_batch(
                ["company.getById", "company.getById"],
                [{"companyId": "1"}, {"companyId": "nonexistent"}],
            )

    err = exc_info.value
    assert 1 in err.errors
    assert 0 in err.results
    assert isinstance(err.errors[1], WareraNotFoundError)


@respx.mock
@pytest.mark.asyncio
async def test_batch_empty_returns_empty_list():
    async with HttpSession(base_url=BASE) as session:
        results = await session.post_batch([], [])
    assert results == []
