"""
TERRA-X In-Situ Field Kit Re-Scoring Engine
Processes uploaded field measurement data:
- Portable XRF / XRD mineralogy (SiO2, FeO, TiO2, Al2O3, clay/sulfate ratios)
- In-situ shear vane (direct cohesion c in kPa and peak friction angle phi in degrees)
- Dynamic cone penetrometer (penetration resistance, bearing capacity q_u in kPa)
- Microscopic grain imagery (Wadell sphericity, angularity, particle size distribution d50)

Converts remote estimates into in-situ verified ground truth, upgrading
Fidelity Ledger statuses from UNCONSTRAINED/PARTIAL to STRONG.
"""

from typing import Dict, Any, Optional
from targets.registry import PlanetaryTarget
from .scoring import ScoringEngine, AFIScoreResult


class FieldKitEngine:
    """Ingests in-situ geotechnical/geochemical field assays and re-scores test articles."""

    @classmethod
    def re_score_with_field_kit(
        cls,
        base_features: Dict[str, Any],
        field_kit_payload: Dict[str, Any],
        target: PlanetaryTarget,
        function_profile: str,
        wheel_diameter_m: float = 0.50,
    ) -> Dict[str, Any]:
        """
        Merges field-kit ground truth into remote-sensing feature set and re-evaluates AFI.
        """
        updated_features = dict(base_features)
        upgraded_fields = []

        # 1. Shear Vane Geotechnical Data
        shear_vane = field_kit_payload.get("shear_vane")
        if shear_vane:
            if "friction_angle_deg" in shear_vane:
                updated_features["friction_angle_deg"] = float(shear_vane["friction_angle_deg"])
                upgraded_fields.append("friction_angle_deg (in-situ shear vane)")
            if "cohesion_kpa" in shear_vane:
                updated_features["cohesion_kpa"] = float(shear_vane["cohesion_kpa"])
                upgraded_fields.append("cohesion_kpa (in-situ shear vane)")

        # 2. Dynamic Cone Penetrometer
        penetrometer = field_kit_payload.get("penetrometer")
        if penetrometer:
            if "bearing_capacity_kpa" in penetrometer:
                updated_features["bearing_capacity_kpa"] = float(penetrometer["bearing_capacity_kpa"])
                upgraded_features.append("bearing_capacity_kpa (dynamic cone penetrometer)")

        # 3. Microscopic Grain Imagery
        grain_photo = field_kit_payload.get("grain_photo_analysis")
        if grain_photo:
            if "wadell_roundness" in grain_photo:
                updated_features["grain_wadell_roundness"] = float(grain_photo["wadell_roundness"])
                upgraded_fields.append("grain_wadell_roundness (microscopic petrographic image)")
            if "d50_um" in grain_photo:
                updated_features["grain_d50_um"] = float(grain_photo["d50_um"])
                upgraded_fields.append("grain_d50_um (sediment particle sizing)")

        # 4. Portable XRF / XRD Mineralogy
        mineralogy = field_kit_payload.get("xrf_xrd_mineralogy")
        if mineralogy:
            updated_features["xrf_xrd_verified"] = True
            updated_features["mineral_composition"] = mineralogy
            upgraded_fields.append("mineralogy (in-situ XRF/XRD assay)")

        # Field measurements dramatically reduce sensor uncertainty tau
        field_tau = 0.02

        # Re-score
        res = ScoringEngine.compute_afi(
            function_profile=function_profile,
            target=target,
            earth_features=updated_features,
            wheel_diameter_m=wheel_diameter_m,
            sensor_uncertainty_tau=field_tau,
        )

        return {
            "cell_id": updated_features.get("cell_id"),
            "upgraded_fields": upgraded_fields,
            "re_scored_result": res.to_dict(),
            "field_verified": True,
            "uncertainty_tau": field_tau,
        }

