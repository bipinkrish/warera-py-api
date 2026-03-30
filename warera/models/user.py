from __future__ import annotations

from .common import WareraModel


class UserLiteDates(WareraModel):
    last_connection_at: str | None = None


class UserDates(UserLiteDates):
    last_notifications_check_at: str | None = None
    last_country_message_check_at: str | None = None
    last_global_message_check_at: str | None = None
    last_events_check_at: str | None = None
    last_work_offer_applications: list[str] | None = None
    last_hires_at: list[str] | None = None
    last_work_at: str | None = None
    last_company_joined_at: str | None = None
    last_daily_reward_claimed_at: str | None = None
    last_skills_reset_at: str | None = None
    last_help_asked_at: str | None = None


class UserLeveling(WareraModel):
    level: int | None = None
    total_xp: int | None = None
    daily_xp_left: int | None = None
    available_skill_points: int | None = None
    spent_skill_points: int | None = None
    total_skill_points: int | None = None
    free_reset: int | None = None


class SkillDetail(WareraModel):
    level: int | None = None
    current_bar_value: float | None = None
    value: float | None = None
    weapon: float | None = None
    equipment: float | None = None
    limited: float | None = None
    total: float | None = None
    hourly_bar_regen: float | None = None
    total_after_soft_cap: float | None = None
    overflow: float | None = None


class UserSkills(WareraModel):
    energy: SkillDetail | None = None
    health: SkillDetail | None = None
    hunger: SkillDetail | None = None
    attack: SkillDetail | None = None
    companies: SkillDetail | None = None
    entrepreneurship: SkillDetail | None = None
    production: SkillDetail | None = None
    critical_chance: SkillDetail | None = None
    critical_damages: SkillDetail | None = None
    armor: SkillDetail | None = None
    precision: SkillDetail | None = None
    dodge: SkillDetail | None = None
    loot_chance: SkillDetail | None = None
    management: SkillDetail | None = None


class UserStatsWealth(WareraModel):
    companies: float | None = None
    items: float | None = None
    money: float | None = None
    equipments: float | None = None
    weapons: float | None = None
    total: float | None = None


class UserStatsCase1ByRarity(WareraModel):
    uncommon: int | None = None
    rare: int | None = None
    common: int | None = None


class UserStatsCase1(WareraModel):
    by_rarity: UserStatsCase1ByRarity | None = None
    opened_count: int | None = None


class UserStats(WareraModel):
    estimated_company_values: float | None = None
    estimated_inventory_value: float | None = None
    estimated_wealth: float | None = None
    works_count: int | None = None
    damages_count: int | None = None
    wealth: UserStatsWealth | None = None
    case1: UserStatsCase1 | None = None


class RankingDetail(WareraModel):
    value: float | None = None
    rank: int | None = None
    tier: str | None = None


class UserRankings(WareraModel):
    user_damages: RankingDetail | None = None
    weekly_user_damages: RankingDetail | None = None
    user_wealth: RankingDetail | None = None
    user_level: RankingDetail | None = None
    user_referrals: RankingDetail | None = None
    user_terrain: RankingDetail | None = None
    user_cases_opened: RankingDetail | None = None
    user_bounty: RankingDetail | None = None


class UserEquipment(WareraModel):
    ammo: str | None = None
    helmet: str | None = None
    chest: str | None = None
    boots: str | None = None
    pants: str | None = None
    gloves: str | None = None


class UserMissionsClaimedAt(WareraModel):
    starting: str | None = None
    daily: str | None = None
    weekly: str | None = None


class UserMissions(WareraModel):
    claimed_at: UserMissionsClaimedAt | None = None
    rerolled_daily_missions: int | None = None
    rerolled_weekly_missions: int | None = None


class UserLite(WareraModel):
    username: str | None = None
    username_lower: str | None = None
    can_onboard: bool | None = None
    country: str | None = None
    is_active: bool | None = None
    avatar_url: str | None = None
    mu: str | None = None
    military_rank: int | None = None
    created_at: str | None = None
    updated_at: str | None = None
    email_verified: bool | None = None
    dates: UserLiteDates | None = None
    leveling: UserLeveling | None = None
    stats: UserStats | None = None
    rankings: UserRankings | None = None


class User(UserLite):
    dates: UserDates | None = None
    skills: UserSkills | None = None
    missions: UserMissions | None = None
    equipment: UserEquipment | None = None
    party: str | None = None
    company: str | None = None
    mu_max_level_rewarded: int | None = None
