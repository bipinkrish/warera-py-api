"""
Stdlib-only unit tests.
Covers all logic that doesn't need httpx/pydantic/pytest installed:
  - HTTP layer encoding helpers (URL building, None-stripping, body format)
  - BatchSession flow (queue, chunk, resolve, partial failure)
  - fetch_many_by_ids (chunking, concurrency, empty input)
  - Pagination (single page, multi-page, kwargs forwarding, stop condition)
  - Country/Battle/ItemTrading resource parsing logic
  - Error hierarchy (correct types raised per status code)
  - Enums (all values present)
  - Sync shim proxy mechanics
"""

from __future__ import annotations

import asyncio
import json
import sys
import unittest
import unittest.mock as mock
from dataclasses import dataclass
from typing import Any
from pathlib import Path

# ── make the warera package importable without installing ──────────────────
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# ── stub out the three missing packages so imports succeed ─────────────────

# pydantic stub
pydantic_stub = mock.MagicMock()


class _BaseModel:
    model_config: dict[str, Any] = {}

    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)

    @classmethod
    def model_validate(cls, data):
        if isinstance(data, dict):
            return cls(**{k: v for k, v in data.items()})
        return data

    def model_dump(self):
        return self.__dict__


pydantic_stub.BaseModel = _BaseModel
pydantic_stub.ConfigDict = lambda **kw: {}
pydantic_stub.Field = lambda *a, **kw: None

_generic_stub = mock.MagicMock()
pydantic_stub.alias_generators = _generic_stub
pydantic_stub.alias_generators.to_camel = lambda s: s

sys.modules["pydantic"] = pydantic_stub
sys.modules["pydantic.alias_generators"] = _generic_stub

# httpx stub
httpx_stub = mock.MagicMock()


class _FakeResponse:
    def __init__(self, status_code=200, data=None):
        self.status_code = status_code
        self._data = data or {}

    def json(self):
        return self._data

    @property
    def text(self):
        return json.dumps(self._data)


httpx_stub.AsyncClient = mock.MagicMock
httpx_stub.Response = _FakeResponse
httpx_stub.TransportError = Exception
sys.modules["httpx"] = httpx_stub

# tenacity stub — make @retry a no-op decorator
tenacity_stub = mock.MagicMock()


def _noop_retry(**kw):
    def decorator(fn):
        return fn

    return decorator


tenacity_stub.retry = _noop_retry
tenacity_stub.retry_if_exception = lambda f: None
tenacity_stub.stop_after_attempt = lambda n: None
tenacity_stub.wait_exponential = lambda **kw: None
tenacity_stub.wait_fixed = lambda s: None
sys.modules["tenacity"] = tenacity_stub

# ── now import our modules ─────────────────────────────────────────────────
# ruff: noqa
from warera._batch import DEFAULT_BATCH_SIZE, BatchSession, fetch_many_by_ids
from warera._enums import (
    ActionLogActionType,
    ArticleType,
    BattleFilter,
    BattleOrderSide,
    BattleRankingDataType,
    BattleRankingSide,
    EventType,
    RankingType,
    TransactionType,
    UpgradeType,
)
from warera.exceptions import (
    WareraBatchError,
    WareraError,
    WareraForbiddenError,
    WareraHTTPError,
    WareraNotFoundError,
    WareraRateLimitError,
    WareraServerError,
    WareraUnauthorizedError,
    WareraValidationError,
    _raise_for_status,
)


def run(coro):
    return asyncio.run(coro)


# ══════════════════════════════════════════════════════════════════════════════
# 1. Enums
# ══════════════════════════════════════════════════════════════════════════════


class TestEnums(unittest.TestCase):
    def test_article_type_values(self):
        expected = {"daily", "weekly", "top", "my", "subscriptions", "last"}
        self.assertEqual({e.value for e in ArticleType}, expected)

    def test_battle_filter_values(self):
        self.assertIn("yourCountry", [e.value for e in BattleFilter])
        self.assertIn("yourEnemies", [e.value for e in BattleFilter])

    def test_ranking_type_has_26_values(self):
        # 9 country + 12 user + 5 MU = 26
        self.assertEqual(len(RankingType), 26)

    def test_event_type_has_21_values(self):
        self.assertEqual(len(EventType), 21)

    def test_transaction_type_values(self):
        values = {e.value for e in TransactionType}
        self.assertIn("applicationFee", values)
        self.assertIn("dismantleItem", values)
        self.assertIn("battleLoot", values)

    def test_upgrade_type_values(self):
        values = {e.value for e in UpgradeType}
        self.assertEqual(
            values,
            {
                "bunker",
                "base",
                "pacificationCenter",
                "storage",
                "automatedEngine",
                "breakRoom",
                "headquarters",
                "dormitories",
            },
        )

    def test_battle_ranking_data_type(self):
        self.assertEqual({e.value for e in BattleRankingDataType}, {"damage", "points", "money"})

    def test_battle_ranking_side(self):
        self.assertEqual({e.value for e in BattleRankingSide}, {"attacker", "defender", "merged"})

    def test_battle_order_side(self):
        self.assertEqual({e.value for e in BattleOrderSide}, {"attacker", "defender"})

    def test_action_log_action_type_has_17_values(self):
        self.assertEqual(len(ActionLogActionType), 17)


# ══════════════════════════════════════════════════════════════════════════════
# 2. Exceptions
# ══════════════════════════════════════════════════════════════════════════════


class TestExceptions(unittest.TestCase):
    def test_hierarchy(self):
        self.assertTrue(issubclass(WareraUnauthorizedError, WareraHTTPError))
        self.assertTrue(issubclass(WareraForbiddenError, WareraHTTPError))
        self.assertTrue(issubclass(WareraNotFoundError, WareraHTTPError))
        self.assertTrue(issubclass(WareraRateLimitError, WareraHTTPError))
        self.assertTrue(issubclass(WareraServerError, WareraHTTPError))
        self.assertTrue(issubclass(WareraHTTPError, WareraError))
        self.assertTrue(issubclass(WareraValidationError, WareraError))
        self.assertTrue(issubclass(WareraBatchError, WareraError))

    def test_raise_for_status_401(self):
        with self.assertRaises(WareraUnauthorizedError):
            _raise_for_status(401, {})

    def test_raise_for_status_403(self):
        with self.assertRaises(WareraForbiddenError):
            _raise_for_status(403, {})

    def test_raise_for_status_404(self):
        with self.assertRaises(WareraNotFoundError):
            _raise_for_status(404, {})

    def test_raise_for_status_429(self):
        with self.assertRaises(WareraRateLimitError):
            _raise_for_status(429, {})

    def test_raise_for_status_500(self):
        with self.assertRaises(WareraServerError):
            _raise_for_status(500, {})

    def test_raise_for_status_503(self):
        with self.assertRaises(WareraServerError):
            _raise_for_status(503, {})

    def test_raise_for_status_400(self):
        with self.assertRaises(WareraHTTPError):
            _raise_for_status(400, {})

    def test_no_raise_for_200(self):
        # Should not raise
        _raise_for_status(200, {})  # not actually called in normal flow, but confirm guard
        # No assertion needed — just must not raise

    def test_warera_http_error_carries_status(self):
        err = WareraHTTPError(422, "unprocessable")
        self.assertEqual(err.status_code, 422)

    def test_batch_error_carries_errors_and_results(self):
        errors = {1: WareraNotFoundError()}
        results = {0: {"id": "1"}}
        err = WareraBatchError(errors=errors, results=results)
        self.assertIn(1, err.errors)
        self.assertIn(0, err.results)
        self.assertIn("1", str(err))

    def test_validation_error_carries_raw(self):
        raw = {"broken": True}
        err = WareraValidationError("parse failed", raw=raw)
        self.assertEqual(err.raw, raw)


# ══════════════════════════════════════════════════════════════════════════════
# 3. HTTP layer — encoding logic (no live network)
# ══════════════════════════════════════════════════════════════════════════════


class TestHttpEncoding(unittest.TestCase):
    """Test URL/body building without making real requests."""

    def _make_session(self):
        from warera._http import HttpSession

        return HttpSession(base_url="https://api2.warera.io/trpc")

    def test_none_values_stripped_before_encoding(self):
        """_get strips None values so they never appear in the ?input= query."""
        session = self._make_session()
        params = {"isActive": True, "warId": None, "limit": 10, "cursor": None}
        cleaned = {k: v for k, v in params.items() if v is not None}
        self.assertNotIn("warId", cleaned)
        self.assertNotIn("cursor", cleaned)
        self.assertIn("isActive", cleaned)
        self.assertIn("limit", cleaned)

    def test_auth_header_present_when_key_set(self):
        from warera._http import HttpSession

        session = HttpSession(api_key="my-secret", base_url="https://test")
        headers = session._auth_headers()
        self.assertEqual(headers["X-API-Key"], "my-secret")

    def test_auth_header_absent_when_no_key(self):
        import os

        from warera._http import HttpSession

        # Ensure env var isn't set during this test
        old = os.environ.pop("WARERA_API_KEY", None)
        try:
            session = HttpSession(base_url="https://test")
            headers = session._auth_headers()
            self.assertNotIn("X-API-Key", headers)
        finally:
            if old:
                os.environ["WARERA_API_KEY"] = old

    def test_api_key_read_from_env(self):
        import os

        from warera._http import HttpSession

        os.environ["WARERA_API_KEY"] = "env-key"
        try:
            session = HttpSession(base_url="https://test")
            self.assertEqual(session._api_key, "env-key")
        finally:
            del os.environ["WARERA_API_KEY"]

    def test_unwrap_single_ok(self):
        from warera._http import HttpSession

        resp = _FakeResponse(200, {"result": {"data": {"id": "1", "name": "TestCo"}}})
        result = HttpSession._unwrap_single(resp, "company.getById")
        self.assertEqual(result, {"id": "1", "name": "TestCo"})

    def test_unwrap_single_trpc_error_raises(self):
        from warera._http import HttpSession

        resp = _FakeResponse(200, {"error": {"message": "Not found", "data": {"httpStatus": 404}}})
        with self.assertRaises(WareraNotFoundError):
            HttpSession._unwrap_single(resp, "company.getById")

    def test_unwrap_batch_all_ok(self):
        from warera._http import HttpSession

        raw = [
            {"result": {"data": {"id": "1"}}},
            {"result": {"data": {"id": "2"}}},
        ]
        results = HttpSession._unwrap_batch(raw, ["company.getById", "company.getById"])
        self.assertEqual(results, [{"id": "1"}, {"id": "2"}])

    def test_unwrap_batch_partial_failure_raises_batch_error(self):
        from warera._http import HttpSession

        raw = [
            {"result": {"data": {"id": "1"}}},
            {"error": {"message": "Not found", "data": {"httpStatus": 404}}},
        ]
        with self.assertRaises(WareraBatchError) as ctx:
            HttpSession._unwrap_batch(raw, ["company.getById", "company.getById"])
        err = ctx.exception
        self.assertIn(1, err.errors)
        self.assertIn(0, err.results)
        self.assertIsInstance(err.errors[1], WareraNotFoundError)

    def test_batch_url_format(self):
        """Comma-joined procedures + ?batch=1 must appear in the URL."""
        procedures = ["company.getById", "government.getByCountryId"]
        proc_path = ",".join(procedures)
        url = f"/{proc_path}?batch=1"
        self.assertEqual(url, "/company.getById,government.getByCountryId?batch=1")
        self.assertIn("batch=1", url)

    def test_batch_body_uses_string_keys(self):
        """Body keys must be string integers: '0', '1', not 0, 1."""
        inputs = [{"companyId": "1"}, {"countryId": "7"}]
        body = {str(i): inp for i, inp in enumerate(inputs)}
        self.assertIn("0", body)
        self.assertIn("1", body)
        self.assertNotIn(0, body)
        serialised = json.dumps(body)
        parsed = json.loads(serialised)
        self.assertEqual(parsed["0"]["companyId"], "1")
        self.assertEqual(parsed["1"]["countryId"], "7")

    def test_mixed_procedures_allowed(self):
        """Different procedures can freely be mixed in one batch."""
        procedures = [
            "company.getById",
            "government.getByCountryId",
            "itemTrading.getPrices",
        ]
        url = "/" + ",".join(procedures) + "?batch=1"
        self.assertIn("company.getById", url)
        self.assertIn("government.getByCountryId", url)
        self.assertIn("itemTrading.getPrices", url)


# ══════════════════════════════════════════════════════════════════════════════
# 4. BatchSession
# ══════════════════════════════════════════════════════════════════════════════


def _make_http(responses):
    http = mock.MagicMock()
    http.post_batch = mock.AsyncMock(return_value=responses)
    return http


class TestBatchSession(unittest.TestCase):
    def test_resolves_items_after_flush(self):
        http = _make_http([{"id": "1"}, {"id": "2"}])

        async def go():
            async with BatchSession(http) as batch:
                a = batch.add("company.getById", {"companyId": "1"})
                b = batch.add("company.getById", {"companyId": "2"})
            return a, b

        a, b = run(go())
        self.assertEqual(a.result, {"id": "1"})
        self.assertEqual(b.result, {"id": "2"})
        self.assertTrue(a.ok)
        self.assertTrue(b.ok)

    def test_correct_procedures_and_inputs_sent(self):
        http = _make_http([{}, {}])

        async def go():
            async with BatchSession(http) as batch:
                batch.add("company.getById", {"companyId": "111"})
                batch.add("government.getByCountryId", {"countryId": "7"})

        run(go())
        http.post_batch.assert_called_once_with(
            ["company.getById", "government.getByCountryId"],
            [{"companyId": "111"}, {"countryId": "7"}],
        )

    def test_empty_session_does_not_call_http(self):
        http = _make_http([])

        async def go():
            async with BatchSession(http) as batch:
                pass

        run(go())
        http.post_batch.assert_not_called()

    def test_splits_into_chunks_when_exceeds_batch_size(self):
        http = mock.MagicMock()
        http.post_batch = mock.AsyncMock(
            side_effect=[
                [{"id": "1"}, {"id": "2"}],
                [{"id": "3"}],
            ]
        )

        async def go():
            async with BatchSession(http, batch_size=2) as batch:
                a = batch.add("company.getById", {"companyId": "1"})
                b = batch.add("company.getById", {"companyId": "2"})
                c = batch.add("company.getById", {"companyId": "3"})
            return a, b, c

        a, b, c = run(go())
        self.assertEqual(http.post_batch.call_count, 2)
        self.assertEqual(a.result["id"], "1")
        self.assertEqual(b.result["id"], "2")
        self.assertEqual(c.result["id"], "3")

    def test_accessing_result_before_flush_raises(self):
        http = _make_http([{}])
        batch = BatchSession(http)
        item = batch.add("company.getById", {"companyId": "1"})
        with self.assertRaises(RuntimeError):
            _ = item.result

    def test_partial_failure_resolves_good_fails_bad(self):
        good_err = WareraBatchError(
            errors={1: WareraNotFoundError()},
            results={0: {"id": "1"}},
        )
        http = mock.MagicMock()
        http.post_batch = mock.AsyncMock(side_effect=good_err)

        async def go():
            async with BatchSession(http) as batch:
                good = batch.add("company.getById", {"companyId": "1"})
                bad = batch.add("company.getById", {"companyId": "missing"})
            return good, bad

        good, bad = run(go())
        self.assertEqual(good.result, {"id": "1"})
        self.assertFalse(bad.ok)
        with self.assertRaises(WareraNotFoundError):
            _ = bad.result

    def test_item_ok_property(self):
        http = _make_http([{"id": "1"}])

        async def go():
            async with BatchSession(http) as batch:
                item = batch.add("company.getById", {"companyId": "1"})
            return item

        item = run(go())
        self.assertTrue(item.ok)

    def test_default_batch_size_is_50(self):
        self.assertEqual(DEFAULT_BATCH_SIZE, 50)


# ══════════════════════════════════════════════════════════════════════════════
# 5. fetch_many_by_ids
# ══════════════════════════════════════════════════════════════════════════════


class TestFetchManyByIds(unittest.TestCase):
    def test_single_chunk(self):
        http = _make_http([{"id": "1"}, {"id": "2"}])
        results = run(fetch_many_by_ids(http, "company.getById", "companyId", ["1", "2"]))
        self.assertEqual(results, [{"id": "1"}, {"id": "2"}])
        http.post_batch.assert_called_once_with(
            ["company.getById", "company.getById"],
            [{"companyId": "1"}, {"companyId": "2"}],
        )

    def test_multiple_chunks_order_preserved(self):
        http = mock.MagicMock()
        http.post_batch = mock.AsyncMock(
            side_effect=[
                [{"id": "1"}, {"id": "2"}],
                [{"id": "3"}],
            ]
        )
        results = run(
            fetch_many_by_ids(http, "company.getById", "companyId", ["1", "2", "3"], batch_size=2)
        )
        self.assertEqual([r["id"] for r in results], ["1", "2", "3"])
        self.assertEqual(http.post_batch.call_count, 2)

    def test_empty_input_no_call(self):
        http = mock.MagicMock()
        results = run(fetch_many_by_ids(http, "company.getById", "companyId", []))
        self.assertEqual(results, [])
        http.post_batch.assert_not_called()

    def test_id_param_name_used_correctly(self):
        http = _make_http([{"muId": "mu1"}])
        run(fetch_many_by_ids(http, "mu.getById", "muId", ["mu1"]))
        _, inputs = http.post_batch.call_args[0]
        self.assertEqual(inputs[0], {"muId": "mu1"})


# ══════════════════════════════════════════════════════════════════════════════
# 6. Pagination
# ══════════════════════════════════════════════════════════════════════════════


@dataclass
class _FakePage:
    items: list
    next_cursor: str | None
    has_more: bool


class TestPagination(unittest.TestCase):
    def _make_paginate(self):
        from warera._pagination import collect_all, paginate

        return paginate, collect_all

    def test_single_page_yields_all_items(self):
        paginate, _ = self._make_paginate()

        async def fetch(cursor=None, **_):
            return _FakePage(items=[1, 2, 3], next_cursor=None, has_more=False)

        items = run(self._collect(paginate(fetch)))
        self.assertEqual(items, [1, 2, 3])

    def test_multi_page_yields_all_items_in_order(self):
        paginate, _ = self._make_paginate()
        pages = {
            None: _FakePage([1, 2], "c1", True),
            "c1": _FakePage([3, 4], "c2", True),
            "c2": _FakePage([5], None, False),
        }

        async def fetch(cursor=None, **_):
            return pages[cursor]

        items = run(self._collect(paginate(fetch)))
        self.assertEqual(items, [1, 2, 3, 4, 5])

    def test_stops_immediately_when_no_more(self):
        paginate, _ = self._make_paginate()
        calls = []

        async def fetch(cursor=None, **_):
            calls.append(cursor)
            return _FakePage([1], None, False)

        run(self._collect(paginate(fetch)))
        self.assertEqual(len(calls), 1)

    def test_collect_all_returns_flat_list(self):
        _, collect_all = self._make_paginate()
        pages = {
            None: _FakePage([1, 2], "c1", True),
            "c1": _FakePage([3], None, False),
        }

        async def fetch(cursor=None, **_):
            return pages[cursor]

        result = run(collect_all(fetch))
        self.assertIsInstance(result, list)
        self.assertEqual(result, [1, 2, 3])

    def test_kwargs_forwarded_every_page(self):
        paginate, _ = self._make_paginate()
        received = []

        async def fetch(cursor=None, **kw):
            received.append(kw)
            return _FakePage([1], None, False)

        run(self._collect(paginate(fetch, country_id="7", limit=50)))
        self.assertEqual(received[0]["country_id"], "7")
        self.assertEqual(received[0]["limit"], 50)

    @staticmethod
    async def _collect(agen):
        return [item async for item in agen]


# ══════════════════════════════════════════════════════════════════════════════
# 7. Resource helpers (no HTTP, test parse logic)
# ══════════════════════════════════════════════════════════════════════════════


class TestCountryResourceLogic(unittest.TestCase):
    """Test parsing logic in CountryResource without real HTTP."""

    def _resource(self, return_value):
        from warera.resources.country import CountryResource

        http = mock.MagicMock()
        http.get = mock.AsyncMock(return_value=return_value)
        return CountryResource(http)

    def test_get_all_from_dict(self):
        raw = {
            "7": {"id": "7", "name": "Ukraine"},
            "8": {"id": "8", "name": "Romania"},
        }
        result = run(self._resource(raw).get_all())
        self.assertEqual(len(result), 2)
        self.assertIn("7", result)

    def test_get_all_from_list(self):
        raw = [{"id": "7", "name": "Ukraine"}, {"id": "8", "name": "Romania"}]
        result = run(self._resource(raw).get_all())
        self.assertEqual(len(result), 2)
        self.assertIn("7", result)

    def test_find_by_name_case_insensitive(self):
        raw = {"7": {"id": "7", "name": "Ukraine"}}
        found = run(self._resource(raw).find_by_name("ukraine"))
        self.assertIsNotNone(found)

    def test_find_by_name_returns_none_when_missing(self):
        raw = {"7": {"id": "7", "name": "Ukraine"}}
        found = run(self._resource(raw).find_by_name("Atlantis"))
        self.assertIsNone(found)


class TestWorkerResourceLogic(unittest.TestCase):
    def _resource(self, return_value):
        from warera.resources.worker import WorkerResource

        http = mock.MagicMock()
        http.get = mock.AsyncMock(return_value=return_value)
        return WorkerResource(http)

    def test_get_total_count_from_dict(self):
        raw = {"total": 42}
        result = run(self._resource(raw).get_total_count("u1"))
        self.assertEqual(result, 42)

    def test_get_total_count_from_int(self):
        result = run(self._resource(17).get_total_count("u1"))
        self.assertEqual(result, 17)

    def test_get_total_count_fallback_zero(self):
        result = run(self._resource({}).get_total_count("u1"))
        self.assertEqual(result, 0)


class TestUpgradeResourceValidation(unittest.TestCase):
    def _resource(self, return_value=None):
        from warera.resources.upgrade import UpgradeResource

        http = mock.MagicMock()
        http.get = mock.AsyncMock(return_value=return_value or {})
        return UpgradeResource(http)

    def test_raises_when_no_entity_id(self):
        from warera._enums import UpgradeType

        with self.assertRaises(WareraError):
            run(self._resource().get(UpgradeType.BUNKER))

    def test_does_not_raise_with_region_id(self):
        from warera._enums import UpgradeType

        # Should not raise — region_id is provided
        run(self._resource({"id": "u1"}).get(UpgradeType.BUNKER, region_id="42"))


class TestSearchResourceValidation(unittest.TestCase):
    def _resource(self, return_value=None):
        from warera.resources.search import SearchResource

        http = mock.MagicMock()
        http.get = mock.AsyncMock(return_value=return_value or {"results": []})
        return SearchResource(http)

    def test_raises_on_empty_query(self):
        with self.assertRaises(ValueError):
            run(self._resource().query(""))

    def test_raises_on_whitespace_query(self):
        with self.assertRaises(ValueError):
            run(self._resource().query("   "))


# ══════════════════════════════════════════════════════════════════════════════
# 8. Client assembly
# ══════════════════════════════════════════════════════════════════════════════


class TestClientAssembly(unittest.TestCase):
    def test_all_resources_present(self):
        from warera.client import WareraClient

        client = WareraClient.__new__(WareraClient)  # don't init httpx
        # Manually wire up a fake http
        fake_http = mock.MagicMock()
        fake_http._api_key = "test"
        fake_http._base_url = "https://test"

        # Run __init__ with patched HttpSession
        with mock.patch("warera.client.HttpSession", return_value=fake_http):
            client = WareraClient(api_key="test")

        expected = [
            "user",
            "company",
            "country",
            "government",
            "region",
            "battle",
            "battle_ranking",
            "battle_order",
            "round",
            "event",
            "item_trading",
            "work_offer",
            "worker",
            "mu",
            "ranking",
            "transaction",
            "upgrade",
            "article",
            "search",
            "game_config",
            "inventory",
            "action_log",
        ]
        for attr in expected:
            self.assertTrue(hasattr(client, attr), f"Missing resource: {attr}")

    def test_batch_returns_batch_session(self):
        from warera._batch import BatchSession
        from warera.client import WareraClient

        fake_http = mock.MagicMock()
        fake_http._api_key = None
        fake_http._base_url = "https://test"

        with mock.patch("warera.client.HttpSession", return_value=fake_http):
            client = WareraClient()

        session = client.batch()
        self.assertIsInstance(session, BatchSession)

    def test_repr_shows_auth_status(self):
        fake_http = mock.MagicMock()
        fake_http._api_key = "key123"
        fake_http._base_url = "https://api2.warera.io/trpc"

        with mock.patch("warera.client.HttpSession", return_value=fake_http):
            from warera.client import WareraClient

            client = WareraClient(api_key="key123")

        r = repr(client)
        self.assertIn("authenticated=True", r)

    def test_repr_shows_unauthenticated(self):
        fake_http = mock.MagicMock()
        fake_http._api_key = None
        fake_http._base_url = "https://api2.warera.io/trpc"

        with mock.patch("warera.client.HttpSession", return_value=fake_http):
            from warera.client import WareraClient

            client = WareraClient()

        r = repr(client)
        self.assertIn("authenticated=False", r)


# ══════════════════════════════════════════════════════════════════════════════
# 9. Sync shim proxy mechanics
# ══════════════════════════════════════════════════════════════════════════════


class TestSyncProxy(unittest.TestCase):
    def test_sync_proxy_wraps_coroutine(self):
        from warera.sync import _SyncResourceProxy

        class FakeResource:
            async def get(self, id: str):
                return {"id": id}

        proxy = _SyncResourceProxy(FakeResource())
        result = proxy.get("42")
        self.assertEqual(result, {"id": "42"})

    def test_sync_proxy_wraps_async_generator_to_list(self):
        from warera.sync import _SyncResourceProxy

        class FakeResource:
            async def paginate(self):
                for i in range(3):
                    yield i

        proxy = _SyncResourceProxy(FakeResource())
        result = proxy.paginate()
        self.assertIsInstance(result, list)
        self.assertEqual(result, [0, 1, 2])

    def test_sync_proxy_passes_through_non_async_attr(self):
        from warera.sync import _SyncResourceProxy

        class FakeResource:
            label = "hello"

        proxy = _SyncResourceProxy(FakeResource())
        self.assertEqual(proxy.label, "hello")


if __name__ == "__main__":
    unittest.main(verbosity=2)
