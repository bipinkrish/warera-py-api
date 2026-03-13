from __future__ import annotations

from ..models.item_trading import ItemOffer, ItemPrice, TradingOrder
from ._base import BaseResource


class ItemTradingResource(BaseResource):
    """
    Endpoints:
      • itemTrading.getPrices
      • tradingOrder.getTopOrders
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

    async def get_offer(self, item_offer_id: str) -> ItemOffer:
        """Get a specific item market offer by ID."""
        raw = await self._get("itemOffer.getById", itemOfferId=item_offer_id)
        return ItemOffer.model_validate(raw)
