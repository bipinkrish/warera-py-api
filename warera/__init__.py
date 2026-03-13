"""
warera-client — Python client for the WarEra tRPC API (v0.17.4-beta)

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
    ArticleType,
    BattleDirection,
    BattleFilter,
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
    Article,
    ArticleLite,
    Battle,
    BattleLive,
    BattleRankingEntry,
    Company,
    Country,
    CursorPage,
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
    WorkOffer,
)

__version__ = "0.1.0"

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
    "ArticleType",
    "BattleDirection",
    "BattleFilter",
    "BattleRankingDataType",
    "BattleRankingEntityType",
    "BattleRankingSide",
    "EventType",
    "RankingType",
    "TransactionType",
    "UpgradeType",
    # Models
    "Article",
    "ArticleLite",
    "Battle",
    "BattleLive",
    "BattleRankingEntry",
    "Company",
    "Country",
    "CursorPage",
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
]
