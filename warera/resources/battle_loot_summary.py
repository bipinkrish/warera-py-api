from __future__ import annotations

from ..models.battle_loot_summary import BattleLootSummary
from ._base import BaseResource


class BattleLootSummaryResource(BaseResource):
    """
    Endpoints:
      • battleLootSummary.getByBattleAndUser
    """

    async def get_by_battle_and_user(
        self,
        battle_id: str,
        user_id: str,
    ) -> BattleLootSummary:
        """Get the loot summary for a specific user in a specific battle."""
        raw = await self._get(
            "battleLootSummary.getByBattleAndUser",
            battleId=battle_id,
            userId=user_id,
        )
        return BattleLootSummary.model_validate(raw)
