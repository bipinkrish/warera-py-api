from __future__ import annotations

from typing import Any
from pydantic import Field
from .common import WareraModel


class TournamentMatch(WareraModel):
    attacker: str
    defender: str
    is_qualification_round: bool
    battle: str


class TournamentRound(WareraModel):
    round_number: int
    cases: int
    skill_value: int | float | None = None
    is_qualification_round: bool
    matches: list[TournamentMatch]


class TournamentRegistered(WareraModel):
    countries: list[str]
    mus: list[str]
    users: list[str]


class Tournament(WareraModel):
    v: int | None = Field(default=None, alias="__v")
    name: str
    description: str | None = None
    is_active: bool
    status: str
    start_at: str
    team_size: int
    team_count: int
    rounds_count: int
    type: str
    max_rarity: str
    skill_key: str
    auto_qualify1st_round: list[str] = Field(default_factory=list, alias="autoQualify1stRound")
    registered: TournamentRegistered
    active_round: int
    rounds: dict[str, TournamentRound]
    created_at: str
    updated_at: str


class TournamentTeam(WareraModel):
    v: int | None = Field(default=None, alias="__v")
    tournament: str
    number: int
    countries: list[str]
    mus: list[str]
    users: list[str]
    participants: list[str]
    color_scheme: str
    estimated_users: int
    status: str
    created_at: str
    updated_at: str
