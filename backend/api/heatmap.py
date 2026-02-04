"""
Heatmap API endpoints
"""
from fastapi import APIRouter, Query, HTTPException
from datetime import datetime
from typing import Optional
from services.duckdb_service import get_db_service
from services.h3_service import h3_service
from config import settings

router = APIRouter(prefix="/api", tags=["heatmap"])


@router.get("/heatmap")
async def get_heatmap(
    resolution: int = Query(
        default=settings.H3_DEFAULT_RESOLUTION,
        ge=min(settings.H3_RESOLUTIONS),
        le=max(settings.H3_RESOLUTIONS),
        description="H3 resolution level"
    ),
    min_count: int = Query(default=1, ge=0, description="Minimum vehicle count per hexagon")
):
    """
    Get heatmap data for a specific H3 resolution
    
    Returns aggregated vehicle counts per hexagon at the specified resolution.
    Supports dynamic resolution scaling for zoom levels.
    """
    try:
        # Validate resolution
        if resolution not in settings.H3_RESOLUTIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid resolution. Must be one of {settings.H3_RESOLUTIONS}"
            )
        
        db_service = get_db_service(read_only=True)

        # Fetch aggregated data
        hexagons = db_service.get_heatmap_data(resolution, min_count)
        
        # Enrich with geometry
        enriched_hexagons = []
        for hex_data in hexagons:
            h3_index = hex_data["h3_index"]
            
            # Get hexagon center
            lat, lon = h3_service.get_hexagon_center(h3_index)
            
            # Get hexagon boundary
            boundary = h3_service.get_hexagon_boundary(h3_index)
            
            enriched_hexagons.append({
                "h3_index": h3_index,
                "center": {"lat": lat, "lon": lon},
                "boundary": [{"lat": lat, "lon": lon} for lat, lon in boundary],
                "count": hex_data["count"],
                "last_updated": hex_data["last_updated"].isoformat() if isinstance(hex_data["last_updated"], datetime) else hex_data["last_updated"]
            })
        
        # Calculate total vehicles
        total_vehicles = sum(h["count"] for h in enriched_hexagons)
        
        return {
            "resolution": resolution,
            "timestamp": datetime.utcnow().isoformat(),
            "hexagons": enriched_hexagons,
            "total_vehicles": total_vehicles,
            "hexagon_count": len(enriched_hexagons),
            "metadata": {
                "min_count_filter": min_count,
                "available_resolutions": settings.H3_RESOLUTIONS
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"Internal server error: {str(e)}"
        print(f"❌ API Error (resolution={resolution}):")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_detail)


@router.get("/heatmap/geojson")
async def get_heatmap_geojson(
    resolution: int = Query(
        default=settings.H3_DEFAULT_RESOLUTION,
        ge=min(settings.H3_RESOLUTIONS),
        le=max(settings.H3_RESOLUTIONS),
        description="H3 resolution level"
    ),
    min_count: int = Query(default=1, ge=0, description="Minimum vehicle count per hexagon")
):
    """
    Get heatmap data as GeoJSON FeatureCollection
    
    Optimized for deck.gl and other mapping libraries.
    """
    try:
        # Validate resolution
        if resolution not in settings.H3_RESOLUTIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid resolution. Must be one of {settings.H3_RESOLUTIONS}"
            )
        
        db_service = get_db_service(read_only=True)

        # Fetch aggregated data
        hexagons = db_service.get_heatmap_data(resolution, min_count)
        
        # Build GeoJSON features
        features = []
        for hex_data in hexagons:
            h3_index = hex_data["h3_index"]
            boundary = h3_service.get_hexagon_boundary(h3_index)
            
            # Create polygon coordinates (GeoJSON format: [lon, lat])
            coordinates = [[lon, lat] for lat, lon in boundary]
            coordinates.append(coordinates[0])  # Close the polygon
            
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coordinates]
                },
                "properties": {
                    "h3_index": h3_index,
                    "count": hex_data["count"],
                    "resolution": resolution,
                    "last_updated": hex_data["last_updated"].isoformat() if isinstance(hex_data["last_updated"], datetime) else hex_data["last_updated"]
                }
            }
            features.append(feature)
        
        return {
            "type": "FeatureCollection",
            "features": features,
            "properties": {
                "timestamp": datetime.utcnow().isoformat(),
                "resolution": resolution,
                "total_vehicles": sum(f["properties"]["count"] for f in features),
                "hexagon_count": len(features)
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/stats")
async def get_stats():
    """
    Get database and aggregation statistics
    """
    try:
        db_service = get_db_service(read_only=True)
        stats = db_service.get_stats()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "database": stats,
            "configuration": {
                "resolutions": settings.H3_RESOLUTIONS,
                "window_size_minutes": settings.WINDOW_SIZE_MINUTES,
                "retention_minutes": settings.RETENTION_MINUTES
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
