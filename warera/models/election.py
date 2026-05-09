from __future__ import annotations

from pydantic import AliasChoices, BaseModel, Field

from .common import WareraModel


class ElectionCandidate(BaseModel):
    """A candidate in an election."""

    user: str | None = None
    vote_count: int | None = Field(
        default=None, validation_alias=AliasChoices("voteCount", "vote_count")
    )
    article: str | None = None
    party: str | None = None
    is_elected: bool | None = Field(
        default=None, validation_alias=AliasChoices("isElected", "is_elected")
    )


class Election(WareraModel):
    """An election event in a country."""

    country: str | None = None
    elected_candidates: list[str] | None = Field(
        default=None,
        validation_alias=AliasChoices("electedCandidates", "elected_candidates"),
    )
    is_active: bool | None = Field(
        default=None, validation_alias=AliasChoices("isActive", "is_active")
    )
    type: str | None = None
    candidates: list[ElectionCandidate] | None = None
    votes_start_at: str | None = Field(
        default=None, validation_alias=AliasChoices("votesStartAt", "votes_start_at")
    )
    votes_end_at: str | None = Field(
        default=None, validation_alias=AliasChoices("votesEndAt", "votes_end_at")
    )
    votes_count: int | None = Field(
        default=None, validation_alias=AliasChoices("votesCount", "votes_count")
    )
    elected_count: int | None = Field(
        default=None, validation_alias=AliasChoices("electedCount", "elected_count")
    )
    created_at: str | None = None
    status: str | None = None
    votes: dict[str, int] | None = None
