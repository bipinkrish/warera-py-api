from __future__ import annotations

from ..models.mu_member import MuMember
from ._base import BaseResource


class MuMemberResource(BaseResource):
    """
    Endpoints:
      • muMember.getByMu
    """

    async def get_by_mu(self, mu_id: str) -> list[MuMember]:
        """
        Get all members and their activity statistics for a military unit.

        Args:
            mu_id: The military unit ID.

        Returns:
            A list of :class:`~warera.models.MuMember` objects.
        """
        raw = await self._get("muMember.getByMu", muId=mu_id)
        if isinstance(raw, list):
            return [MuMember.model_validate(m) for m in raw]
        if isinstance(raw, dict):
            items = raw.get("items", raw.get("data", []))
            return [MuMember.model_validate(m) for m in (items if isinstance(items, list) else [])]
        return []
