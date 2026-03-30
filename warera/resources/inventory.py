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
            
            # If the data is mapped by slot (e.g. {"weapon": {...}, "helmet": {...}})
            actual_data = raw_items if raw_items is not None else raw
            if isinstance(actual_data, dict):
                equipments = []
                for slot_name, item_data in actual_data.items():
                    if isinstance(item_data, dict):
                        mapped = {"slot": slot_name, **item_data}
                        if "code" in item_data and "item_code" not in item_data:
                            mapped["item_code"] = item_data["code"]
                        if "name" not in item_data and "code" in item_data:
                            mapped["name"] = item_data["code"]
                        equipments.append(Equipment.model_validate(mapped))
                    elif isinstance(item_data, str):
                        equipments.append(Equipment.model_validate({
                            "slot": slot_name,
                            "item_code": item_data,
                            "name": item_data
                        }))
                return equipments

            # Single equipment object — wrap in list
            return [Equipment.model_validate(raw)]
        return []
