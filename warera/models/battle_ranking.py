from __future__ import annotations

from .common import WareraModel


class BattleRankingEntry(WareraModel):
    rank: int | None = None
    entity_id: str | None = None
    entity_type: str | None = None  # "user" | "country" | "mu"
    name: str | None = None
    country_id: str | None = None
    value: float | None = None  # damage / points / money depending on dataType
    side: str | None = None  # "attacker" | "defender"
