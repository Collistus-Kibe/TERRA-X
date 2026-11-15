"""
TERRA-X Test Suite: Scoring Engine & Fidelity Ledger
Validates:
- AFI_f = M_f * (1 - C_f) * T_f
- Missing data strictly yields UNCONSTRAINED (no imputation)
- Biological sign flip in ASTROBIO vs Engineering functions
- Hard breaks always emitted
"""

import unittest
from targets.registry import TargetRegistry
from engine.scoring import ScoringEngine, FidelityStatus


class TestScoringEngine(unittest.TestCase):

    def setUp(self):
        self.registry = TargetRegistry()
        self.lunar_target = self.registry.get_target("MOON_SOUTH_POLE_SHACKLETON")
        self.mars_target = self.registry.get_target("MARS_JEZERO_DELTA")

    def test_afi_equation_exact_product(self):
        """Verifies that AFI_f equals M * (1 - C) * T."""
        features = {
            "slope_deg": 12.0,
            "friction_angle_deg": 38.0,
            "h_rms_m": 0.15,
            "thermal_inertia_si": 420.0,
            "sky_view_factor": 0.70,
            "soil_moisture_wtd": 0.01,
            "vegetation_ndvi": 0.02,
            "grain_wadell_roundness": 0.25,
            "biological_activity_index": 0.02,
        }
        res = ScoringEngine.compute_afi("MOBILITY", self.lunar_target, features)
        expected_afi = res.M_match * (1.0 - res.C_confounder) * res.T_transferable
        self.assertAlmostEqual(res.afi_score, expected_afi, delta=0.0001)

    def test_missing_data_strictly_unconstrained(self):
        """Missing values must NOT be imputed and must be labeled UNCONSTRAINED in the ledger."""
        features_incomplete = {
            # slope_deg is omitted
            # friction_angle_deg is omitted
            "h_rms_m": 0.12,
            "soil_moisture_wtd": 0.01,
            "vegetation_ndvi": 0.02,
        }
        res = ScoringEngine.compute_afi("MOBILITY", self.lunar_target, features_incomplete)
        
        # Search ledger for Slope Ratio
        slope_entry = next((e for e in res.fidelity_ledger if "Slope Ratio" in e.subsystem_name), None)
        self.assertIsNotNone(slope_entry)
        self.assertEqual(slope_entry.status, FidelityStatus.UNCONSTRAINED)
        self.assertIsNone(slope_entry.earth_value)
        self.assertEqual(slope_entry.transferability_fraction, 0.0)

    def test_biological_sign_flip_astrobio_vs_mobility(self):
        """Biology is a positive signal for ASTROBIO, but a confounder for MOBILITY."""
        features = {
            "slope_deg": 10.0,
            "friction_angle_deg": 35.0,
            "h_rms_m": 0.10,
            "thermal_inertia_si": 400.0,
            "sky_view_factor": 0.85,
            "soil_moisture_wtd": 0.02,
            "vegetation_ndvi": 0.02,
            "grain_wadell_roundness": 0.25,
            "biological_activity_index": 0.25, # High extremophile biological signal
        }
        res_mobility = ScoringEngine.compute_afi("MOBILITY", self.mars_target, features)
        res_astrobio = ScoringEngine.compute_afi("ASTROBIO", self.mars_target, features)

        # In ASTROBIO, biological penalty must be <= 0 (inverted / signal bonus)
        conf_bio_astrobio = res_astrobio.confounder_breakdown["biological_penalty"]
        conf_bio_mobility = res_mobility.confounder_breakdown["biological_penalty"]

        self.assertLess(conf_bio_astrobio, 0.0)
        self.assertGreater(conf_bio_mobility, 0.0)

    def test_hard_breaks_presence(self):
        """Hard breaks must always be reported."""
        features = {
            "slope_deg": 10.0,
            "friction_angle_deg": 35.0,
            "h_rms_m": 0.10,
        }
        res = ScoringEngine.compute_afi("MOBILITY", self.lunar_target, features)
        self.assertTrue(len(res.hard_breaks) > 0)
        self.assertTrue(any("LUNAR_VACUUM" in hb for hb in res.hard_breaks))
        self.assertTrue(any("LUNAR_1_6TH_GRAVITY" in hb for hb in res.hard_breaks))


if __name__ == "__main__":
    unittest.main()

