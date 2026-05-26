from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from .._pagination import collect_all, paginate
from ..models.common import CursorPage
from ..models.mercenary_contract_auction import MercenaryContractAuction
from ._base import BaseResource


class MercenaryContractAuctionResource(BaseResource):
    """
    Endpoints:
      • mercenaryContractAuction.getPaginatedAuctions
    """

    async def get_paginated_auctions(
        self,
        *,
        country_id: str | None = None,
        battle_id: str | None = None,
        status: str | None = None,
        limit: int = 10,
        cursor: str | None = None,
    ) -> CursorPage[MercenaryContractAuction]:
        """
        Get mercenary contract auctions (cursor-paginated).
        """
        raw = await self._get(
            "mercenaryContractAuction.getPaginatedAuctions",
            countryId=country_id,
            battleId=battle_id,
            status=status,
            limit=limit,
            cursor=cursor,
        )
        return CursorPage.from_raw(raw, MercenaryContractAuction)

    async def paginate(self, **kwargs: Any) -> AsyncIterator[MercenaryContractAuction]:
        """Async generator over mercenary contract auctions matching the given filters."""
        async for item in paginate(self.get_paginated_auctions, **kwargs):
            yield item

    async def collect_all(self, **kwargs: Any) -> list[MercenaryContractAuction]:
        """Collect all mercenary contract auctions across all pages."""
        return await collect_all(self.get_paginated_auctions, **kwargs)
