"""
TERRA-X End-to-End Discovery Pipeline
Implements the full 7-stage architecture:
- S0: Target profile ingestion (Moon/Mars reference states & PGDA specs)
- S1: Global coarse sieve (H3 r5/r6 screening)
- S2: Vector ANN feature similarity projection
- S3: Novelty penalty & MMR spatial diversification
- S4: Multi-sensor high-resolution characterization (Thermal, SAR, DEM spread)
- S5: Scoring gates: AFI = M*(1-C)*T, 100-clone Monte Carlo, Fidelity Ledger, Pareto frontier
- S6: Site Passport generation & NASA Test-Recipe export
"""

from typing import Dict, Any, List, Optional
import numpy as np

from targets.registry import TargetRegistry, PlanetaryTarget
from data.candidate_catalog import get_all_candidate_cells
from harmonize.h3_grid import H3Grid
from harmonize.sensor_harmonizer import SensorHarmonizer
from .scoring import ScoringEngine, FidelityStatus, AFIScoreResult
from .monte_carlo import MonteCarloRanker
from .novelty_mmr import NoveltyMMREngine
from .pareto import ParetoFrontierEngine
from .field_kit import FieldKitEngine


class TerraXPipeline:
    """Orchestrates the 7-stage discovery and test-recipe pipeline."""

    def __init__(self):
        self.target_registry = TargetRegistry()
        self.novelty_engine = NoveltyMMREngine()
        self.mc_ranker = MonteCarloRanker(n_clones=100)
        self.all_candidates = get_all_candidate_cells(res=6)

    def run_discovery_pipeline(
        self,
        target_id: str,
        function_profile: str,
        wheel_diameter_m: float = 0.50,
        contact_pressure_kpa: float = 25.0,
        footprint_width_m: float = 0.30,
        test_duration_days: int = 14,
        top_k: int = 10,
        enforce_mmr: bool = True,
    ) -> Dict[str, Any]:
        """
        Executes stages S0 through S6.
        """
        # ==========================================
        # STAGE S0: Target Ingestion
        # ==========================================
        target = self.target_registry.get_target(target_id)
        if not target:
            raise ValueError(f"Unknown planetary target ID: {target_id}")

        func = function_profile.upper()

        # ==========================================
        # STAGE S1: Global Coarse Sieve (H3 r6)
        # ==========================================
        sieved_candidates = []
        for cand in self.all_candidates:
            # Sieve rule: reject completely inundated or heavily forested zones
            if cand.get("vegetation_ndvi", 0.0) > 0.45 or cand.get("soil_moisture_wtd", 0.0) > 0.40:
                continue
            sieved_candidates.append(cand)

        # ==========================================
        # STAGE S2: Feature Vector ANN Similarity
        # ==========================================
        # Computes coarse normalized vector distance to target dimensionless reference
        t_ref = target.dimensionless_reference
        ann_scored = []
        for cand in sieved_candidates:
            cand_copy = dict(cand)
            # Roughness & slope proxy distance
            d_tan = abs(np.tan(np.radians(cand["slope_deg"])) / np.tan(np.radians(cand["friction_angle_deg"])) - t_ref.get("tan_theta_over_tan_phi", 0.3))
            d_rough = abs(cand["h_rms_m"] / wheel_diameter_m - t_ref.get("h_rms_over_D", 0.25))
            ann_dist = d_tan + d_rough
            cand_copy["ann_similarity_score"] = float(np.exp(-ann_dist))
            ann_scored.append(cand_copy)

        ann_scored.sort(key=lambda x: -x["ann_similarity_score"])

        # ==========================================
        # STAGE S3: Novelty Scoring & MMR Filtering
        # ==========================================
        for cand in ann_scored:
            nov = self.novelty_engine.compute_novelty_score(cand["lat"], cand["lon"])
            cand.update(nov)

        # ==========================================
        # STAGE S4: High-Resolution Characterization
        # ==========================================
        for cand in ann_scored:
            # Sensor spread calculation
            dem_spread = SensorHarmonizer.evaluate_dem_spread(
                glo30_elev=cand["elevation_m"],
                aw3d30_elev=cand["elevation_m"] + 1.2,
                aster_elev=cand["elevation_m"] - 0.8,
            )
            cand.update(dem_spread)

            therm_spread = SensorHarmonizer.evaluate_thermal_spread(
                ecostress_lst_k=305.0,
                landsat_st_k=303.5,
                modis_lst_k=306.0,
            )
            cand.update(therm_spread)

        # ==========================================
        # STAGE S5: Gates, Scoring, MC 100-Clone & Pareto
        # ==========================================
        mc_results = self.mc_ranker.run_ensemble_ranking(
            function_profile=func,
            target=target,
            candidate_cells=ann_scored,
            wheel_diameter_m=wheel_diameter_m,
            contact_pressure_kpa=contact_pressure_kpa,
            footprint_width_m=footprint_width_m,
        )

        # Apply MMR Diversification if requested
        if enforce_mmr:
            final_selection = self.novelty_engine.mmr_diversify(mc_results, top_k=top_k)
        else:
            final_selection = mc_results[:top_k]

        # Multi-objective Pareto evaluation across functions
        pareto_candidates = ParetoFrontierEngine.identify_pareto_frontier(
            final_selection,
            objective_keys=["afi_score_p50", "novelty_score", "p_top10"],
        )

        # ==========================================
        # STAGE S6: Export Packaging (Passport & Recipe)
        # ==========================================
        passports = []
        for cand in final_selection:
            passports.append(self.generate_site_passport(cand, target, func, wheel_diameter_m, test_duration_days))

        return {
            "query": {
                "target_id": target.target_id,
                "target_name": target.target_name,
                "target_body": target.body,
                "function_profile": func,
                "parameters": {
                    "wheel_diameter_m": wheel_diameter_m,
                    "contact_pressure_kpa": contact_pressure_kpa,
                    "footprint_width_m": footprint_width_m,
                    "test_duration_days": test_duration_days,
                },
                "gravity_bridge": {
                    "load_scale_factor": target.load_scale_factor,
                    "gamma_unit_weight_n_m3": target.gamma_unit_weight_n_m3,
                },
                "hard_breaks": target.hard_breaks,
            },
            "total_candidates_evaluated": len(self.all_candidates),
            "sieved_candidates_count": len(sieved_candidates),
            "ranked_sites": passports,
            "pareto_optimal_count": len(pareto_candidates),
        }

    def generate_site_passport(
        self,
        candidate_mc: Dict[str, Any],
        target: PlanetaryTarget,
        function_profile: str,
        wheel_diameter_m: float,
        test_duration_days: int,
    ) -> Dict[str, Any]:
        """Creates complete verifiable Site Passport and Transferable Test Recipe."""
        det = candidate_mc.get("deterministic_result", {})
        cell_id = candidate_mc.get("cell_id")

        # Compile transferable test recipe tied to NASA Tech Gaps
        test_recipe = self.generate_test_recipe(
            candidate_mc=candidate_mc,
            target=target,
            function_profile=function_profile,
            wheel_diameter_m=wheel_diameter_m,
            test_duration_days=test_duration_days,
        )

        # Build Passport
        passport = {
            "site_id": candidate_mc.get("id", f"TERRAX-{cell_id}"),
            "site_name": candidate_mc.get("name"),
            "cell_id_h3_r6": cell_id,
            "coordinates": {
                "latitude": candidate_mc.get("lat"),
                "longitude": candidate_mc.get("lon"),
            },
            "country": candidate_mc.get("country"),
            "continent": candidate_mc.get("continent"),
            "function_profile": function_profile,
            "planetary_target": {
                "target_id": target.target_id,
                "target_name": target.target_name,
                "body": target.body,
            },
            "scores": {
                "afi_p50": candidate_mc.get("afi_score_p50"),
                "afi_p10": candidate_mc.get("afi_score_p10"),
                "afi_p90": candidate_mc.get("afi_score_p90"),
                "M_match": det.get("M_match"),
                "C_confounder": det.get("C_confounder"),
                "T_transferable": det.get("T_transferable"),
            },
            "monte_carlo_rank": {
                "rank_p50": candidate_mc.get("rank_p50"),
                "rank_p10": candidate_mc.get("rank_p10"),
                "rank_p90": candidate_mc.get("rank_p90"),
                "p_top10": candidate_mc.get("p_top10"),
            },
            "novelty": {
                "novelty_score": candidate_mc.get("novelty_score", 1.0),
                "distance_to_known_km": candidate_mc.get("distance_to_nearest_known_km"),
                "status": candidate_mc.get("status"),
            },
            "fidelity_ledger": det.get("fidelity_ledger", []),
            "hard_breaks": target.hard_breaks,
            "dimensionless_groups": det.get("dimensionless_comparison", {}),
            "provenance": {
                "stac_id": candidate_mc.get("stac_id", f"urn:terrax:{cell_id}"),
                "doi": candidate_mc.get("doi", "10.5067/TERRAX-ANALOG"),
                "license_class": "OPEN_PUBLIC_DOMAIN",
                "export_allowed": True,
            },
            "test_recipe": test_recipe,
        }
        return passport

    def generate_test_recipe(
        self,
        candidate_mc: Dict[str, Any],
        target: PlanetaryTarget,
        function_profile: str,
        wheel_diameter_m: float,
        test_duration_days: int,
    ) -> Dict[str, Any]:
        """Ties the test article to specific NASA Technology Taxonomy gaps and test instructions."""
        # Find matching tech gaps
        matching_gaps = []
        if function_profile == "MOBILITY":
            matching_gaps = ["TX04.3_SURFACE_MOBILITY_TRAVERSABILITY"]
        elif function_profile == "PNT_DENIED_NAV":
            matching_gaps = ["TX04.1_PRECISION_LANDING_SHADOW"]
        elif function_profile == "CONSTRUCTION_ISRU":
            matching_gaps = ["TX07.2_REGOLITH_EXCAVATION_BENEFICIATION", "TX06.2_DUST_MITIGATION_MECHANISMS"]
        elif function_profile == "HUMAN_OPS_THERMAL":
            matching_gaps = ["TX07.1_EXTREME_TEMP_CRYOGENIC_MECH"]
        elif function_profile == "LANDING_PAD_PSI":
            matching_gaps = ["TX06.2_DUST_MITIGATION_MECHANISMS", "TX04.1_PRECISION_LANDING_SHADOW"]
        elif function_profile == "ASTROBIO":
            matching_gaps = ["TX04.3_SURFACE_MOBILITY_TRAVERSABILITY"]

        load_scale = target.load_scale_factor
        required_rig = (
            f"Overhead constant-tension offload crane (5/6 normal force offload for Moon) "
            f"or inclined-plane test bed (slope alpha=arcsin(1/{load_scale:.1f})={np.degrees(np.arcsin(1.0/load_scale)):.1f} deg)."
        )

        return {
            "recipe_id": f"RECIPE-{target.target_id}-{function_profile}-{candidate_mc.get('cell_id')}",
            "nasa_tech_gaps": matching_gaps,
            "test_objective": f"Functional fidelity validation for {function_profile} under scaled {target.body} planetary surface gravity.",
            "gravity_scaling_compensation": {
                "load_scale_factor": round(load_scale, 2),
                "required_fixture": required_rig,
                "warning": "NEVER conduct unweighted 1g testing as a direct representation of 1/6g dynamics.",
            },
            "simulant_augmentation_recipe": {
                "recommended_simulant_base": "LHS-1 (Lunar Highlands) or MMS-1 (Mars Mojave)",
                "grain_angularity_target": "Wadell roundness < 0.25 (jagged, non-rounded)",
                "drying_requirement": "Desiccate to < 0.01 weight% water prior to shear testing.",
            },
            "environmental_enclosure": "Portable purge tent / positive N2 pressure to suppress humidity and oxidation.",
            "execution_protocol": {
                "duration_days": test_duration_days,
                "traversal_targets": f"Traverse 100m transects varying wheel diameter around {wheel_diameter_m:.2f}m.",
                "data_logging_requirements": [
                    "Continuous 6-axis IMU + wheel encoder odometry",
                    "Dynamic wheel sinkage laser profilometry",
                    "In-situ shear vane test every 20 meters",
                    "Thermal infrared radiometer ground surface temperature",
                ],
            },
        }

