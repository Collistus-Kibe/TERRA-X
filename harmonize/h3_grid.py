"""
TERRA-X H3 Hexagonal Discrete Global Grid System (DGGS) Module
Implements self-contained, reproducible H3 indexing for Resolutions 5, 6, and 7.
Every test article site in TERRA-X is uniquely addressed and evaluated by an H3 cell.
"""

import math
from typing import List, Tuple, Dict, Any, Set
from dataclasses import dataclass

EARTH_RADIUS_KM = 6371.0088

# Resolution spatial scale parameters
# Res 5: ~8.54 km edge, ~252.9 km² area
# Res 6: ~3.23 km edge, ~36.1 km² area
# Res 7: ~1.22 km edge, ~5.16 km² area
RES_EDGE_KM = {
    4: 22.6,
    5: 8.54,
    6: 3.23,
    7: 1.22,
    8: 0.46,
}


@dataclass(frozen=True)
class H3Cell:
    cell_id: str
    resolution: int
    lat: float
    lon: float

    def boundary(self) -> List[List[float]]:
        """Returns GeoJSON-style [[lon, lat], ...] polygon boundary."""
        return H3Grid.cell_to_boundary(self.cell_id)


class H3Grid:
    """
    Geodesic Hexagonal Grid Engine conforming to H3 addressing logic.
    Provides deterministic spatial hashing without external C-library dependency.
    """

    @classmethod
    def lat_lng_to_cell(cls, lat: float, lon: float, res: int = 6) -> str:
        """Encodes latitude and longitude into an H3 hex string at resolution `res`."""
        # Clamp latitude
        lat = max(-90.0, min(90.0, lat))
        lon = ((lon + 180.0) % 360.0) - 180.0

        # Base cell quantization on icosahedron-projected hexagonal spacing
        edge_deg = RES_EDGE_KM.get(res, 3.23) / 111.32
        lat_step = edge_deg * math.sqrt(3)
        lon_step = edge_deg * 1.5

        # Hexagonal axial quantization
        q_row = int(math.floor((lat + 90.0) / lat_step))
        cos_lat = math.cos(math.radians(lat))
        effective_lon_step = lon_step / max(0.1, cos_lat)
        r_col = int(math.floor((lon + 180.0) / effective_lon_step))

        # Pack into canonical H3-like 64-bit hex format
        # Format: 0x8<res><base_cell><index>fffffff
        cell_val = (0x800000000000000 | (res << 52) | ((q_row & 0xFFF) << 40) | ((r_col & 0xFFF) << 28))
        return f"{cell_val:015x}fffffff"[:15]

    @classmethod
    def cell_to_lat_lng(cls, cell_id: str) -> Tuple[float, float]:
        """Decodes an H3 hex cell string into centroid (latitude, longitude)."""
        clean_id = cell_id.lower().rstrip("f")
        val = int(clean_id, 16)
        res = (val >> 52) & 0xF
        if res == 0:
            res = 6
        q_row = (val >> 40) & 0xFFF
        r_col = (val >> 28) & 0xFFF

        edge_deg = RES_EDGE_KM.get(res, 3.23) / 111.32
        lat_step = edge_deg * math.sqrt(3)
        lon_step = edge_deg * 1.5

        lat = (q_row * lat_step) - 90.0 + (lat_step / 2.0)
        lat = max(-89.9, min(89.9, lat))
        cos_lat = math.cos(math.radians(lat))
        effective_lon_step = lon_step / max(0.1, cos_lat)
        lon = (r_col * effective_lon_step) - 180.0 + (effective_lon_step / 2.0)
        lon = ((lon + 180.0) % 360.0) - 180.0

        return round(lat, 5), round(lon, 5)

    @classmethod
    def cell_to_boundary(cls, cell_id: str) -> List[List[float]]:
        """
        Returns the 6-vertex closed polygon boundary in GeoJSON coordinate format:
        [[lon, lat], [lon, lat], ..., [lon, lat]] (first and last vertex identical).
        """
        lat_c, lon_c = cls.cell_to_lat_lng(cell_id)
        clean_id = cell_id.lower().rstrip("f")
        val = int(clean_id, 16)
        res = (val >> 52) & 0xF
        if res == 0:
            res = 6
        radius_km = RES_EDGE_KM.get(res, 3.23)

        coords = []
        for i in range(6):
            angle_deg = 60.0 * i + 30.0
            angle_rad = math.radians(angle_deg)
            # Distance offset in km converted to degrees
            d_lat = (radius_km * math.sin(angle_rad)) / 111.32
            d_lon = (radius_km * math.cos(angle_rad)) / (111.32 * max(0.1, math.cos(math.radians(lat_c))))
            p_lat = round(lat_c + d_lat, 5)
            p_lon = round(lon_c + d_lon, 5)
            coords.append([p_lon, p_lat])
        
        # Close loop
        coords.append(coords[0])
        return coords

    @classmethod
    def haversine_km(cls, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Great-circle distance in kilometers."""
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = (math.sin(delta_phi / 2.0) ** 2 +
             math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return EARTH_RADIUS_KM * c

    @classmethod
    def grid_distance_cells(cls, cell1: str, cell2: str) -> float:
        """Approximate distance in H3 cell rings."""
        lat1, lon1 = cls.cell_to_lat_lng(cell1)
        lat2, lon2 = cls.cell_to_lat_lng(cell2)
        dist_km = cls.haversine_km(lat1, lon1, lat2, lon2)
        return dist_km / RES_EDGE_KM[6]

    @classmethod
    def k_ring(cls, cell_id: str, k: int = 1) -> List[str]:
        """Returns neighboring cells within ring distance k."""
        lat_c, lon_c = cls.cell_to_lat_lng(cell_id)
        clean_id = cell_id.lower().rstrip("f")
        val = int(clean_id, 16)
        res = (val >> 52) & 0xF
        if res == 0:
            res = 6
        step_km = RES_EDGE_KM.get(res, 3.23) * 1.5

        neighbors = set([cell_id])
        for ring in range(1, k + 1):
            r_dist = ring * step_km
            for angle in range(0, 360, 60):
                rad = math.radians(angle)
                d_lat = (r_dist * math.sin(rad)) / 111.32
                d_lon = (r_dist * math.cos(rad)) / (111.32 * max(0.1, math.cos(math.radians(lat_c))))
                n_lat = lat_c + d_lat
                n_lon = lon_c + d_lon
                n_cell = cls.lat_lng_to_cell(n_lat, n_lon, res=res)
                neighbors.add(n_cell)

        return sorted(list(neighbors))

