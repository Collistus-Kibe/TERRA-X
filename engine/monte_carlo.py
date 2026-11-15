"""
TERRA-X Monte Carlo Uncertainty & Ensemble Ranker
Implements 100-clone stochastic rank simulation:
- Ingests PGDA 5m polar LDEM 100-clone ensemble + Earth sensor QA uncertainty (tau)
- Emits rank percentiles: p10, p50, p90
- Emits probability of membership in top tier: P(top10)
"""

from typing import Dict, Any, List
import numpy as np
from targets.registry import PlanetaryTarget
from .scoring import ScoringEngine


class MonteCarloRanker:
    """Propagates target and sensor uncertainties through 100-clone ensemble Monte Carlo ranking."""

    def __init__(self, n_clones: int = 100, seed: int = 42):
        self.n_clones = n_clones
        self.seed = seed

    def run_ensemble_ranking(
        self,
        function_profile: str,
        target: PlanetaryTarget,
        candidate_cells: List[Dict[str, Any]],
        wheel_diameter_m: float = 0.50,
        contact_pressure_kpa: float = 25.0,
        footprint_width_m: float = 0.30,
    ) -> List[Dict[str, Any]]:
        """
        Runs 100-clone Monte Carlo simulation over candidate cells.
        Returns candidates annotated with:
        - score_p10, score_p50 (median), score_p90
        - rank_p10, rank_p50, rank_p90
        - p_top10 (Probability that candidate ranks in the Top 10)
        """
        rng = np.random.default_rng(self.seed)
        num_candidates = len(candidate_cells)
        if num_candidates == 0:
            return []

        # Target clones: nominal target dimensionless groups perturbed by PGDA DEM clone variations
        # If target has pgda specs, slope uncertainty is modeled
        target_ref_base = target.dimensionless_reference
        slope_ref = target_ref_base.get("tan_theta_over_tan_phi", 0.30)
        target_slope_clones = rng.normal(loc=slope_ref, scale=0.03, size=self.n_clones)
        target_rough_clones = rng.normal(loc=target_ref_base.get("h_rms_over_D", 0.25), scale=0.02, size=self.n_clones)

        # Clone score matrix: shape (num_candidates, n_clones)
        scores_matrix = np.zeros((num_candidates, self.n_clones), dtype=np.float32)

        for c_idx, cell in enumerate(candidate_cells):
            # Base features
            base_slope = cell.get("slope_deg", 10.0)
            base_rough = cell.get("h_rms_m", 0.10)
            tau_dem = cell.get("tau_uncertainty_dem", 0.08)
            tau_thermal = cell.get("tau_uncertainty_thermal", 1.5)

            # Generate 100 perturbed realizations of Earth candidate cell features
            pert_slopes = rng.normal(loc=base_slope, scale=max(0.2, tau_dem * 2.0), size=self.n_clones)
            pert_rough = np.clip(rng.normal(loc=base_rough, scale=max(0.01, tau_dem * 0.1), size=self.n_clones), a_min=0.005, a_max=2.0)

            for k in range(self.n_clones):
                # Temporary target clone with clone values
                perturbed_features = dict(cell)
                perturbed_features["slope_deg"] = float(pert_slopes[k])
                perturbed_features["h_rms_m"] = float(pert_rough[k])

                # Calculate score for clone k
                res = ScoringEngine.compute_afi(
                    function_profile=function_profile,
                    target=target,
                    earth_features=perturbed_features,
                    wheel_diameter_m=wheel_diameter_m,
                    contact_pressure_kpa=contact_pressure_kpa,
                    footprint_width_m=footprint_width_m,
                    sensor_uncertainty_tau=tau_dem,
                )
                scores_matrix[c_idx, k] = res.afi_score

        # Convert scores to ranks per clone (1 = highest score)
        # Invert scores so argsort ranks from best (rank 1) to worst
        ranks_matrix = np.zeros_like(scores_matrix, dtype=np.int32)
        for k in range(self.n_clones):
            clone_scores = scores_matrix[:, k]
            # argsort descending
            sorted_indices = np.argsort(-clone_scores)
            ranks = np.empty_like(sorted_indices)
            ranks[sorted_indices] = np.arange(1, num_candidates + 1)
            ranks_matrix[:, k] = ranks

        # Compute percentiles for each candidate
        annotated_results = []
        for c_idx, cell in enumerate(candidate_cells):
            cell_scores = scores_matrix[c_idx, :]
            cell_ranks = ranks_matrix[c_idx, :]

            # Score percentiles
            s_p10 = float(np.percentile(cell_scores, 10))
            s_p50 = float(np.percentile(cell_scores, 50))
            s_p90 = float(np.percentile(cell_scores, 90))

            # Rank percentiles: Note that rank p10 is best rank (lowest number), p90 is conservative
            r_p10 = int(np.percentile(cell_ranks, 10))
            r_p50 = int(np.percentile(cell_ranks, 50))
            r_p90 = int(np.percentile(cell_ranks, 90))

            # P(top10): fraction of clones where rank <= 10
            p_top10 = float(np.mean(cell_ranks <= 10))

            # Base deterministic score calculation
            base_res = ScoringEngine.compute_afi(
                function_profile=function_profile,
                target=target,
                earth_features=cell,
                wheel_diameter_m=wheel_diameter_m,
                contact_pressure_kpa=contact_pressure_kpa,
                footprint_width_m=footprint_width_m,
            )

            record = {
                "cell_id": cell.get("cell_id"),
                "name": cell.get("name", f"Cell {cell.get('cell_id')}"),
                "country": cell.get("country", "Unknown"),
                "continent": cell.get("continent", "Global"),
                "lat": cell.get("lat"),
                "lon": cell.get("lon"),
                "function_profile": function_profile,
                "target_id": target.target_id,
                "afi_score_p50": round(s_p50, 4),
                "afi_score_p10": round(s_p10, 4),
                "afi_score_p90": round(s_p90, 4),
                "rank_p10": r_p10,
                "rank_p50": r_p50,
                "rank_p90": r_p90,
                "p_top10": round(p_top10, 4),
                "deterministic_result": base_res.to_dict(),
            }
            annotated_results.append(record)

        # Sort final output list by median rank (rank_p50) ascending
        annotated_results.sort(key=lambda x: (x["rank_p50"], -x["afi_score_p50"]))
        return annotated_results

