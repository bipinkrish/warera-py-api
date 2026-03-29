from __future__ import annotations

from typing import Any

from .common import WareraModel


class Equipment(WareraModel):
    """
    A single equipped item returned by inventory.fetchCurrentEquipment.

    Fields are loosely typed since the exact response schema is not defined
    in the API spec.  Raw data is always accessible via model's
    ``__pydantic_extra__`` or ``model_dump()``.
    """

    slot: str | None = None
    item_id: str | None = None
    item_code: str | None = None
    name: str | None = None
    rarity: str | None = None
    stats: dict[str, Any] | None = None
