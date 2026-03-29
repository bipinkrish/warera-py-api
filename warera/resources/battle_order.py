from __future__ import annotations

from .._enums import BattleOrderSide
from ..models.battle_order import BattleOrder
from ._base import BaseResource


class BattleOrderResource(BaseResource):
    """
    Endpoints:
      • battleOrder.getByBattle
    """

    async def get_by_battle(
        self,
        battle_id: str,
        side: BattleOrderSide | str,
    ) -> list[BattleOrder]:
        """
        Get active battle orders for a specific battle and side.

        Args:
            battle_id:  The unique identifier of the battle.
            side:       Which side — attacker or defender.
        """
        raw = await self._get(
            "battleOrder.getByBattle",
            battleId=battle_id,
            side=side,
        )
        if isinstance(raw, list):
            return [BattleOrder.model_validate(r) for r in raw]
        if isinstance(raw, dict):
            raw_items = raw.get("items", raw.get("data", []))
            items = raw_items if isinstance(raw_items, list) else []
        else:
            items = []
        return [BattleOrder.model_validate(r) for r in items]
