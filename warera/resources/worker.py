from __future__ import annotations
from ..models.worker import Worker, WorkerCount
from ._base import BaseResource


class WorkerResource(BaseResource):
    """
    Endpoints:
      • worker.getWorkers
      • worker.getTotalWorkersCount
    """

    async def get_workers(
        self,
        *,
        company_id: str | None = None,
        user_id: str | None = None,
    ) -> list[Worker]:
        """
        Get workers, optionally filtered by company or user.
        At least one of company_id or user_id should be provided.
        """
        raw = await self._get(
            "worker.getWorkers",
            companyId=company_id,
            userId=user_id,
        )
        if isinstance(raw, list):
            return [Worker.model_validate(w) for w in raw]
        items = raw.get("items", raw.get("data", [])) if isinstance(raw, dict) else []
        return [Worker.model_validate(w) for w in items]

    async def get_total_count(self, user_id: str) -> int:
        """Get the total number of workers employed by a user across all their companies."""
        raw = await self._get("worker.getTotalWorkersCount", userId=user_id)
        if isinstance(raw, dict):
            return raw.get("total", raw.get("count", 0))
        if isinstance(raw, int):
            return raw
        return 0
