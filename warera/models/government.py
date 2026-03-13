from __future__ import annotations

from .common import WareraModel


class GovernmentMember(WareraModel):
    user_id: str | None = None
    role: str | None = None
    party_id: str | None = None


class Government(WareraModel):
    country_id: str | None = None
    president: str | None = None
    vice_president: str | None = None
    min_of_defense: str | None = None
    min_of_economy: str | None = None
    min_of_foreign_affairs: str | None = None
    congress_members: list[str] = []  # API returns a list of user IDs

    def has_president(self) -> bool:
        return self.president is not None
