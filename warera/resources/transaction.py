from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from .._enums import TransactionType
from .._pagination import collect_all, paginate
from ..models.common import CursorPage
from ..models.transaction import Transaction
from ._base import BaseResource


class TransactionResource(BaseResource):
    """
    Endpoints:
      • transaction.getPaginatedTransactions  (cursor-paginated)
    """

    async def get_paginated(
        self,
        *,
        limit: int = 10,
        cursor: str | None = None,
        user_id: str | None = None,
        mu_id: str | None = None,
        country_id: str | None = None,
        party_id: str | None = None,
        item_code: str | None = None,
        transaction_type: TransactionType | str | list[TransactionType | str] | None = None,
    ) -> CursorPage[Transaction]:
        """
        Get paginated transactions with optional filters.

        `transaction_type` uniquely accepts a single type string OR a list — both are
        valid per the API schema. When a list is passed it is serialised as-is.
        """
        raw = await self._get(
            "transaction.getPaginatedTransactions",
            limit=limit,
            cursor=cursor,
            userId=user_id,
            muId=mu_id,
            countryId=country_id,
            partyId=party_id,
            itemCode=item_code,
            transactionType=transaction_type,
        )
        return CursorPage.from_raw(raw, Transaction)

    async def paginate(self, **kwargs: Any) -> AsyncIterator[Transaction]:
        """Async generator over all transactions matching the given filters."""
        async for item in paginate(self.get_paginated, **kwargs):
            yield item

    async def collect_all(self, **kwargs: Any) -> list[Transaction]:
        """Collect all matching transactions across all pages (use with care on large datasets)."""
        return await collect_all(self.get_paginated, **kwargs)
