from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from .._batch import fetch_many_by_ids
from .._pagination import collect_all, paginate
from ..models.common import CursorPage
from ..models.user import User, UserLite
from ._base import BaseResource


class UserResource(BaseResource):
    """
    Endpoints:
      • user.getUserById
      • user.getUserLite
      • user.getUsersByCountry  (cursor-paginated)
    """

    async def get_by_id(self, user_id: str) -> User:
        """Get a user's profile by ID."""
        raw = await self._get("user.getUserById", userId=user_id)
        return User.model_validate(raw)

    async def get_lite(self, user_id: str) -> UserLite:
        """Get a user's lite profile by ID. (Deprecated in favor of get_by_id)"""
        raw = await self._get("user.getUserLite", userId=user_id)
        return UserLite.model_validate(raw)

    async def get_by_country(
        self,
        country_id: str,
        *,
        limit: int = 10,
        cursor: str | None = None,
    ) -> CursorPage[UserLite]:
        """Get users belonging to a country (cursor-paginated)."""
        raw = await self._get(
            "user.getUsersByCountry",
            countryId=country_id,
            limit=limit,
            cursor=cursor,
        )
        return CursorPage.from_raw(raw, UserLite)

    # ------------------------------------------------------------------
    # Pagination helpers
    # ------------------------------------------------------------------

    async def paginate_by_country(self, country_id: str, **kwargs: Any) -> AsyncIterator[UserLite]:
        """Async generator — yields every user in a country across all pages."""
        async for item in paginate(self.get_by_country, country_id=country_id, **kwargs):
            yield item

    async def collect_by_country(self, country_id: str, **kwargs: Any) -> list[UserLite]:
        """Return all users in a country as a flat list."""
        return await collect_all(self.get_by_country, country_id=country_id, **kwargs)

    # ------------------------------------------------------------------
    # Batch helper
    # ------------------------------------------------------------------

    async def get_many(self, user_ids: list[str], batch_size: int = 50) -> list[User]:
        """
        Fetch multiple users by ID in batched POST requests.
        Returns results in the same order as `user_ids`.
        """
        raw_list = await fetch_many_by_ids(
            self._http, "user.getUserById", "userId", user_ids, batch_size
        )
        return [User.model_validate(r) for r in raw_list]
