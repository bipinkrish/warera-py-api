from __future__ import annotations

from typing import Any

from ..models.item_trading import ItemOffer, ItemPrice, TradingOrder
from ._base import BaseResource


class PublicOrdersSummary:
    """
    Summary of all public trading orders for a country's market owner.

    Attributes:
        buy_orders:               All buy orders.
        sell_orders:              All sell orders.
        all_orders:               Combined list of buy and sell orders.
        total_buy_money_invested: Total currency committed to buy orders.
        total_sell_quantities:    Dict mapping item code → total quantity for sale.
    """

    def __init__(self, raw: dict[str, Any]) -> None:
        self.buy_orders: list[TradingOrder] = [
            TradingOrder.model_validate(o) for o in raw.get("buyOrders", [])
        ]
        self.sell_orders: list[TradingOrder] = [
            TradingOrder.model_validate(o) for o in raw.get("sellOrders", [])
        ]
        self.all_orders: list[TradingOrder] = [
            TradingOrder.model_validate(o) for o in raw.get("allOrders", [])
        ]
        self.total_buy_money_invested: float = float(raw.get("totalBuyMoneyInvested", 0))
        self.total_sell_quantities: dict[str, float] = raw.get("totalSellQuantities", {})

    def __repr__(self) -> str:
        return (
            f"PublicOrdersSummary(buy={len(self.buy_orders)}, "
            f"sell={len(self.sell_orders)}, "
            f"invested={self.total_buy_money_invested})"
        )


class ItemTradingResource(BaseResource):
    """
    Endpoints:
      • itemTrading.getPrices
      • tradingOrder.getTopOrders
      • tradingOrder.getPublicOrdersByOwner
      • itemOffer.getById
    """

    async def get_prices(self) -> dict[str, ItemPrice]:
        """
        Get current market prices for all items.
        Returns a dict keyed by item code.
        """
        raw = await self._get("itemTrading.getPrices")
        if isinstance(raw, dict):
            return {
                k: ItemPrice.model_validate(v)
                if isinstance(v, dict)
                else ItemPrice(price=float(v), item_code=k)
                for k, v in raw.items()
            }
        if isinstance(raw, list):
            prices = [ItemPrice.model_validate(p) for p in raw]
            return {p.item_code: p for p in prices if p.item_code}
        return {}

    async def get_price(self, item_code: str) -> ItemPrice | None:
        """Client-side helper: get the price for a single item."""
        prices = await self.get_prices()
        return prices.get(item_code)

    async def get_top_orders(
        self,
        item_code: str,
        *,
        limit: int = 10,
    ) -> list[TradingOrder]:
        """Get the best buy/sell orders for a given item."""
        raw = await self._get(
            "tradingOrder.getTopOrders",
            itemCode=item_code,
            limit=limit,
        )
        if isinstance(raw, list):
            return [TradingOrder.model_validate(o) for o in raw]
        if isinstance(raw, dict):
            raw_items = raw.get("items", raw.get("data", []))
            items = raw_items if isinstance(raw_items, list) else []
        else:
            items = []
        return [TradingOrder.model_validate(o) for o in items]

    async def get_public_orders_by_owner(self, country_id: str) -> PublicOrdersSummary:
        """
        Get all public trading orders for a country's market, grouped by
        buy/sell and with aggregated statistics.

        Args:
            country_id: The country whose public market orders to fetch.

        Returns:
            A :class:`PublicOrdersSummary` containing buy orders, sell orders,
            combined orders, total invested currency, and per-item sell quantities.
        """
        raw = await self._get("tradingOrder.getPublicOrdersByOwner", countryId=country_id)
        if isinstance(raw, dict):
            return PublicOrdersSummary(raw)
        return PublicOrdersSummary({})

    async def get_offer(self, item_offer_id: str) -> ItemOffer:
        """Get a specific item market offer by ID."""
        raw = await self._get("itemOffer.getById", itemOfferId=item_offer_id)
        return ItemOffer.model_validate(raw)
