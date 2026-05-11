from __future__ import annotations

from pydantic import AliasChoices, Field

from .common import WareraModel


class Donation(WareraModel):
    """A donation made to a military unit, country, or party."""

    user_id: str | None = Field(
        default=None, validation_alias=AliasChoices("userId", "user_id")
    )
    mu_id: str | None = Field(
        default=None, validation_alias=AliasChoices("muId", "mu_id")
    )
    country_id: str | None = Field(
        default=None, validation_alias=AliasChoices("countryId", "country_id")
    )
    party_id: str | None = Field(
        default=None, validation_alias=AliasChoices("partyId", "party_id")
    )
    amount: float | None = None
    created_at: str | None = None
    updated_at: str | None = None


class DonationTotals(WareraModel):
    """Aggregate donation totals for a target."""

    total_amount: float | None = None
    donor_count: int | None = None
