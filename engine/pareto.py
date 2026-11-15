"""
TERRA-X Multi-Objective Pareto Frontier Engine
Computes non-dominated Pareto frontiers across competing functional objectives:
e.g. MOBILITY vs HUMAN_OPS_THERMAL vs CONSTRUCTION_ISRU.
"""

from typing import Dict, Any, List
import numpy as np


class ParetoFrontierEngine:
    """Calculates non-dominated Pareto candidate sets across multiple functions."""

    @staticmethod
    def identify_pareto_frontier(
        candidates: List[Dict[str, Any]],
        objective_keys: List[str],
    ) -> List[Dict[str, Any]]:
        """
        Determines the Pareto non-dominated set.
        A candidate A dominates B if A is >= B in all objectives and strictly > B in at least one.
        """
        if not candidates or not objective_keys:
            return candidates

        n = len(candidates)
        # Build matrix: shape (n, num_objectives)
        matrix = np.zeros((n, len(objective_keys)), dtype=np.float32)
        for i, c in enumerate(candidates):
            for j, k in enumerate(objective_keys):
                matrix[i, j] = float(c.get(k, 0.0))

        is_pareto = np.ones(n, dtype=bool)
        for i in range(n):
            for j in range(n):
                if i != j and is_pareto[j]:
                    # Check if candidate j dominates candidate i
                    if np.all(matrix[j] >= matrix[i]) and np.any(matrix[j] > matrix[i]):
                        is_pareto[i] = False
                        break

        pareto_candidates = []
        for i, c in enumerate(candidates):
            c_copy = dict(c)
            c_copy["is_pareto_optimal"] = bool(is_pareto[i])
            if is_pareto[i]:
                pareto_candidates.append(c_copy)

        return pareto_candidates

