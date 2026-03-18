from typing import Any

from pydantic import AliasChoices, AliasPath, Field

from .common import WareraModel


class Battle(WareraModel):
    war_id: str | None = Field(
        default=None, validation_alias=AliasChoices("war", "warId", "war_id")
    )
    region_id: str | None = Field(
        default=None, validation_alias=AliasChoices("region", "regionId", "region_id")
    )
    attacker_country_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices(AliasPath("attacker", "country"), "attacker_country_id"),
    )
    defender_country_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices(AliasPath("defender", "country"), "defender_country_id"),
    )
    attacker_score: float | None = None
    defender_score: float | None = None
    is_active: bool | None = None
    winner_country_id: str | None = Field(
        default=None, validation_alias=AliasChoices("winner_country", "winnerCountry", "winner_country_id")
    )
    start_time: str | None = None
    end_time: str | None = None
    current_round: int | dict[str, Any] | None = None
    total_rounds: int | None = None
    battle_type: str | None = None


class BattleLive(WareraModel):
    """Response from battle.getLiveBattleData."""

    battle_id: str | None = None
    round_number: int | None = None
    attacker_score: float | None = None
    defender_score: float | None = None
    attacker_damage: float | None = None
    defender_damage: float | None = None
    time_remaining: int | None = None
    is_active: bool | None = None
