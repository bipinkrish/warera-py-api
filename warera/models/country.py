from __future__ import annotations

from .common import WareraModel


class Country(WareraModel):
    name: str | None = None
    code: str | None = None
    flag: str | None = None
    color: str | None = None
    currency: str | None = None
    wealth: float | None = None
    population: int | None = None
    regions: int | None = None
    ruling_party: str | None = None
    president_id: str | None = None
    alliance_id: str | None = None
    is_occupied: bool | None = None
    capital_region_id: str | None = None
