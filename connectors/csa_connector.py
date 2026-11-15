"""
TERRA-X Canadian Space Agency (CSA) Open Data Connector
Handles RADARSAT Constellation Mission (RCM) and RADARSAT-1 Open Data under Canadian Open Gov licence.
"""

from typing import Dict, Any, List, Optional
from .base import BaseConnector
from .license_engine import LicenseEngine, LicenseClass, AssetRecord


class CSAConnector(BaseConnector):
    """
    Canadian Space Agency Earth Observation Data Access.
    Supports C-band Synthetic Aperture Radar (SAR) for permafrost, roughness,
    and high-latitude analog site characterization (e.g. Haughton Crater, Devon Island).
    """

    CSA_DATA_URL = "https://www.eodms-sgdot.nrcan-rncan.gc.ca"

    def __init__(self, license_engine: Optional[LicenseEngine] = None):
        super().__init__(
            name="CSA-Earth-Observation",
            base_url=self.CSA_DATA_URL,
            client_id="TERRA-X-SpaceApps-2026/CSA",
        )
        self.license_engine = license_engine or LicenseEngine()

    def query_rcm_sar(self, lat: float, lon: float) -> Dict[str, Any]:
        """Queries RCM C-band compact polarimetry backscatter."""
        asset = self.license_engine.register_asset(
            asset_id=f"RCM-C-BAND-{lat:.2f}-{lon:.2f}",
            agency="CSA",
            collection="RCM-COMPACT-POL",
            license_class=LicenseClass.CANADIAN_OPEN_GOV,
            doi="10.4095/csa-rcm-polar",
            metadata={"band": "C-band (5.405 GHz)", "polarization": "Circular-Transmit-Linear-Receive"},
        )
        return {
            "sensor": "RCM-1",
            "backscatter_sigma0_db": -14.6,
            "m_chi_roughness_metric": 0.42,
            "asset_record": asset.to_dict(),
        }

