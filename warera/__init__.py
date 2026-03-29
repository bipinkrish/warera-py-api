"""
warera-client — Python client for the WarEra tRPC API (v0.24.1-beta)

Quick start:
    import asyncio
    from warera import WareraClient

    async def main():
        async with WareraClient(api_key="YOUR_KEY") as client:
            user = await client.user.get_lite("12345")
            print(user.username)

    asyncio.run(main())

Sync:
    from warera.sync import WareraClient
    client = WareraClient(api_key="YOUR_KEY")
    user = client.user.get_lite("12345")
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
    Equipment,
    Event,
    GameConfig,
    GameDates,
    Government,
    Hit,
    ItemOffer,
    ItemPrice,
    MilitaryUnit,
    RankingEntry,
    Region,
    Round,
    SearchResults,
    TradingOrder,
    Transaction,
    Upgrade,
    User,
    Worker,
    WorkerCount,
    WorkOffer,
)

__version__ = "0.1.5"

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
    "Equipment",
    "Event",
    "GameConfig",
    "GameDates",
    "Government",
    "Hit",
    "ItemOffer",
    "ItemPrice",
    "MilitaryUnit",
    "RankingEntry",
    "Region",
    "Round",
    "SearchResults",
    "TradingOrder",
    "Transaction",
    "Upgrade",
    "User",
    "WorkOffer",
    "Worker",
    "WorkerCount",
]
