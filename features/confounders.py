"""
TERRA-X Confounder Assessment Engine
Computes function-dependent Earth-ADDED confounder severity C_f in [0, 1].
Confounders include:
- Moisture (SMAP / IMERG / soil water content): introduces capillary cohesion absent in vacuum
- Vegetation (NDVI / canopy cover): root cohesion, radar volume scattering, occlusion
- Atmosphere (barometric pressure, convective heat transfer vs vacuum radiation)
- Rounded Grains (Wadell sphericity / aeolian roundness vs jagged impact regolith)
- Biology (SIGN FLIPS: signal for BIOSIGNATURE_PRESERVATION / ASTROBIO, confounder for contamination / engineering)
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
    """Calculates function-specific Earth-added confounder severity C_f across all 10 exploration profiles."""

    # Function-specific sensitivity weights to each Earth confounder
    # [moisture, vegetation, grain_rounding, atmosphere, biology]
    PROFILE_WEIGHTS = {
        # 1. Rover Mobility
        "ROVER_MOBILITY": {
            "moisture": 0.35,      # Capillary cohesion alters traction & slip
            "vegetation": 0.30,    # Roots increase apparent cohesion unnaturally
            "rounding": 0.25,      # Rounded sands lack jagged regolith interlocking
            "atmosphere": 0.05,    # Aerodynamic drag negligible for slow rovers
            "biology": 0.05,       # Biofilms slightly change soil shear
        },
        "MOBILITY": {  # Backward compatibility alias
            "moisture": 0.35, "vegetation": 0.30, "rounding": 0.25, "atmosphere": 0.05, "biology": 0.05
        },

        # 2. Landing Pad Construction
        "LANDING_PAD_CONSTRUCTION": {
            "moisture": 0.25,      # Wet soil resists rocket plume scour unnaturally
            "vegetation": 0.25,    # Vegetation prevents natural ejecta liberation
            "rounding": 0.20,      # Fluidization and gas-particle shear differ
            "atmosphere": 0.25,    # 1 atm chokes supersonic plume expansion
            "biology": 0.05,
        },
        "LANDING_PAD_PSI": {  # Backward compatibility alias
            "moisture": 0.25, "vegetation": 0.25, "rounding": 0.20, "atmosphere": 0.25, "biology": 0.05
        },

        # 3. Regolith Excavation
        "REGOLITH_EXCAVATION": {
            "moisture": 0.40,      # Moisture radically changes cutting & wedge shear resistance
            "vegetation": 0.30,    # Root networks prevent realistic trenching & blade loading
            "rounding": 0.20,      # Rounded grains underestimate abrasive blade wear
            "atmosphere": 0.05,
            "biology": 0.05,
        },

        # 4. ISRU Construction & Beneficiation
        "ISRU_CONSTRUCTION": {
            "moisture": 0.35,      # Water steam causes gas bubbles/voids in microwave/laser sintering
            "vegetation": 0.30,    # Organic debris ruins 3D printing & regolith binder reactions
            "rounding": 0.20,      # Rounded grains do not compact or interlock like impact regolith
            "atmosphere": 0.10,    # Oxidation during high-temp molten regolith electrolysis
            "biology": 0.05,       # Carbon contamination in extraction reactors
        },
        "CONSTRUCTION_ISRU": {  # Backward compatibility alias
            "moisture": 0.35, "vegetation": 0.30, "rounding": 0.20, "atmosphere": 0.10, "biology": 0.05
        },

        # 5. Thermal Survivability
        "THERMAL_SURVIVABILITY": {
            "moisture": 0.15,      # Latent heat of vaporization distorts temperature swings
            "vegetation": 0.20,    # Evapotranspiration dampens diurnal ground extremes
            "rounding": 0.05,
            "atmosphere": 0.55,    # Convective cooling completely absent in vacuum, minimal on Mars
            "biology": 0.05,
        },
        "HUMAN_OPS_THERMAL": {  # Backward compatibility alias
            "moisture": 0.15, "vegetation": 0.20, "rounding": 0.05, "atmosphere": 0.55, "biology": 0.05
        },

        # 6. Dust & Wind Dynamics
        "DUST_AND_WIND": {
            "moisture": 0.40,      # Moisture capillary films prevent electrostatic levitation & saltation
            "vegetation": 0.30,    # Plants act as windbreaks and trap dust artificially
            "rounding": 0.15,      # Fluvial/aeolian rounded particles lack jagged abrasive points
            "atmosphere": 0.10,    # Dense air alters Reynolds/Stokes drag numbers
            "biology": 0.05,
        },

        # 7. Water & Ice Resources
        "WATER_AND_ICE_RESOURCES": {
            "moisture": 0.25,      # Liquid water capillary flow masks cryo-adsorbed / buried ice physics
            "vegetation": 0.35,    # Biological water cycling confounds subsurface neutron/radar returns
            "rounding": 0.10,
            "atmosphere": 0.25,    # Atmospheric vapor equilibrium prevents sublimation-loss studies
            "biology": 0.05,
        },

        # 8. Biosignature Preservation
        "BIOSIGNATURE_PRESERVATION": {
            "moisture": 0.20,      # Modern hydrological flushing leaches ancient preserved biomarkers
            "vegetation": 0.45,    # Modern plant root systems contaminate deep rock cores
            "rounding": 0.05,
            "atmosphere": 0.15,    # Modern oxic atmosphere degrades organic fossils
            "biology": -0.35,      # SIGN FLIP: Presence of extremophile biosignatures is TARGET SIGNAL!
        },
        "ASTROBIO": {  # Backward compatibility alias
            "moisture": 0.20, "vegetation": 0.45, "rounding": 0.05, "atmosphere": 0.15, "biology": -0.35
        },

        # 9. Subsurface & Lava Tubes
        "SUBSURFACE_AND_LAVA_TUBES": {
            "moisture": 0.25,      # Water seepage & stalactite formation alter basalt vault stability
            "vegetation": 0.35,    # Tree roots break lava tube ceilings and mask skylight openings
            "rounding": 0.10,
            "atmosphere": 0.20,    # Wind/draft currents inside terrestrial caves
            "biology": 0.10,       # Guano and organic speleothems
        },

        # 10. Communication & Illumination
        "COMMUNICATION_AND_ILLUMINATION": {
            "moisture": 0.05,      # Wet soil slightly shifts RF dielectric permittivity
            "vegetation": 0.50,    # Tree canopies corrupt visual feature tracking & optical LIDAR
            "rounding": 0.05,
            "atmosphere": 0.30,    # Atmospheric Rayleigh scattering & clouds absent on Moon
            "biology": 0.10,
        },
        "PNT_DENIED_NAV": {  # Backward compatibility alias
            "moisture": 0.05, "vegetation": 0.50, "rounding": 0.05, "atmosphere": 0.30, "biology": 0.10
        },
    }

    @classmethod
    def evaluate(
        cls,
        function_profile: str,
        soil_moisture_wtd: float = 0.02,
        vegetation_ndvi: float = 0.05,
        grain_wadell_roundness: float = 0.35,
        atmospheric_pressure_kpa: float = 101.3,
        biological_activity_index: float = 0.05,
    ) -> ConfounderAssessment:
        func = function_profile.upper()
        weights = cls.PROFILE_WEIGHTS.get(func, cls.PROFILE_WEIGHTS["ROVER_MOBILITY"])

        # 1. Moisture penalty: non-linear threshold (vacuum/hyper-arid threshold ~ 0.015)
        m_norm = min(1.0, max(0.0, (soil_moisture_wtd - 0.01) / 0.15))
        p_moisture = m_norm * weights["moisture"]

        # 2. Vegetation penalty: NDVI > 0.08 indicates active biomass
        v_norm = min(1.0, max(0.0, (vegetation_ndvi - 0.05) / 0.35))
        p_vegetation = v_norm * weights["vegetation"]

        # 3. Grain rounding penalty: Wadell > 0.25 indicates water/wind weathering
        r_norm = min(1.0, max(0.0, (grain_wadell_roundness - 0.20) / 0.50))
        p_rounding = r_norm * weights["rounding"]

        # 4. Atmospheric penalty: Earth 101.3 kPa vs vacuum (<1e-12 kPa) or Mars (~0.6 kPa)
        p_atmosphere = 1.0 * weights["atmosphere"]

        # 5. Biological penalty / signal (SIGN FLIP for Astrobio/Biosignature Preservation)
        b_weight = weights["biology"]
        if b_weight < 0:
            # Positive signal: biological activity reduces penalty (increases overall AFI)
            p_biology = -abs(b_weight) * min(1.0, biological_activity_index / 0.5)
        else:
            p_biology = min(1.0, biological_activity_index / 0.5) * b_weight

        # Sum penalties and bound strictly in [0.01, 0.95]
        total_C = p_moisture + p_vegetation + p_rounding + p_atmosphere + p_biology
        total_C = max(0.01, min(0.95, total_C))

        notes = []
        if p_moisture > 0.08:
            notes.append(f"Capillary moisture ({soil_moisture_wtd:.3f} wtd) creates artificial cohesion absent in planetary vacuum.")
        if p_vegetation > 0.10:
            notes.append(f"Vegetation canopy (NDVI={vegetation_ndvi:.2f}) introduces root mechanical reinforcing.")
        if p_rounding > 0.08:
            notes.append(f"Weathered grain roundness (Wadell={grain_wadell_roundness:.2f}) fails to replicate jagged impact regolith.")
        if b_weight < 0 and biological_activity_index > 0.02:
            notes.append(f"Biological extremophile presence (index={biological_activity_index:.2f}) is a POSITIVE SIGNAL for biosignature studies.")

        return ConfounderAssessment(
            function_profile=func,
            total_confounder_C=round(total_C, 4),
            moisture_penalty=round(p_moisture, 4),
            vegetation_penalty=round(p_vegetation, 4),
            grain_rounding_penalty=round(p_rounding, 4),
            atmospheric_penalty=round(p_atmosphere, 4),
            biological_penalty=round(p_biology, 4),
            breakdown_notes=notes,
        )
