from __future__ import annotations

from .common import WareraModel


class Transaction(WareraModel):
    id: str | None = None
    type: str | None = None
    from_id: str | None = None
    to_id: str | None = None
    amount: float | None = None
    item_code: str | None = None
    item_quantity: int | None = None
    description: str | None = None
    created_at: str | None = None
    mu_id: str | None = None
    country_id: str | None = None
    party_id: str | None = None
