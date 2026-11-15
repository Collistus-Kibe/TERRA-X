"""
TERRA-X Planetary DEM Harmonizer & Unscaling Engine
Handles planetary DEM unscaling (USGS LOLA int16 * 0.5), slope computation,
and multi-scale roughness estimation.
"""

from typing import Dict, Any, Tuple
import numpy as np


class PlanetaryDEMHarmonizer:
    """Standardizes planetary and terrestrial elevation models."""

    @staticmethod
    def unscale_lola(raw_int16: np.ndarray) -> np.ndarray:
        """
        USGS LOLA 118m:
        Converts 16-bit signed integer raster into meters using scale factor 0.5.
        GDAL equivalent: gdal_translate -unscale (scale 0.5, offset 0.0)
        """
        return np.asarray(raw_int16, dtype=np.float32) * 0.5

    @staticmethod
    def compute_slope_and_aspect(
        elevation_grid: np.ndarray,
        dx_m: float = 30.0,
        dy_m: float = 30.0,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Computes gradient, tan(theta), slope in degrees, and aspect angle in degrees
        using central difference kernels (Horn's method).
        """
        grid = np.asarray(elevation_grid, dtype=np.float32)
        if grid.ndim != 2 or grid.shape[0] < 3 or grid.shape[1] < 3:
            # Fallback for 1D or small samples
            val = float(grid.flat[0]) if grid.size > 0 else 0.0
            return np.array([[0.0]]), np.array([[0.0]]), np.array([[0.0]])

        # Gradient along y (rows) and x (cols)
        gy, gx = np.gradient(grid, dy_m, dx_m)

        # tan(theta) = sqrt(gx^2 + gy^2)
        tan_theta = np.sqrt(gx**2 + gy**2)
        slope_rad = np.arctan(tan_theta)
        slope_deg = np.degrees(slope_rad)

        # Aspect: direction of maximum downhill slope (0 deg = North)
        aspect_rad = np.arctan2(-gx, gy)
        aspect_deg = (np.degrees(aspect_rad) + 360.0) % 360.0

        return tan_theta, slope_deg, aspect_deg

    @staticmethod
    def compute_rms_roughness(elevation_grid: np.ndarray, detrend: bool = True) -> float:
        """
        Computes root-mean-square roughness h_rms = sqrt(mean((z - z_mean)^2)).
        If detrend is True, fits a local planar trend and calculates RMS of residuals.
        """
        grid = np.asarray(elevation_grid, dtype=np.float32)
        if grid.size <= 1:
            return 0.01

        if not detrend:
            return float(np.std(grid))

        # Detrend with least-squares plane
        rows, cols = grid.shape
        y, x = np.mgrid[:rows, :cols]
        X = np.column_stack([x.ravel(), y.ravel(), np.ones(grid.size)])
        z = grid.ravel()

        # Solve plane: z = a*x + b*y + c
        plane_params, _, _, _ = np.linalg.lstsq(X, z, rcond=None)
        trend = (X @ plane_params).reshape(rows, cols)
        residuals = grid - trend
        h_rms = float(np.sqrt(np.mean(residuals**2)))
        return max(0.001, h_rms)

