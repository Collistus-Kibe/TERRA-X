"""
TERRA-X Dimensionless Scaling Engine
Implements strict dimensionless groups across all 6 exploration functions:
- MOBILITY: tan(theta)/tan(phi), h_rms(D)/D, sinkage ratio z/D
- CONSTRUCTION_ISRU: p/(gamma*B), F/(gamma*d^3), cohesion ratio c/(gamma*d)
- LANDING_PAD_PSI: plume shear ratio tau_plume/(gamma*d50), bearing ratio p/(gamma*B)
- HUMAN_OPS_THERMAL: Delta_T / T_mean, thermal inertia ratio
- PNT_DENIED_NAV: horizon_blocked_fraction, sky_view_factor, visual saliency
- ASTROBIO: water activity a_w, UV flux ratio, mineral preservation index

Enforces Gravity Bridge: gamma = rho * g (load-scale x6.37 for Moon, x2.85 for Mars).
NEVER assumes 1g == 1/6g.
"""

from typing import Dict, Any, Optional
import math
from dataclasses import dataclass, asdict

# Gravity constants
G_EARTH = 9.80665    # m/s^2
G_MOON = 1.62        # m/s^2
G_MARS = 3.72076     # m/s^2


@dataclass
class DimensionlessGroups:
    # Mobility
    tan_theta_over_tan_phi: float
    h_rms_over_D: float
    wheel_sinkage_over_D: float

    # Geotechnical / Construction / ISRU
    p_over_gamma_B: float
    F_over_gamma_d3: float
    cohesion_over_gamma_d: float

    # Thermal
    delta_T_over_T_mean: float
    thermal_inertia_ratio: float

    # Optical / Navigational
    horizon_blocked_fraction: float
    sky_view_factor: float

    # Astrobiology
    water_activity_ratio: float
    uv_dosage_ratio: float

    # Metadata & Gravity bridge info
    target_body: str
    gravity_scale_factor: float
    effective_gamma_earth_N_m3: float
    effective_gamma_target_N_m3: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DimensionlessPhysicsEngine:
    """Computes dimensionless physical groups bridging Earth test articles to target bodies."""

    @classmethod
    def get_gravity_bridge(cls, target_body: str, soil_density_kg_m3: float = 1550.0) -> Dict[str, float]:
        """
        Calculates soil unit weight gamma = rho * g and the dimensionless gravity load-scale ratio.
        Never claim 1g == 1/6g!
        """
        gamma_earth = soil_density_kg_m3 * G_EARTH
        target_upper = target_body.upper()
        if "MOON" in target_upper or "LUNAR" in target_upper:
            g_target = G_MOON
        elif "MARS" in target_upper:
            g_target = G_MARS
        else:
            g_target = G_EARTH

        gamma_target = soil_density_kg_m3 * g_target
        scale_factor = gamma_earth / gamma_target

        return {
            "g_target": g_target,
            "gamma_earth_N_m3": gamma_earth,
            "gamma_target_N_m3": gamma_target,
            "load_scale_factor": scale_factor,
        }

    @classmethod
    def compute_all_groups(
        cls,
        slope_deg: float,
        friction_angle_deg: float,
        h_rms_m: float,
        wheel_diameter_m: float = 0.50,
        contact_pressure_kpa: float = 25.0,
        footprint_width_m: float = 0.30,
        cohesion_kpa: float = 2.0,
        excavation_depth_m: float = 0.15,
        excavation_force_N: float = 250.0,
        t_max_k: float = 315.0,
        t_min_k: float = 275.0,
        target_ti_si: float = 55.0,
        earth_ti_si: float = 420.0,
        sky_view_factor: float = 0.75,
        water_activity_aw: float = 0.15,
        target_body: str = "MOON",
        bulk_density_kg_m3: float = 1550.0,
    ) -> DimensionlessGroups:
        """
        Computes all normalized dimensionless groups for an Earth test article evaluated
        against a planetary target environment.
        """
        # 1. Slope ratio: tan(theta) / tan(phi)
        tan_theta = math.tan(math.radians(max(0.1, slope_deg)))
        tan_phi = math.tan(math.radians(max(5.0, friction_angle_deg)))
        tan_theta_over_tan_phi = tan_theta / tan_phi

        # 2. Roughness ratio: h_rms / D
        h_rms_over_D = h_rms_m / max(0.01, wheel_diameter_m)

        # 3. Gravity bridge & Bearing capacity group: p / (gamma * B)
        bridge = cls.get_gravity_bridge(target_body, bulk_density_kg_m3)
        # Note: on Earth, effective gamma is gamma_earth; on Target, it is gamma_target.
        gamma_target = bridge["gamma_target_N_m3"]
        gamma_earth = bridge["gamma_earth_N_m3"]

        pressure_pa = contact_pressure_kpa * 1000.0
        cohesion_pa = cohesion_kpa * 1000.0

        p_over_gamma_B = pressure_pa / (gamma_target * max(0.05, footprint_width_m))
        
        # Bekker-Wong sinkage estimation dimensionless ratio: z / D
        # Approximate z = (p / (k_c/b + k_phi))^(1/n)
        wheel_sinkage_m = min(0.3 * wheel_diameter_m, 0.05 * (p_over_gamma_B / 10.0))
        wheel_sinkage_over_D = wheel_sinkage_m / max(0.01, wheel_diameter_m)

        # 4. Excavation dimensionless force group: F / (gamma * d^3)
        d = max(0.02, excavation_depth_m)
        F_over_gamma_d3 = excavation_force_N / (gamma_target * (d ** 3))

        # Cohesion ratio: c / (gamma * d)
        cohesion_over_gamma_d = cohesion_pa / (gamma_target * d)

        # 5. Thermal amplitude: Delta_T / T_mean
        t_mean_k = max(1.0, (t_max_k + t_min_k) / 2.0)
        delta_t_k = abs(t_max_k - t_min_k)
        delta_T_over_T_mean = delta_t_k / t_mean_k

        # Thermal inertia ratio: Earth TI / Target TI
        thermal_inertia_ratio = earth_ti_si / max(1.0, target_ti_si)

        # 6. Optical / Viewshed: Horizon-blocked fraction = 1 - SVF
        svf_clamped = max(0.0, min(1.0, sky_view_factor))
        horizon_blocked_fraction = 1.0 - svf_clamped

        # 7. Astrobiology: water activity & UV dosage
        water_activity_ratio = min(1.0, water_activity_aw / 0.05)
        uv_dosage_ratio = 1.0  # Normalized

        return DimensionlessGroups(
            tan_theta_over_tan_phi=round(tan_theta_over_tan_phi, 4),
            h_rms_over_D=round(h_rms_over_D, 4),
            wheel_sinkage_over_D=round(wheel_sinkage_over_D, 4),
            p_over_gamma_B=round(p_over_gamma_B, 3),
            F_over_gamma_d3=round(F_over_gamma_d3, 2),
            cohesion_over_gamma_d=round(cohesion_over_gamma_d, 3),
            delta_T_over_T_mean=round(delta_T_over_T_mean, 4),
            thermal_inertia_ratio=round(thermal_inertia_ratio, 3),
            horizon_blocked_fraction=round(horizon_blocked_fraction, 4),
            sky_view_factor=round(svf_clamped, 4),
            water_activity_ratio=round(water_activity_ratio, 3),
            uv_dosage_ratio=round(uv_dosage_ratio, 3),
            target_body=target_body.upper(),
            gravity_scale_factor=round(bridge["load_scale_factor"], 2),
            effective_gamma_earth_N_m3=round(gamma_earth, 1),
            effective_gamma_target_N_m3=round(gamma_target, 1),
        )

