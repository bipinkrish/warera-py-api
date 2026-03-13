from __future__ import annotations

from .._enums import RankingType
from ..models.ranking import RankingEntry
from ._base import BaseResource


class RankingResource(BaseResource):
    """
    Endpoints:
      • ranking.getRanking
    """

    async def get(self, ranking_type: RankingType | str) -> list[RankingEntry]:
        """
        Get a ranking leaderboard.

        Args:
            ranking_type: One of 25 ranking types (country, user, or MU).
                          Use the RankingType enum for tab-completion.

        Example:
            entries = await client.ranking.get(RankingType.USER_WEALTH)
            for e in entries:
                print(e.rank, e.name, e.value)
        """
        raw = await self._get("ranking.getRanking", rankingType=ranking_type)
        if isinstance(raw, list):
            return [RankingEntry.model_validate(r) for r in raw]
        if isinstance(raw, dict):
            raw_items = raw.get("items", raw.get("data", []))
            items = raw_items if isinstance(raw_items, list) else []
        else:
            items = []
        return [RankingEntry.model_validate(r) for r in items]
