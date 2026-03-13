from pydantic import AliasChoices, Field

from .common import WareraModel


class RankingEntry(WareraModel):
    rank: int | None = None
    entity_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices("user", "country", "mu", "entityId", "entity_id"),
    )
    name: str | None = None
    country_id: str | None = None
    value: float | None = None
    image: str | None = None
