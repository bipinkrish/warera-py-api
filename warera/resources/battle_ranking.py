from __future__ import annotations

from .._enums import BattleRankingDataType, BattleRankingEntityType, BattleRankingSide
from ..models.battle_ranking import BattleRankingEntry
from ._base import BaseResource


class BattleRankingResource(BaseResource):
    """
    Endpoints:
      • battleRanking.getRanking
    """

    async def get(
        self,
        data_type: BattleRankingDataType | str,
        type: BattleRankingEntityType | str,
        side: BattleRankingSide | str,
        *,
        battle_id: str | None = None,
        round_id: str | None = None,
        war_id: str | None = None,
    ) -> list[BattleRankingEntry]:
        """
        Get battle rankings.

        Args:
            data_type:  What to rank by — damage, points, or money.
            type:       Entity type — user, country, or mu.
            side:       Which side — attacker or defender.
            battle_id:  Optional filter by battle.
            round_id:   Optional filter by round.
            war_id:     Optional filter by war.
        """
        raw = await self._get(
            "battleRanking.getRanking",
            dataType=data_type,
            type=type,
            side=side,
            battleId=battle_id,
            roundId=round_id,
            warId=war_id,
        )
        if isinstance(raw, list):
            return [BattleRankingEntry.model_validate(r) for r in raw]
        if isinstance(raw, dict):
            raw_items = raw.get("items", raw.get("data", []))
            items = raw_items if isinstance(raw_items, list) else []
        else:
            items = []
        return [BattleRankingEntry.model_validate(r) for r in items]
