# Changelog

## [0.1.9] — 2026-05-26

### New endpoints (1:1 Parity with TypeScript Client)

**BattleLootSummary**
- `client.battle_loot_summary.get_by_battle_and_user(battle_id, user_id)` — `battleLootSummary.getByBattleAndUser`

**MercenaryContractAuction**
- `client.mercenary_contract_auction.get_paginated_auctions(...)` — `mercenaryContractAuction.getPaginatedAuctions`
- `client.mercenary_contract_auction.collect_all(...)` / `client.mercenary_contract_auction.paginate(...)` — full autopagination helpers

**Tournament**
- `client.tournament.get_last_tournament()` — `tournament.getLastTournament`
- `client.tournament.get_team_by_id(tournament_team_id)` — `tournamentTeam.getById`
- `client.tournament.get_teams_by_tournament(tournament_id)` — `tournamentTeam.getByTournamentId`

### Synchronized Pydantic Models
Massive update to sync all existing models with the latest TRPC schema. Added all missing properties (fully backwards compatible, leveraging `extra="allow"`):
- **Article**: Added `author`, `is_deleted`, `is_published`, `published_at`, `stats`.
- **Company**: Added `active_upgrade_levels`, `concrete_invested`, `dates`, `estimated_value`, `is_full`, `item_code`, `moved_up_at`, `region`, `updated_at`, `user`, `worker_count`, `workers`.
- **Government**: Added `country`.
- **Item Trading**: Added `offer_at`, `type`, `user` to `TradingOrder` and `ItemOffer`.
- **Military Unit**: Added `active_upgrade_levels`, `avatar_url`, `rankings`, `region`, `roles`, `updated_at`, `user`.
- **Party**: Added `country`, `leader`, `region`.
- **Transaction**: Added `updated_at`, `user_id`.
- **User**: Massive update adding all progression and state tracking objects: `infos`, `skills`, `UserDates.last_citizenship_change_at`, `UserLiteDates.last_taking_control_at`, `UserRankings` (gems, premium tracking), `UserEquipment.weapon`, `available_color_schemes`, `equipped_skin_keys`, `finished_tours`, `should_update_profile`.

## [0.1.8] — 2026-05-10

### New endpoints (from TRPC wrapper)

**Party**
- `client.party.get(party_id)` — `party.getById`
- `client.party.get_paginated(country_id, ...)` — `party.getManyPaginated`
- `client.party.collect_all(...)` / `client.party.paginate(...)` — full autopagination helpers
- `client.party.get_by_country(country_id)` — convenience shortcut

**Donation**
- `client.donation.get_paginated(mu_id, country_id, party_id, ...)` — `donation.getManyPaginated`
- `client.donation.get_totals(mu_id, country_id, party_id)` — `donation.getTotalDonations`
- `client.donation.collect_all(...)` / `client.donation.paginate(...)` — full autopagination helpers

**Election**
- `client.election.get_paginated(country_id, ...)` — `election.getElections`
- `client.election.collect_all(...)` / `client.election.paginate(...)` — full autopagination helpers
- `client.election.get_by_country(country_id)` — convenience shortcut

**GameStat**
- `client.game_stat.get_equipment_avg(item_code)` — `gameStat.getEquipmentAvgByCode`

**MuMember**
- `client.mu_member.get_by_mu(mu_id)` — `muMember.getByMu`

**Work** (new namespace)
- `client.work.get_stats_by_user(user_id, days, timezone)` — `work.getStatsByUserId`
- `client.work.get_stats_by_company(company_id, days, timezone)` — `work.getStatsByCompany`
- `client.work.get_stats_by_worker_and_company(worker_id, company_id, days, timezone)` — `work.getStatsByWorkerAndCompany`

**Company** (extended)
- `client.company.get_recommended_regions(item_code, include_deposit)` — `company.getRecommendedRegionIdsByItemCode`
- `client.company.get_production_bonus(company_id)` — `company.getProductionBonus`

**WorkOffer** (extended)
- `client.work_offer.get_wage_stats(energy, production, citizenship)` — `workOffer.getWageStats`

**ItemTrading** (extended)
- `client.item_trading.get_public_orders_by_owner(country_id)` — `tradingOrder.getPublicOrdersByOwner`

### New models
- `Party`, `PartyEthics`
- `Donation`, `DonationTotals`
- `Election`, `ElectionCandidate`
- `WorkStats`
- `MuMember`

### Rate-limit header support (screenshot feature)
Instead of a hardcoded delay, the HTTP session now reads the server's own
rate-limit response headers (`ratelimit-limit`, `ratelimit-remaining`,
`ratelimit-reset`) after every request and automatically sleeps for exactly
as long as the server reports before the next request when the quota reaches
zero. This means the client self-adapts to any future changes the server
makes to its rate-limit policy — no code changes needed.

Two read-only properties are exposed on `WareraClient` for introspection:
- `client.rate_limit_remaining` — requests left in the current window
- `client.rate_limit_total` — total requests per window

### Tests
- New test file `tests/unit/test_new_resources.py` covering all new resources
- New rate-limit header tests in `tests/unit/test_http.py`

## [0.1.7] — previous release
