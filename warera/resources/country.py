from __future__ import annotations

import time
from typing import TYPE_CHECKING

from ..models.country import Country
from ._base import BaseResource

if TYPE_CHECKING:
    from .._http import HttpSession

# How long (seconds) to cache the full country list before re-fetching.
# Country data changes very rarely; 10 minutes is a safe, conservative TTL.
_COUNTRY_CACHE_TTL = 600.0


class CountryResource(BaseResource):
    """
    Endpoints:
      • country.getCountryById
      • country.getAllCountries
    """

    def __init__(self, http: HttpSession) -> None:
        super().__init__(http)
        # Per-instance cache so different WareraClient objects are independent.
        self._country_cache: dict[str, Country] | None = None
        self._cache_time: float = 0.0

    async def get(self, country_id: str) -> Country:
        """Get a single country by ID."""
        raw = await self._get("country.getCountryById", countryId=country_id)
        return Country.model_validate(raw)

    async def get_all(self) -> dict[str, Country]:
        """
        Get all countries.
        Returns a dict keyed by country ID for O(1) lookups.
        """
        raw = await self._get("country.getAllCountries")
        if isinstance(raw, dict):
            return {k: Country.model_validate(v) for k, v in raw.items()}
        if isinstance(raw, list):
            countries = [Country.model_validate(c) for c in raw]
            return {c.id: c for c in countries if c.id}
        return {}

    def invalidate_cache(self) -> None:
        """Explicitly clear the country cache, forcing a fresh fetch on next call."""
        self._country_cache = None
        self._cache_time = 0.0

    async def find_by_name(self, name: str) -> Country | None:
        """
        Client-side helper: return the country matching `name` (case-insensitive).

        Results are cached for up to _COUNTRY_CACHE_TTL seconds (default 10 min)
        so repeated calls — e.g. on every /scan add, /scan info, /scan history
        invocation — do not each trigger a full API round-trip.
        Call invalidate_cache() to force an immediate refresh.

        Returns None if no country with that name exists.
        """
        now = time.monotonic()
        if self._country_cache is None or (now - self._cache_time) > _COUNTRY_CACHE_TTL:
            self._country_cache = await self.get_all()
            self._cache_time = now

        name_lower = name.lower()
        for country in self._country_cache.values():
            if country.name and country.name.lower() == name_lower:
                return country
        return None
