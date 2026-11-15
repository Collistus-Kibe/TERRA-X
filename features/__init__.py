"""
TERRA-X Dimensionless Features & Confounder Architecture
Calculates dimensionless similarity groups and function-dependent Earth confounders.
"""

from .dimensionless import DimensionlessPhysicsEngine, DimensionlessGroups
from .confounders import ConfounderEngine, ConfounderAssessment
from .geomorphology import GeomorphologyEngine

__all__ = [
    "DimensionlessPhysicsEngine",
    "DimensionlessGroups",
    "ConfounderEngine",
    "ConfounderAssessment",
    "GeomorphologyEngine",
]

