from __future__ import annotations

from .common import WareraModel


class User(WareraModel):
    username: str | None = None
    country_id: str | None = None
    level: int | None = None
    wealth: float | None = None
    military_unit_id: str | None = None
    party_id: str | None = None
    avatar: str | None = None
    is_premium: bool | None = None
    created_at: str | None = None
    last_online: str | None = None
    division: int | None = None
    experience: float | None = None
    prestige: float | None = None
    strength: float | None = None
    endurance: float | None = None
    damage: float | None = None
    terrain: float | None = None
    referral_code: str | None = None
    region_id: str | None = None
