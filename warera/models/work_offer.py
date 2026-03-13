from __future__ import annotations

from .common import WareraModel


class WorkOffer(WareraModel):
    id: str | None = None
    company_id: str | None = None
    region_id: str | None = None
    salary: float | None = None
    energy: float | None = None
    production: float | None = None
    citizenship: str | None = None
    positions: int | None = None
    filled: int | None = None
    created_at: str | None = None
