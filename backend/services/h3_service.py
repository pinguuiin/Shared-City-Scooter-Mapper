"""
H3 service for spatial indexing and multi-resolution aggregation
"""
import h3
from typing import List, Dict, Tuple
from collections import defaultdict
from config import settings


class H3Service:
    """Service for H3 spatial operations"""

    @staticmethod
    def _latlng_to_cell(lat: float, lon: float, resolution: int) -> str:
        if hasattr(h3, "latlng_to_cell"):
            return h3.latlng_to_cell(lat, lon, resolution)
        return h3.geo_to_h3(lat, lon, resolution)

    @staticmethod
    def _cell_to_parent(h3_index: str, target_resolution: int) -> str:
        if hasattr(h3, "cell_to_parent"):
            return h3.cell_to_parent(h3_index, target_resolution)
        return h3.h3_to_parent(h3_index, target_resolution)

    @staticmethod
    def _cell_to_boundary(h3_index: str) -> List[Tuple[float, float]]:
        if hasattr(h3, "cell_to_boundary"):
            return h3.cell_to_boundary(h3_index)
        return h3.h3_to_geo_boundary(h3_index)

    @staticmethod
    def _cell_to_latlng(h3_index: str) -> Tuple[float, float]:
        if hasattr(h3, "cell_to_latlng"):
            return h3.cell_to_latlng(h3_index)
        return h3.h3_to_geo(h3_index)

    @staticmethod
    def _get_resolution(h3_index: str) -> int:
        if hasattr(h3, "get_resolution"):
            return h3.get_resolution(h3_index)
        return h3.h3_get_resolution(h3_index)

    @staticmethod
    def _is_valid_cell(h3_index: str) -> bool:
        if hasattr(h3, "is_valid_cell"):
            return h3.is_valid_cell(h3_index)
        return h3.h3_is_valid(h3_index)
    
    @staticmethod
    def encode_location(lat: float, lon: float, resolution: int) -> str:
        """
        Convert lat/lon to H3 hexagon ID at specified resolution
        
        Args:
            lat: Latitude
            lon: Longitude
            resolution: H3 resolution (0-15)
        
        Returns:
            H3 hexagon ID as string
        """
        return H3Service._latlng_to_cell(lat, lon, resolution)
    
    @staticmethod
    def get_parent_hexagons(h3_index: str, target_resolution: int) -> str:
        """
        Get parent hexagon at coarser resolution
        
        Args:
            h3_index: H3 hexagon ID
            target_resolution: Target H3 resolution (must be < current resolution)
        
        Returns:
            Parent H3 hexagon ID
        """
        return H3Service._cell_to_parent(h3_index, target_resolution)
    
    @staticmethod
    def get_all_resolutions(lat: float, lon: float) -> Dict[int, str]:
        """
        Encode a location to all configured H3 resolutions
        
        Args:
            lat: Latitude
            lon: Longitude
        
        Returns:
            Dictionary mapping resolution to H3 index
        """
        result = {}
        
        # Start with finest resolution
        finest_resolution = max(settings.H3_RESOLUTIONS)
        h3_index = H3Service._latlng_to_cell(lat, lon, finest_resolution)
        result[finest_resolution] = h3_index
        
        # Get parent hexagons for coarser resolutions
        for resolution in sorted(settings.H3_RESOLUTIONS, reverse=True):
            if resolution == finest_resolution:
                continue
            result[resolution] = H3Service._cell_to_parent(h3_index, resolution)
        
        return result
    
    @staticmethod
    def aggregate_by_resolution(
        locations: List[Dict[str, float]], 
        resolution: int
    ) -> Dict[str, int]:
        """
        Aggregate vehicle locations into H3 hexagons at specified resolution
        
        Args:
            locations: List of dicts with 'lat' and 'lon' keys
            resolution: H3 resolution for aggregation
        
        Returns:
            Dictionary mapping H3 index to vehicle count
        """
        aggregation = defaultdict(int)
        
        for loc in locations:
            h3_index = H3Service._latlng_to_cell(loc["lat"], loc["lon"], resolution)
            aggregation[h3_index] += 1
        
        return dict(aggregation)
    
    @staticmethod
    def aggregate_multi_resolution(
        locations: List[Dict[str, float]]
    ) -> Dict[int, Dict[str, int]]:
        """
        Aggregate vehicle locations across all configured resolutions
        
        Args:
            locations: List of dicts with 'lat' and 'lon' keys
        
        Returns:
            Nested dict: {resolution: {h3_index: count}}
        """
        result = {}
        
        for resolution in settings.H3_RESOLUTIONS:
            result[resolution] = H3Service.aggregate_by_resolution(locations, resolution)
        
        return result
    
    @staticmethod
    def get_hexagon_boundary(h3_index: str) -> List[Tuple[float, float]]:
        """
        Get the boundary coordinates of an H3 hexagon
        
        Args:
            h3_index: H3 hexagon ID
        
        Returns:
            List of (lat, lon) tuples forming the boundary
        """
        return H3Service._cell_to_boundary(h3_index)
    
    @staticmethod
    def get_hexagon_center(h3_index: str) -> Tuple[float, float]:
        """
        Get the center coordinates of an H3 hexagon
        
        Args:
            h3_index: H3 hexagon ID
        
        Returns:
            (lat, lon) tuple
        """
        return H3Service._cell_to_latlng(h3_index)
    
    @staticmethod
    def get_resolution(h3_index: str) -> int:
        """
        Get the resolution of an H3 hexagon
        
        Args:
            h3_index: H3 hexagon ID
        
        Returns:
            Resolution (0-15)
        """
        return H3Service._get_resolution(h3_index)
    
    @staticmethod
    def is_valid_h3(h3_index: str) -> bool:
        """
        Validate an H3 index
        
        Args:
            h3_index: H3 hexagon ID to validate
        
        Returns:
            True if valid, False otherwise
        """
        try:
            return H3Service._is_valid_cell(h3_index)
        except:
            return False
    
    @staticmethod
    def get_hexagons_in_bounds(min_lat: float, max_lat: float, min_lon: float, max_lon: float, resolution: int) -> List[str]:
        """
        Get all H3 hexagons that cover a bounding box
        
        Args:
            min_lat: Minimum latitude
            max_lat: Maximum latitude
            min_lon: Minimum longitude
            max_lon: Maximum longitude
            resolution: H3 resolution
        
        Returns:
            List of H3 hexagon IDs covering the bounding box
        """
        # Create a polygon from bounding box
        polygon = {
            "type": "Polygon",
            "coordinates": [[
                [min_lon, min_lat],
                [min_lon, max_lat],
                [max_lon, max_lat],
                [max_lon, min_lat],
                [min_lon, min_lat]
            ]]
        }
        
        # Use polyfill to get all hexagons
        if hasattr(h3, "polyfill_geojson"):
            hexagons = h3.polyfill_geojson(polygon, resolution)
        elif hasattr(h3, "polyfill"):
            # Convert to old format
            coords = polygon["coordinates"][0]
            geo_json = {
                "type": "Polygon",
                "coordinates": [coords]
            }
            hexagons = h3.polyfill(geo_json, resolution, geo_json_conformant=True)
        else:
            # Fallback: sample points and deduplicate hexagons
            hexagons = set()
            lat_step = (max_lat - min_lat) / 20
            lon_step = (max_lon - min_lon) / 20
            for lat in [min_lat + i * lat_step for i in range(21)]:
                for lon in [min_lon + j * lon_step for j in range(21)]:
                    hex_id = H3Service._latlng_to_cell(lat, lon, resolution)
                    hexagons.add(hex_id)
        
        return list(hexagons)


# Singleton instance
h3_service = H3Service()
