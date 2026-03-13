from __future__ import annotations

from .common import WareraModel


class Round(WareraModel):
    id: str | None = None
    battle_id: str | None = None
    round_number: int | None = None
    attacker_score: float | None = None
    defender_score: float | None = None
    attacker_damage: float | None = None
    defender_damage: float | None = None
    winner_side: str | None = None
    start_time: str | None = None
    end_time: str | None = None


class Hit(WareraModel):
    """A single hit entry from round.getLastHits."""

    user_id: str | None = None
    country_id: str | None = None
    mu_id: str | None = None
    side: str | None = None
    damage: float | None = None
    weapon: str | None = None
    timestamp: str | None = None
