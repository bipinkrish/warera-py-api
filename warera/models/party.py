from __future__ import annotations

from pydantic import AliasChoices, Field

from .common import WareraModel


class PartyEthics(WareraModel):
    """Ethics alignment values for a political party."""

    militarism: float | None = None
    isolationism: float | None = None
    imperialism: float | None = None
    industrialism: float | None = None


class Party(WareraModel):
    """A political party in WarEra."""

    name: str | None = None
    description: str | None = None
    country: str | None = None
    country_id: str | None = Field(
        default=None, validation_alias=AliasChoices("country", "countryId", "country_id")
    )
    region: str | None = None
    region_id: str | None = Field(
        default=None, validation_alias=AliasChoices("region", "regionId", "region_id")
    )
    leader: str | None = None
    leader_id: str | None = Field(
        default=None, validation_alias=AliasChoices("leader", "leaderId", "leader_id")
    )
    council_members: list[str] | None = None
    members: list[str] | None = None
    ethics: PartyEthics | None = None
    avatar_url: str | None = None
    treasurer: str | None = None
    primary_winner: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
