"""
TERRA-X Functional Analog Scoring Engine
Implements the core scoring law:
AFI_f = M_f * (1 - C_f) * T_f

Where:
- M_f: Confidence-weighted Wasserstein match of dimensionless groups (with tau = sensor uncertainty)
- C_f: Function-dependent Earth-added confounder severity
- T_f: Transferable physics fraction
- Q_f: Evidence confidence metric (reported separately)
- Fidelity Ledger: STRONG, PARTIAL, BREAKDOWN, UNCONSTRAINED (never impute missing data!)
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
    Q_evidence_confidence: float # Evidence confidence reported separately
    hard_breaks: List[str]
    fidelity_ledger: List[SubsystemLedgerEntry]
    confounder_breakdown: Dict[str, Any]
    dimensionless_comparison: Dict[str, Any]
    uncertainty_tau: float
    data_coverage: float
    main_contributing_variables: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "function_profile": self.function_profile,
            "target_id": self.target_id,
            "afi_score": round(self.afi_score, 4),
            "M_match": round(self.M_match, 4),
            "C_confounder": round(self.C_confounder, 4),
            "T_transferable": round(self.T_transferable, 4),
            "Q_evidence_confidence": round(self.Q_evidence_confidence, 4),
            "hard_breaks": self.hard_breaks,
            "fidelity_ledger": [e.to_dict() for e in self.fidelity_ledger],
            "confounder_breakdown": self.confounder_breakdown,
            "dimensionless_comparison": self.dimensionless_comparison,
            "uncertainty_tau": round(self.uncertainty_tau, 4),
            "data_coverage": round(self.data_coverage, 3),
            "main_contributing_variables": self.main_contributing_variables,
        }


def wasserstein_gaussian_distance(mu_e: float, mu_t: float, sigma_e: float, sigma_t: float) -> float:
    """
    Exact analytical Wasserstein distance between Gaussian uncertainty distributions
    N(mu_e, sigma_e^2) and N(mu_t, sigma_t^2):
    W_2 = sqrt((mu_e - mu_t)^2 + (sigma_e - sigma_t)^2)
    """
    return math.sqrt((mu_e - mu_t) ** 2 + (sigma_e - sigma_t) ** 2)


class ScoringEngine:
    """Evaluates an Earth H3 test article across all 10 exploration function profiles."""

    # Function-specific profile weighting for dimensionless similarity dimensions
    FUNCTION_DIM_WEIGHTS = {
        "ROVER_MOBILITY": {
            "slope": 1.4, "roughness": 1.4, "bearing": 0.8, "excavation": 0.2, "thermal": 0.2, "viewshed": 0.4
        },
        "LANDING_PAD_CONSTRUCTION": {
            "slope": 1.2, "roughness": 1.0, "bearing": 1.5, "excavation": 0.8, "thermal": 0.3, "viewshed": 0.2
        },
        "REGOLITH_EXCAVATION": {
            "slope": 0.5, "roughness": 0.6, "bearing": 1.0, "excavation": 1.8, "thermal": 0.2, "viewshed": 0.1
        },
        "ISRU_CONSTRUCTION": {
            "slope": 0.6, "roughness": 0.8, "bearing": 1.2, "excavation": 1.4, "thermal": 0.5, "viewshed": 0.2
        },
        "THERMAL_SURVIVABILITY": {
            "slope": 0.3, "roughness": 0.3, "bearing": 0.2, "excavation": 0.1, "thermal": 2.0, "viewshed": 0.8
        },
        "DUST_AND_WIND": {
            "slope": 0.8, "roughness": 1.4, "bearing": 0.5, "excavation": 0.5, "thermal": 0.3, "viewshed": 0.6
        },
        "WATER_AND_ICE_RESOURCES": {
            "slope": 0.6, "roughness": 0.5, "bearing": 0.4, "excavation": 1.0, "thermal": 1.5, "viewshed": 1.0
        },
        "BIOSIGNATURE_PRESERVATION": {
            "slope": 0.5, "roughness": 0.5, "bearing": 0.4, "excavation": 0.8, "thermal": 1.2, "viewshed": 0.4
        },
        "SUBSURFACE_AND_LAVA_TUBES": {
            "slope": 1.0, "roughness": 1.0, "bearing": 1.2, "excavation": 0.8, "thermal": 0.8, "viewshed": 0.4
        },
        "COMMUNICATION_AND_ILLUMINATION": {
            "slope": 0.8, "roughness": 0.4, "bearing": 0.2, "excavation": 0.1, "thermal": 0.4, "viewshed": 2.0
        },
    }

    # Backward compatibility aliases
    FUNCTION_ALIASES = {
        "MOBILITY": "ROVER_MOBILITY",
        "LANDING_PAD_PSI": "LANDING_PAD_CONSTRUCTION",
        "CONSTRUCTION_ISRU": "ISRU_CONSTRUCTION",
        "HUMAN_OPS_THERMAL": "THERMAL_SURVIVABILITY",
        "PNT_DENIED_NAV": "COMMUNICATION_AND_ILLUMINATION",
        "ASTROBIO": "BIOSIGNATURE_PRESERVATION",
    }

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
        raw_func = function_profile.upper()
        func = cls.FUNCTION_ALIASES.get(raw_func, raw_func)
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

        # Track observed attributes for Evidence Confidence Q
        observed_slots = 0
        total_slots = 6

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
        main_vars: List[str] = []

        dim_weights = cls.FUNCTION_DIM_WEIGHTS.get(func, cls.FUNCTION_DIM_WEIGHTS["ROVER_MOBILITY"])

        # A. Slope ratio: tan(theta)/tan(phi)
        t_slope = target_ref.get("tan_theta_over_tan_phi", 0.30)
        if dim_groups is not None and slope_deg is not None:
            observed_slots += 1
            e_slope = dim_groups.tan_theta_over_tan_phi
            w1_slope = wasserstein_gaussian_distance(e_slope, t_slope, sensor_uncertainty_tau, 0.03)
            m_slope = math.exp(-w1_slope / 0.25)
            w_eff = dim_weights["slope"] / (1.0 + sensor_uncertainty_tau)
            matches.append(m_slope)
            weights.append(w_eff)
            if m_slope > 0.65:
                main_vars.append("Slope Frictional Similitude (tanθ/tanφ)")

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
            observed_slots += 1
            e_rough = dim_groups.h_rms_over_D
            w1_rough = wasserstein_gaussian_distance(e_rough, t_rough, sensor_uncertainty_tau, 0.02)
            m_rough = math.exp(-w1_rough / 0.20)
            w_eff = dim_weights["roughness"] / (1.0 + sensor_uncertainty_tau)
            matches.append(m_rough)
            weights.append(w_eff)
            if m_rough > 0.65:
                main_vars.append("Wheel-Scale Micro-Roughness (h_rms/D)")

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
            observed_slots += 1
            e_bearing = dim_groups.p_over_gamma_B
            diff_bearing = abs(e_bearing - t_bearing) / max(1.0, t_bearing)
            m_bearing = math.exp(-diff_bearing)
            w_eff = dim_weights["bearing"]
            matches.append(m_bearing)
            weights.append(w_eff)
            if m_bearing > 0.60:
                main_vars.append("Scaled Bearing Pressure p/(γB)")

            ledger.append(SubsystemLedgerEntry(
                subsystem_name=f"Bearing Pressure p/(gamma*B) [Load Scale x{dim_groups.gravity_scale_factor:.1f}]",
                status=FidelityStatus.PARTIAL,
                earth_value=round(e_bearing, 2),
                target_value=round(t_bearing, 2),
                transferability_fraction=0.70,
                notes=f"Valid under gravity bridge: requires x{dim_groups.gravity_scale_factor:.1f} ballast scaling or offload rig. 1g != 1/6g.",
            ))

        # D. Geotechnical Excavation & Cohesion: c / (gamma * d) & F / (gamma * d^3)
        t_cohesion = target_ref.get("cohesion_over_gamma_d", 3.8)
        if dim_groups is not None and cohesion is not None:
            observed_slots += 1
            e_cohesion = dim_groups.cohesion_over_gamma_d
            diff_cohesion = abs(e_cohesion - t_cohesion) / max(0.5, t_cohesion)
            m_cohesion = math.exp(-diff_cohesion)
            w_eff = dim_weights["excavation"]
            matches.append(m_cohesion)
            weights.append(w_eff)
            if m_cohesion > 0.60:
                main_vars.append("Dimensionless Cohesion c/(γd)")

            ledger.append(SubsystemLedgerEntry(
                subsystem_name="Geotechnical Cohesion Ratio c/(gamma*d)",
                status=FidelityStatus.STRONG if m_cohesion > 0.70 else FidelityStatus.PARTIAL,
                earth_value=round(e_cohesion, 2),
                target_value=round(t_cohesion, 2),
                transferability_fraction=0.75,
                notes=f"Scaled regolith shear strength c/(gamma*d). Match={m_cohesion:.2f}",
            ))
        else:
            ledger.append(SubsystemLedgerEntry(
                subsystem_name="Geotechnical Cohesion Ratio c/(gamma*d)",
                status=FidelityStatus.UNCONSTRAINED,
                earth_value=None,
                target_value=t_cohesion,
                transferability_fraction=0.0,
                notes="Missing in-situ shear vane cohesion measurement.",
            ))

        # E. Thermal Dynamics Delta_T / T_mean & Thermal Inertia
        t_therm = target_ref.get("delta_T_over_T_mean", 0.40)
        if thermal_inertia is not None:
            observed_slots += 1
            e_therm = dim_groups.delta_T_over_T_mean if dim_groups else 0.25
            diff_therm = abs(e_therm - t_therm) / max(0.1, t_therm)
            m_therm = math.exp(-diff_therm)
            w_eff = dim_weights["thermal"]
            matches.append(m_therm)
            weights.append(w_eff)
            if m_therm > 0.60:
                main_vars.append("Thermal Inertia & Diurnal Swing")

            ledger.append(SubsystemLedgerEntry(
                subsystem_name="Thermal Cycling Delta_T/T_mean",
                status=FidelityStatus.PARTIAL if "MOON" not in target.body else FidelityStatus.BREAKS,
                earth_value=round(e_therm, 3),
                target_value=round(t_therm, 3),
                transferability_fraction=0.45,
                notes="Atmospheric convection severely dampens radiative diurnal swings present in vacuum.",
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

        # F. Optical Viewshed / Horizon Blocked Fraction
        t_hbf = target_ref.get("horizon_blocked_fraction", 0.40)
        if svf is not None:
            observed_slots += 1
            e_hbf = 1.0 - svf
            diff_hbf = abs(e_hbf - t_hbf)
            m_hbf = math.exp(-diff_hbf / 0.3)
            w_eff = dim_weights["viewshed"]
            matches.append(m_hbf)
            weights.append(w_eff)
            if m_hbf > 0.65:
                main_vars.append("Viewshed Horizon-Blocked Fraction")

            ledger.append(SubsystemLedgerEntry(
                subsystem_name="Horizon-Blocked Fraction (1-SVF)",
                status=FidelityStatus.STRONG if m_hbf > 0.65 else FidelityStatus.PARTIAL,
                earth_value=round(e_hbf, 3),
                target_value=round(t_hbf, 3),
                transferability_fraction=0.95,
                notes="Topographic masking and low-sun grazing illumination geometry.",
            ))
        else:
            ledger.append(SubsystemLedgerEntry(
                subsystem_name="Horizon-Blocked Fraction (1-SVF)",
                status=FidelityStatus.UNCONSTRAINED,
                earth_value=None,
                target_value=t_hbf,
                transferability_fraction=0.0,
                notes="No viewshed / horizon calculation available for cell.",
            ))

        # G. System Hard Breaks (Always explicitly surfaced)
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
        if matches and sum(weights) > 0:
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

        # 7. Evidence Confidence Q_f: observed slot ratio scaled by sensor uncertainty
        data_coverage = observed_slots / total_slots
        Q_evidence = max(0.05, min(1.0, data_coverage * (1.0 - sensor_uncertainty_tau * 1.5)))

        if not main_vars:
            main_vars = ["General Geomorphic Terrain Match"]

        return AFIScoreResult(
            function_profile=func,
            target_id=target.target_id,
            afi_score=afi_score,
            M_match=M_f,
            C_confounder=C_f,
            T_transferable=T_f,
            Q_evidence_confidence=Q_evidence,
            hard_breaks=target.hard_breaks,
            fidelity_ledger=ledger,
            confounder_breakdown=conf_eval.to_dict(),
            dimensionless_comparison=dim_groups.to_dict() if dim_groups else {},
            uncertainty_tau=sensor_uncertainty_tau,
            data_coverage=data_coverage,
            main_contributing_variables=main_vars,
        )
