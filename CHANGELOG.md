# Changelog

All notable changes to this project will be documented in this file.

## [0.1.5] — 2026-03-30

Adapts the SDK to WarEra API **v0.24.1-beta**.

### Added
- **`BattleRankingSide.MERGED`** — new `"merged"` enum value for the merged battle rankings that combine attacker + defender into a single list.
- **`TransactionType.BATTLE_LOOT`** — new `"battleLoot"` transaction type for the revamped battle loot system.
- **`BattleOrderSide`** enum — `attacker` / `defender` for the new battle-order endpoint.
- **`ActionLogActionType`** enum — all 17 action types (orders, mercenary contracts, citizenship changes, resistance, missions, etc.).
- **`BattleOrderResource`** (`client.battle_order`) — wraps `battleOrder.getByBattle`.
- **`InventoryResource`** (`client.inventory`) — wraps `inventory.fetchCurrentEquipment`.
- **`ActionLogResource`** (`client.action_log`) — wraps `actionLog.getPaginated` with cursor-pagination helpers.
- **`BattleOrder`**, **`Equipment`**, **`ActionLog`** models.
- Sync shim support for all three new resources.

### Changed
- API version references updated from `v0.17.4-beta` to `v0.24.1-beta`.

## [0.1.4]

Initial tracked release.
