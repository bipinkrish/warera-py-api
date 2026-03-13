from __future__ import annotations

from typing import Any

from .common import WareraModel


class GameDates(WareraModel):
    next_day_at: str | None = None
    next_regen_at: str | None = None
    previous_day_at: str | None = None
    next_congress_elections_at: str | None = None
    next_presidential_elections_at: str | None = None
    next_month_at: str | None = None
    daily_mission_regen_at: str | None = None
    weekly_mission_regen_at: str | None = None
    game_day: int | None = None
    game_month: int | None = None
    game_year: int | None = None
    real_date: str | None = None
    day_duration_seconds: int | None = None


class GameConfig(WareraModel):
    """
    Full static game configuration.
    Fields are loosely typed since the exact schema is not defined in the spec.
    Raw data is accessible via model's __pydantic_extra__ or as dict via model_dump().
    """

    items: dict[str, Any] | None = None
    resources: dict[str, Any] | None = None
    industries: dict[str, Any] | None = None
    levels: list[Any] | None = None
    weapons: dict[str, Any] | None = None
    upgrades: dict[str, Any] | None = None
