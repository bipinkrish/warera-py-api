# warera-client

A robust Python client for the [WarEra](https://warera.io) tRPC API — schema v0.24.1-beta.

```python
async with WareraClient(api_key="YOUR_KEY") as client:
    user   = await client.user.get_lite("12345")
    prices = await client.item_trading.get_prices()
    gov    = await client.government.get("7")
```

## Features

- **Full API coverage** — all 38 endpoints across 23 namespaces
- **Typed** — Pydantic v2 models for every request and response
- **Async-first** — built on `httpx.AsyncClient`; sync shim included
- **Cursor pagination** — transparent `paginate()` generator and `collect_all()` helper
- **Batch requests** — `BatchSession` for multiple procedures in one HTTP round-trip; auto-chunked `get_many` for ID lists
- **Resilient** — automatic retry with exponential backoff on 429 and 5xx errors
- **Optional auth** — `X-API-Key` gives higher rate limits; works without it too

## Installation

```bash
pip install warera-client
```

Requires Python 3.10+.

## Quick start

### Async (recommended)

```python
import asyncio
from warera import WareraClient
from warera._enums import RankingType, BattleFilter

async def main():
    # API key is optional — reads WARERA_API_KEY env var automatically
    async with WareraClient(api_key="YOUR_KEY") as client:

        # Simple lookups
        user    = await client.user.get_lite("12345")
        country = await client.country.find_by_name("Ukraine")
        gov     = await client.government.get(country.id)
        prices  = await client.item_trading.get_prices()

        print(user.username, country.name, gov.has_president())
        print(f"Iron: {prices.get('iron').price}")

        # Paginated — stream all users in a country
        async for u in client.user.paginate_by_country(country.id, limit=50):
            print(u.username)

        # Rankings
        top = await client.ranking.get(RankingType.USER_WEALTH)
        for entry in top[:5]:
            print(f"#{entry.rank} {entry.name}: {entry.value}")

asyncio.run(main())
```

### Sync

```python
from warera.sync import WareraClient

client = WareraClient(api_key="YOUR_KEY")

user    = client.user.get_lite("12345")
prices  = client.item_trading.get_prices()
battles = client.battle.get_active()   # collects all pages automatically
```

## Authentication

```python
# Option 1 — pass key directly
client = WareraClient(api_key="abc123")

# Option 2 — environment variable (recommended for scripts)
# export WARERA_API_KEY=abc123
client = WareraClient()   # key picked up automatically

# Option 3 — no key (anonymous, lower rate limits, header omitted entirely)
client = WareraClient()
```

---

## All Resource Methods

### `client.user`

```python
await client.user.get_lite(user_id: str) -> User
await client.user.get_by_country(country_id, *, limit=10, cursor=None) -> CursorPage[User]
await client.user.paginate_by_country(country_id, **kwargs)           # async generator
await client.user.collect_by_country(country_id, **kwargs) -> list[User]
await client.user.get_many(user_ids: list[str], batch_size=50) -> list[User]
```

### `client.company`

```python
await client.company.get(company_id: str) -> Company
await client.company.get_companies(*, user_id=None, per_page=10, cursor=None) -> CursorPage[Company]
await client.company.get_by_user(user_id, **kwargs) -> list[Company]
await client.company.paginate(**kwargs)                                # async generator
await client.company.get_many(company_ids: list[str], batch_size=50) -> list[Company]
```

### `client.country`

```python
await client.country.get(country_id: str) -> Country
await client.country.get_all() -> dict[str, Country]
await client.country.find_by_name(name: str) -> Country | None
client.country.invalidate_cache()           # force a fresh fetch on next find_by_name call
```

`find_by_name` caches the full country list for 10 minutes per client instance so
repeated calls do not each trigger an API round-trip. Call `invalidate_cache()` to
bypass the cache immediately.

### `client.government`

```python
await client.government.get(country_id: str) -> Government
# gov.has_president() -> bool
```

### `client.region`

```python
await client.region.get(region_id: str) -> Region
await client.region.get_all() -> dict[str, Region]
await client.region.get_many(region_ids: list[str], batch_size=50) -> list[Region]
```

### `client.battle`

```python
await client.battle.get(battle_id: str) -> Battle
await client.battle.get_live(battle_id, *, round_number=None) -> BattleLive
await client.battle.get_many(*, is_active=None, limit=10, cursor=None,
    direction=None, filter=None, defender_region_id=None,
    war_id=None, country_id=None) -> CursorPage[Battle]
await client.battle.get_active(**kwargs) -> list[Battle]
await client.battle.paginate(**kwargs)   # async generator
```

Enums: `BattleFilter.ALL / YOUR_COUNTRY / YOUR_ENEMIES`, `BattleDirection.FORWARD / BACKWARD`

`Battle.current_round` is `str | int | dict[str, Any] | None` — the API returns a plain
round ID string (e.g. `"69be5841ee1366a85052a171"`) for active battles, an integer
for some contexts, or a nested object.

### `client.battle_ranking`

```python
await client.battle_ranking.get(
    data_type: BattleRankingDataType,
    type: BattleRankingEntityType,
    side: BattleRankingSide,
    *, battle_id=None, round_id=None, war_id=None
) -> list[BattleRankingEntry]
```

Enums: `BattleRankingDataType.DAMAGE / POINTS / MONEY`,  
`BattleRankingEntityType.USER / COUNTRY / MU`,  
`BattleRankingSide.ATTACKER / DEFENDER / MERGED`

### `client.battle_order`

```python
await client.battle_order.get_by_battle(
    battle_id: str,
    side: BattleOrderSide,
) -> list[BattleOrder]
```

Enums: `BattleOrderSide.ATTACKER / DEFENDER`

### `client.round`

```python
await client.round.get(round_id: str) -> Round
await client.round.get_last_hits(round_id: str) -> list[Hit]
await client.round.get_many(round_ids: list[str], batch_size=50) -> list[Round]
```

### `client.event`

```python
await client.event.get_paginated(*, limit=10, cursor=None,
    country_id=None, event_types=None) -> CursorPage[Event]
await client.event.paginate(**kwargs)    # async generator
await client.event.collect_all(**kwargs) -> list[Event]
```

Enum: `EventType` — 21 values including `WAR_DECLARED`, `BATTLE_OPENED`, `REGION_LIBERATED`, etc.

### `client.item_trading`

```python
await client.item_trading.get_prices() -> dict[str, ItemPrice]
await client.item_trading.get_price(item_code: str) -> ItemPrice | None
await client.item_trading.get_top_orders(item_code, *, limit=10) -> list[TradingOrder]
await client.item_trading.get_offer(item_offer_id: str) -> ItemOffer
```

### `client.work_offer`

```python
await client.work_offer.get(work_offer_id: str) -> WorkOffer
await client.work_offer.get_by_company(company_id: str) -> list[WorkOffer]
await client.work_offer.get_paginated(*, limit=10, cursor=None, user_id=None,
    region_id=None, energy=None, production=None, citizenship=None) -> CursorPage[WorkOffer]
await client.work_offer.paginate(**kwargs)    # async generator
await client.work_offer.collect_all(**kwargs) -> list[WorkOffer]
```

### `client.worker`

```python
await client.worker.get_workers(*, company_id=None, user_id=None) -> list[Worker]
await client.worker.get_total_count(user_id: str) -> int
```

### `client.mu`

```python
await client.mu.get(mu_id: str) -> MilitaryUnit
await client.mu.get_paginated(*, limit=20, cursor=None, member_id=None,
    user_id=None, search=None) -> CursorPage[MilitaryUnit]
await client.mu.paginate(**kwargs)    # async generator
await client.mu.collect_all(**kwargs) -> list[MilitaryUnit]
await client.mu.get_many(mu_ids: list[str], batch_size=50) -> list[MilitaryUnit]
```

`MilitaryUnit.members` is `list[str] | None` — the API returns a list of member user ID
strings, not a count integer.

### `client.ranking`

```python
await client.ranking.get(ranking_type: RankingType) -> list[RankingEntry]
```

`RankingType` enum — 26 values:

| Category | Values |
|----------|--------|
| Country  | `WEEKLY_COUNTRY_DAMAGES` `WEEKLY_COUNTRY_DAMAGES_PER_CITIZEN` `COUNTRY_REGION_DIFF` `COUNTRY_DEVELOPMENT` `COUNTRY_ACTIVE_POPULATION` `COUNTRY_DAMAGES` `COUNTRY_WEALTH` `COUNTRY_PRODUCTION_BONUS` `COUNTRY_BOUNTY` |
| User     | `WEEKLY_USER_DAMAGES` `USER_DAMAGES` `USER_WEALTH` `USER_LEVEL` `USER_REFERRALS` `USER_SUBSCRIBERS` `USER_TERRAIN` `USER_PREMIUM_MONTHS` `USER_PREMIUM_GIFTS` `USER_CASES_OPENED` `USER_GEMS_PURCHASED` `USER_BOUNTY` |
| MU       | `MU_WEEKLY_DAMAGES` `MU_DAMAGES` `MU_TERRAIN` `MU_WEALTH` `MU_BOUNTY` |

### `client.transaction`

```python
await client.transaction.get_paginated(*, limit=10, cursor=None,
    user_id=None, mu_id=None, country_id=None, party_id=None,
    item_code=None,
    transaction_type: TransactionType | list[TransactionType] | None = None
) -> CursorPage[Transaction]
await client.transaction.paginate(**kwargs)    # async generator
await client.transaction.collect_all(**kwargs) -> list[Transaction]
```

`TransactionType`: `APPLICATION_FEE` `TRADING` `ITEM_MARKET` `WAGE` `DONATION` `ARTICLE_TIP` `OPEN_CASE` `CRAFT_ITEM` `DISMANTLE_ITEM` `BATTLE_LOOT`

### `client.upgrade`

```python
await client.upgrade.get(upgrade_type: UpgradeType, *,
    region_id=None, company_id=None, mu_id=None) -> Upgrade
```

`UpgradeType`: `BUNKER` `BASE` `PACIFICATION_CENTER` `STORAGE` `AUTOMATED_ENGINE` `BREAK_ROOM` `HEADQUARTERS` `DORMITORIES`

### `client.article`

```python
await client.article.get(article_id: str) -> Article
await client.article.get_lite(article_id: str) -> ArticleLite
await client.article.get_paginated(type: ArticleType, *, limit=10, cursor=None,
    user_id=None, categories=None, languages=None,
    positive_score_only=None) -> CursorPage[ArticleLite]
await client.article.paginate(type, **kwargs)    # async generator
await client.article.collect_all(type, **kwargs) -> list[ArticleLite]
```

`ArticleType`: `DAILY` `WEEKLY` `TOP` `MY` `SUBSCRIPTIONS` `LAST`

### `client.search`

```python
await client.search.query(search_text: str) -> SearchResults
# results.results -> list[SearchResult]  (id, type, name, image)
```

### `client.game_config`

```python
await client.game_config.get_dates() -> GameDates
await client.game_config.get() -> GameConfig
```

### `client.inventory`

```python
await client.inventory.get_equipment(user_id: str) -> list[Equipment]
```

### `client.action_log`

```python
await client.action_log.get_many(*, limit=20, cursor=None,
    user_id=None, mu_id=None, country_id=None,
    action_type: ActionLogActionType | None = None
) -> CursorPage[ActionLog]
await client.action_log.paginate(**kwargs)    # async generator
await client.action_log.get_all(**kwargs) -> list[ActionLog]
```

Enum: `ActionLogActionType` — 17 values including `SET_ORDER`, `CHANGED_USERNAME`, `INCREASE_RESISTANCE`, etc.

---

## Pagination

Every paginated endpoint has three calling patterns:

```python
# 1. Single page — manual cursor control
page = await client.battle.get_many(is_active=True, limit=20)
print(page.items)       # list[Battle]
print(page.next_cursor) # str | None
print(page.has_more)    # bool

# 2. Async generator — yields items one by one across all pages
async for battle in client.battle.paginate(is_active=True):
    print(battle.id)

# 3. Collect all into a flat list
all_battles = await client.battle.get_active()
```

---

## Batch Requests

Send multiple procedures in **one HTTP round-trip** using `BatchSession`.

### Mixed procedures

```python
async with client.batch() as batch:
    country_item = batch.add("country.getCountryById",      {"countryId": "7"})
    gov_item     = batch.add("government.getByCountryId",   {"countryId": "7"})
    prices_item  = batch.add("itemTrading.getPrices",       {})
    dates_item   = batch.add("gameConfig.getDates",         {})

# After the block — all resolved in one POST:
country = country_item.result    # raw dict (no model parsing in manual batch)
gov     = gov_item.result
prices  = prices_item.result
dates   = dates_item.result
```

### Batch-fetch many IDs (auto-chunked)

```python
# Fetches 200 companies in 4 concurrent batches of 50
companies = await client.company.get_many(company_ids)    # list[Company]
users     = await client.user.get_many(user_ids)          # list[User]
regions   = await client.region.get_many(region_ids)      # list[Region]
```

Partial failures are handled gracefully — if the server returns a 404 for individual
IDs within a batch, those entries are returned as `None` rather than raising and
dropping the entire chunk. Filter with `[u for u in users if u is not None]`.

### Partial failure handling

```python
async with client.batch() as batch:
    good = batch.add("country.getAllCountries", {})
    bad  = batch.add("company.getById", {"companyId": "nonexistent"})

print(good.ok)     # True
print(bad.ok)      # False
if not bad.ok:
    print(bad._error)   # WareraNotFoundError
```

### Wire format (for reference)

```
POST /trpc/proc0,proc1,proc2?batch=1
Content-Type: application/json
X-API-Key: <token>

{"0": {input0}, "1": {input1}, "2": {input2}}
```

---

## Error Handling

```python
from warera.exceptions import (
    WareraError,             # base — catch everything
    WareraUnauthorizedError, # 401 — bad/missing API key
    WareraForbiddenError,    # 403
    WareraNotFoundError,     # 404
    WareraRateLimitError,    # 429 — auto-retried; raised after all retries exhausted
                             #   .retry_after  → float | None  (seconds from Retry-After header)
    WareraServerError,       # 5xx — auto-retried
    WareraValidationError,   # Pydantic parse failure
    WareraBatchError,        # one or more batch items failed
                             #   .errors  → dict[int, WareraError]
                             #   .results → dict[int, Any]
)

try:
    user = await client.user.get_lite("99999")
except WareraNotFoundError:
    print("User not found")
except WareraRateLimitError as e:
    print(f"Still rate-limited after retries. Retry after: {e.retry_after}s")
except WareraError as e:
    print(f"API error: {e}")
```

---

## Configuration

```python
WareraClient(
    api_key: str | None = None,       # also reads WARERA_API_KEY env var
    base_url: str = "https://api2.warera.io/trpc",
    timeout: float = 10.0,            # seconds
    max_retries: int = 3,             # retry attempts for 429 / 5xx errors
    retry_backoff_factor: float = 0.5,# exponential backoff multiplier between retries
    batch_size: int = 50,             # default max procedures per batch POST
)
```

All parameters are applied at runtime. `max_retries` and `retry_backoff_factor` directly
control the tenacity retry policy — increasing `max_retries` will produce that many actual
retry attempts before raising.

---

## Project Structure

```
warera/
├── __init__.py          # public API surface
├── client.py            # WareraClient
├── sync.py              # sync shim
├── exceptions.py        # error hierarchy
├── _enums.py            # all StrEnum classes from schema
├── _http.py             # httpx session, GET/POST encoding, retry
├── _pagination.py       # paginate(), collect_all()
├── _batch.py            # BatchSession, BatchItem, fetch_many_by_ids
├── models/              # Pydantic response models (23 files)
└── resources/           # Resource classes (22 files)
```

---

## Development

```bash
git clone https://github.com/you/warera-client
cd warera-client
pip install -e ".[dev]"

# Unit tests (no API key needed)
pytest tests/unit/ -v

# Integration tests (live API)
WARERA_API_KEY=your_key pytest tests/integration/ -v

# Lint + type check
ruff check warera/
mypy warera/
```

---

## License

MIT
