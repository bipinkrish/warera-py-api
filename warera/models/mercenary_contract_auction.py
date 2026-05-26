from __future__ import annotations

from pydantic import Field

from .common import WareraModel


class MercenaryContractAuctionBid(WareraModel):
    bid_at: str
    mu: str
    payout: int | float
    per_k: int | float
    user: str


class MercenaryContractAuction(WareraModel):
    v: int | None = Field(default=None, alias="__v")
    battle: str
    bids: list[MercenaryContractAuctionBid]
    budget: int | float
    country: str
    created_at: str
    created_by: str
    current_payout: int | float
    current_per_k: int | float
    current_winner: str | None = None
    current_winner_user: str | None = None
    duration: int
    expires_at: str
    for_country: str
    for_country_side: str
    initial_per_k: int | float
    minimum_damage: int | float
    professionals_only: bool
    round: str
    round_number: int
    status: str
    updated_at: str
