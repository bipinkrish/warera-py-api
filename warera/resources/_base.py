"""Base class shared by all resource namespaces."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .._http import HttpSession


class BaseResource:
    def __init__(self, http: HttpSession) -> None:
        self._http = http

    async def _get(self, procedure: str, **params: Any) -> Any:
        """Call a single GET procedure, stripping None values from params."""
        cleaned = {k: v for k, v in params.items() if v is not None}
        return await self._http.get(procedure, cleaned)
