from __future__ import annotations

from pydantic import AliasChoices, Field
from .common import WareraModel


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
    created_at: str | None = None
