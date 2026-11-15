"""
TERRA-X Planetary Target Registry
Loads ground-truth planetary targets (Moon South Pole, Mars Jezero, Gale Crater, etc.),
their hard breaks, dimensionless reference groups, and uncertainty profiles.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import json
from pathlib import Path


@dataclass
class PlanetaryTarget:
    target_id: str
    target_name: str
    body: str
    latitude: float
    longitude: float
    gravity_ms2: float
    atmosphere_bar: float
    regolith_density_kg_m3: float
    gamma_unit_weight_n_m3: float
    load_scale_factor: float
    primary_functions: List[str]
    hard_breaks: List[str]
    dimensionless_reference: Dict[str, float]
    pgda_dem_specs: Dict[str, Any]
    tech_gaps: List[str]


class TargetRegistry:
    """Manages planetary target catalogs and loads reference profiles."""

    def __init__(self, catalog_path: Optional[Path] = None):
        if catalog_path is None:
            catalog_path = Path(__file__).resolve().parent.parent / "manifests" / "target_catalogs.json"

        self.targets: Dict[str, PlanetaryTarget] = {}
        if catalog_path.exists():
            with open(catalog_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data.get("targets", []):
                    pt = PlanetaryTarget(**item)
                    self.targets[pt.target_id] = pt

    def get_target(self, target_id: str) -> Optional[PlanetaryTarget]:
        return self.targets.get(target_id)

    def list_targets(self) -> List[Dict[str, Any]]:
        return [
            {
                "target_id": t.target_id,
                "target_name": t.target_name,
                "body": t.body,
                "coordinates": [t.latitude, t.longitude],
                "gravity_ms2": t.gravity_ms2,
                "primary_functions": t.primary_functions,
                "hard_breaks": t.hard_breaks,
                "load_scale_factor": t.load_scale_factor,
            }
            for t in self.targets.values()
        ]

