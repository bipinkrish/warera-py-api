from __future__ import annotations

from ..models.inventory import Equipment
from ._base import BaseResource


class InventoryResource(BaseResource):
    """
    Endpoints:
      • inventory.fetchCurrentEquipment
    """

    async def get_equipment(self, user_id: str) -> list[Equipment]:
        """
        Get the currently equipped items for a user.

        Args:
            user_id: The unique identifier of the user.
        """
        raw = await self._get(
            "inventory.fetchCurrentEquipment",
            userId=user_id,
        )
        if isinstance(raw, list):
            return [Equipment.model_validate(r) for r in raw]
        if isinstance(raw, dict):
            # Could be a single item or wrapped list
            raw_items = raw.get("items", raw.get("data", None))
            if isinstance(raw_items, list):
                return [Equipment.model_validate(r) for r in raw_items]
            # Single equipment object — wrap in list
            return [Equipment.model_validate(raw)]
        return []
