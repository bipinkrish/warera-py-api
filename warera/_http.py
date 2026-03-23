"""
Core HTTP session for the WarEra tRPC API.

Two call modes:
  • Single  → GET  /trpc/<procedure>?input=<url-encoded JSON>
  • Batch   → POST /trpc/<proc0>,<proc1>,...?batch=1   body: {"0": input0, ...}

Auth is optional: X-API-Key header is injected only when a key is present.
Retry logic covers 429 (rate limit) and 5xx errors with exponential backoff.
The retry parameters (max_retries, retry_backoff_factor) passed to HttpSession
are respected at runtime — they are not hard-wired in a static decorator.
"""

from __future__ import annotations

import contextlib
import json
import os
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
    WareraRateLimitError,
    WareraServerError,
    _raise_for_status,
)

# Public constant so client.py can import it instead of duplicating the string.
DEFAULT_BASE_URL = "https://api2.warera.io/trpc"
_ENV_KEY = "WARERA_API_KEY"


def _is_retryable(exc: BaseException) -> bool:
    """Retry on rate-limit errors, server errors, and network errors."""
    return isinstance(exc, (WareraRateLimitError, WareraServerError, httpx.TransportError))


class HttpSession:
    """
    Manages an httpx.AsyncClient with auth injection, encoding helpers,
    and retry logic.

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
                headers={"User-Agent": "warera-client/0.1.0"},
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
                if self._client is None:
                    raise RuntimeError(
                        "HTTP client is not initialised — call __aenter__ first"
                    )
                resp = await self._client.get(url, headers=self._auth_headers())
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
    ) -> list[Any]:
        """
        Execute a tRPC batch POST.
        Returns a list of parsed `result.data` values in the same order
        as `procedures`. Raises WareraBatchError if any item fails.
        """
        await self._ensure_client()

        if not procedures:
            return []

        proc_path = ",".join(procedures)
        url = f"/{proc_path}?batch=1"
        # tRPC batch body: keys are string-integers
        body = {str(i): inp for i, inp in enumerate(inputs)}

        raw_list = await self._post_batch_with_retry(url, body)
        return self._unwrap_batch(raw_list, procedures)

    async def _post_batch_with_retry(
        self, url: str, body: dict[str, Any]
    ) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] | None = None
        async for attempt in self._retrying():
            with attempt:
                if self._client is None:
                    raise RuntimeError(
                        "HTTP client is not initialised — call __aenter__ first"
                    )
                headers = {**self._auth_headers(), "Content-Type": "application/json"}
                resp = await self._client.post(url, json=body, headers=headers)
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
        from .exceptions import WareraBatchError, WareraError, WareraHTTPError

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
                    from .exceptions import WareraValidationError

                    errors[i] = WareraValidationError(
                        f"Bad shape at batch index {i} ({proc}): {item}", item
                    )

        if errors:
            raise WareraBatchError(errors=errors, results=results)

        return [results[i] for i in range(len(procedures))]
