"""
Pydantic models for data validation and serialization
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class BikeLocation(BaseModel):
    """Raw bike location from GBFS feed"""
    bike_id: str
    lat: float
    lon: float
    is_reserved: bool = False
    is_disabled: bool = False
    vehicle_type_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class H3Aggregation(BaseModel):
    """Aggregated data for a single H3 hexagon"""
    h3_index: str
    resolution: int
    count: int
    timestamp: datetime
    avg_density: Optional[float] = None


class HeatmapResponse(BaseModel):
    """Response format for heatmap API"""
    resolution: int
    timestamp: datetime
    hexagons: List[dict]
    total_vehicles: int
    metadata: Optional[dict] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    services: dict
