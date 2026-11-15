"""
TERRA-X Test Suite: Data Contracts & Multi-Agency Connectors
Validates pinned collections, runtime resolutions, license audits, rate limits, and unscaling.
"""

import unittest
import numpy as np
from connectors.license_engine import LicenseEngine, LicenseClass, AssetRecord
from connectors.nasa_cmr import NASAConnector
from connectors.usgs_stac import USGSLandsatConnector
from connectors.cdse_stac import CDSEConnector
from connectors.mars_psa import MarsPSAConnector
from connectors.asia_connectors import JAXAConnector, HimawariConnector, ISROPRADANConnector
from connectors.csa_connector import CSAConnector
from connectors.pds_ode import PDSODEConnector


class TestDataConnectors(unittest.TestCase):

    def setUp(self):
        self.license_engine = LicenseEngine()

    def test_license_engine_export_guardrail(self):
        """Restricted assets (e.g. ISRO PRADAN manual auth) must be blocked from export."""
        open_asset = self.license_engine.register_asset(
            asset_id="NASA-GLO-30",
            agency="NASA",
            collection="GLO-30",
            license_class=LicenseClass.OPEN_PUBLIC_DOMAIN,
        )
        restricted_asset = self.license_engine.register_asset(
            asset_id="ISRO-CH2",
            agency="ISRO",
            collection="TMC",
            license_class=LicenseClass.RESTRICTED_MANUAL_AUTH,
        )
        assets = [open_asset, restricted_asset]
        exported = self.license_engine.validate_for_export(assets)
        self.assertEqual(len(exported), 1)
        self.assertEqual(exported[0].asset_id, "NASA-GLO-30")

    def test_nasa_cmr_ecostress_and_high_lat_fallback(self):
        """
        ECOSTRESS V003 is valid between -52 deg and +52 deg.
        Latitudes > 52 deg (e.g. Haughton Crater at 75 deg N) must trigger fallback to Landsat ST + MODIS + CCI.
        """
        nasa = NASAConnector(self.license_engine)
        
        # Test low-latitude query (Atacama at -24.08 deg)
        res_low = nasa.fetch_thermal_inertia_granules(latitude=-24.08, longitude=-69.86)
        self.assertEqual(res_low["strategy"], "ECOSTRESS_V003_DIRECT")
        self.assertIn("FieldOfViewObstruction_None", res_low["qa_flags"])

        # Test high-latitude query (Haughton at +75.38 deg)
        res_high = nasa.fetch_thermal_inertia_granules(latitude=75.38, longitude=-89.68)
        self.assertEqual(res_high["strategy"], "HIGH_LATITUDE_FALLBACK_LANDSAT_MODIS_CCI")
        self.assertIn("Landsat_C2L2_ST_Filtered", res_high["qa_flags"])

    def test_cdse_stac_modern_v1_endpoint(self):
        """Verifies modern CDSE STAC endpoint (legacy /stac deprecated 2025-11-17)."""
        cdse = CDSEConnector(self.license_engine)
        self.assertEqual(cdse.CDSE_STAC_URL, "https://stac.dataspace.copernicus.eu/v1")
        glo30 = cdse.search_glo30_dem(bbox=[-70.0, -25.0, -69.0, -24.0])
        self.assertTrue(len(glo30["features"]) > 0)
        self.assertEqual(glo30["registered_assets"][0]["license_class"], LicenseClass.OPEN_CC_BY_4.value)

    def test_jaxa_aw3d30_canopy_mask_fallback(self):
        """AW3D30 is a DSM; heavy canopy must force fallback to bare-earth GLO-30."""
        jaxa = JAXAConnector(self.license_engine)
        
        # Arid bare ground (canopy 2%)
        res_arid = jaxa.get_elevation_profile(lat=-24.0, lon=-69.0, canopy_cover_percent=2.0)
        self.assertEqual(res_arid["source_used"], "JAXA_AW3D30_DSM_VALIDATED")

        # Forested area (canopy 45%)
        res_forest = jaxa.get_elevation_profile(lat=0.0, lon=25.0, canopy_cover_percent=45.0)
        self.assertEqual(res_forest["source_used"], "COP_DEM_GLO30_FALLBACK")
        self.assertEqual(res_forest["dsm_flag"], "AW3D30_DSM_REJECTED_DUE_TO_CANOPY_BIAS")

    def test_pds_lola_int16_unscaling(self):
        """USGS LOLA 118m must unscale int16 * 0.5 to float32 meters."""
        pds = PDSODEConnector(self.license_engine)
        raw_int16 = np.array([-2000, 0, 4500, 12000], dtype=np.int16)
        unscaled = pds.unscale_lola_elevation(raw_int16)
        
        self.assertEqual(unscaled.dtype, np.float32)
        np.testing.assert_allclose(unscaled, [-1000.0, 0.0, 2250.0, 6000.0])

    def test_pds_pgda_100_clone_ensemble(self):
        """PGDA polar DEM generator must produce exactly 100 clones with specified RMSE."""
        pds = PDSODEConnector(self.license_engine)
        ens = pds.generate_pgda_polar_dem_ensemble(
            center_lat=-89.9,
            center_lon=0.0,
            nominal_elev_m=-1200.0,
            elevation_rmse_m=0.85,
            n_clones=100,
            random_seed=42,
        )
        self.assertEqual(ens["clones_count"], 100)
        self.assertEqual(len(ens["elevation_clones"]), 100)
        self.assertEqual(len(ens["slope_clones"]), 100)
        # Check mean is close to nominal
        self.assertAlmostEqual(np.mean(ens["elevation_clones"]), -1200.0, delta=0.3)


if __name__ == "__main__":
    unittest.main()

