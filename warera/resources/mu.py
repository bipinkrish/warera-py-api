from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from .._batch import fetch_many_by_ids
from .._pagination import collect_all, paginate
from ..models.common import CursorPage
from ..models.military_unit import MilitaryUnit
from ._base import BaseResource


class MUResource(BaseResource):
    """
    Endpoints:
      • mu.getById
      • mu.getManyPaginated  (cursor-paginated)
    """

    async def get(self, mu_id: str) -> MilitaryUnit:
        """Get a military unit by ID."""
        raw = await self._get("mu.getById", muId=mu_id)
        return MilitaryUnit.model_validate(raw)

    async def get_paginated(
        self,
        *,
        limit: int = 20,
        cursor: str | None = None,
        member_id: str | None = None,
        user_id: str | None = None,
        search: str | None = None,
    ) -> CursorPage[MilitaryUnit]:
        """
        Get military units (cursor-paginated).

        Args:
            member_id:  Filter: MUs that this user is a member of.
            user_id:    Filter: MUs owned/created by this user.
            search:     Text search across MU names.
        """
        raw = await self._get(
            "mu.getManyPaginated",
            limit=limit,
            cursor=cursor,
            memberId=member_id,
            userId=user_id,
            search=search,
        )
        return CursorPage.from_raw(raw, MilitaryUnit)

    async def paginate(self, **kwargs: Any) -> AsyncIterator[MilitaryUnit]:
        """Async generator over all military units matching the given filters."""
        async for item in paginate(self.get_paginated, **kwargs):
            yield item

    async def collect_all(self, **kwargs: Any) -> list[MilitaryUnit]:
        """Collect all military units across all pages."""
        return await collect_all(self.get_paginated, **kwargs)

    async def get_many(self, mu_ids: list[str], batch_size: int = 50) -> list[MilitaryUnit]:
        """Fetch multiple military units by ID in batched POST requests."""
        raw_list = await fetch_many_by_ids(self._http, "mu.getById", "muId", mu_ids, batch_size)
        return [MilitaryUnit.model_validate(r) for r in raw_list]
