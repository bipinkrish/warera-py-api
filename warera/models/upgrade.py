from __future__ import annotations

from .common import WareraModel


class Upgrade(WareraModel):
    id: str | None = None
    type: str | None = None
    level: int | None = None
    entity_id: str | None = None
    entity_type: str | None = None  # "region" | "company" | "mu"
    region_id: str | None = None
    company_id: str | None = None
    mu_id: str | None = None
    max_level: int | None = None
    cost: float | None = None
    built_at: str | None = None
