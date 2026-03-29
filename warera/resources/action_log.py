from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from .._enums import ActionLogActionType
from .._pagination import collect_all, paginate
from ..models.action_log import ActionLog
from ..models.common import CursorPage
from ._base import BaseResource


class ActionLogResource(BaseResource):
    """
    Endpoints:
      • actionLog.getPaginated  (cursor-paginated)
    """

    async def get_many(
        self,
        *,
        limit: int = 20,
        cursor: str | None = None,
        user_id: str | None = None,
        mu_id: str | None = None,
        country_id: str | None = None,
        action_type: ActionLogActionType | str | None = None,
    ) -> CursorPage[ActionLog]:
        """
        Get paginated action logs with optional filtering.

        Args:
            limit:       Number of results per page (1-100, default 20).
            cursor:      Pagination cursor for the next page.
            user_id:     Filter by user ID.
            mu_id:       Filter by military unit ID.
            country_id:  Filter by country ID.
            action_type: Filter by action type.
        """
        raw = await self._get(
            "actionLog.getPaginated",
            limit=limit,
            cursor=cursor,
            userId=user_id,
            muId=mu_id,
            countryId=country_id,
            actionType=action_type,
        )
        return CursorPage.from_raw(raw, ActionLog)

    async def get_all(self, **kwargs: Any) -> list[ActionLog]:
        """Convenience: collect all action logs matching the given filters."""
        return await collect_all(self.get_many, **kwargs)

    # ------------------------------------------------------------------
    # Pagination helpers
    # ------------------------------------------------------------------

    async def paginate(self, **kwargs: Any) -> AsyncIterator[ActionLog]:
        """Async generator over action logs matching the given filters."""
        async for item in paginate(self.get_many, **kwargs):
            yield item
