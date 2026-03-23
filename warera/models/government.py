from __future__ import annotations

from pydantic import Field

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
    # Use default_factory so each Government instance gets its own list.
    # A bare `= []` class-level default would be shared across all instances,
    # which is a classic mutable-default bug even though Pydantic v2 copies it
    # internally — it's still inconsistent with every other list field here
    # and signals the wrong intent to readers.
    congress_members: list[str] = Field(default_factory=list)

    def has_president(self) -> bool:
        return self.president is not None
