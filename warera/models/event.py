from __future__ import annotations

from typing import Any

from .common import WareraModel


class Event(WareraModel):
    id: str | None = None
    type: str | None = None
    country_id: str | None = None
    data: dict[str, Any] | None = None
    created_at: str | None = None
    message: str | None = None
