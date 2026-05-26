from __future__ import annotations

from ..models.tournament import Tournament, TournamentTeam
from ._base import BaseResource


class TournamentResource(BaseResource):
    """
    Endpoints:
      • tournament.getLastTournament
      • tournamentTeam.getById
      • tournamentTeam.getByTournamentId
    """

    async def get_last_tournament(self) -> Tournament:
        """Get the latest tournament details."""
        raw = await self._get("tournament.getLastTournament")
        return Tournament.model_validate(raw)

    async def get_team_by_id(self, tournament_team_id: str) -> TournamentTeam:
        """Get a tournament team by its ID."""
        raw = await self._get(
            "tournamentTeam.getById",
            tournamentTeamId=tournament_team_id,
        )
        return TournamentTeam.model_validate(raw)

    async def get_teams_by_tournament(self, tournament_id: str) -> list[TournamentTeam]:
        """Get all teams for a specific tournament."""
        raw = await self._get(
            "tournamentTeam.getByTournamentId",
            tournamentId=tournament_id,
        )
        if isinstance(raw, list):
            return [TournamentTeam.model_validate(item) for item in raw]
        return []
