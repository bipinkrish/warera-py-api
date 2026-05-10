"""
Core HTTP session for the WarEra tRPC API.

Two call modes:
  • Single  → GET  /trpc/<procedure>?input=<url-encoded JSON>
  • Batch   → POST /trpc/<proc0>,<proc1>,...?batch=1   body: {"0": input0, ...}

Auth is optional: X-API-Key header is injected only when a key is present.

Rate-limit handling: the API returns standard rate-limit headers on every response:
  ratelimit-limit:     total requests allowed in the current window
  ratelimit-remaining: requests remaining in the current window
  ratelimit-reset:     seconds until the window resets

Rather than using a hardcoded delay, this session reads these headers after every
response and automatically waits when remaining reaches 0, for exactly as long as
the server says it will take for the window to reset.  This means the client
self-adapts to any future changes the server makes to its rate-limit policy.

Retry logic covers 429 (rate limit) and 5xx errors with exponential backoff.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import os
import time
from typing import Any
from urllib.parse import quote

import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from .exceptions import (
    WareraBatchError,
    WareraError,
    WareraHTTPError,
    WareraRateLimitError,
    WareraServerError,
    WareraValidationError,
    _raise_for_status,
)

# Public constant so client.py can import it instead of duplicating the string.
DEFAULT_BASE_URL = "https://api2.warera.io/trpc"
_ENV_KEY = "WARERA_API_KEY"


def _is_retryable(exc: BaseException) -> bool:
    """Retry on rate-limit errors, server errors, and network errors."""
    return isinstance(exc, (WareraRateLimitError, WareraServerError, httpx.TransportError))


class _RateLimitState:
    """
    Tracks the server-reported rate-limit window and enforces waits when
    the remaining quota hits zero.

    The API returns three headers per response:
      ratelimit-limit     – max requests per window (e.g. 500)
      ratelimit-remaining – requests left in the current window (e.g. 490)
      ratelimit-reset     – seconds until the window resets (e.g. 43)

    After each response we record ``remaining`` and compute the absolute
    monotonic timestamp at which the window will reset.  Before the next
    outgoing request we check whether we still have quota; if not, we
    sleep until the reset timestamp.
    """

    def __init__(self) -> None:
        self.limit: int | None = None
        self.remaining: int | None = None
        # Absolute monotonic time (seconds) when the window resets.
        self._reset_at: float | None = None
        self._lock: asyncio.Lock | None = None

    # asyncio.Lock must be created inside a running event-loop, so we
    # initialise it lazily instead of in __init__.
    def _get_lock(self) -> asyncio.Lock:
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    def update(self, headers: httpx.Headers) -> None:
        """Parse and store the rate-limit values from a response's headers."""
        raw_limit = headers.get("ratelimit-limit")
        raw_remaining = headers.get("ratelimit-remaining")
        raw_reset = headers.get("ratelimit-reset")

        if raw_limit is not None:
            with contextlib.suppress(ValueError):
                self.limit = int(raw_limit)

        if raw_remaining is not None:
            with contextlib.suppress(ValueError):
                self.remaining = int(raw_remaining)

        if raw_reset is not None:
            with contextlib.suppress(ValueError):
                self._reset_at = time.monotonic() + float(raw_reset)

    async def wait_if_exhausted(self) -> None:
        """
        If the current window is exhausted (remaining == 0) sleep until
        the window resets, then reset our internal state so subsequent
        requests proceed normally.
        """
        async with self._get_lock():
            if self.remaining is not None and self.remaining <= 0 and self._reset_at is not None:
                wait_secs = self._reset_at - time.monotonic()
                if wait_secs > 0:
                    await asyncio.sleep(wait_secs)
                # Reset state — next response will give us fresh values.
                self.remaining = None
                self._reset_at = None


class HttpSession:
    """
    Manages an httpx.AsyncClient with auth injection, header-based rate-limit
    throttling, and retry logic.

    Not intended for direct use — accessed through WareraClient.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 10.0,
        max_retries: int = 3,
        retry_backoff_factor: float = 0.5,
    ) -> None:
        # Resolve API key: explicit arg > env var > None
        self._api_key: str | None = api_key or os.environ.get(_ENV_KEY)
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries
        self._retry_backoff = retry_backoff_factor
        self._client: httpx.AsyncClient | None = None
        self._rate_limit = _RateLimitState()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def __aenter__(self) -> HttpSession:
        await self._ensure_client()
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.aclose()

    async def _ensure_client(self) -> None:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                timeout=self._timeout,
                headers={"User-Agent": "warera-client"},
                follow_redirects=True,
            )

    async def aclose(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    # ------------------------------------------------------------------
    # Auth helpers
    # ------------------------------------------------------------------

    def _auth_headers(self) -> dict[str, str]:
        if self._api_key:
            return {"X-API-Key": self._api_key}
        return {}

    # ------------------------------------------------------------------
    # Retry helper — built at call time so max_retries / retry_backoff_factor
    # are actually honoured instead of being silently ignored by a static
    # @retry decorator with hardcoded values.
    # ------------------------------------------------------------------

    def _retrying(self) -> AsyncRetrying:
        """Return an AsyncRetrying instance configured from this session's params."""
        return AsyncRetrying(
            retry=retry_if_exception(_is_retryable),
            stop=stop_after_attempt(self._max_retries),
            wait=wait_exponential(
                multiplier=self._retry_backoff,
                min=self._retry_backoff,
                max=10,
            ),
            reraise=True,
        )

    # ------------------------------------------------------------------
    # Single call  →  GET /procedure?input=<json>
    # ------------------------------------------------------------------

    async def get(self, procedure: str, params: dict[str, Any]) -> Any:
        """
        Execute a single tRPC GET call.
        Returns the parsed `result.data` from the response.
        """
        await self._ensure_client()

        clean = {k: v for k, v in params.items() if v is not None}
        encoded = quote(json.dumps(clean, separators=(",", ":")), safe="")
        url = f"/{procedure}?input={encoded}"

        response = await self._get_with_retry(url)
        return self._unwrap_single(response, procedure)

    async def _get_with_retry(self, url: str) -> httpx.Response:
        result: httpx.Response | None = None
        async for attempt in self._retrying():
            with attempt:
                # Respect the server-reported rate-limit window before sending.
                await self._rate_limit.wait_if_exhausted()
                if self._client is None:
                    raise RuntimeError(
                        "HTTP client is not initialised — call __aenter__ first"
                    )
                resp = await self._client.get(url, headers=self._auth_headers())
                # Update rate-limit state from response headers.
                self._rate_limit.update(resp.headers)
                self._check_response(resp)
                result = resp
        return result  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # Batch call  →  POST /proc0,proc1,...?batch=1   body: {"0": {}, ...}
    # ------------------------------------------------------------------

    async def post_batch(
        self,
        procedures: list[str],
        inputs: list[dict[str, Any]],
        *,
        chunk_size: int = 50,
    ) -> list[Any]:
        """
        Execute one or more tRPC batch POSTs, automatically splitting oversized
        lists into chunks of at most ``chunk_size`` (hard-capped at 50, the
        server's enforced limit).

        Returns a list of parsed ``result.data`` values in the same order as
        ``procedures``.  Raises :exc:`WareraBatchError` if any item fails.

        Args:
            procedures: Procedure names to call, e.g. ``["company.getById", ...]``.
            inputs:     Corresponding input dicts, one per procedure.
            chunk_size: Max procedures per physical HTTP request.  Values above
                        the server hard limit of 50 are clamped silently.
        """
        await self._ensure_client()

        if not procedures:
            return []

        # Clamp to the server hard limit regardless of what was passed.
        _MAX_BATCH = 50
        effective = min(max(1, chunk_size), _MAX_BATCH)

        # Fast path: fits in one request.
        if len(procedures) <= effective:
            proc_path = ",".join(procedures)
            url = f"/{proc_path}?batch=1"
            body = {str(i): inp for i, inp in enumerate(inputs)}
            raw_list = await self._post_batch_with_retry(url, body)
            return self._unwrap_batch(raw_list, procedures)

        # Slow path: split into chunks and collect results in order.
        # Chunks are fired concurrently — the header-based rate-limit tracker
        # will sleep automatically if the window is exhausted mid-flight.
        chunks: list[tuple[list[str], list[dict[str, Any]]]] = []
        for start in range(0, len(procedures), effective):
            end = start + effective
            chunks.append((procedures[start:end], inputs[start:end]))

        async def _run_chunk(
            procs: list[str], inps: list[dict[str, Any]]
        ) -> list[Any]:
            proc_path = ",".join(procs)
            url = f"/{proc_path}?batch=1"
            body = {str(i): inp for i, inp in enumerate(inps)}
            raw = await self._post_batch_with_retry(url, body)
            return self._unwrap_batch(raw, procs)

        chunk_results = await asyncio.gather(*[_run_chunk(p, i) for p, i in chunks])
        return [item for sublist in chunk_results for item in sublist]

    async def _post_batch_with_retry(
        self, url: str, body: dict[str, Any]
    ) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] | None = None
        async for attempt in self._retrying():
            with attempt:
                # Respect the server-reported rate-limit window before sending.
                await self._rate_limit.wait_if_exhausted()
                if self._client is None:
                    raise RuntimeError(
                        "HTTP client is not initialised — call __aenter__ first"
                    )
                headers = {**self._auth_headers(), "Content-Type": "application/json"}
                resp = await self._client.post(url, json=body, headers=headers)
                # Update rate-limit state from response headers.
                self._rate_limit.update(resp.headers)
                self._check_response(resp)
                data = resp.json()
                if not isinstance(data, list):
                    raise ValueError(
                        f"Expected list from batch endpoint, got {type(data).__name__}"
                    )
                result = data
        return result  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # Response parsing helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _check_response(resp: httpx.Response) -> None:
        """Raise the appropriate WareraHTTPError for non-2xx responses."""
        if resp.status_code < 400:
            return

        # Surface the Retry-After header value when rate-limited so callers
        # can respect it without having to inspect the raw response themselves.
        if resp.status_code == 429:
            retry_after: float | None = None
            raw_header = resp.headers.get("Retry-After")
            if raw_header is not None:
                with contextlib.suppress(ValueError):
                    retry_after = float(raw_header)
            try:
                body = resp.json()
            except Exception:
                body = resp.text
            raise WareraRateLimitError(retry_after=retry_after, response_body=body)

        try:
            body = resp.json()
        except Exception:
            body = resp.text
        _raise_for_status(resp.status_code, body)

    @staticmethod
    def _unwrap_single(resp: httpx.Response, procedure: str) -> Any:
        """
        tRPC single response shape:
          { "result": { "data": <payload> } }
        or an error:
          { "error": { "message": "...", "code": ... } }
        """
        try:
            data = resp.json()
        except Exception as exc:
            raise ValueError(f"Non-JSON response from {procedure}: {resp.text}") from exc

        if "error" in data:
            err = data["error"]
            code = err.get("data", {}).get("httpStatus", 500)
            _raise_for_status(code, err)

        try:
            return data["result"]["data"]
        except (KeyError, TypeError) as exc:
            raise ValueError(
                f"Unexpected tRPC response shape from {procedure}: {data}"
            ) from exc

    @staticmethod
    def _unwrap_batch(raw_list: list[dict[str, Any]], procedures: list[str]) -> list[Any]:
        """
        tRPC batch response shape:
          [
            { "result": { "data": <payload> } },   ← success
            { "error": { "message": "...", ... } }, ← failure
            ...
          ]

        Returns a list of unwrapped data values.
        Raises WareraBatchError if any item errored.
        """
        results: dict[int, Any] = {}
        errors: dict[int, WareraError] = {}

        for i, (item, proc) in enumerate(zip(raw_list, procedures, strict=True)):
            if "error" in item:
                err = item["error"]
                code = err.get("data", {}).get("httpStatus", 500)
                try:
                    _raise_for_status(code, err)
                except WareraHTTPError as e:
                    errors[i] = e
            else:
                try:
                    results[i] = item["result"]["data"]
                except (KeyError, TypeError):
                    errors[i] = WareraValidationError(
                        f"Bad shape at batch index {i} ({proc}): {item}", item
                    )

        if errors:
            raise WareraBatchError(errors=errors, results=results)

        return [results[i] for i in range(len(procedures))]
