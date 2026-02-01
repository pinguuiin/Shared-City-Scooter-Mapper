"""
H3 service for spatial indexing and multi-resolution aggregation
"""
import h3
from typing import List, Dict, Tuple
from collections import defaultdict
from app.config import settings


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


# Singleton instance
h3_service = H3Service()
