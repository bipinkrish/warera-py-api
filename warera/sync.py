"""
Synchronous shim over WareraClient.

Every async method is wrapped so callers don't need asyncio boilerplate.
Useful for scripts, notebooks, and REPLs.

Usage:
    from warera.sync import WareraClient

    client = WareraClient(api_key="...")
    user    = client.user.get_lite("12345")
    prices  = client.item_trading.get_prices()

    # Batch
    with client.batch() as batch:
        c1  = batch.add("company.getById", {"companyId": "111"})
        gov = batch.add("government.getByCountryId", {"countryId": "7"})
    print(c1.result)

Note: Each method call opens and closes its own asyncio event loop via
asyncio.run(). For high-throughput workloads, prefer the async client.
"""

from __future__ import annotations

import asyncio
import functools
import inspect
from typing import Any, cast

from ._batch import BatchSession
from .client import WareraClient as _AsyncClient


def _run(coro: Any) -> Any:
    """
    Run a coroutine synchronously.

    Uses asyncio.get_running_loop() to safely detect whether we are already
    inside a running event loop (e.g. Jupyter). The older get_event_loop()
    is deprecated in Python 3.10 and raises a RuntimeError in 3.12 when
    called with no current loop, making get_running_loop() the correct choice.
    """
    try:
        loop = asyncio.get_running_loop()
        # Already inside a running event loop (e.g. Jupyter) — use nest_asyncio.
        import nest_asyncio

        nest_asyncio.apply()
        return loop.run_until_complete(coro)
    except RuntimeError:
        # No running loop — safe to call asyncio.run().
        return asyncio.run(coro)


def _sync_generator(async_gen_fn: Any, *args: Any, **kwargs: Any) -> list[Any]:
    """Drain an async generator into a list synchronously."""

    async def _collect() -> list[Any]:
        return [item async for item in async_gen_fn(*args, **kwargs)]

    return cast("list[Any]", _run(_collect()))


def _wrap_resource(async_resource: Any) -> _SyncResourceProxy:
    return _SyncResourceProxy(async_resource)


class _SyncResourceProxy:
    """
    Wraps an async resource class, making every coroutine method callable
    synchronously and every async generator method return a list.
    """

    def __init__(self, resource: Any) -> None:
        self._resource = resource

    def __getattr__(self, name: str) -> Any:
        attr = getattr(self._resource, name)

        if inspect.iscoroutinefunction(attr):

            @functools.wraps(attr)
            def sync_method(*args: Any, **kwargs: Any) -> Any:
                return _run(attr(*args, **kwargs))

            return sync_method

        if inspect.isasyncgenfunction(attr):

            @functools.wraps(attr)
            def sync_gen(*args: Any, **kwargs: Any) -> list[Any]:
                return _sync_generator(attr, *args, **kwargs)

            return sync_gen

        return attr


class _SyncBatchSession:
    """Synchronous wrapper around BatchSession."""

    def __init__(self, session: BatchSession) -> None:
        self._session = session

    def add(self, procedure: str, input_: dict[str, Any] | None = None) -> Any:
        return self._session.add(procedure, input_)

    def __enter__(self) -> _SyncBatchSession:
        return self

    def __exit__(self, *_: Any) -> None:
        _run(self._session.flush())


class WareraClient:
    """
    Synchronous WarEra API client.

    Wraps the async WareraClient — every method is callable without await.
    Constructor arguments are identical to the async client.
    """

    def __init__(self, api_key: str | None = None, **kwargs: Any) -> None:
        self._async_client = _AsyncClient(api_key=api_key, **kwargs)
        _run(self._async_client._http.__aenter__())

        # Wrap every resource namespace
        self.user = _wrap_resource(self._async_client.user)
        self.company = _wrap_resource(self._async_client.company)
        self.country = _wrap_resource(self._async_client.country)
        self.government = _wrap_resource(self._async_client.government)
        self.region = _wrap_resource(self._async_client.region)
        self.battle = _wrap_resource(self._async_client.battle)
        self.battle_ranking = _wrap_resource(self._async_client.battle_ranking)
        self.battle_order = _wrap_resource(self._async_client.battle_order)
        self.round = _wrap_resource(self._async_client.round)
        self.event = _wrap_resource(self._async_client.event)
        self.item_trading = _wrap_resource(self._async_client.item_trading)
        self.work_offer = _wrap_resource(self._async_client.work_offer)
        self.worker = _wrap_resource(self._async_client.worker)
        self.mu = _wrap_resource(self._async_client.mu)
        self.ranking = _wrap_resource(self._async_client.ranking)
        self.transaction = _wrap_resource(self._async_client.transaction)
        self.upgrade = _wrap_resource(self._async_client.upgrade)
        self.article = _wrap_resource(self._async_client.article)
        self.search = _wrap_resource(self._async_client.search)
        self.game_config = _wrap_resource(self._async_client.game_config)
        self.inventory = _wrap_resource(self._async_client.inventory)
        self.action_log = _wrap_resource(self._async_client.action_log)

    def batch(self, batch_size: int | None = None) -> _SyncBatchSession:
        return _SyncBatchSession(self._async_client.batch(batch_size))

    def close(self) -> None:
        _run(self._async_client.aclose())

    def __enter__(self) -> WareraClient:
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    def __repr__(self) -> str:
        return repr(self._async_client).replace("WareraClient", "sync.WareraClient")
