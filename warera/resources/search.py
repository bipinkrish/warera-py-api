from __future__ import annotations

from ..models.search import SearchResult, SearchResults
from ._base import BaseResource


class SearchResource(BaseResource):
    """
    Endpoints:
      • search.searchAnything
    """

    async def query(self, search_text: str) -> SearchResults:
        """
        Global search across all entity types (users, countries, companies, MUs, articles).

        Args:
            search_text: The search query. Must be at least 1 character.

        Returns:
            SearchResults containing a list of matched entities with type and ID.
        """
        if not search_text.strip():
            raise ValueError("search_text must not be empty")

        raw = await self._get("search.searchAnything", searchText=search_text)

        results: list[SearchResult] = []
        if isinstance(raw, dict):
            # API returns {userIds: [...], muIds: [...], ...}
            mappings = {
                "userIds": "user",
                "muIds": "mu",
                "countryIds": "country",
                "regionIds": "region",
                "partyIds": "party",
                "articleIds": "article",
                "companyIds": "company",
            }
            for key, entity_type in mappings.items():
                ids = raw.get(key, [])
                if isinstance(ids, list):
                    for eid in ids:
                        results.append(SearchResult(id=eid, type=entity_type))

        return SearchResults(results=results, total=len(results))
