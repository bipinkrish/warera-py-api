from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from .._enums import BattleDirection, BattleFilter
from .._pagination import collect_all, paginate
from ..models.battle import Battle, BattleLive
from ..models.common import CursorPage
from ._base import BaseResource


class BattleResource(BaseResource):
    """
    Endpoints:
      • battle.getById
      • battle.getLiveBattleData
      • battle.getBattles  (cursor-paginated)
    """

    async def get(self, battle_id: str) -> Battle:
        """Get full battle info by ID."""
        raw = await self._get("battle.getById", battleId=battle_id)
        return Battle.model_validate(raw)

    async def get_live(
        self,
        battle_id: str,
        *,
        round_number: int | None = None,
    ) -> BattleLive:
        """Get live battle data (scores, damage, time remaining)."""
        raw = await self._get(
            "battle.getLiveBattleData",
            battleId=battle_id,
            roundNumber=round_number,
        )
        return BattleLive.model_validate(raw)

    async def get_many(
        self,
        *,
        is_active: bool | None = None,
        limit: int = 10,
        cursor: str | None = None,
        direction: BattleDirection | str | None = None,
        filter: BattleFilter | str | None = None,
        defender_region_id: str | None = None,
        war_id: str | None = None,
        country_id: str | None = None,
    ) -> CursorPage[Battle]:
        """Get battles with optional filters (cursor-paginated)."""
        raw = await self._get(
            "battle.getBattles",
            isActive=is_active,
            limit=limit,
            cursor=cursor,
            direction=direction,
            filter=filter,
            defenderRegionId=defender_region_id,
            warId=war_id,
            countryId=country_id,
        )
        return CursorPage.from_raw(raw, Battle)

    async def get_active(self, **kwargs: Any) -> list[Battle]:
        """Convenience: return all currently active battles."""
        return await collect_all(self.get_many, is_active=True, **kwargs)

    # ------------------------------------------------------------------
    # Pagination helpers
    # ------------------------------------------------------------------

    async def paginate(self, **kwargs: Any) -> AsyncIterator[Battle]:
        """Async generator over battles matching the given filters."""
        async for item in paginate(self.get_many, **kwargs):
            yield item
