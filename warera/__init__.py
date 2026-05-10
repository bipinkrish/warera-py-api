"""
warera-client — Python client for the WarEra tRPC API

Quick start:
    import asyncio
    from warera import WareraClient

    async def main():
        async with WareraClient(api_key="YOUR_KEY") as client:
            user = await client.user.get_by_id("12345")
            print(user.username)

    asyncio.run(main())

Sync:
    from warera.sync import WareraClient
    client = WareraClient(api_key="YOUR_KEY")
    user = client.user.get_by_id("12345")
"""

from ._enums import (
    ActionLogActionType,
    ArticleType,
    BattleDirection,
    BattleFilter,
    BattleOrderSide,
    BattleRankingDataType,
    BattleRankingEntityType,
    BattleRankingSide,
    EventType,
    RankingType,
    TransactionType,
    UpgradeType,
)
from .client import WareraClient
from .exceptions import (
    WareraBatchError,
    WareraError,
    WareraForbiddenError,
    WareraHTTPError,
    WareraNotFoundError,
    WareraRateLimitError,
    WareraServerError,
    WareraUnauthorizedError,
    WareraValidationError,
)
from .models import (
    ActionLog,
    Article,
    ArticleLite,
    Battle,
    BattleLive,
    BattleOrder,
    BattleRankingEntry,
    Company,
    Country,
    CursorPage,
    Donation,
    DonationTotals,
    Election,
    ElectionCandidate,
    Equipment,
    Event,
    GameConfig,
    GameDates,
    Government,
    Hit,
    ItemOffer,
    ItemPrice,
    MilitaryUnit,
    MuMember,
    Party,
    PartyEthics,
    RankingEntry,
    Region,
    Round,
    SearchResults,
    TradingOrder,
    Transaction,
    Upgrade,
    User,
    UserLite,
    Worker,
    WorkerCount,
    WorkOffer,
    WorkStats,
)

__version__ = "0.2.0"

__all__ = [
    # Client
    "WareraClient",
    # Exceptions
    "WareraError",
    "WareraHTTPError",
    "WareraUnauthorizedError",
    "WareraForbiddenError",
    "WareraNotFoundError",
    "WareraRateLimitError",
    "WareraServerError",
    "WareraValidationError",
    "WareraBatchError",
    # Enums
    "ActionLogActionType",
    "ArticleType",
    "BattleDirection",
    "BattleFilter",
    "BattleOrderSide",
    "BattleRankingDataType",
    "BattleRankingEntityType",
    "BattleRankingSide",
    "EventType",
    "RankingType",
    "TransactionType",
    "UpgradeType",
    # Models
    "ActionLog",
    "Article",
    "ArticleLite",
    "Battle",
    "BattleLive",
    "BattleOrder",
    "BattleRankingEntry",
    "Company",
    "Country",
    "CursorPage",
    "Donation",
    "DonationTotals",
    "Election",
    "ElectionCandidate",
    "Equipment",
    "Event",
    "GameConfig",
    "GameDates",
    "Government",
    "Hit",
    "ItemOffer",
    "ItemPrice",
    "MilitaryUnit",
    "MuMember",
    "Party",
    "PartyEthics",
    "RankingEntry",
    "Region",
    "Round",
    "SearchResults",
    "TradingOrder",
    "Transaction",
    "Upgrade",
    "User",
    "UserLite",
    "WorkOffer",
    "WorkStats",
    "Worker",
    "WorkerCount",
]
