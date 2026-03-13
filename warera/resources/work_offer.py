from __future__ import annotations
from typing import Any
from .._pagination import paginate, collect_all
from ..models.common import CursorPage
from ..models.work_offer import WorkOffer
from ._base import BaseResource


class WorkOfferResource(BaseResource):
    """
    Endpoints:
      • workOffer.getById
      • workOffer.getWorkOfferByCompanyId
      • workOffer.getWorkOffersPaginated  (cursor-paginated)
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
        items = raw.get("items", raw.get("data", [])) if isinstance(raw, dict) else []
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

    async def paginate(self, **kwargs: Any):
        """Async generator over work offers matching the given filters."""
        async for item in paginate(self.get_paginated, **kwargs):
            yield item

    async def collect_all(self, **kwargs: Any) -> list[WorkOffer]:
        """Collect all work offers across all pages."""
        return await collect_all(self.get_paginated, **kwargs)
