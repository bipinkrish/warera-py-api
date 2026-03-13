from __future__ import annotations

from .common import WareraModel


class Worker(WareraModel):
    user_id: str | None = None
    company_id: str | None = None
    salary: float | None = None
    started_at: str | None = None


class WorkerCount(WareraModel):
    user_id: str | None = None
    total: int | None = None
