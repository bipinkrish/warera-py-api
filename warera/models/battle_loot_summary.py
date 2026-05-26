from __future__ import annotations

from typing import Any
from .common import WareraModel


class BattleLootPoolItem(WareraModel):
    item: dict[str, Any]  # RoundWeapon
    pool: str
    rank: int
    round: str | None = None


class BattleLootSummary(WareraModel):
    v: int | None = None  # __v
    battle: str
    case1_count: int
    case2_count: int
    created_at: str
    hits: int
    pool_loot: list[BattleLootPoolItem]
    total_dmg: int
    total_money_from_bounty: int
    total_money_from_contract: int
    updated_at: str
    user: str

