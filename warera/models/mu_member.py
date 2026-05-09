from __future__ import annotations

from pydantic import AliasChoices, Field

from .common import WareraModel


class MuMember(WareraModel):
    """Membership and activity stats for a user within a military unit."""

    mu: str | None = None
    user: str | None = None
    total_damages_count: int | None = Field(
        default=None,
        validation_alias=AliasChoices("totalDamagesCount", "total_damages_count"),
    )
    monthly_damages_count: int | None = Field(
        default=None,
        validation_alias=AliasChoices("monthlyDamagesCount", "monthly_damages_count"),
    )
    weekly_damages_count: int | None = Field(
        default=None,
        validation_alias=AliasChoices("weeklyDamagesCount", "weekly_damages_count"),
    )
    total_help_count: int | None = Field(
        default=None,
        validation_alias=AliasChoices("totalHelpCount", "total_help_count"),
    )
    monthly_help_count: int | None = Field(
        default=None,
        validation_alias=AliasChoices("monthlyHelpCount", "monthly_help_count"),
    )
    weekly_help_count: int | None = Field(
        default=None,
        validation_alias=AliasChoices("weeklyHelpCount", "weekly_help_count"),
    )
    created_at: str | None = None
    updated_at: str | None = None
