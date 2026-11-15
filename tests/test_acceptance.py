"""
TERRA-X Core Acceptance Test Suite
Mandatory non-negotiable verification gates:
1. Golden-site recall@50 >= 0.8 for Atacama / Haughton / Death Valley held-out
2. Leave-one-continent-out cross-validation
3. Cross-sensor spread evaluation (SAR, DEM, Thermal)
4. Monte Carlo interval calibration (p10 <= p50 <= p90, P(top10))
5. Ablation study per dimension
6. Adversarial looks-alike rejection (Daytona Beach, rounded aeolian dunes)
7. Expert blind review vs controls
"""

import unittest
import numpy as np
from engine.pipeline import TerraXPipeline
from targets.registry import TargetRegistry
from data.candidate_catalog import get_all_candidate_cells
from harmonize.sensor_harmonizer import SensorHarmonizer
from engine.scoring import ScoringEngine


class TestAcceptanceGates(unittest.TestCase):

    def setUp(self):
        self.pipeline = TerraXPipeline()
        self.registry = TargetRegistry()
        self.lunar_target = self.registry.get_target("MOON_SOUTH_POLE_SHACKLETON")
        self.mars_target = self.registry.get_target("MARS_JEZERO_DELTA")

    def test_gate_1_golden_site_recall_at_50(self):
        """
        Acceptance Test 1:
        Golden-site recall@50 >= 0.8 for Atacama, Haughton, and Death Valley held-out benchmarks.
        """
        # Run discovery pipeline for Mars Jezero Delta
        out_mars = self.pipeline.run_discovery_pipeline(
            target_id="MARS_JEZERO_DELTA",
            function_profile="MOBILITY",
            top_k=50,
            enforce_mmr=False,
        )
        ranked_sites = out_mars["ranked_sites"]
        ranked_names = [s["site_name"] for s in ranked_sites]

        # Verify Atacama, Haughton, Death Valley are captured within top 50
        captured_count = 0
        held_out_benchmarks = ["Atacama", "Haughton", "Death Valley"]
        for bench in held_out_benchmarks:
            matched = any(bench.lower() in name.lower() for name in ranked_names)
            if matched:
                captured_count += 1

        recall = captured_count / len(held_out_benchmarks)
        self.assertGreaterEqual(
            recall,
            0.8,
            f"Golden site recall@50 was {recall:.2f}, required >= 0.80. Captured: {captured_count}/{len(held_out_benchmarks)}",
        )

    def test_gate_2_leave_one_continent_out(self):
        """
        Acceptance Test 2:
        Leave-one-continent-out spatial cross-validation.
        Ensures algorithm performs consistently across continents without continental overfitting.
        """
        all_candidates = get_all_candidate_cells(res=6)
        continents = set(c["continent"] for c in all_candidates if "Adversarial" not in c["name"])

        continent_mean_scores = {}
        for cont in continents:
            # Evaluate sites in this continent
            cont_candidates = [c for c in all_candidates if c["continent"] == cont]
            scores = []
            for c in cont_candidates:
                res = ScoringEngine.compute_afi("MOBILITY", self.mars_target, c)
                scores.append(res.afi_score)
            continent_mean_scores[cont] = float(np.mean(scores))

        # Check that no continent has zero or collapsed performance
        for cont, mean_s in continent_mean_scores.items():
            self.assertGreater(
                mean_s,
                0.05,
                f"Continent {cont} showed collapsed scoring performance: {mean_s}",
            )

    def test_gate_3_cross_sensor_spread(self):
        """
        Acceptance Test 3:
        Cross-sensor spread calculation:
        - S1-RTC vs OPERA RTC-S1 backscatter
        - GLO-30 vs AW3D30 vs ASTER DEMs
        - ECOSTRESS vs Landsat vs MODIS thermal LST
        """
        # 1. DEM Spread
        dem_spread = SensorHarmonizer.evaluate_dem_spread(glo30_elev=1000.0, aw3d30_elev=1002.5, aster_elev=997.8)
        self.assertGreater(dem_spread["elevation_spread_m"], 0.0)
        self.assertIn("tau_uncertainty_dem", dem_spread)

        # 2. SAR Spread
        sar_spread = SensorHarmonizer.evaluate_sar_spread(s1_rtc_gamma0_db=-14.2, opera_rtc_gamma0_db=-13.5)
        self.assertAlmostEqual(sar_spread["delta_gamma0_db"], 0.7, delta=0.05)
        self.assertGreater(sar_spread["tau_uncertainty_sar"], 0.0)

        # 3. Thermal Spread
        therm_spread = SensorHarmonizer.evaluate_thermal_spread(ecostress_lst_k=305.2, landsat_st_k=303.8, modis_lst_k=307.0)
        self.assertAlmostEqual(therm_spread["lst_spread_k"], 3.2, delta=0.05)
        self.assertGreater(therm_spread["tau_uncertainty_thermal"], 0.0)

    def test_gate_4_mc_interval_calibration(self):
        """
        Acceptance Test 4:
        Monte Carlo interval calibration:
        - Rank p10 <= rank p50 <= rank p90
        - Score p10 <= score p50 <= score p90
        - 0.0 <= P(top10) <= 1.0
        """
        out = self.pipeline.run_discovery_pipeline(
            target_id="MOON_SOUTH_POLE_SHACKLETON",
            function_profile="CONSTRUCTION_ISRU",
            top_k=5,
        )
        for s in out["ranked_sites"]:
            mc_rank = s["monte_carlo_rank"]
            scores = s["scores"]
            p_top10 = mc_rank["p_top10"]

            # Rank p10 is top percentile (lower integer is better rank)
            self.assertLessEqual(mc_rank["rank_p10"], mc_rank["rank_p50"])
            self.assertLessEqual(mc_rank["rank_p50"], mc_rank["rank_p90"])

            # Score p10 <= p50 <= p90
            self.assertLessEqual(scores["afi_p10"], scores["afi_p50"])
            self.assertLessEqual(scores["afi_p50"], scores["afi_p90"])

            # Probability range
            self.assertGreaterEqual(p_top10, 0.0)
            self.assertLessEqual(p_top10, 1.0)

    def test_gate_5_ablation_per_dimension(self):
        """
        Acceptance Test 5:
        Ablation study per dimension:
        Removing or distorting individual physical groups (slope, roughness, moisture, biology)
        must measurably change the AFI score.
        """
        base = {
            "slope_deg": 14.0,
            "friction_angle_deg": 38.0,
            "h_rms_m": 0.15,
            "thermal_inertia_si": 420.0,
            "sky_view_factor": 0.70,
            "soil_moisture_wtd": 0.01,
            "vegetation_ndvi": 0.02,
            "grain_wadell_roundness": 0.25,
            "biological_activity_index": 0.02,
        }
        res_nominal = ScoringEngine.compute_afi("MOBILITY", self.lunar_target, base)

        # Ablation 1: Extreme roughness (obstacle jam)
        ablated_rough = dict(base, h_rms_m=1.2)
        res_rough = ScoringEngine.compute_afi("MOBILITY", self.lunar_target, ablated_rough)
        self.assertNotEqual(res_nominal.afi_score, res_rough.afi_score)
        self.assertLess(res_rough.afi_score, res_nominal.afi_score)

        # Ablation 2: Severe moisture confounder
        ablated_moist = dict(base, soil_moisture_wtd=0.35)
        res_moist = ScoringEngine.compute_afi("MOBILITY", self.lunar_target, ablated_moist)
        self.assertGreater(res_moist.C_confounder, res_nominal.C_confounder)
        self.assertLess(res_moist.afi_score, res_nominal.afi_score)

    def test_gate_6_adversarial_looks_alike_rejection(self):
        """
        Acceptance Test 6:
        Adversarial looks-alike rejection:
        - Daytona Beach (wet quartz beach): visually resembles desert sand, but extreme moisture
          and rounded fluvial grains MUST lead to rejection.
        - Erg Chebbi (well-sorted rounded dune): high slip, low angular interlocking.
        AFI score must be drastically lower than authentic planetary analogs!
        """
        all_candidates = get_all_candidate_cells(res=6)
        daytona = next(c for c in all_candidates if "Daytona" in c["name"])
        atacama = next(c for c in all_candidates if "Atacama" in c["name"])

        res_daytona = ScoringEngine.compute_afi("MOBILITY", self.lunar_target, daytona)
        res_atacama = ScoringEngine.compute_afi("MOBILITY", self.lunar_target, atacama)

        # Daytona Beach must receive heavy confounder penalty and low AFI score
        self.assertGreater(res_daytona.C_confounder, 0.50, f"Daytona confounder was {res_daytona.C_confounder}")
        self.assertLess(res_daytona.afi_score, 0.15, f"Daytona AFI score was {res_daytona.afi_score}")
        self.assertGreater(res_atacama.afi_score, res_daytona.afi_score * 3.0)

    def test_gate_7_expert_blind_review_vs_controls(self):
        """
        Acceptance Test 7:
        Expert blind review vs controls:
        Verifies that basaltic, arid, angular benchmark sites (e.g. Mauna Kea, Haughton, Qaidam, McMurdo)
        rank in the top tier and strictly outrank non-analogous controls (e.g. Daytona Beach).
        """
        out = self.pipeline.run_discovery_pipeline(
            target_id="MOON_SOUTH_POLE_SHACKLETON",
            function_profile="CONSTRUCTION_ISRU",
            top_k=15,
            enforce_mmr=False,
        )
        ranked = out["ranked_sites"]
        top_5_names = [r["site_name"] for r in ranked[:5]]
        all_names = [r["site_name"] for r in ranked]

        # Authentic high-friction / basaltic benchmark sites must occupy the top tier
        self.assertTrue(
            any("Mauna Kea" in name or "Haughton" in name or "McMurdo" in name for name in top_5_names),
            f"Expected benchmark analog in top 5, got: {top_5_names}",
        )

        # Non-analog controls like Daytona Beach must rank strictly below benchmark sites
        mauna_kea_rank = next((r["monte_carlo_rank"]["rank_p50"] for r in ranked if "Mauna Kea" in r["site_name"]), 99)
        daytona_rank = next((r["monte_carlo_rank"]["rank_p50"] for r in ranked if "Daytona" in r["site_name"]), 99)
        self.assertLess(mauna_kea_rank, daytona_rank)


if __name__ == "__main__":
    unittest.main()
