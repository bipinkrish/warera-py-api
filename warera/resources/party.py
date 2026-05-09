from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from .._pagination import collect_all, paginate
from ..models.common import CursorPage
from ..models.party import Party
from ._base import BaseResource


class PartyResource(BaseResource):
    """
    Endpoints:
      • party.getById
      • party.getManyPaginated  (cursor-paginated)
    """

    async def get(self, party_id: str) -> Party:
        """Get a single political party by ID."""
        raw = await self._get("party.getById", partyId=party_id)
        return Party.model_validate(raw)

    async def get_paginated(
        self,
        *,
        country_id: str | None = None,
        limit: int = 20,
        cursor: str | None = None,
        direction: str | None = None,
    ) -> CursorPage[Party]:
        """
        Get political parties (cursor-paginated), optionally filtered by country.

        Args:
            country_id: Filter to parties in this country.
            direction:  ``"forward"`` (default) or ``"backward"`` pagination.
        """
        raw = await self._get(
            "party.getManyPaginated",
            countryId=country_id,
            limit=limit,
            cursor=cursor,
            direction=direction,
        )
        return CursorPage.from_raw(raw, Party)

    async def paginate(self, **kwargs: Any) -> AsyncIterator[Party]:
        """Async generator over all parties matching the given filters."""
        async for item in paginate(self.get_paginated, **kwargs):
            yield item

    async def collect_all(self, **kwargs: Any) -> list[Party]:
        """Collect all parties across all pages."""
        return await collect_all(self.get_paginated, **kwargs)

    async def get_by_country(self, country_id: str) -> list[Party]:
        """Convenience: fetch all parties in a given country."""
        return await self.collect_all(country_id=country_id)
