from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from .._enums import EventType
from .._pagination import collect_all, paginate
from ..models.common import CursorPage
from ..models.event import Event
from ._base import BaseResource


class EventResource(BaseResource):
    """
    Endpoints:
      • event.getEventsPaginated  (cursor-paginated)
    """

    async def get_paginated(
        self,
        *,
        limit: int = 10,
        cursor: str | None = None,
        country_id: str | None = None,
        event_types: list[EventType | str] | None = None,
    ) -> CursorPage[Event]:
        """Get game events, optionally filtered by country and/or event type."""
        raw = await self._get(
            "event.getEventsPaginated",
            limit=limit,
            cursor=cursor,
            countryId=country_id,
            eventTypes=event_types,
        )
        return CursorPage.from_raw(raw, Event)

    async def paginate(self, **kwargs: Any) -> AsyncIterator[Event]:
        """Async generator over all events matching the given filters."""
        async for item in paginate(self.get_paginated, **kwargs):
            yield item

    async def collect_all(self, **kwargs: Any) -> list[Event]:
        """Collect all events across all pages into a flat list."""
        return await collect_all(self.get_paginated, **kwargs)
