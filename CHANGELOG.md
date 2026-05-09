# Changelog

## [0.2.0] — 2026-05-09

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
