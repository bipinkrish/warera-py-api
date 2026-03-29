from __future__ import annotations

from typing import Any

from .common import WareraModel


class ActionLog(WareraModel):
    """A single action log entry from actionLog.getPaginated."""

    user_id: str | None = None
    mu_id: str | None = None
    country_id: str | None = None
    action_type: str | None = None
    timestamp: str | None = None
    details: dict[str, Any] | None = None
