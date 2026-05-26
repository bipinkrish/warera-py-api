from __future__ import annotations

from ..models.work_stats import WorkStats
from ._base import BaseResource


class WorkResource(BaseResource):
    """
    Endpoints:
      • work.getStatsByUserId
      • work.getStatsByCompany
      • work.getStatsByWorkerAndCompany
    """

    async def get_stats_by_user(
        self,
        user_id: str,
        *,
        days: int = 30,
        timezone: str = "UTC",
    ) -> list[WorkStats]:
        """
        Get daily work statistics for all companies owned by a user.

        Args:
            user_id:  The user whose work stats to retrieve.
            days:     Number of past days to include (default 30).
            timezone: IANA timezone string for grouping daily buckets (e.g. ``"Europe/Paris"``).

        Returns:
            A list of :class:`~warera.models.WorkStats` items, one per day.
        """
        raw = await self._get(
            "work.getStatsByUserId",
            userId=user_id,
            days=days,
            timezone=timezone,
        )
        return self._parse_stats_list(raw)

    async def get_stats_by_company(
        self,
        company_id: str,
        *,
        days: int = 30,
        timezone: str = "UTC",
    ) -> list[WorkStats]:
        """
        Get daily work statistics for a specific company.

        Args:
            company_id: The company to query.
            days:       Number of past days to include (default 30).
            timezone:   IANA timezone string for grouping daily buckets.

        Returns:
            A list of :class:`~warera.models.WorkStats` items, one per day.
        """
        raw = await self._get(
            "work.getStatsByCompany",
            companyId=company_id,
            days=days,
            timezone=timezone,
        )
        return self._parse_stats_list(raw)

    async def get_stats_by_worker_and_company(
        self,
        worker_id: str,
        company_id: str,
        *,
        days: int = 30,
        timezone: str = "UTC",
    ) -> list[WorkStats]:
        """
        Get daily work statistics for a specific worker at a specific company.

        Args:
            worker_id:  The worker (user) ID.
            company_id: The company ID.
            days:       Number of past days to include (default 30).
            timezone:   IANA timezone string for grouping daily buckets.

        Returns:
            A list of :class:`~warera.models.WorkStats` items, one per day.
        """
        raw = await self._get(
            "work.getStatsByWorkerAndCompany",
            workerId=worker_id,
            companyId=company_id,
            days=days,
            timezone=timezone,
        )
        return self._parse_stats_list(raw)

    @staticmethod
    def _parse_stats_list(raw: object) -> list[WorkStats]:
        if isinstance(raw, list):
            return [WorkStats.model_validate(item) for item in raw]
        if isinstance(raw, dict):
            items = raw.get("items", raw.get("data", []))
            return [
                WorkStats.model_validate(item)
                for item in (items if isinstance(items, list) else [])
            ]
        return []
