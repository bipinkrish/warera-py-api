from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from .._pagination import collect_all, paginate
from ..models.common import CursorPage
from ..models.election import Election
from ._base import BaseResource


class ElectionResource(BaseResource):
    """
    Endpoints:
      • election.getElections  (cursor-paginated)
    """

    async def get_paginated(
        self,
        *,
        country_id: str | None = None,
        limit: int = 20,
        cursor: str | None = None,
        direction: str | None = None,
    ) -> CursorPage[Election]:
        """
        Get elections (cursor-paginated), optionally filtered by country.

        Args:
            country_id: Filter to elections in this country.
            direction:  ``"forward"`` (default) or ``"backward"`` pagination.
        """
        raw = await self._get(
            "election.getElections",
            countryId=country_id,
            limit=limit,
            cursor=cursor,
            direction=direction,
        )
        return CursorPage.from_raw(raw, Election)

    async def paginate(self, **kwargs: Any) -> AsyncIterator[Election]:
        """Async generator over all elections matching the given filters."""
        async for item in paginate(self.get_paginated, **kwargs):
            yield item

    async def collect_all(self, **kwargs: Any) -> list[Election]:
        """Collect all elections across all pages."""
        return await collect_all(self.get_paginated, **kwargs)

    async def get_by_country(self, country_id: str) -> list[Election]:
        """Convenience: fetch all elections in a given country."""
        return await self.collect_all(country_id=country_id)
