"""
TERRA-X Confounder Assessment Engine
Computes function-dependent Earth-ADDED confounder severity C_f in [0, 1].
Confounders include:
- Moisture (SMAP / IMERG / soil water content): introduces capillary cohesion absent in vacuum
- Vegetation (NDVI / canopy cover): root cohesion, radar volume scattering, occlusion
- Atmosphere (barometric pressure, convective heat transfer vs vacuum radiation)
- Rounded Grains (Wadell sphericity / aeolian roundness vs jagged impact regolith)
- Biology (SIGN FLIPS: signal for ASTROBIO, confounder for contamination / engineering)
"""

from typing import Dict, Any, List
from dataclasses import dataclass, asdict


@dataclass
class ConfounderAssessment:
    function_profile: str
    total_confounder_C: float
    moisture_penalty: float
    vegetation_penalty: float
    grain_rounding_penalty: float
    atmospheric_penalty: float
    biological_penalty: float
    breakdown_notes: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ConfounderEngine:
    """Calculates function-specific Earth-added confounder severity C_f."""

    # Function-specific sensitivity weights to each Earth confounder
    # [moisture, vegetation, grain_rounding, atmosphere, biology]
    PROFILE_WEIGHTS = {
        "MOBILITY": {
            "moisture": 0.35,      # Capillary cohesion alters traction
            "vegetation": 0.30,    # Roots increase apparent cohesion
            "rounding": 0.25,      # Rounded sands lack jagged interlocking
            "atmosphere": 0.05,    # Aerodynamic drag negligible for slow rovers
            "biology": 0.05,       # Biofilms slightly change soil shear
        },
        "CONSTRUCTION_ISRU": {
            "moisture": 0.35,      # Moisture radically changes excavation & compaction
            "vegetation": 0.30,    # Organic debris ruins sintering / 3D printing
            "rounding": 0.20,      # Rounded grains do not sinter or interlock like regolith
            "atmosphere": 0.10,    # Oxidation during sintering
            "biology": 0.05,       # Organic contamination
        },
        "LANDING_PAD_PSI": {
            "moisture": 0.25,      # Wet soil resists plume scour unnaturally
            "vegetation": 0.25,    # Grass/bushes prevent ejecta liberation
            "rounding": 0.20,      # Fluidization dynamics differ
            "atmosphere": 0.25,    # Earth ambient pressure chokes supersonic jet expansion
            "biology": 0.05,
        },
        "HUMAN_OPS_THERMAL": {
            "moisture": 0.15,      # Latent heat & evaporative cooling
            "vegetation": 0.20,    # Evapotranspiration distorts surface energy balance
            "rounding": 0.05,
            "atmosphere": 0.55,    # Convective cooling completely absent on Moon, minimal on Mars
            "biology": 0.05,
        },
        "PNT_DENIED_NAV": {
            "moisture": 0.05,      # Wet surfaces change specular reflectivity
            "vegetation": 0.50,    # Tree canopies corrupt visual feature tracking & LIDAR
            "rounding": 0.10,
            "atmosphere": 0.25,    # Atmospheric haze / Rayleigh scattering absent on Moon
            "biology": 0.10,
        },
        "ASTROBIO": {
            "moisture": 0.25,      # Excessive water masks hyper-arid limits
            "vegetation": 0.40,    # Higher plant canopy overwhelms microbial biosignatures
            "rounding": 0.05,
            "atmosphere": 0.15,    # Oxygenation vs anoxic preservation
            "biology": -0.30,      # SIGN FLIP: Biological extremophile presence is TARGET SIGNAL!
        },
    }

    @classmethod
    def evaluate(
        cls,
        function_profile: str,
        soil_moisture_wtd: float = 0.02,        # 0.00 to 0.40
        vegetation_ndvi: float = 0.05,          # -0.2 to 0.9
        grain_wadell_roundness: float = 0.35,   # 0.1 (very angular) to 0.9 (well rounded)
        atmospheric_pressure_kpa: float = 101.3, # 101.3 kPa at sea level
        biological_activity_index: float = 0.05, # 0.0 (sterile) to 1.0 (dense biosphere)
    ) -> ConfounderAssessment:
        func = function_profile.upper()
        weights = cls.PROFILE_WEIGHTS.get(func, cls.PROFILE_WEIGHTS["MOBILITY"])

        # 1. Moisture penalty: non-linear threshold (vacuum/hyper-arid threshold ~ 0.015)
        m_norm = min(1.0, max(0.0, (soil_moisture_wtd - 0.01) / 0.15))
        p_moisture = m_norm * weights["moisture"]

        # 2. Vegetation penalty: NDVI > 0.10 indicates active biomass
        v_norm = min(1.0, max(0.0, (vegetation_ndvi - 0.05) / 0.35))
        p_vegetation = v_norm * weights["vegetation"]

        # 3. Grain rounding penalty: angularity of lunar/martian regolith is high (roundness < 0.25)
        # Rounded grains (> 0.45) receive steep penalty
        r_norm = min(1.0, max(0.0, (grain_wadell_roundness - 0.20) / 0.50))
        p_rounding = r_norm * weights["rounding"]

        # 4. Atmospheric penalty: Earth 101 kPa vs Moon 0 bar / Mars 6 mbar
        p_atmosphere = (min(1.0, atmospheric_pressure_kpa / 101.3)) * weights["atmosphere"]

        # 5. Biological penalty / signal (SIGN FLIP FOR ASTROBIO)
        notes = []
        if func == "ASTROBIO":
            # For Astrobiology: extremophile presence is a positive analog signal!
            # High modern anthropogenic overgrowth is still bad, but cryptoendolithic habitability is good
            p_biology = -1.0 * min(0.3, biological_activity_index * abs(weights["biology"]))
            notes.append(f"ASTROBIO sign flip applied: biological index {biological_activity_index:.2f} treated as candidate biosignature signal.")
        else:
            p_biology = min(1.0, biological_activity_index) * weights["biology"]
            if biological_activity_index > 0.2:
                notes.append("Elevated biological organics present: risk of simulant/hardware contamination.")

        # Sum of confounder penalties
        c_raw = p_moisture + p_vegetation + p_rounding + p_atmosphere + p_biology
        total_C = max(0.01, min(0.95, round(c_raw, 4)))

        if soil_moisture_wtd > 0.08:
            notes.append(f"Elevated soil moisture ({soil_moisture_wtd:.3f}): causes artificial capillary cohesion.")
        if vegetation_ndvi > 0.15:
            notes.append(f"Vegetation detected (NDVI={vegetation_ndvi:.2f}): root binding and optical occlusion confound test.")
        if grain_wadell_roundness > 0.50:
            notes.append(f"Fluvial/aeolian rounded grains (roundness={grain_wadell_roundness:.2f}): lacks regolith angular interlocking.")

        return ConfounderAssessment(
            function_profile=func,
            total_confounder_C=total_C,
            moisture_penalty=round(p_moisture, 4),
            vegetation_penalty=round(p_vegetation, 4),
            grain_rounding_penalty=round(p_rounding, 4),
            atmospheric_penalty=round(p_atmosphere, 4),
            biological_penalty=round(p_biology, 4),
            breakdown_notes=notes,
        )

