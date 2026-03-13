from __future__ import annotations

from ..models.game_config import GameConfig, GameDates
from ._base import BaseResource


class GameConfigResource(BaseResource):
    """
    Endpoints:
      • gameConfig.getDates
      • gameConfig.getGameConfig
    """

    async def get_dates(self) -> GameDates:
        """Get current in-game date information."""
        raw = await self._get("gameConfig.getDates")
        return GameDates.model_validate(raw)

    async def get(self) -> GameConfig:
        """Get the full static game configuration (items, resources, industries, etc.)."""
        raw = await self._get("gameConfig.getGameConfig")
        return GameConfig.model_validate(raw)
