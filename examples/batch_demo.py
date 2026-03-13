"""
Batch request examples — fetching many resources in a single HTTP round-trip.
"""

import asyncio

from warera import WareraClient


async def example_mixed_batch() -> None:
    """Load country + government + prices in one request."""
    async with WareraClient() as client:
        # Fetch any valid country ID first
        countries = await client.country.get_all()
        if not countries:
            print("No countries found to test batch.")
            return
        cid = list(countries.keys())[0]
        print(f"Using country ID: {cid} for batch test")

        async with client.batch() as batch:
            country_item = batch.add("country.getCountryById", {"countryId": cid})
            gov_item = batch.add("government.getByCountryId", {"countryId": cid})
            prices_item = batch.add("itemTrading.getPrices", {})
            dates_item = batch.add("gameConfig.getDates", {})

        print("Country raw:", country_item.result)
        print("Government raw:", gov_item.result)
        print(
            "Prices keys:",
            list(prices_item.result.keys())[:5] if isinstance(prices_item.result, dict) else "N/A",
        )
        print("Game dates:", dates_item.result)


async def example_many_companies(country_id: str) -> None:
    """
    Batch-fetch companies owned by each citizen of a country.
    Demonstrates get_many (auto-chunked batch under the hood).
    """
    async with WareraClient() as client:
        # Step 1 — get first page of citizens
        page = await client.user.get_by_country(country_id, limit=20)
        user_ids = [u.id for u in page.items if u.id]
        print(f"Fetched {len(user_ids)} user IDs")

        # Step 2 — batch fetch all users in one round-trip
        users = await client.user.get_many(user_ids)
        print(f"Fetched {len(users)} users via batch")
        for u in users[:3]:
            print(f"  {u.username} (level {u.level})")


async def example_ruling_parties(country_ids: list[str]) -> None:
    """
    Mirrors the TypeScript batch pattern from the docs:
    fetch the ruling party for each country in one batch POST.
    """
    async with WareraClient() as client:
        # Get governments for all countries in one batch
        async with client.batch() as batch:
            gov_items = [
                batch.add("government.getByCountryId", {"countryId": cid}) for cid in country_ids
            ]

        for cid, gov_item in zip(country_ids, gov_items, strict=True):
            if gov_item.ok:
                data = gov_item.result
                print(f"Country {cid}: president={data.get('presidentId', 'none')}")
            else:
                print(f"Country {cid}: ERROR — {gov_item._error}")


async def example_partial_batch_error() -> None:
    """Show that a partial batch failure doesn't crash everything."""
    async with WareraClient() as client:
        async with client.batch() as batch:
            good = batch.add("country.getAllCountries", {})
            bad = batch.add("company.getById", {"companyId": "nonexistent_id_99999"})

        print("Good item ok:", good.ok)
        print("Bad item ok: ", bad.ok)

        if good.ok:
            print("Countries fetched successfully")
        if not bad.ok:
            print(f"Bad item error: {bad._error}")


if __name__ == "__main__":
    asyncio.run(example_mixed_batch())
    print()
    # Uncomment to test with real IDs:
    # asyncio.run(example_many_companies("7"))
    # asyncio.run(example_ruling_parties(["7", "8", "9"]))
