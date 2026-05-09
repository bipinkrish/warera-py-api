from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from .._pagination import collect_all, paginate
from ..models.common import CursorPage
from ..models.work_offer import WorkOffer
from ._base import BaseResource


class WageRange:
    """Min/max/average wage range."""

    __slots__ = ("min", "max", "average")

    def __init__(self, raw: dict[str, Any]) -> None:
        self.min: float = float(raw.get("min", 0))
        self.max: float = float(raw.get("max", 0))
        self.average: float = float(raw.get("average", 0))

    def __repr__(self) -> str:
        return f"WageRange(min={self.min}, max={self.max}, avg={self.average})"


class WageStats:
    """
    Result of ``workOffer.getWageStats``.

    Attributes:
        allowed_range:        Min/max/average wages allowed for the given worker profile.
        top_offer:            Highest absolute offer on the market.
        top_eligible_offer:   Best offer this worker qualifies for.
        top_eligible_offers:  List of top raw offer dicts this worker qualifies for.
    """

    def __init__(self, raw: dict[str, Any]) -> None:
        self.allowed_range = WageRange(raw.get("allowedRange", {}))
        self.top_offer: float = float(raw.get("topOffer", 0))
        self.top_eligible_offer: float = float(raw.get("topEligibleOffer", 0))
        self.top_eligible_offers: list[dict[str, Any]] = raw.get("topEligibleOffers", [])

    def __repr__(self) -> str:
        return (
            f"WageStats(top_offer={self.top_offer}, top_eligible={self.top_eligible_offer}, "
            f"allowed_range={self.allowed_range})"
        )


class WorkOfferResource(BaseResource):
    """
    Endpoints:
      • workOffer.getById
      • workOffer.getWorkOfferByCompanyId
      • workOffer.getWorkOffersPaginated   (cursor-paginated)
      • workOffer.getWageStats
    """

    async def get(self, work_offer_id: str) -> WorkOffer:
        """Get a single work offer by ID."""
        raw = await self._get("workOffer.getById", workOfferId=work_offer_id)
        return WorkOffer.model_validate(raw)

    async def get_by_company(self, company_id: str) -> list[WorkOffer]:
        """Get all work offers posted by a specific company."""
        raw = await self._get("workOffer.getWorkOfferByCompanyId", companyId=company_id)
        if isinstance(raw, list):
            return [WorkOffer.model_validate(o) for o in raw]
        if isinstance(raw, dict):
            raw_items = raw.get("items", raw.get("data", []))
            items = raw_items if isinstance(raw_items, list) else []
        else:
            items = []
        return [WorkOffer.model_validate(o) for o in items]

    async def get_paginated(
        self,
        *,
        limit: int = 10,
        cursor: str | None = None,
        user_id: str | None = None,
        region_id: str | None = None,
        energy: float | None = None,
        production: float | None = None,
        citizenship: str | None = None,
    ) -> CursorPage[WorkOffer]:
        """
        Get work offers with optional filters (cursor-paginated).

        Args:
            energy:      Filter: offers requiring at most this energy.
            production:  Filter: offers with at least this production value.
            citizenship: Filter: offers open to this citizenship.
        """
        raw = await self._get(
            "workOffer.getWorkOffersPaginated",
            limit=limit,
            cursor=cursor,
            userId=user_id,
            regionId=region_id,
            energy=energy,
            production=production,
            citizenship=citizenship,
        )
        return CursorPage.from_raw(raw, WorkOffer)

    async def get_wage_stats(
        self,
        *,
        energy: float,
        production: float,
        citizenship: str,
    ) -> WageStats:
        """
        Get wage statistics for a given worker profile — the range of allowed wages,
        the top market offer, and the best offers this worker is eligible for.

        Args:
            energy:      The worker's energy stat.
            production:  The worker's production stat.
            citizenship: The worker's citizenship country ID or code.

        Returns:
            A :class:`WageStats` object.
        """
        raw = await self._get(
            "workOffer.getWageStats",
            energy=energy,
            production=production,
            citizenship=citizenship,
        )
        if isinstance(raw, dict):
            return WageStats(raw)
        return WageStats({})

    async def paginate(self, **kwargs: Any) -> AsyncIterator[WorkOffer]:
        """Async generator over work offers matching the given filters."""
        async for item in paginate(self.get_paginated, **kwargs):
            yield item

    async def collect_all(self, **kwargs: Any) -> list[WorkOffer]:
        """Collect all work offers across all pages."""
        return await collect_all(self.get_paginated, **kwargs)
