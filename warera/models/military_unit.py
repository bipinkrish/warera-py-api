from __future__ import annotations

from .common import WareraModel


class MilitaryUnit(WareraModel):
    id: str | None = None
    name: str | None = None
    country_id: str | None = None
    owner_id: str | None = None
    members: int | None = None
    damage: float | None = None
    terrain: float | None = None
    wealth: float | None = None
    image: str | None = None
    description: str | None = None
    is_recruiting: bool | None = None
    created_at: str | None = None
