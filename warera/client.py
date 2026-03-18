"""
WareraClient — the single entry point for the WarEra API client library.

Async usage (recommended):
    async with WareraClient(api_key="...") as client:
        user = await client.user.get_lite("12345")

Sync usage (convenience shim):
    from warera.sync import WareraClient
    client = WareraClient(api_key="...")
    user = client.user.get_lite("12345")

No API key (anonymous, lower rate limits):
    async with WareraClient() as client:   # reads WARERA_API_KEY env var if set
        countries = await client.country.get_all()

Batch requests (one HTTP round-trip for many calls):
    async with client.batch() as batch:
        c1 = batch.add("company.getById",        {"companyId": "111"})
        c2 = batch.add("company.getById",        {"companyId": "222"})
        gov = batch.add("government.getByCountryId", {"countryId": "7"})
    print(c1.result, c2.result, gov.result)
"""

from __future__ import annotations

from typing import Any

from ._batch import BatchSession
from ._http import HttpSession
from .resources.article import ArticleResource
from .resources.battle import BattleResource
from .resources.battle_ranking import BattleRankingResource
from .resources.company import CompanyResource
from .resources.country import CountryResource
from .resources.event import EventResource
from .resources.game_config import GameConfigResource
from .resources.government import GovernmentResource
from .resources.item_trading import ItemTradingResource
from .resources.mu import MUResource
from .resources.ranking import RankingResource
from .resources.region import RegionResource
from .resources.round_ import RoundResource
from .resources.search import SearchResource
from .resources.transaction import TransactionResource
from .resources.upgrade import UpgradeResource
from .resources.user import UserResource
from .resources.work_offer import WorkOfferResource
from .resources.worker import WorkerResource

_DEFAULT_BASE_URL = "https://api2.warera.io/trpc"


class WareraClient:
    """
    Async client for the WarEra tRPC API (v0.17.4-beta).

    All resource namespaces are exposed as attributes:
        client.user          → UserResource
        client.company       → CompanyResource
        client.country       → CountryResource
        client.government    → GovernmentResource
        client.region        → RegionResource
        client.battle        → BattleResource
        client.battle_ranking→ BattleRankingResource
        client.round         → RoundResource
        client.event         → EventResource
        client.item_trading  → ItemTradingResource
        client.work_offer    → WorkOfferResource
        client.worker        → WorkerResource
        client.mu            → MUResource
        client.ranking       → RankingResource
        client.transaction   → TransactionResource
        client.upgrade       → UpgradeResource
        client.article       → ArticleResource
        client.search        → SearchResource
        client.game_config   → GameConfigResource
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str = _DEFAULT_BASE_URL,
        timeout: float = 10.0,
        max_retries: int = 3,
        retry_backoff_factor: float = 0.5,
        batch_size: int = 50,
    ) -> None:
        """
        Args:
            api_key:              X-API-Key token. If None, also checks WARERA_API_KEY
                                  environment variable. Omitting auth works but gives
                                  lower rate limits.
            base_url:             Override the API base URL (useful for testing).
            timeout:              HTTP request timeout in seconds.
            max_retries:          Max retry attempts for 429 / 5xx errors.
            retry_backoff_factor: Multiplier for exponential backoff between retries.
            batch_size:           Default max procedures per batch POST.
        """
        self._http = HttpSession(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            retry_backoff_factor=retry_backoff_factor,
        )
        self._batch_size = batch_size

        # --- Resource namespaces ---
        self.user = UserResource(self._http)
        self.company = CompanyResource(self._http)
        self.country = CountryResource(self._http)
        self.government = GovernmentResource(self._http)
        self.region = RegionResource(self._http)
        self.battle = BattleResource(self._http)
        self.battle_ranking = BattleRankingResource(self._http)
        self.round = RoundResource(self._http)
        self.event = EventResource(self._http)
        self.item_trading = ItemTradingResource(self._http)
        self.work_offer = WorkOfferResource(self._http)
        self.worker = WorkerResource(self._http)
        self.mu = MUResource(self._http)
        self.ranking = RankingResource(self._http)
        self.transaction = TransactionResource(self._http)
        self.upgrade = UpgradeResource(self._http)
        self.article = ArticleResource(self._http)
        self.search = SearchResource(self._http)
        self.game_config = GameConfigResource(self._http)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def __aenter__(self) -> WareraClient:
        await self._http.__aenter__()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self._http.__aexit__(*args)

    async def aclose(self) -> None:
        """Explicitly close the underlying HTTP session."""
        await self._http.aclose()

    # ------------------------------------------------------------------
    # Batch
    # ------------------------------------------------------------------

    def batch(self, batch_size: int | None = None) -> BatchSession:
        """
        Create a BatchSession for sending multiple procedures in one HTTP round-trip.

        Usage:
            async with client.batch() as batch:
                item_a = batch.add("company.getById",        {"companyId": "111"})
                item_b = batch.add("government.getByCountryId", {"countryId": "7"})
            # Both resolved after the block
            print(item_a.result)
            print(item_b.result)

        Args:
            batch_size: Override the client's default batch chunk size.
        """
        return BatchSession(
            http=self._http,
            batch_size=batch_size or self._batch_size,
        )

    # ------------------------------------------------------------------
    # Repr
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        has_key = bool(self._http._api_key)
        return f"WareraClient(authenticated={has_key}, base_url={self._http._base_url!r})"

    def __str__(self) -> str:
        return repr(self)
