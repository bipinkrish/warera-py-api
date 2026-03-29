"""
All StrEnum classes derived directly from the WarEra API schema v0.24.1-beta.
Import from here to get tab-completion and typo safety on enum values.
"""

from __future__ import annotations

import enum

# Use StrEnum from enum if available (Python 3.11+), otherwise fallback
if hasattr(enum, "StrEnum"):
    from enum import StrEnum  # type: ignore[attr-defined]
else:

    class StrEnum(str, enum.Enum):  # type: ignore[no-redef]
        """Fallback for Python < 3.11."""

        def __str__(self) -> str:
            return str(self.value)


class ArticleType(StrEnum):  # type: ignore[misc]
    DAILY = "daily"
    WEEKLY = "weekly"
    TOP = "top"
    MY = "my"
    SUBSCRIPTIONS = "subscriptions"
    LAST = "last"


# ---------------------------------------------------------------------------
# Battle
# ---------------------------------------------------------------------------


class BattleDirection(StrEnum):  # type: ignore[misc]
    FORWARD = "forward"
    BACKWARD = "backward"


class BattleFilter(StrEnum):  # type: ignore[misc]
    ALL = "all"
    YOUR_COUNTRY = "yourCountry"
    YOUR_ENEMIES = "yourEnemies"


# ---------------------------------------------------------------------------
# Battle Ranking
# ---------------------------------------------------------------------------


class BattleRankingDataType(StrEnum):  # type: ignore[misc]
    DAMAGE = "damage"
    POINTS = "points"
    MONEY = "money"


class BattleRankingEntityType(StrEnum):  # type: ignore[misc]
    USER = "user"
    COUNTRY = "country"
    MU = "mu"


class BattleRankingSide(StrEnum):  # type: ignore[misc]
    ATTACKER = "attacker"
    DEFENDER = "defender"
    MERGED = "merged"


# ---------------------------------------------------------------------------
# Event
# ---------------------------------------------------------------------------


class EventType(StrEnum):  # type: ignore[misc]
    WAR_DECLARED = "warDeclared"
    PEACE_AGREEMENT = "peace_agreement"
    BATTLE_OPENED = "battleOpened"
    BATTLE_ENDED = "battleEnded"
    NEW_PRESIDENT = "newPresident"
    REGION_TRANSFER = "regionTransfer"
    PEACE_MADE = "peaceMade"
    COUNTRY_MONEY_TRANSFER = "countryMoneyTransfer"
    DEPOSIT_DISCOVERED = "depositDiscovered"
    DEPOSIT_DEPLETED = "depositDepleted"
    SYSTEM_REVOLT = "systemRevolt"
    BANKRUPTCY = "bankruptcy"
    ALLIANCE_FORMED = "allianceFormed"
    ALLIANCE_BROKEN = "allianceBroken"
    REGION_LIBERATED = "regionLiberated"
    STRATEGIC_RESOURCES_RESHUFFLED = "strategicResourcesReshuffled"
    RESISTANCE_INCREASED = "resistanceIncreased"
    RESISTANCE_DECREASED = "resistanceDecreased"
    REVOLUTION_STARTED = "revolutionStarted"
    REVOLUTION_ENDED = "revolutionEnded"
    FINANCED_REVOLT = "financedRevolt"


# ---------------------------------------------------------------------------
# Ranking
# ---------------------------------------------------------------------------


class RankingType(StrEnum):  # type: ignore[misc]
    # Country rankings
    WEEKLY_COUNTRY_DAMAGES = "weeklyCountryDamages"
    WEEKLY_COUNTRY_DAMAGES_PER_CITIZEN = "weeklyCountryDamagesPerCitizen"
    COUNTRY_REGION_DIFF = "countryRegionDiff"
    COUNTRY_DEVELOPMENT = "countryDevelopment"
    COUNTRY_ACTIVE_POPULATION = "countryActivePopulation"
    COUNTRY_DAMAGES = "countryDamages"
    COUNTRY_WEALTH = "countryWealth"
    COUNTRY_PRODUCTION_BONUS = "countryProductionBonus"
    COUNTRY_BOUNTY = "countryBounty"

    # User rankings
    WEEKLY_USER_DAMAGES = "weeklyUserDamages"
    USER_DAMAGES = "userDamages"
    USER_WEALTH = "userWealth"
    USER_LEVEL = "userLevel"
    USER_REFERRALS = "userReferrals"
    USER_SUBSCRIBERS = "userSubscribers"
    USER_TERRAIN = "userTerrain"
    USER_PREMIUM_MONTHS = "userPremiumMonths"
    USER_PREMIUM_GIFTS = "userPremiumGifts"
    USER_CASES_OPENED = "userCasesOpened"
    USER_GEMS_PURCHASED = "userGemsPurchased"
    USER_BOUNTY = "userBounty"

    # Military unit rankings
    MU_WEEKLY_DAMAGES = "muWeeklyDamages"
    MU_DAMAGES = "muDamages"
    MU_TERRAIN = "muTerrain"
    MU_WEALTH = "muWealth"
    MU_BOUNTY = "muBounty"


# ---------------------------------------------------------------------------
# Transaction
# ---------------------------------------------------------------------------


class TransactionType(StrEnum):  # type: ignore[misc]
    APPLICATION_FEE = "applicationFee"
    TRADING = "trading"
    ITEM_MARKET = "itemMarket"
    WAGE = "wage"
    DONATION = "donation"
    ARTICLE_TIP = "articleTip"
    OPEN_CASE = "openCase"
    CRAFT_ITEM = "craftItem"
    DISMANTLE_ITEM = "dismantleItem"
    BATTLE_LOOT = "battleLoot"


# ---------------------------------------------------------------------------
# Upgrade
# ---------------------------------------------------------------------------


class UpgradeType(StrEnum):  # type: ignore[misc]
    BUNKER = "bunker"
    BASE = "base"
    PACIFICATION_CENTER = "pacificationCenter"
    STORAGE = "storage"
    AUTOMATED_ENGINE = "automatedEngine"
    BREAK_ROOM = "breakRoom"
    HEADQUARTERS = "headquarters"
    DORMITORIES = "dormitories"


# ---------------------------------------------------------------------------
# Battle Order
# ---------------------------------------------------------------------------


class BattleOrderSide(StrEnum):  # type: ignore[misc]
    ATTACKER = "attacker"
    DEFENDER = "defender"


# ---------------------------------------------------------------------------
# Action Log
# ---------------------------------------------------------------------------


class ActionLogActionType(StrEnum):  # type: ignore[misc]
    SET_ORDER = "setOrder"
    UNSET_ORDER = "unsetOrder"
    UPDATE_ORDER = "updateOrder"
    SET_MERCENARY_CONTRACTS = "setMercenaryContracts"
    REMOVE_MERCENARY_CONTRACT = "removeMercenaryContract"
    CREATE_MERCENARY_CONTRACT_PROPOSAL = "createMercenaryContractProposal"
    CANCEL_MERCENARY_CONTRACT_PROPOSAL = "cancelMercenaryContractProposal"
    ACCEPT_MERCENARY_CONTRACT = "acceptMercenaryContract"
    CANCEL_MERCENARY_CONTRACT = "cancelMercenaryContract"
    COMPLETE_MERCENARY_CONTRACT = "completeMercenaryContract"
    CHANGED_USERNAME = "changedUsername"
    CHANGED_CITIZENSHIP = "changedCitizenship"
    CHANGED_DESCRIPTION = "changedDescription"
    INCREASE_RESISTANCE = "increaseResistance"
    DECREASE_RESISTANCE = "decreaseResistance"
    CLAIM_MISSION_XP = "claimMissionXp"
    CLAIM_FINISHED_MISSION_XP = "claimFinishedMissionXp"
