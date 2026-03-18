"""
Batch request system for the WarEra tRPC API.

Wire protocol (from observed TypeScript usage):
  POST /trpc/proc0,proc1,proc2,...?batch=1
  Content-Type: application/json
  X-API-Key: <token>          ← optional, same as single calls

  Body:
  {
    "0": { ...input for proc0 },
    "1": { ...input for proc1 },
    "2": { ...input for proc2 }
  }

  Response: JSON array, one element per procedure, same order.

Usage:
    async with client.batch() as batch:
        company_a = batch.add("company.getById",   {"companyId": "111"})
        company_b = batch.add("company.getById",   {"companyId": "222"})
        gov       = batch.add("government.getByCountryId", {"countryId": "7"})
    # All three resolved in one HTTP round-trip
    print(company_a.result)
    print(gov.result)
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar, cast

from .exceptions import WareraBatchError, WareraError

T = TypeVar("T")

# Max procedures per batch POST (keep URLs sane and avoid server limits)
DEFAULT_BATCH_SIZE = 50


@dataclass
class BatchItem(Generic[T]):
    """
    A placeholder returned immediately when a call is added to a BatchSession.
    After the session flushes, `result` or `error` will be populated.
    """

    procedure: str
    input: dict[str, Any]
    _result: T | None = field(default=None, repr=False)
    _error: WareraError | None = field(default=None, repr=False)
    _resolved: bool = field(default=False, repr=False)

    def __str__(self) -> str:
        status = "resolved" if self._resolved else "pending"
        return f"<BatchItem {self.procedure} ({status})>"

    @property
    def result(self) -> T:
        if not self._resolved:
            raise RuntimeError(
                "BatchItem has not been resolved yet. "
                "Access .result after the `async with batch:` block exits."
            )
        if self._error is not None:
            raise self._error
        return self._result  # type: ignore[return-value]

    @property
    def ok(self) -> bool:
        """True if the item resolved without error."""
        return self._resolved and self._error is None

    def _resolve(self, data: Any) -> None:
        self._result = data
        self._resolved = True

    def _fail(self, error: WareraError) -> None:
        self._error = error
        self._resolved = True


class BatchSession:
    """
    Collects tRPC procedure calls and flushes them in one or more batch POSTs.

    Use as an async context manager via `client.batch()`:

        async with client.batch() as batch:
            item1 = batch.add("company.getById", {"companyId": "123"})
            item2 = batch.add("user.getUserLite", {"userId": "456"})

        # After the block: item1.result, item2.result are populated.

    If batch_size < number of queued calls, they are split into multiple
    concurrent POST requests automatically.
    """

    def __init__(self, http: Any, batch_size: int = DEFAULT_BATCH_SIZE) -> None:
        # `http` is an HttpSession instance — typed as Any to avoid circular import
        self._http = http
        self._batch_size = batch_size
        self._queue: list[BatchItem[Any]] = []

    def __str__(self) -> str:
        return f"<BatchSession queued={len(self._queue)}>"

    def __len__(self) -> int:
        return len(self._queue)

    def add(self, procedure: str, input_: dict[str, Any] | None = None) -> BatchItem[Any]:
        """
        Queue a procedure call. Returns a BatchItem that will be resolved
        when the session flushes.
        """
        item: BatchItem[Any] = BatchItem(procedure=procedure, input=input_ or {})
        self._queue.append(item)
        return item

    async def flush(self) -> None:
        """
        Execute all queued calls. Splits into chunks of `batch_size` and
        fires chunks concurrently. Called automatically on `__aexit__`.
        """
        if not self._queue:
            return

        # Split queue into chunks
        chunks: list[list[BatchItem[Any]]] = [
            self._queue[i : i + self._batch_size]
            for i in range(0, len(self._queue), self._batch_size)
        ]

        # Fire all chunks concurrently
        await asyncio.gather(*[self._flush_chunk(chunk) for chunk in chunks])

    async def _flush_chunk(self, chunk: list[BatchItem[Any]]) -> None:
        procedures = [item.procedure for item in chunk]
        inputs = [item.input for item in chunk]

        try:
            results = await self._http.post_batch(procedures, inputs)
            for item, data in zip(chunk, results, strict=True):
                item._resolve(data)
        except WareraBatchError as exc:
            # Partial success — resolve what succeeded, fail what didn't
            for i, item in enumerate(chunk):
                if i in exc.errors:
                    item._fail(exc.errors[i])
                elif i in exc.results:
                    item._resolve(exc.results[i])
        except WareraError as exc:
            # Entire chunk failed (e.g. network error)
            for item in chunk:
                item._fail(exc)

    async def __aenter__(self) -> BatchSession:
        return self

    async def __aexit__(self, exc_type: Any, *_: Any) -> None:
        # Only flush if no exception is propagating
        if exc_type is None:
            await self.flush()


# ---------------------------------------------------------------------------
# Auto-chunked many-by-IDs helper
# ---------------------------------------------------------------------------


async def fetch_many_by_ids(
    http: Any,
    procedure: str,
    id_param: str,
    ids: list[str],
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> list[Any]:
    """
    Fetch the same procedure for many IDs, auto-splitting into batch chunks
    fired concurrently.

    Args:
        http:       HttpSession instance
        procedure:  e.g. "company.getById"
        id_param:   The input key name, e.g. "companyId"
        ids:        List of ID strings to fetch
        batch_size: Max IDs per batch POST (default 50)

    Returns:
        List of raw API responses in the same order as `ids`.
    """
    if not ids:
        return []

    chunks = [ids[i : i + batch_size] for i in range(0, len(ids), batch_size)]

    async def fetch_chunk(chunk: list[str]) -> list[Any]:
        procedures = [procedure] * len(chunk)
        inputs = [{id_param: id_} for id_ in chunk]
        return cast("list[Any]", await http.post_batch(procedures, inputs))

    chunk_results = await asyncio.gather(*[fetch_chunk(c) for c in chunks])
    return [item for sublist in chunk_results for item in sublist]
