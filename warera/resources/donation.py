from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from .._pagination import collect_all, paginate
from ..models.common import CursorPage
from ..models.donation import Donation, DonationTotals
from ._base import BaseResource


class DonationResource(BaseResource):
    """
    Endpoints:
      • donation.getManyPaginated  (cursor-paginated)
      • donation.getTotalDonations
    """

    async def get_paginated(
        self,
        *,
        mu_id: str | None = None,
        country_id: str | None = None,
        party_id: str | None = None,
        limit: int = 20,
        cursor: str | None = None,
        direction: str | None = None,
    ) -> CursorPage[Donation]:
        """
        Get donations (cursor-paginated), filtered by target entity.

        At least one of ``mu_id``, ``country_id``, or ``party_id`` is recommended.

        Args:
            direction: ``"forward"`` (default) or ``"backward"`` pagination.
        """
        raw = await self._get(
            "donation.getManyPaginated",
            muId=mu_id,
            countryId=country_id,
            partyId=party_id,
            limit=limit,
            cursor=cursor,
            direction=direction,
        )
        return CursorPage.from_raw(raw, Donation)

    async def paginate(self, **kwargs: Any) -> AsyncIterator[Donation]:
        """Async generator over donations matching the given filters."""
        async for item in paginate(self.get_paginated, **kwargs):
            yield item

    async def collect_all(self, **kwargs: Any) -> list[Donation]:
        """Collect all donations across all pages."""
        return await collect_all(self.get_paginated, **kwargs)

    async def get_totals(
        self,
        *,
        mu_id: str | None = None,
        country_id: str | None = None,
        party_id: str | None = None,
    ) -> DonationTotals:
        """
        Get aggregate donation totals (total amount and donor count) for a target.

        Args:
            mu_id:      Military unit to aggregate for.
            country_id: Country to aggregate for.
            party_id:   Party to aggregate for.
        """
        raw = await self._get(
            "donation.getTotalDonations",
            muId=mu_id,
            countryId=country_id,
            partyId=party_id,
        )
        return DonationTotals.model_validate(raw)
