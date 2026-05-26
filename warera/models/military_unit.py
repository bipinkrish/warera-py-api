from __future__ import annotations

from .common import WareraModel


class MuActiveUpgradeLevels(WareraModel):
    pass


class MuRankings(WareraModel):
    pass


class MuRoles(WareraModel):
    pass


class MilitaryUnit(WareraModel):
    id: str | None = None
    name: str | None = None
    country_id: str | None = None
    owner_id: str | None = None
    members: list[str] | None = None  # API returns a list of member user ID strings
    damage: float | None = None
    terrain: float | None = None
    wealth: float | None = None
    image: str | None = None
    description: str | None = None
    is_recruiting: bool | None = None
    active_upgrade_levels: MuActiveUpgradeLevels | None = None
    avatar_url: str | None = None
    rankings: MuRankings | None = None
    region: str | None = None
    roles: MuRoles | None = None
    user: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
