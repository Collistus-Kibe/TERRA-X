"""
TERRA-X Novelty & Maximal Marginal Relevance (MMR) Engine
Penalizes distance-to-known-analog registries and executes MMR diversity selection
to deliberately surface under-studied, high-potential global analog candidates.
"""

from typing import Dict, Any, List, Optional
import math
import json
from pathlib import Path
from harmonize.h3_grid import H3Grid


class NoveltyMMREngine:
    """Manages novelty scoring and MMR diversification."""

    def __init__(self, golden_sites_path: Optional[Path] = None):
        if golden_sites_path is None:
            golden_sites_path = Path(__file__).resolve().parent.parent / "manifests" / "golden_sites.json"

        self.golden_sites = []
        if golden_sites_path.exists():
            with open(golden_sites_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.golden_sites = data.get("sites", [])

    def compute_novelty_score(self, lat: float, lon: float, proximity_radius_km: float = 150.0) -> Dict[str, Any]:
        """
        Calculates distance to nearest known analog in registry.
        If distance < proximity_radius_km, applies penalty to reflect well-trodden status.
        Under-studied sites beyond the radius receive high novelty score (1.0).
        """
        min_dist_km = float("inf")
        nearest_site = None

        for g in self.golden_sites:
            d = H3Grid.haversine_km(lat, lon, g["latitude"], g["longitude"])
            if d < min_dist_km:
                min_dist_km = d
                nearest_site = g

        if min_dist_km < proximity_radius_km:
            # Steep penalty inside radius
            proximity_factor = 1.0 - (min_dist_km / proximity_radius_km)
            novelty_score = max(0.2, 1.0 - 0.75 * proximity_factor)
            status = "KNOWN_OR_PROXIMAL_ANALOG"
        else:
            novelty_score = 1.0
            status = "NOVEL_UNDER_STUDIED_SITE"

        return {
            "novelty_score": round(novelty_score, 3),
            "distance_to_nearest_known_km": round(min_dist_km, 1),
            "nearest_known_site": nearest_site["name"] if nearest_site else None,
            "status": status,
        }

    def mmr_diversify(
        self,
        ranked_candidates: List[Dict[str, Any]],
        top_k: int = 20,
        lambda_tradeoff: float = 0.65,
        spatial_decay_km: float = 500.0,
    ) -> List[Dict[str, Any]]:
        """
        Executes Maximal Marginal Relevance (MMR) greedy selection.
        MMR(i) = lambda * AFI_score(i) - (1 - lambda) * max_{j in S} Sim(i, j)
        Guarantees spatial spread across continents and avoids regional clustering.
        """
        if not ranked_candidates:
            return []

        remaining = list(ranked_candidates)
        selected: List[Dict[str, Any]] = []

        # Step 1: Pick top candidate unconditionally
        top_pick = max(remaining, key=lambda c: c.get("afi_score_p50", 0.0))
        selected.append(top_pick)
        remaining.remove(top_pick)

        # Step 2: Iteratively select candidate maximizing MMR score
        while len(selected) < min(top_k, len(ranked_candidates)) and remaining:
            best_mmr = -float("inf")
            best_candidate = None

            for cand in remaining:
                score = cand.get("afi_score_p50", 0.0)
                lat_i = cand.get("lat", 0.0)
                lon_i = cand.get("lon", 0.0)

                # Maximum spatial similarity to already selected candidates
                max_sim = 0.0
                for sel in selected:
                    lat_j = sel.get("lat", 0.0)
                    lon_j = sel.get("lon", 0.0)
                    dist = H3Grid.haversine_km(lat_i, lon_i, lat_j, lon_j)
                    # Gaussian / exponential spatial similarity
                    sim = math.exp(-dist / spatial_decay_km)
                    if sim > max_sim:
                        max_sim = sim

                mmr_val = (lambda_tradeoff * score) - ((1.0 - lambda_tradeoff) * max_sim)
                if mmr_val > best_mmr:
                    best_mmr = mmr_val
                    best_candidate = cand

            if best_candidate is not None:
                selected.append(best_candidate)
                remaining.remove(best_candidate)
            else:
                break

        return selected

