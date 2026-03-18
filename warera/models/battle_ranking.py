from __future__ import annotations

from pydantic import AliasChoices, Field
from .common import WareraModel


class BattleRankingEntry(WareraModel):
    rank: int | None = None
    entity_id: str | None = Field(
        default=None, validation_alias=AliasChoices("user", "country", "mu", "entityId", "entity_id")
    )
    entity_type: str | None = None  # "user" | "country" | "mu"
    name: str | None = None
    country_id: str | None = Field(
        default=None, validation_alias=AliasChoices("country", "countryId", "country_id")
    )
    value: float | None = None  # damage / points / money depending on dataType
    side: str | None = None  # "attacker" | "defender"
