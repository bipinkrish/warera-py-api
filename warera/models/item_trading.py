from __future__ import annotations

from .common import WareraModel


class ItemPrice(WareraModel):
    item_code: str | None = None
    price: float | None = None
    quantity: int | None = None
    country_id: str | None = None
    updated_at: str | None = None


class TradingOrder(WareraModel):
    id: str | None = None
    item_code: str | None = None
    price: float | None = None
    quantity: int | None = None
    order_type: str | None = None  # "buy" | "sell"
    country_id: str | None = None
    user_id: str | None = None
    created_at: str | None = None
    expires_at: str | None = None


class ItemOffer(WareraModel):
    id: str | None = None
    item_code: str | None = None
    price: float | None = None
    quantity: int | None = None
    seller_id: str | None = None
    country_id: str | None = None
    region_id: str | None = None
    created_at: str | None = None
