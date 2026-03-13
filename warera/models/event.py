from __future__ import annotations

from .common import WareraModel


class Event(WareraModel):
    id: str | None = None
    type: str | None = None
    country_id: str | None = None
    data: dict | None = None
    created_at: str | None = None
    message: str | None = None
