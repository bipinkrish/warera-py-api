from __future__ import annotations

from .common import WareraModel


class Company(WareraModel):
    id: str | None = None
    name: str | None = None
    owner_id: str | None = None
    country_id: str | None = None
    region_id: str | None = None
    type: str | None = None
    quality: int | None = None
    size: int | None = None
    employees: int | None = None
    production: float | None = None
    wealth: float | None = None
    image: str | None = None
    is_hiring: bool | None = None
    created_at: str | None = None
