from __future__ import annotations

from .common import WareraModel


class UserDates(WareraModel):
    last_connection_at: str | None = None
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


class UserStats(WareraModel):
    damages_count: int | None = None


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


class User(WareraModel):
    username: str | None = None
    country: str | None = None
    is_active: bool | None = None
    avatar_url: str | None = None
    mu: str | None = None
    military_rank: int | None = None
    created_at: str | None = None
    dates: UserDates | None = None
    leveling: UserLeveling | None = None
    skills: UserSkills | None = None
    stats: UserStats | None = None
    rankings: UserRankings | None = None
