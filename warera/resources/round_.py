from __future__ import annotations

from .._batch import fetch_many_by_ids
from ..models.round_ import Hit, Round
from ._base import BaseResource


class RoundResource(BaseResource):
    """
    Endpoints:
      • round.getById
      • round.getLastHits
    """

    async def get(self, round_id: str) -> Round:
        """Get a battle round by ID."""
        raw = await self._get("round.getById", roundId=round_id)
        return Round.model_validate(raw)

    async def get_last_hits(self, round_id: str) -> list[Hit]:
        """Get the most recent hits in a battle round."""
        raw = await self._get("round.getLastHits", roundId=round_id)
        if isinstance(raw, list):
            return [Hit.model_validate(h) for h in raw]
        if isinstance(raw, dict):
            raw_items = raw.get("items", raw.get("data", []))
            items = raw_items if isinstance(raw_items, list) else []
        else:
            items = []
        return [Hit.model_validate(h) for h in items]

    async def get_many(self, round_ids: list[str], batch_size: int = 50) -> list[Round]:
        """Fetch multiple rounds by ID in batched POST requests."""
        raw_list = await fetch_many_by_ids(
            self._http, "round.getById", "roundId", round_ids, batch_size
        )
        return [Round.model_validate(r) for r in raw_list]
