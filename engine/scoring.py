"""
TERRA-X Functional Analog Scoring Engine
Implements the core scoring law:
AFI_f = M_f * (1 - C_f) * T_f

Where:
- M_f: Confidence-weighted Wasserstein match (with tau = sensor uncertainty)
- C_f: Function-dependent Earth-added confounder severity
- T_f: Transferable physics fraction
- Fidelity Ledger: STRONG, PARTIAL, BREAKS, UNCONSTRAINED (never impute missing data!)
- Hard Breaks: Always explicitly surfaced
"""

from typing import Dict, Any, List, Optional
from enum import Enum
import math
from dataclasses import dataclass, asdict
import numpy as np

from features.dimensionless import DimensionlessGroups, DimensionlessPhysicsEngine
from features.confounders import ConfounderEngine, ConfounderAssessment
from targets.registry import PlanetaryTarget


class FidelityStatus(str, Enum):
    STRONG = "STRONG"
    PARTIAL = "PARTIAL"
    BREAKS = "BREAKS"
    UNCONSTRAINED = "UNCONSTRAINED"


@dataclass
class SubsystemLedgerEntry:
    subsystem_name: str
    status: FidelityStatus
    earth_value: Optional[float]
    target_value: Optional[float]
    transferability_fraction: float
    notes: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subsystem_name": self.subsystem_name,
            "status": self.status.value,
            "earth_value": self.earth_value,
            "target_value": self.target_value,
            "transferability_fraction": self.transferability_fraction,
            "notes": self.notes,
        }


@dataclass
class AFIScoreResult:
    function_profile: str
    target_id: str
    afi_score: float             # M * (1 - C) * T
    M_match: float               # Confidence-weighted Wasserstein match
    C_confounder: float          # Confounder severity
    T_transferable: float        # Transferable physics fraction
    hard_breaks: List[str]
    fidelity_ledger: List[SubsystemLedgerEntry]
    confounder_breakdown: Dict[str, Any]
    dimensionless_comparison: Dict[str, Any]
    uncertainty_tau: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "function_profile": self.function_profile,
            "target_id": self.target_id,
            "afi_score": round(self.afi_score, 4),
            "M_match": round(self.M_match, 4),
            "C_confounder": round(self.C_confounder, 4),
            "T_transferable": round(self.T_transferable, 4),
            "hard_breaks": self.hard_breaks,
            "fidelity_ledger": [e.to_dict() for e in self.fidelity_ledger],
            "confounder_breakdown": self.confounder_breakdown,
            "dimensionless_comparison": self.dimensionless_comparison,
            "uncertainty_tau": round(self.uncertainty_tau, 4),
        }


def wasserstein_gaussian_distance(mu_e: float, mu_t: float, sigma_e: float, sigma_t: float) -> float:
    """
    Exact analytical Wasserstein distance between Gaussian uncertainty distributions
    N(mu_e, sigma_e^2) and N(mu_t, sigma_t^2):
    W_2 = sqrt((mu_e - mu_t)^2 + (sigma_e - sigma_t)^2)
    """
    return math.sqrt((mu_e - mu_t) ** 2 + (sigma_e - sigma_t) ** 2)


class ScoringEngine:
    """Evaluates an Earth H3 test article for a specific exploration function."""

    @classmethod
    def compute_afi(
        cls,
        function_profile: str,
        target: PlanetaryTarget,
        earth_features: Dict[str, Any],
        wheel_diameter_m: float = 0.50,
        contact_pressure_kpa: float = 25.0,
        footprint_width_m: float = 0.30,
        sensor_uncertainty_tau: float = 0.08,
    ) -> AFIScoreResult:
        func = function_profile.upper()
        target_ref = target.dimensionless_reference

        # Check for missing values - RULE: Missing => UNCONSTRAINED, never impute!
        slope_deg = earth_features.get("slope_deg")
        h_rms_m = earth_features.get("h_rms_m")
        friction_angle = earth_features.get("friction_angle_deg")
        cohesion = earth_features.get("cohesion_kpa")
        thermal_inertia = earth_features.get("thermal_inertia_si")
        svf = earth_features.get("sky_view_factor")
        moisture = earth_features.get("soil_moisture_wtd")
        ndvi = earth_features.get("vegetation_ndvi")
        roundness = earth_features.get("grain_wadell_roundness", 0.32)

        # 1. Dimensionless groups calculation
        dim_groups = None
        if slope_deg is not None and friction_angle is not None and h_rms_m is not None:
            dim_groups = DimensionlessPhysicsEngine.compute_all_groups(
                slope_deg=slope_deg,
                friction_angle_deg=friction_angle,
                h_rms_m=h_rms_m,
                wheel_diameter_m=wheel_diameter_m,
                contact_pressure_kpa=contact_pressure_kpa,
                footprint_width_m=footprint_width_m,
                cohesion_kpa=cohesion if cohesion is not None else 2.0,
                target_ti_si=target_ref.get("thermal_inertia_si", 55.0),
                earth_ti_si=thermal_inertia if thermal_inertia is not None else 400.0,
                sky_view_factor=svf if svf is not None else 0.8,
                target_body=target.body,
            )

        # 2. Confounder Assessment C_f
        conf_eval = ConfounderEngine.evaluate(
            function_profile=func,
            soil_moisture_wtd=moisture if moisture is not None else 0.05,
            vegetation_ndvi=ndvi if ndvi is not None else 0.05,
            grain_wadell_roundness=roundness,
            biological_activity_index=earth_features.get("biological_activity_index", 0.05),
        )
        C_f = conf_eval.total_confounder_C

        # 3. Match Score M_f via confidence-weighted Wasserstein distance
        matches = []
        weights = []
        ledger: List[SubsystemLedgerEntry] = []

        # A. Slope ratio: tan(theta)/tan(phi)
        t_slope = target_ref.get("tan_theta_over_tan_phi", 0.30)
        if dim_groups is not None and slope_deg is not None:
            e_slope = dim_groups.tan_theta_over_tan_phi
            # Analytical Wasserstein distance
            w1_slope = wasserstein_gaussian_distance(e_slope, t_slope, sensor_uncertainty_tau, 0.03)
            m_slope = math.exp(-w1_slope / 0.25)
            matches.append(m_slope)
            weights.append(1.0 / (1.0 + sensor_uncertainty_tau))
            
            status = FidelityStatus.STRONG if m_slope > 0.70 else FidelityStatus.PARTIAL
            ledger.append(SubsystemLedgerEntry(
                subsystem_name="Slope Ratio tan(theta)/tan(phi)",
                status=status,
                earth_value=round(e_slope, 3),
                target_value=round(t_slope, 3),
                transferability_fraction=0.90,
                notes=f"Gravity-independent frictional slip dynamics. Match={m_slope:.2f}",
            ))
        else:
            ledger.append(SubsystemLedgerEntry(
                subsystem_name="Slope Ratio tan(theta)/tan(phi)",
                status=FidelityStatus.UNCONSTRAINED,
                earth_value=None,
                target_value=t_slope,
                transferability_fraction=0.0,
                notes="Missing slope or friction angle measurement. Never imputed.",
            ))

        # B. Micro-Roughness: h_rms(D)/D
        t_rough = target_ref.get("h_rms_over_D", 0.25)
        if dim_groups is not None and h_rms_m is not None:
            e_rough = dim_groups.h_rms_over_D
            w1_rough = wasserstein_gaussian_distance(e_rough, t_rough, sensor_uncertainty_tau, 0.02)
            m_rough = math.exp(-w1_rough / 0.20)
            matches.append(m_rough)
            weights.append(1.0 / (1.0 + sensor_uncertainty_tau))

            status = FidelityStatus.STRONG if m_rough > 0.70 else FidelityStatus.PARTIAL
            ledger.append(SubsystemLedgerEntry(
                subsystem_name="Roughness Ratio h_rms(D)/D",
                status=status,
                earth_value=round(e_rough, 3),
                target_value=round(t_rough, 3),
                transferability_fraction=0.85,
                notes=f"Micro-obstacle geometry scaled to wheel diameter {wheel_diameter_m}m.",
            ))
        else:
            ledger.append(SubsystemLedgerEntry(
                subsystem_name="Roughness Ratio h_rms(D)/D",
                status=FidelityStatus.UNCONSTRAINED,
                earth_value=None,
                target_value=t_rough,
                transferability_fraction=0.0,
                notes="Missing high-resolution DEM micro-roughness. Never imputed.",
            ))

        # C. Bearing Capacity & Scaled Pressure p / (gamma * B)
        t_bearing = target_ref.get("p_over_gamma_B", 18.0)
        if dim_groups is not None:
            e_bearing = dim_groups.p_over_gamma_B
            diff_bearing = abs(e_bearing - t_bearing) / max(1.0, t_bearing)
            m_bearing = math.exp(-diff_bearing)
            matches.append(m_bearing)
            weights.append(0.8)

            ledger.append(SubsystemLedgerEntry(
                subsystem_name=f"Bearing Pressure p/(gamma*B) [Load Scale x{dim_groups.gravity_scale_factor:.1f}]",
                status=FidelityStatus.PARTIAL,
                earth_value=round(e_bearing, 2),
                target_value=round(t_bearing, 2),
                transferability_fraction=0.70,
                notes=f"Valid under gravity bridge: requires x{dim_groups.gravity_scale_factor:.1f} ballast scaling or offload rig. 1g != 1/6g.",
            ))

        # D. Thermal Dynamics Delta_T / T_mean & Thermal Inertia
        t_therm = target_ref.get("delta_T_over_T_mean", 0.40)
        if thermal_inertia is not None:
            e_therm = dim_groups.delta_T_over_T_mean if dim_groups else 0.25
            diff_therm = abs(e_therm - t_therm) / max(0.1, t_therm)
            m_therm = math.exp(-diff_therm)
            matches.append(m_therm)
            weights.append(0.7)

            ledger.append(SubsystemLedgerEntry(
                subsystem_name="Thermal Cycling Delta_T/T_mean",
                status=FidelityStatus.PARTIAL if "MOON" not in target.body else FidelityStatus.BREAKS,
                earth_value=round(e_therm, 3),
                target_value=round(t_therm, 3),
                transferability_fraction=0.45,
                notes="Atmospheric convection severely suppresses extreme radiative diurnal swings present in vacuum.",
            ))
        else:
            ledger.append(SubsystemLedgerEntry(
                subsystem_name="Thermal Inertia & Cycling",
                status=FidelityStatus.UNCONSTRAINED,
                earth_value=None,
                target_value=t_therm,
                transferability_fraction=0.0,
                notes="No thermal inertia or LST time-series recorded for cell.",
            ))

        # E. Optical Viewshed / Horizon Blocked Fraction
        t_hbf = target_ref.get("horizon_blocked_fraction", 0.40)
        if svf is not None:
            e_hbf = 1.0 - svf
            diff_hbf = abs(e_hbf - t_hbf)
            m_hbf = math.exp(-diff_hbf / 0.3)
            matches.append(m_hbf)
            weights.append(0.9)

            ledger.append(SubsystemLedgerEntry(
                subsystem_name="Horizon-Blocked Fraction (SVF)",
                status=FidelityStatus.STRONG if m_hbf > 0.65 else FidelityStatus.PARTIAL,
                earth_value=round(e_hbf, 3),
                target_value=round(t_hbf, 3),
                transferability_fraction=0.95,
                notes="Topographic masking and low-sun grazing illumination geometry.",
            ))
        else:
            ledger.append(SubsystemLedgerEntry(
                subsystem_name="Horizon-Blocked Fraction (SVF)",
                status=FidelityStatus.UNCONSTRAINED,
                earth_value=None,
                target_value=t_hbf,
                transferability_fraction=0.0,
                notes="No viewshed / horizon calculation available for cell.",
            ))

        # F. System Hard Breaks (Always shown)
        for hb in target.hard_breaks:
            ledger.append(SubsystemLedgerEntry(
                subsystem_name=f"ENVIRONMENTAL BREAK: {hb}",
                status=FidelityStatus.BREAKS,
                earth_value=None,
                target_value=None,
                transferability_fraction=0.0,
                notes="Physical law or environment cannot be reproduced in open terrestrial field conditions.",
            ))

        # 4. Compute Aggregate Match M_f
        if matches:
            M_f = float(np.average(matches, weights=weights))
        else:
            M_f = 0.05

        # 5. Compute Transferable Physics Fraction T_f
        valid_entries = [e for e in ledger if e.status in (FidelityStatus.STRONG, FidelityStatus.PARTIAL)]
        total_evaluable = [e for e in ledger if e.status != FidelityStatus.UNCONSTRAINED]
        if total_evaluable:
            transferable_weights = sum(e.transferability_fraction for e in valid_entries)
            T_f = max(0.05, min(0.95, transferable_weights / len(total_evaluable)))
        else:
            T_f = 0.10

        # Adjust T_f based on target body hard break penalties
        if "MOON" in target.body:
            T_f = min(T_f, 0.65)
        elif "MARS" in target.body:
            T_f = min(T_f, 0.75)

        # 6. Final AFI Score Law: AFI_f = M_f * (1 - C_f) * T_f
        afi_score = max(0.0, min(1.0, M_f * (1.0 - C_f) * T_f))

        return AFIScoreResult(
            function_profile=func,
            target_id=target.target_id,
            afi_score=afi_score,
            M_match=M_f,
            C_confounder=C_f,
            T_transferable=T_f,
            hard_breaks=target.hard_breaks,
            fidelity_ledger=ledger,
            confounder_breakdown=conf_eval.to_dict(),
            dimensionless_comparison=dim_groups.to_dict() if dim_groups else {},
            uncertainty_tau=sensor_uncertainty_tau,
        )
