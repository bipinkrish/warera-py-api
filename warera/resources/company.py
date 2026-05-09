from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from .._batch import fetch_many_by_ids
from .._pagination import collect_all, paginate
from ..models.common import CursorPage
from ..models.company import Company
from ._base import BaseResource


class CompanyProductionBonus:
    """Production bonus breakdown for a company."""

    __slots__ = (
        "strategic_bonus",
        "deposit_bonus",
        "ethic_specialization_bonus",
        "ethic_deposit_bonus",
        "total",
    )

    def __init__(
        self,
        strategic_bonus: float,
        deposit_bonus: float,
        ethic_specialization_bonus: float,
        ethic_deposit_bonus: float,
        total: float,
    ) -> None:
        self.strategic_bonus = strategic_bonus
        self.deposit_bonus = deposit_bonus
        self.ethic_specialization_bonus = ethic_specialization_bonus
        self.ethic_deposit_bonus = ethic_deposit_bonus
        self.total = total

    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> "CompanyProductionBonus":
        return cls(
            strategic_bonus=float(raw.get("strategicBonus", 0)),
            deposit_bonus=float(raw.get("depositBonus", 0)),
            ethic_specialization_bonus=float(raw.get("ethicSpecializationBonus", 0)),
            ethic_deposit_bonus=float(raw.get("ethicDepositBonus", 0)),
            total=float(raw.get("total", 0)),
        )

    def __repr__(self) -> str:
        return (
            f"CompanyProductionBonus(total={self.total}, strategic={self.strategic_bonus}, "
            f"deposit={self.deposit_bonus})"
        )


class RecommendedRegion:
    """A recommended region for production of a given item."""

    __slots__ = (
        "region_id",
        "bonus",
        "deposit_bonus",
        "ethic_deposit_bonus",
        "strategic_bonus",
        "ethic_specialization_bonus",
        "tax_percent",
        "deposit_end_at",
        "item_code",
    )

    def __init__(self, raw: dict[str, Any]) -> None:
        self.region_id: str = raw.get("regionId", "")
        self.bonus: float = float(raw.get("bonus", 0))
        self.deposit_bonus: float = float(raw.get("depositBonus", 0))
        self.ethic_deposit_bonus: float = float(raw.get("ethicDepositBonus", 0))
        self.strategic_bonus: float = float(raw.get("strategicBonus", 0))
        self.ethic_specialization_bonus: float = float(raw.get("ethicSpecializationBonus", 0))
        self.tax_percent: float = float(raw.get("taxPercent", 0))
        self.deposit_end_at: str | None = raw.get("depositEndAt")
        self.item_code: str | None = raw.get("itemCode")

    def __repr__(self) -> str:
        return f"RecommendedRegion(region_id={self.region_id!r}, bonus={self.bonus})"


class CompanyResource(BaseResource):
    """
    Endpoints:
      • company.getById
      • company.getCompanies                      (cursor-paginated, filter by userId)
      • company.getRecommendedRegionIdsByItemCode
      • company.getProductionBonus
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

    async def get_recommended_regions(
        self,
        item_code: str,
        *,
        include_deposit: bool = True,
    ) -> list[RecommendedRegion]:
        """
        Get recommended regions for producing a given item, ranked by total bonus.

        Args:
            item_code:       Item code to check (e.g. ``"iron"``, ``"weapon_q1"``).
            include_deposit: Whether to include deposit bonuses in the ranking.

        Returns:
            A list of :class:`RecommendedRegion` objects sorted by bonus (best first).
        """
        raw = await self._get(
            "company.getRecommendedRegionIdsByItemCode",
            itemCode=item_code,
            includeDeposit=include_deposit,
        )
        if isinstance(raw, list):
            return [RecommendedRegion(r) for r in raw]
        if isinstance(raw, dict):
            items = raw.get("items", raw.get("data", []))
            return [RecommendedRegion(r) for r in (items if isinstance(items, list) else [])]
        return []

    async def get_production_bonus(self, company_id: str) -> CompanyProductionBonus:
        """
        Get the full production bonus breakdown for a company.

        Returns a :class:`CompanyProductionBonus` with ``strategic_bonus``,
        ``deposit_bonus``, ``ethic_specialization_bonus``, ``ethic_deposit_bonus``,
        and ``total``.
        """
        raw = await self._get("company.getProductionBonus", companyId=company_id)
        if isinstance(raw, dict):
            return CompanyProductionBonus.from_raw(raw)
        return CompanyProductionBonus.from_raw({})

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
