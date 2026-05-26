"""Unit tests for new resources added from TRPC custom endpoints."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from warera.resources.company import CompanyResource
from warera.resources.donation import DonationResource
from warera.resources.election import ElectionResource
from warera.resources.game_stat import GameStatResource
from warera.resources.item_trading import ItemTradingResource
from warera.resources.mu_member import MuMemberResource
from warera.resources.party import PartyResource
from warera.resources.work import WorkResource
from warera.resources.work_offer import WorkOfferResource


def _mock_http(return_value) -> MagicMock:
    http = MagicMock()
    http.get = AsyncMock(return_value=return_value)
    return http


# ---------------------------------------------------------------------------
# Party
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_party_get_parses_model():
    raw = {
        "_id": "p1",
        "name": "Freedom Party",
        "country": "7",
        "region": "r1",
        "leader": "u1",
        "councilMembers": ["u2", "u3"],
        "members": ["u1", "u2", "u3"],
        "ethics": {
            "militarism": 0.5,
            "isolationism": 0.1,
            "imperialism": 0.2,
            "industrialism": 0.7,
        },
    }
    resource = PartyResource(_mock_http(raw))
    party = await resource.get("p1")

    assert party.id == "p1"
    assert party.name == "Freedom Party"
    assert party.country_id == "7"
    assert party.ethics is not None
    assert party.ethics.militarism == 0.5


@pytest.mark.asyncio
async def test_party_get_paginated_returns_cursor_page():
    raw = {
        "items": [
            {"_id": "p1", "name": "Alpha Party"},
            {"_id": "p2", "name": "Beta Party"},
        ],
        "nextCursor": "cursor123",
        "hasMore": True,
    }
    resource = PartyResource(_mock_http(raw))
    page = await resource.get_paginated(country_id="7")

    assert len(page.items) == 2
    assert page.items[0].name == "Alpha Party"
    assert page.next_cursor == "cursor123"
    assert page.has_more is True


@pytest.mark.asyncio
async def test_party_collect_all_follows_pagination():
    pages = {
        None: {"items": [{"_id": "p1", "name": "A"}], "nextCursor": "c1", "hasMore": True},
        "c1": {"items": [{"_id": "p2", "name": "B"}], "nextCursor": None, "hasMore": False},
    }
    call_cursors: list = []

    async def mock_get(procedure, params):
        cursor = params.get("cursor")
        call_cursors.append(cursor)
        return pages[cursor]

    http = MagicMock()
    http.get = mock_get

    resource = PartyResource(http)
    parties = await resource.collect_all()
    assert len(parties) == 2
    assert parties[0].name == "A"
    assert parties[1].name == "B"


# ---------------------------------------------------------------------------
# Donation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_donation_get_paginated_returns_cursor_page():
    raw = {
        "items": [
            {"_id": "d1", "userId": "u1", "muId": "mu1", "amount": 100.0},
            {"_id": "d2", "userId": "u2", "muId": "mu1", "amount": 50.5},
        ],
        "nextCursor": None,
        "hasMore": False,
    }
    resource = DonationResource(_mock_http(raw))
    page = await resource.get_paginated(mu_id="mu1")

    assert len(page.items) == 2
    assert page.items[0].amount == 100.0
    assert page.items[1].user_id == "u2"
    assert page.has_more is False


@pytest.mark.asyncio
async def test_donation_get_totals():
    raw = {"totalAmount": 1500.75, "donorCount": 12}
    resource = DonationResource(_mock_http(raw))
    totals = await resource.get_totals(mu_id="mu1")

    assert totals.total_amount == 1500.75
    assert totals.donor_count == 12


# ---------------------------------------------------------------------------
# Election
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_election_get_paginated_parses_candidates():
    raw = {
        "items": [
            {
                "_id": "e1",
                "country": "7",
                "isActive": True,
                "type": "president",
                "candidates": [
                    {"user": "u1", "voteCount": 50, "isElected": True},
                    {"user": "u2", "voteCount": 30, "isElected": False},
                ],
                "votesStartAt": "2024-01-01T00:00:00Z",
                "votesEndAt": "2024-01-07T00:00:00Z",
                "votesCount": 80,
                "electedCount": 1,
                "status": "finished",
            }
        ],
        "nextCursor": None,
        "hasMore": False,
    }
    resource = ElectionResource(_mock_http(raw))
    page = await resource.get_paginated(country_id="7")

    assert len(page.items) == 1
    election = page.items[0]
    assert election.id == "e1"
    assert election.is_active is True
    assert election.candidates is not None
    assert len(election.candidates) == 2
    assert election.candidates[0].vote_count == 50
    assert election.candidates[0].is_elected is True


# ---------------------------------------------------------------------------
# GameStat
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_game_stat_get_equipment_avg_float():
    resource = GameStatResource(_mock_http(42.5))
    avg = await resource.get_equipment_avg("sword")
    assert avg == 42.5


@pytest.mark.asyncio
async def test_game_stat_get_equipment_avg_int():
    resource = GameStatResource(_mock_http(100))
    avg = await resource.get_equipment_avg("helmet")
    assert avg == 100.0
    assert isinstance(avg, float)


@pytest.mark.asyncio
async def test_game_stat_get_equipment_avg_dict():
    resource = GameStatResource(_mock_http({"value": 73.3}))
    avg = await resource.get_equipment_avg("armor")
    assert avg == 73.3


# ---------------------------------------------------------------------------
# MuMember
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_mu_member_get_by_mu_list():
    raw = [
        {
            "_id": "m1",
            "mu": "mu1",
            "user": "u1",
            "totalDamagesCount": 500,
            "monthlyDamagesCount": 100,
            "weeklyDamagesCount": 30,
            "totalHelpCount": 10,
            "monthlyHelpCount": 3,
            "weeklyHelpCount": 1,
        },
        {
            "_id": "m2",
            "mu": "mu1",
            "user": "u2",
            "totalDamagesCount": 200,
            "monthlyDamagesCount": 50,
            "weeklyDamagesCount": 10,
            "totalHelpCount": 5,
            "monthlyHelpCount": 1,
            "weeklyHelpCount": 0,
        },
    ]
    resource = MuMemberResource(_mock_http(raw))
    members = await resource.get_by_mu("mu1")

    assert len(members) == 2
    assert members[0].user == "u1"
    assert members[0].total_damages_count == 500
    assert members[0].monthly_damages_count == 100
    assert members[1].user == "u2"


@pytest.mark.asyncio
async def test_mu_member_get_by_mu_wrapped():
    raw = {"items": [{"_id": "m1", "mu": "mu1", "user": "u1", "totalDamagesCount": 10}]}
    resource = MuMemberResource(_mock_http(raw))
    members = await resource.get_by_mu("mu1")

    assert len(members) == 1
    assert members[0].user == "u1"


@pytest.mark.asyncio
async def test_mu_member_empty_response():
    resource = MuMemberResource(_mock_http([]))
    members = await resource.get_by_mu("mu_empty")
    assert members == []


# ---------------------------------------------------------------------------
# Work
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_work_get_stats_by_user():
    raw = [
        {
            "dailyDate": "2024-01-01",
            "total": 1000.0,
            "wage": 50.0,
            "employeeProd": 700.0,
            "selfWork": 200.0,
            "automatedEngine": 100.0,
        },
        {
            "dailyDate": "2024-01-02",
            "total": 900.0,
            "wage": 45.0,
            "employeeProd": 600.0,
            "selfWork": 200.0,
            "automatedEngine": 100.0,
        },
    ]
    resource = WorkResource(_mock_http(raw))
    stats = await resource.get_stats_by_user("u1", days=7, timezone="UTC")

    assert len(stats) == 2
    assert stats[0].daily_date == "2024-01-01"
    assert stats[0].total == 1000.0
    assert stats[0].employee_prod == 700.0
    assert stats[1].self_work == 200.0


@pytest.mark.asyncio
async def test_work_get_stats_by_company():
    raw = [
        {
            "dailyDate": "2024-01-01",
            "total": 500.0,
            "wage": 25.0,
            "employeeProd": 300.0,
            "selfWork": 150.0,
            "automatedEngine": 50.0,
        }
    ]
    resource = WorkResource(_mock_http(raw))
    stats = await resource.get_stats_by_company("c1", days=30, timezone="Europe/Paris")
    assert len(stats) == 1
    assert stats[0].total == 500.0


@pytest.mark.asyncio
async def test_work_get_stats_by_worker_and_company():
    raw = [
        {
            "dailyDate": "2024-01-01",
            "total": 200.0,
            "wage": 10.0,
            "employeeProd": 200.0,
            "selfWork": 0.0,
            "automatedEngine": 0.0,
        }
    ]
    resource = WorkResource(_mock_http(raw))
    stats = await resource.get_stats_by_worker_and_company("u1", "c1", days=7)
    assert len(stats) == 1
    assert stats[0].automated_engine == 0.0


@pytest.mark.asyncio
async def test_work_stats_empty():
    resource = WorkResource(_mock_http([]))
    stats = await resource.get_stats_by_user("u_none")
    assert stats == []


# ---------------------------------------------------------------------------
# Company — new endpoints
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_company_get_recommended_regions():
    raw = [
        {
            "regionId": "r1",
            "bonus": 0.15,
            "depositBonus": 0.10,
            "ethicDepositBonus": 0.05,
            "strategicBonus": 0.08,
            "ethicSpecializationBonus": 0.03,
            "taxPercent": 10.0,
        },
        {
            "regionId": "r2",
            "bonus": 0.12,
            "depositBonus": 0.07,
            "ethicDepositBonus": 0.02,
            "strategicBonus": 0.05,
            "ethicSpecializationBonus": 0.01,
            "taxPercent": 5.0,
        },
    ]
    resource = CompanyResource(_mock_http(raw))
    regions = await resource.get_recommended_regions("iron")

    assert len(regions) == 2
    assert regions[0].region_id == "r1"
    assert regions[0].bonus == 0.15
    assert regions[1].tax_percent == 5.0


@pytest.mark.asyncio
async def test_company_get_production_bonus():
    raw = {
        "strategicBonus": 0.08,
        "depositBonus": 0.10,
        "ethicSpecializationBonus": 0.03,
        "ethicDepositBonus": 0.05,
        "total": 0.26,
    }
    resource = CompanyResource(_mock_http(raw))
    bonus = await resource.get_production_bonus("c1")

    assert bonus.strategic_bonus == 0.08
    assert bonus.deposit_bonus == 0.10
    assert bonus.total == 0.26


@pytest.mark.asyncio
async def test_company_get_production_bonus_empty():
    resource = CompanyResource(_mock_http({}))
    bonus = await resource.get_production_bonus("c_empty")
    assert bonus.total == 0.0


# ---------------------------------------------------------------------------
# WorkOffer — wage stats
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_work_offer_get_wage_stats():
    raw = {
        "allowedRange": {"min": 10.0, "max": 100.0, "average": 55.0},
        "topOffer": 120.0,
        "topEligibleOffer": 90.0,
        "topEligibleOffers": [
            {"_id": "wo1", "wage": 90.0, "wageAfterTax": 81.0},
            {"_id": "wo2", "wage": 85.0, "wageAfterTax": 76.5},
        ],
    }
    resource = WorkOfferResource(_mock_http(raw))
    stats = await resource.get_wage_stats(energy=100.0, production=0.8, citizenship="7")

    assert stats.top_offer == 120.0
    assert stats.top_eligible_offer == 90.0
    assert stats.allowed_range.min == 10.0
    assert stats.allowed_range.max == 100.0
    assert stats.allowed_range.average == 55.0
    assert len(stats.top_eligible_offers) == 2


@pytest.mark.asyncio
async def test_work_offer_get_wage_stats_empty():
    resource = WorkOfferResource(_mock_http({}))
    stats = await resource.get_wage_stats(energy=100.0, production=0.5, citizenship="7")
    assert stats.top_offer == 0.0
    assert stats.top_eligible_offer == 0.0


# ---------------------------------------------------------------------------
# ItemTrading — public orders by owner
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_item_trading_get_public_orders_by_owner():
    raw = {
        "buyOrders": [
            {
                "_id": "bo1",
                "user": "u1",
                "country": "7",
                "itemCode": "iron",
                "quantity": 100,
                "price": 1.5,
                "offerAt": "2024-01-01",
                "type": "buy",
            },
        ],
        "sellOrders": [
            {
                "_id": "so1",
                "user": "u1",
                "country": "7",
                "itemCode": "wood",
                "quantity": 50,
                "price": 0.8,
                "offerAt": "2024-01-01",
                "type": "sell",
            },
        ],
        "allOrders": [
            {
                "_id": "bo1",
                "user": "u1",
                "country": "7",
                "itemCode": "iron",
                "quantity": 100,
                "price": 1.5,
                "offerAt": "2024-01-01",
                "type": "buy",
            },
            {
                "_id": "so1",
                "user": "u1",
                "country": "7",
                "itemCode": "wood",
                "quantity": 50,
                "price": 0.8,
                "offerAt": "2024-01-01",
                "type": "sell",
            },
        ],
        "totalBuyMoneyInvested": 150.0,
        "totalSellQuantities": {"wood": 50},
    }
    resource = ItemTradingResource(_mock_http(raw))
    summary = await resource.get_public_orders_by_owner("7")

    assert len(summary.buy_orders) == 1
    assert len(summary.sell_orders) == 1
    assert len(summary.all_orders) == 2
    assert summary.total_buy_money_invested == 150.0
    assert summary.total_sell_quantities["wood"] == 50


@pytest.mark.asyncio
async def test_item_trading_get_public_orders_empty():
    resource = ItemTradingResource(_mock_http({}))
    summary = await resource.get_public_orders_by_owner("7")
    assert summary.buy_orders == []
    assert summary.sell_orders == []
    assert summary.total_buy_money_invested == 0.0
