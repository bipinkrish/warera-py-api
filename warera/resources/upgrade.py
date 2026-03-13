from __future__ import annotations

from .._enums import UpgradeType
from ..exceptions import WareraError
from ..models.upgrade import Upgrade
from ._base import BaseResource


class UpgradeResource(BaseResource):
    """
    Endpoints:
      • upgrade.getUpgradeByTypeAndEntity
    """

    async def get(
        self,
        upgrade_type: UpgradeType | str,
        *,
        region_id: str | None = None,
        company_id: str | None = None,
        mu_id: str | None = None,
    ) -> Upgrade:
        """
        Get an upgrade by type and the entity it belongs to.

        Exactly one of region_id, company_id, or mu_id must be provided
        depending on the upgrade type:
          • Region upgrades  (bunker, base, pacificationCenter, storage):  region_id
          • Company upgrades (automatedEngine, breakRoom):                  company_id
          • MU upgrades      (headquarters, dormitories):                   mu_id

        Args:
            upgrade_type:  The upgrade type. Use the UpgradeType enum.
            region_id:     Region the upgrade belongs to.
            company_id:    Company the upgrade belongs to.
            mu_id:         Military unit the upgrade belongs to.
        """
        provided = sum(x is not None for x in (region_id, company_id, mu_id))
        if provided == 0:
            raise WareraError("upgrade.get requires exactly one of: region_id, company_id, mu_id")

        raw = await self._get(
            "upgrade.getUpgradeByTypeAndEntity",
            upgradeType=upgrade_type,
            regionId=region_id,
            companyId=company_id,
            muId=mu_id,
        )
        return Upgrade.model_validate(raw)
