from __future__ import annotations

from typing import Any

from .common import WareraModel


class Region(WareraModel):
    id: str | None = None
    name: str | None = None
    original_country_id: str | None = None
    owner_country_id: str | None = None
    population: int | None = None
    hospital: int | None = None
    defense_system: int | None = None
    is_capital: bool | None = None
    resources: list[str] = []
    coordinates: dict[str, Any] | None = None
