from __future__ import annotations

from .._batch import fetch_many_by_ids
from ..models.region import Region
from ._base import BaseResource


class RegionResource(BaseResource):
    """
    Endpoints:
      • region.getById
      • region.getRegionsObject
    """

    async def get(self, region_id: str) -> Region:
        """Get a single region by ID."""
        raw = await self._get("region.getById", regionId=region_id)
        return Region.model_validate(raw)

    async def get_all(self) -> dict[str, Region]:
        """
        Get all regions as a dict keyed by region ID.
        This is a large payload — cache it if you call it repeatedly.
        """
        raw = await self._get("region.getRegionsObject")
        if isinstance(raw, dict):
            return {k: Region.model_validate(v) for k, v in raw.items()}
        if isinstance(raw, list):
            regions = [Region.model_validate(r) for r in raw]
            return {r.id: r for r in regions if r.id}
        return {}

    async def get_many(self, region_ids: list[str], batch_size: int = 50) -> list[Region]:
        """Fetch multiple regions by ID in batched POST requests."""
        raw_list = await fetch_many_by_ids(
            self._http, "region.getById", "regionId", region_ids, batch_size
        )
        return [Region.model_validate(r) for r in raw_list]
