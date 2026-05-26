# Warera Python Client

[![PyPI version](https://badge.fury.io/py/warera-client.svg)](https://pypi.org/project/warera-client/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> A robust, fully-typed, async-first Python client for the [WarEra](https://warera.io) tRPC API (v0.24.5-beta).

```python
async with WareraClient(api_key="YOUR_KEY") as client:
    user   = await client.user.get_by_id("12345")
    prices = await client.item_trading.get_prices()
    gov    = await client.government.get("7")
```

## Features

- **Full API coverage** — all endpoints across 32 resource namespaces.
- **Fully Typed** — Pydantic v2 models for *every* request and response.
- **Async-first** — built on `httpx.AsyncClient`; sync shim included.
- **Cursor pagination** — transparent `paginate()` generator and `collect_all()` helper.
- **Batch requests** — `BatchSession` for multiple procedures in one HTTP round-trip; auto-chunked `get_many` for ID lists.
- **Smart batch splitting** — any batch larger than the server's hard limit of 50 is automatically split and fired concurrently; no manual chunking needed.
- **Adaptive rate limiting** — reads `ratelimit-remaining` / `ratelimit-reset` response headers and sleeps exactly as long as the server says.
- **Resilient** — automatic retry with exponential backoff on 429 and 5xx errors.
- **Optional auth** — `X-API-Key` gives higher rate limits; works anonymously too.

## Installation

```bash
pip install warera-client
```

Requires Python 3.10+.

---

## Quick Start

### Async (recommended)

```python
import asyncio
from warera import WareraClient

async def main():
    # API key is optional - also reads WARERA_API_KEY env var
    async with WareraClient(api_key="YOUR_KEY") as client:

        # Simple lookups
        user    = await client.user.get_by_id("12345")
        country = await client.country.find_by_name("Ukraine")
        gov     = await client.government.get(country.id)
        prices  = await client.item_trading.get_prices()

        print(user.username, country.name)
        print(f"Iron: {prices.get('iron').price}")

        # Paginated - stream all users in a country
        async for u in client.user.paginate_by_country(country.id, limit=50):
            print(u.username)

asyncio.run(main())
```

### Sync

```python
from warera.sync import WareraClient

client = WareraClient(api_key="YOUR_KEY")
user    = client.user.get_by_id("12345")
prices  = client.item_trading.get_prices()
battles = client.battle.get_active()   # collects all pages automatically
```

---

## Authentication

```python
# Option 1 - pass key directly
client = WareraClient(api_key="abc123")

# Option 2 - environment variable (recommended for scripts/CI)
# export WARERA_API_KEY=abc123
client = WareraClient()   # key picked up automatically

# Option 3 - no key (anonymous, lower rate limits)
client = WareraClient()
```

---

## Rate Limiting

> [!NOTE]
> The client dynamically reads the rate-limit headers the API attaches to **every** response (`ratelimit-limit`, `ratelimit-remaining`, `ratelimit-reset`).
> 
> When `ratelimit-remaining` reaches `0`, the client automatically sleeps for exactly `ratelimit-reset` seconds before the next request. No hardcoded delays, no guessing! If the server changes its policy, the client adapts automatically.

You can inspect the current quota at any time via `client.rate_limit_remaining` and
`client.rate_limit_total` (both return `None` until the first response is received):

```python
async with WareraClient(api_key="YOUR_KEY") as client:
    await client.user.get_by_id("1")
    print(client.rate_limit_remaining)  # e.g. 499
    print(client.rate_limit_total)      # e.g. 500
```

---

## All Resource Methods

Each section follows this layout: **method signatures** → **enums** (if any) → **model fields** (if any) → **example** (if any).

### `client.user`

```python
await client.user.get_by_id(user_id: str) -> User
await client.user.get_by_country(country_id, *, limit=10, cursor=None) -> CursorPage[User]
await client.user.paginate_by_country(country_id, **kwargs)            # async generator
await client.user.collect_by_country(country_id, **kwargs) -> list[User]
await client.user.get_many(user_ids: list[str], batch_size=50) -> list[User]
```

### `client.company`

```python
await client.company.get(company_id: str) -> Company
await client.company.get_companies(*, user_id=None, per_page=10, cursor=None) -> CursorPage[Company]
await client.company.get_by_user(user_id, **kwargs) -> list[Company]
await client.company.paginate(**kwargs)                                 # async generator
await client.company.get_many(company_ids: list[str], batch_size=50) -> list[Company]
await client.company.get_recommended_regions(item_code, *, include_deposit=True) -> list[RecommendedRegion]
await client.company.get_production_bonus(company_id: str) -> CompanyProductionBonus
```

<details><summary><b><code>RecommendedRegion</code></b> fields</summary>
<code>region_id</code>, <code>bonus</code>, <code>deposit_bonus</code>, <code>ethic_deposit_bonus</code>, <code>strategic_bonus</code>, <code>ethic_specialization_bonus</code>, <code>tax_percent</code>, <code>deposit_end_at</code>, <code>item_code</code>
</details>

<details><summary><b><code>CompanyProductionBonus</code></b> fields</summary>
<code>strategic_bonus</code>, <code>deposit_bonus</code>, <code>ethic_specialization_bonus</code>, <code>ethic_deposit_bonus</code>, <code>total</code>
</details>

```python
regions = await client.company.get_recommended_regions("iron", include_deposit=True)
for r in regions:
    print(f"Region {r.region_id}: total bonus {r.bonus:.0%}, tax {r.tax_percent}%")

bonus = await client.company.get_production_bonus("my_company_id")
print(f"Total production bonus: {bonus.total:.0%}")
```

### `client.country`

```python
await client.country.get(country_id: str) -> Country
await client.country.get_all() -> dict[str, Country]
await client.country.find_by_name(name: str) -> Country | None   # case-insensitive, cached 10 min
client.country.invalidate_cache()                                 # synchronous, clears the cache
```

### `client.government`

```python
await client.government.get(country_id: str) -> Government
```

### `client.party`

```python
await client.party.get(party_id: str) -> Party
await client.party.get_paginated(*, country_id=None, limit=20, cursor=None, direction=None) -> CursorPage[Party]
await client.party.get_by_country(country_id: str) -> list[Party]
await client.party.collect_all(**kwargs) -> list[Party]
await client.party.paginate(**kwargs)                              # async generator
```

<details><summary><b><code>Party</code></b> fields</summary>
<code>id</code>, <code>name</code>, <code>description</code>, <code>country</code>, <code>country_id</code>, <code>region</code>, <code>region_id</code>, <code>leader</code>, <code>leader_id</code>, <code>council_members</code>, <code>members</code>, <code>ethics</code> (<code>PartyEthics</code>), <code>avatar_url</code>, <code>treasurer</code>, <code>primary_winner</code>, <code>created_at</code>, <code>updated_at</code>
</details>

<details><summary><b><code>PartyEthics</code></b> fields</summary>
<code>militarism</code>, <code>isolationism</code>, <code>imperialism</code>, <code>industrialism</code> (all <code>float</code>)
</details>

```python
parties = await client.party.get_by_country("7")
for p in parties:
    print(p.name, p.ethics.militarism if p.ethics else "")
```

### `client.donation`

```python
await client.donation.get_paginated(*, mu_id=None, country_id=None, party_id=None,
    limit=20, cursor=None, direction=None) -> CursorPage[Donation]
await client.donation.get_totals(*, mu_id=None, country_id=None, party_id=None) -> DonationTotals
await client.donation.collect_all(**kwargs) -> list[Donation]
await client.donation.paginate(**kwargs)                           # async generator
```

<details><summary><b><code>DonationTotals</code></b> fields</summary>
<code>total_amount</code> (float), <code>donor_count</code> (int)
</details>

```python
totals = await client.donation.get_totals(mu_id="my_mu_id")
print(f"{totals.donor_count} donors, {totals.total_amount} total")
```

### `client.election`

```python
await client.election.get_paginated(*, country_id=None, limit=20, cursor=None, direction=None) -> CursorPage[Election]
await client.election.get_by_country(country_id: str) -> list[Election]
await client.election.collect_all(**kwargs) -> list[Election]
await client.election.paginate(**kwargs)                           # async generator
```

<details><summary><b><code>Election</code></b> fields</summary>
<code>id</code>, <code>country</code>, <code>elected_candidates</code>, <code>is_active</code>, <code>type</code>, <code>candidates</code> (list of <code>ElectionCandidate</code>), <code>votes_start_at</code>, <code>votes_end_at</code>, <code>votes_count</code>, <code>elected_count</code>, <code>created_at</code>, <code>status</code>, <code>votes</code> (dict)
</details>

<details><summary><b><code>ElectionCandidate</code></b> fields</summary>
<code>user</code>, <code>vote_count</code>, <code>article</code>, <code>party</code>, <code>is_elected</code>
</details>

```python
elections = await client.election.get_by_country("7")
for e in elections:
    winner = next((c for c in (e.candidates or []) if c.is_elected), None)
    print(f"{e.type}: winner={winner.user if winner else 'TBD'}, votes={e.votes_count}")
```

### `client.game_stat`

```python
await client.game_stat.get_equipment_avg(item_code: str) -> float
```

Returns the average quality/stat value for the given equipment item code (e.g. `"sword"`, `"helmet"`).

```python
avg = await client.game_stat.get_equipment_avg("sword")
print(f"Average sword quality: {avg:.1f}")
```

### `client.mu_member`

```python
await client.mu_member.get_by_mu(mu_id: str) -> list[MuMember]
```

<details><summary><b><code>MuMember</code></b> fields</summary>
<code>id</code>, <code>mu</code>, <code>user</code>, <code>total_damages_count</code>, <code>monthly_damages_count</code>, <code>weekly_damages_count</code>, <code>total_help_count</code>, <code>monthly_help_count</code>, <code>weekly_help_count</code>, <code>created_at</code>, <code>updated_at</code>
</details>

```python
members = await client.mu_member.get_by_mu("my_mu_id")
top = sorted(members, key=lambda m: m.weekly_damages_count or 0, reverse=True)
for m in top[:5]:
    print(f"User {m.user}: {m.weekly_damages_count} weekly dmg")
```

### `client.work`

```python
await client.work.get_stats_by_user(user_id, *, days=30, timezone="UTC") -> list[WorkStats]
await client.work.get_stats_by_company(company_id, *, days=30, timezone="UTC") -> list[WorkStats]
await client.work.get_stats_by_worker_and_company(worker_id, company_id, *, days=30, timezone="UTC") -> list[WorkStats]
```

`timezone` accepts any IANA timezone string (e.g. `"Europe/Paris"`). Daily buckets are grouped in that timezone so midnight boundaries align correctly.

<details><summary><b><code>WorkStats</code></b> fields</summary>
<code>daily_date</code> (str), <code>total</code>, <code>wage</code>, <code>employee_prod</code>, <code>self_work</code>, <code>automated_engine</code> (all float)
</details>

```python
stats = await client.work.get_stats_by_company("my_company_id", days=7, timezone="UTC")
for day in stats:
    print(f"{day.daily_date}: total={day.total:.0f}, wage={day.wage:.2f}")
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
await client.battle.get_many(*, is_active=None, limit=10, cursor=None, direction=None,
    filter=None, defender_region_id=None, war_id=None, country_id=None) -> CursorPage[Battle]
await client.battle.get_active(**kwargs) -> list[Battle]
await client.battle.paginate(**kwargs)                             # async generator
```

`BattleFilter` - `ALL` `YOUR_COUNTRY` `YOUR_ENEMIES`

`BattleDirection` - `FORWARD` `BACKWARD`

### `client.battle_ranking`

```python
await client.battle_ranking.get(
    data_type: BattleRankingDataType,
    type: BattleRankingEntityType,
    side: BattleRankingSide,
    *, battle_id=None, round_id=None, war_id=None
) -> list[BattleRankingEntry]
```

`BattleRankingDataType` - `DAMAGE` `POINTS` `MONEY`

`BattleRankingEntityType` - `USER` `COUNTRY` `MU`

`BattleRankingSide` - `ATTACKER` `DEFENDER` `MERGED`

### `client.battle_order`

```python
await client.battle_order.get_by_battle(battle_id: str, side: BattleOrderSide) -> list[BattleOrder]
```

`BattleOrderSide` - `ATTACKER` `DEFENDER`

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
await client.event.paginate(**kwargs)                              # async generator
await client.event.collect_all(**kwargs) -> list[Event]
```

`EventType` - 21 values:

| Category | Values |
|---|---|
| War & Peace | `WAR_DECLARED` `PEACE_AGREEMENT` `PEACE_MADE` `ALLIANCE_FORMED` `ALLIANCE_BROKEN` |
| Battle | `BATTLE_OPENED` `BATTLE_ENDED` |
| Territory | `REGION_TRANSFER` `REGION_LIBERATED` `STRATEGIC_RESOURCES_RESHUFFLED` |
| Politics | `NEW_PRESIDENT` `SYSTEM_REVOLT` `REVOLUTION_STARTED` `REVOLUTION_ENDED` `FINANCED_REVOLT` |
| Resistance | `RESISTANCE_INCREASED` `RESISTANCE_DECREASED` |
| Economy | `COUNTRY_MONEY_TRANSFER` `DEPOSIT_DISCOVERED` `DEPOSIT_DEPLETED` `BANKRUPTCY` |

### `client.item_trading`

```python
await client.item_trading.get_prices() -> dict[str, ItemPrice]
await client.item_trading.get_price(item_code: str) -> ItemPrice | None
await client.item_trading.get_top_orders(item_code, *, limit=10) -> list[TradingOrder]
await client.item_trading.get_offer(item_offer_id: str) -> ItemOffer
await client.item_trading.get_public_orders_by_owner(country_id: str) -> PublicOrdersSummary
```

<details><summary><b><code>PublicOrdersSummary</code></b> fields</summary>
<code>buy_orders</code> (list), <code>sell_orders</code> (list), <code>all_orders</code> (list), <code>total_buy_money_invested</code> (float), <code>total_sell_quantities</code> (dict[str, float])
</details>

```python
summary = await client.item_trading.get_public_orders_by_owner("7")
print(f"{len(summary.buy_orders)} buy orders, {len(summary.sell_orders)} sell orders")
print(f"Total capital in buy orders: {summary.total_buy_money_invested:.2f}")
```

### `client.work_offer`

```python
await client.work_offer.get(work_offer_id: str) -> WorkOffer
await client.work_offer.get_by_company(company_id: str) -> list[WorkOffer]
await client.work_offer.get_paginated(*, limit=10, cursor=None, user_id=None,
    region_id=None, energy=None, production=None, citizenship=None) -> CursorPage[WorkOffer]
await client.work_offer.paginate(**kwargs)                         # async generator
await client.work_offer.collect_all(**kwargs) -> list[WorkOffer]
await client.work_offer.get_wage_stats(*, energy, production, citizenship) -> WageStats
```

<details><summary><b><code>WageStats</code></b> fields</summary>
<code>allowed_range</code> (<code>WageRange</code>: <code>min</code>, <code>max</code>, <code>average</code>), <code>top_offer</code> (float), <code>top_eligible_offer</code> (float), <code>top_eligible_offers</code> (list)
</details>

```python
stats = await client.work_offer.get_wage_stats(
    energy=100.0,
    production=0.85,
    citizenship="7",
)
print(f"Best eligible offer: {stats.top_eligible_offer}")
print(f"Allowed wage range: {stats.allowed_range.min} – {stats.allowed_range.max}")
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
await client.mu.paginate(**kwargs)                                 # async generator
await client.mu.collect_all(**kwargs) -> list[MilitaryUnit]
await client.mu.get_many(mu_ids: list[str], batch_size=50) -> list[MilitaryUnit]
```

`MilitaryUnit.members` is `list[str] | None` - member user ID strings.

### `client.ranking`

```python
await client.ranking.get(ranking_type: RankingType) -> list[RankingEntry]
```

`RankingType` - 26 values:

| Category | Values |
|---|---|
| Country | `WEEKLY_COUNTRY_DAMAGES` `WEEKLY_COUNTRY_DAMAGES_PER_CITIZEN` `COUNTRY_REGION_DIFF` `COUNTRY_DEVELOPMENT` `COUNTRY_ACTIVE_POPULATION` `COUNTRY_DAMAGES` `COUNTRY_WEALTH` `COUNTRY_PRODUCTION_BONUS` `COUNTRY_BOUNTY` |
| User | `WEEKLY_USER_DAMAGES` `USER_DAMAGES` `USER_WEALTH` `USER_LEVEL` `USER_REFERRALS` `USER_SUBSCRIBERS` `USER_TERRAIN` `USER_PREMIUM_MONTHS` `USER_PREMIUM_GIFTS` `USER_CASES_OPENED` `USER_GEMS_PURCHASED` `USER_BOUNTY` |
| MU | `MU_WEEKLY_DAMAGES` `MU_DAMAGES` `MU_TERRAIN` `MU_WEALTH` `MU_BOUNTY` |

### `client.transaction`

```python
await client.transaction.get_paginated(*, limit=10, cursor=None,
    user_id=None, mu_id=None, country_id=None, party_id=None,
    item_code=None,
    transaction_type: TransactionType | list[TransactionType] | None = None
) -> CursorPage[Transaction]
await client.transaction.paginate(**kwargs)                        # async generator
await client.transaction.collect_all(**kwargs) -> list[Transaction]
```

`TransactionType` - `APPLICATION_FEE` `TRADING` `ITEM_MARKET` `WAGE` `DONATION` `ARTICLE_TIP` `OPEN_CASE` `CRAFT_ITEM` `DISMANTLE_ITEM` `BATTLE_LOOT`

### `client.upgrade`

```python
await client.upgrade.get(upgrade_type: UpgradeType, *,
    region_id=None, company_id=None, mu_id=None) -> Upgrade
```

`UpgradeType` - `BUNKER` `BASE` `PACIFICATION_CENTER` `STORAGE` `AUTOMATED_ENGINE` `BREAK_ROOM` `HEADQUARTERS` `DORMITORIES`

### `client.article`

```python
await client.article.get(article_id: str) -> Article
await client.article.get_lite(article_id: str) -> ArticleLite
await client.article.get_paginated(type: ArticleType, *, limit=10, cursor=None,
    user_id=None, categories=None, languages=None,
    positive_score_only=None) -> CursorPage[ArticleLite]
await client.article.paginate(type, **kwargs)                      # async generator
await client.article.collect_all(type, **kwargs) -> list[ArticleLite]
```

`ArticleType` - `DAILY` `WEEKLY` `TOP` `MY` `SUBSCRIPTIONS` `LAST`

### `client.search`

```python
await client.search.query(search_text: str) -> SearchResults
```

`SearchResults.results` is a `list[SearchResult]` with fields `id`, `type`, `name`, `image`.

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
await client.action_log.paginate(**kwargs)                         # async generator
await client.action_log.get_all(**kwargs) -> list[ActionLog]
```

`ActionLogActionType` - 17 values:

| Category | Values |
|---|---|
| Orders | `SET_ORDER` `UNSET_ORDER` `UPDATE_ORDER` |
| Mercenary contracts | `SET_MERCENARY_CONTRACTS` `REMOVE_MERCENARY_CONTRACT` `CREATE_MERCENARY_CONTRACT_PROPOSAL` `CANCEL_MERCENARY_CONTRACT_PROPOSAL` `ACCEPT_MERCENARY_CONTRACT` `CANCEL_MERCENARY_CONTRACT` `COMPLETE_MERCENARY_CONTRACT` |
| Profile | `CHANGED_USERNAME` `CHANGED_CITIZENSHIP` `CHANGED_DESCRIPTION` |
| Resistance | `INCREASE_RESISTANCE` `DECREASE_RESISTANCE` |
| Missions | `CLAIM_MISSION_XP` `CLAIM_FINISHED_MISSION_XP` |

### `client.battle_loot_summary`

```python
await client.battle_loot_summary.get_by_battle_and_user(battle_id: str, user_id: str) -> BattleLootSummary
```

### `client.mercenary_contract_auction`

```python
await client.mercenary_contract_auction.get_paginated_auctions(*, country_id=None, battle_id=None, status=None, limit=10, cursor=None) -> CursorPage[MercenaryContractAuction]
await client.mercenary_contract_auction.paginate(**kwargs)                         # async generator
await client.mercenary_contract_auction.collect_all(**kwargs) -> list[MercenaryContractAuction]
```

### `client.tournament`

```python
await client.tournament.get_last_tournament() -> Tournament
await client.tournament.get_team_by_id(tournament_team_id: str) -> TournamentTeam
await client.tournament.get_teams_by_tournament(tournament_id: str) -> list[TournamentTeam]
```

---

## Pagination

Every paginated endpoint exposes three calling patterns:

```python
# 1. Single page - manual cursor control
page = await client.battle.get_many(is_active=True, limit=20)
print(page.items)        # list[Battle]
print(page.next_cursor)  # str | None
print(page.has_more)     # bool

# 2. Async generator - yields items one by one across all pages
async for battle in client.battle.paginate(is_active=True):
    print(battle.id)

# 3. Collect all pages into a flat list
all_battles = await client.battle.get_active()
```

---

## Batch Requests

> [!TIP]
> The server enforces a hard limit of **50 procedures per batch POST**. The client handles this automatically at every level:

| What you call | What happens |
|---|---|
| `client.batch()` with ≤ 50 items | One POST |
| `client.batch()` with > 50 items | Auto-split into ≤ 50-item chunks, fired concurrently |
| `client.company.get_many(200_ids)` | 4 × 50-item POSTs, results merged in order |
| `session._http.post_batch(120_procs, ...)` | Auto-split internally, 3 × concurrent POSTs |

You never need to think about the limit - just pass what you need.

### Mixed procedures

```python
async with client.batch() as batch:
    country_item = batch.add("country.getCountryById",    {"countryId": "7"})
    gov_item     = batch.add("government.getByCountryId", {"countryId": "7"})
    prices_item  = batch.add("itemTrading.getPrices",     {})
    dates_item   = batch.add("gameConfig.getDates",       {})

# After the block - all resolved in one POST:
country = country_item.result
gov     = gov_item.result
prices  = prices_item.result
dates   = dates_item.result
```

### Large batches

```python
# 200 company IDs → 4 concurrent POSTs of 50, results merged
companies = await client.company.get_many(list_of_200_ids)

# Same for any resource with get_many
users   = await client.user.get_many(user_ids)     # list[User]
regions = await client.region.get_many(region_ids)  # list[Region]
rounds  = await client.round.get_many(round_ids)    # list[Round]
mus     = await client.mu.get_many(mu_ids)          # list[MilitaryUnit]
```

### Partial failure handling

```python
async with client.batch() as batch:
    good = batch.add("country.getAllCountries", {})
    bad  = batch.add("company.getById", {"companyId": "nonexistent"})

print(good.ok)     # True
print(bad.ok)      # False
if not bad.ok:
    print(bad._error)  # WareraNotFoundError
```

### Wire format (for reference)

```
POST /trpc/proc0,proc1,...,proc49?batch=1
Content-Type: application/json
X-API-Key: <token>

{"0": {input0}, "1": {input1}, ..., "49": {input49}}
```

---

## Error Handling

```python
from warera.exceptions import (
    WareraError,             # base - catch everything
    WareraUnauthorizedError, # 401 - bad/missing API key
    WareraForbiddenError,    # 403
    WareraNotFoundError,     # 404
    WareraRateLimitError,    # 429 - auto-retried; raised after all retries exhausted
                             #   .retry_after → float | None  (seconds from Retry-After header)
    WareraServerError,       # 5xx - auto-retried
    WareraValidationError,   # Pydantic parse failure
    WareraBatchError,        # one or more batch items failed
                             #   .errors  → dict[int, WareraError]
                             #   .results → dict[int, Any]
)

try:
    user = await client.user.get_by_id("99999")
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
    api_key: str | None = None,        # also reads WARERA_API_KEY env var
    base_url: str = "https://api2.warera.io/trpc",
    timeout: float = 10.0,             # HTTP request timeout in seconds
    max_retries: int = 3,              # retry attempts for 429 / 5xx errors
    retry_backoff_factor: float = 0.5, # exponential backoff multiplier
    batch_size: int = 50,              # max procedures per batch POST chunk
                                       # values above 50 are silently clamped
                                       # to the server's hard limit
)
```

---

## Project Structure

```
warera/
├── __init__.py          # public API surface
├── client.py            # WareraClient
├── sync.py              # sync shim
├── exceptions.py        # error hierarchy
├── _enums.py            # all StrEnum classes from schema
├── _http.py             # httpx session, GET/POST, rate-limit headers, retry
├── _pagination.py       # paginate(), collect_all()
├── _batch.py            # BatchSession, BatchItem, fetch_many_by_ids
├── models/              # Pydantic response models (31 files)
└── resources/           # Resource classes (32 files)
```

---

## Development

```bash
git clone https://github.com/bipinkrish/warera-py-api
cd warera-py-api
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

---

## Credits

- **Bipin Krishnan (`bipinkrish` / `Bipin`)**: Initial architecture, core client implementation, rate-limiting foundations, and testing frameworks.
- **PAIN (`PAIN「ᴀᴋᴀᴛsᴜᴋɪ」` / `CrucifiedPain`)**: Comprehensive expansion of Pydantic schemas, API parity updates, documentation overhauls, and feature additions.
- **[WarEraProjects](https://github.com/wareraprojects/trpc)**: Instrumental in reverse-engineering undocumented API endpoints and the batch-request wire protocol.
- **[Kore-rep](https://github.com/Kore-rep)**: Suggested the implementation of the adaptive rate-limiting engine.
