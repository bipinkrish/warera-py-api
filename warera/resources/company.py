from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from .._batch import fetch_many_by_ids
from .._pagination import collect_all, paginate
from ..models.common import CursorPage
from ..models.company import Company
from ._base import BaseResource


class CompanyResource(BaseResource):
    """
    Endpoints:
      • company.getById
      • company.getCompanies  (cursor-paginated, filter by userId)
    """

    async def get(self, company_id: str) -> Company:
        """Get a single company by ID."""
        raw = await self._get("company.getById", companyId=company_id)
        return Company.model_validate(raw)

    async def get_companies(
        self,
        *,
        user_id: str | None = None,
        per_page: int = 10,
        cursor: str | None = None,
    ) -> CursorPage[Company]:
        """Get companies, optionally filtered by owner user ID (cursor-paginated)."""
        raw = await self._get(
            "company.getCompanies",
            userId=user_id,
            perPage=per_page,
            cursor=cursor,
        )
        return CursorPage.from_raw(raw, Company)

    async def get_by_user(self, user_id: str, **kwargs: Any) -> list[Company]:
        """Convenience: fetch all companies owned by a user (collects all pages)."""
        return await collect_all(self.get_companies, user_id=user_id, **kwargs)

    # ------------------------------------------------------------------
    # Pagination helpers
    # ------------------------------------------------------------------

    async def paginate(self, **kwargs: Any) -> AsyncIterator[Company]:
        """Async generator over all companies matching the given filters."""
        async for item in paginate(self.get_companies, **kwargs):
            yield item

    # ------------------------------------------------------------------
    # Batch helper
    # ------------------------------------------------------------------

    async def get_many(self, company_ids: list[str], batch_size: int = 50) -> list[Company]:
        """Fetch multiple companies by ID in batched POST requests."""
        raw_list = await fetch_many_by_ids(
            self._http, "company.getById", "companyId", company_ids, batch_size
        )
        return [Company.model_validate(r) for r in raw_list]
