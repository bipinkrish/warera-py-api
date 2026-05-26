from __future__ import annotations

from typing import Any

from pydantic import AliasChoices, Field

from .common import WareraModel


class CompanyDates(WareraModel):
    pass


class CompanyActiveUpgradeLevels(WareraModel):
    pass


class Company(WareraModel):
    id: str | None = None
    name: str | None = None
    owner_id: str | None = Field(
        default=None, validation_alias=AliasChoices("owner", "ownerId", "owner_id")
    )
    country_id: str | None = Field(
        default=None, validation_alias=AliasChoices("country", "countryId", "country_id")
    )
    region_id: str | None = Field(
        default=None, validation_alias=AliasChoices("region", "regionId", "region_id")
    )
    type: str | None = None
    quality: int | None = None
    size: int | None = None
    employees: int | None = None
    production: float | None = None
    wealth: float | None = None
    image: str | None = None
    is_hiring: bool | None = None
    active_upgrade_levels: CompanyActiveUpgradeLevels | None = None
    concrete_invested: int | float | None = None
    dates: CompanyDates | None = None
    estimated_value: int | float | None = None
    is_full: bool | None = None
    item_code: str | None = None
    moved_up_at: str | None = None
    region: str | None = None
    user: str | None = None
    worker_count: int | None = None
    workers: list[Any] | None = None
    created_at: str | None = None
    updated_at: str | None = None
