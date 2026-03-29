from __future__ import annotations

from typing import Any

from .common import WareraModel


class BattleOrder(WareraModel):
    """A battle order placed by a military unit for a specific battle and side."""

    battle_id: str | None = None
    side: str | None = None
    mu_id: str | None = None
    mu_name: str | None = None
    country_id: str | None = None
    details: dict[str, Any] | None = None
