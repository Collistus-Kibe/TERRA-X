"""
TERRA-X Geomorphology & Illumination Engine
Computes terrain slope, micro-roughness at wheel scale, horizon blocking / sky-view factor,
and rock size-frequency distributions (Cintala-Mouginis-Mark power-law).
"""

from typing import Dict, Any, List
import math
import numpy as np


class GeomorphologyEngine:
    """Terrain geomorphology, illumination and micro-topography analysis."""

    @staticmethod
    def estimate_boulder_density(
        cfa_fraction: float = 0.05,
        wheel_diameter_m: float = 0.50,
    ) -> Dict[str, Any]:
        """
        Estimates rock abundance and cumulative fractional area (CFA) covered by rocks
        larger than wheel diameter D using Golombek-Rapp-Cintala exponential model:
        F_k(D) = k * exp(-q(k) * D)
        """
        # CFA fraction typically ranges from 0.02 (smooth mare/plains) to 0.20 (rocky crater ejecta)
        k = max(0.01, min(0.35, cfa_fraction))
        q = 1.79 + 0.152 / k
        f_gt_D = k * math.exp(-q * wheel_diameter_m)
        rocks_per_100m2 = f_gt_D / (math.pi * (wheel_diameter_m / 2.0)**2 + 1e-4)

        return {
            "cfa_fraction": round(k, 3),
            "wheel_diameter_m": wheel_diameter_m,
            "fraction_rocks_exceeding_D": round(f_gt_D, 4),
            "rocks_per_100m2": round(rocks_per_100m2, 2),
            "hazard_rating": "HIGH" if f_gt_D > 0.08 else ("MODERATE" if f_gt_D > 0.03 else "LOW"),
        }

    @staticmethod
    def compute_horizon_elevation_profile(
        elevation_profile: List[float],
        distances_m: List[float],
    ) -> Dict[str, Any]:
        """
        Calculates horizon elevation angles across azimuths to determine
        the Horizon-Blocked Fraction (HBF) and Sky-View Factor (SVF).
        SVF = cos^2(theta_horizon_mean)
        HBF = 1 - SVF
        """
        if not elevation_profile or len(elevation_profile) != len(distances_m):
            return {"sky_view_factor": 0.85, "horizon_blocked_fraction": 0.15}

        angles_rad = []
        for z, d in zip(elevation_profile, distances_m):
            if d > 0:
                ang = math.atan(max(0.0, z) / d)
                angles_rad.append(ang)

        mean_horizon_rad = float(np.mean(angles_rad)) if angles_rad else 0.1
        # Upper hemisphere integral for conical / radially symmetric horizon
        svf = max(0.05, min(1.0, math.cos(mean_horizon_rad) ** 2))
        hbf = 1.0 - svf

        return {
            "mean_horizon_angle_deg": round(math.degrees(mean_horizon_rad), 2),
            "sky_view_factor": round(svf, 4),
            "horizon_blocked_fraction": round(hbf, 4),
        }

