"""
Basic async usage example.
"""

import asyncio

from warera import WareraClient
from warera._enums import RankingType


async def main() -> None:
    # Works without a key (lower rate limits), or set WARERA_API_KEY env var
    async with WareraClient() as client:
        # --- Country lookups ---
        all_countries = await client.country.get_all()
        print(f"Total countries: {len(all_countries)}")

        india = await client.country.find_by_name("India")
        if india:
            print(f"India ID: {india.id}")

            # Government
            assert india.id is not None
            gov = await client.government.get(india.id)
            print(f"Has president: {gov.has_president()}")

        # --- Item prices ---
        prices = await client.item_trading.get_prices()
        if "iron" in prices:
            print(f"Iron price: {prices['iron'].price}")

        # --- Active battles ---
        page = await client.battle.get_many(is_active=True, limit=5)
        print(f"\nActive battles (first page): {len(page.items)}")
        for battle in page.items:
            print(
                f"  Battle {battle.id}: {battle.attacker_country_id} vs {battle.defender_country_id}"
            )

        # --- Rankings ---
        top_users = await client.ranking.get(RankingType.USER_WEALTH)
        print(f"\nTop {len(top_users)} wealthiest users:")
        for entry in top_users[:5]:
            display_name = entry.name or entry.entity_id or "Unknown"
            print(f"  #{entry.rank} {display_name}: {entry.value}")

        # --- Search ---
        results = await client.search.query("India")
        print(f"\nSearch 'India': {len(results.results)} results")

        # --- Game dates ---
        dates = await client.game_config.get_dates()
        print(f"\nNext day at: {dates.next_day_at}")


if __name__ == "__main__":
    asyncio.run(main())
