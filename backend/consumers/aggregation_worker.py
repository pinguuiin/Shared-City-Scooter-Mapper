"""
Aggregation Worker - Processes GBFS data and creates H3 aggregations
"""
from datetime import datetime
from typing import Dict, List
from services.h3_service import h3_service
from services.duckdb_service import get_db_service
from config import settings


class AggregationWorker:
    """Worker that aggregates bike locations into H3 hexagons"""
    
    def __init__(self):
        self.h3_service = h3_service
        self.db_service = get_db_service()
        self.resolutions = settings.H3_RESOLUTIONS
        self.previous_active_hexagons = {}  # Track hexagons that had scooters in previous snapshot
        print(f"✅ Aggregation Worker initialized (resolutions: {self.resolutions})")
    
    def process_single_message(self, bike_data: Dict):
        """
        Process a single bike location message
        
        Args:
            bike_data: Dictionary with bike location data
        """
        try:
            # Extract coordinates
            lat = bike_data.get("lat")
            lon = bike_data.get("lon")
            
            if lat is None or lon is None:
                print(f"⚠️  Missing coordinates in message: {bike_data}")
                return
            
            # Store raw location
            location = {
                "bike_id": bike_data.get("bike_id", "unknown"),
                "lat": lat,
                "lon": lon,
                "timestamp": datetime.utcnow(),
                "is_reserved": bike_data.get("is_reserved", False),
                "is_disabled": bike_data.get("is_disabled", False),
                "vehicle_type_id": bike_data.get("vehicle_type_id"),
            }
            
            self.db_service.insert_raw_locations([location])
            
            # Log processing
            bike_id = bike_data.get("bike_id", "unknown")
            print(f"✅ Processed bike {bike_id} at ({lat:.4f}, {lon:.4f})")
        
        except Exception as e:
            print(f"❌ Error processing message: {e}")
    
    def process_batch(self, bike_batch: List[Dict]):
        """
        Process a batch of bike locations and create H3 aggregations
        
        Args:
            bike_batch: List of bike location dictionaries
        """
        if not bike_batch:
            return
        
        print(f"\n📊 Processing batch of {len(bike_batch)} bikes...")
        
        try:
            # 1. Deduplicate and validate bikes in this batch
            unique_bikes_by_id = {}
            
            for bike in bike_batch:
                bike_id = bike.get("bike_id")
                lat = bike.get("lat")
                lon = bike.get("lon")
                
                # Skip if invalid or duplicate bike_id in this batch
                if not bike_id:
                    continue
                if bike_id in unique_bikes_by_id:
                    continue
                if (lat is None or lon is None or
                    not (settings.MIN_LATITUDE <= lat <= settings.MAX_LATITUDE and
                         settings.MIN_LONGITUDE <= lon <= settings.MAX_LONGITUDE)):
                    continue
                
                unique_bikes_by_id[bike_id] = {
                    "bike_id": bike_id,
                    "lat": lat,
                    "lon": lon,
                    "is_reserved": bike.get("is_reserved", False),
                    "is_disabled": bike.get("is_disabled", False),
                    "vehicle_type_id": bike.get("vehicle_type_id"),
                }
            
            if not unique_bikes_by_id:
                print("⚠️  No valid unique bikes in batch")
                return
            
            print(f"📍 {len(unique_bikes_by_id)} unique vehicles (deduplicated from {len(bike_batch)})")
            
            # 2. Store raw locations
            timestamp = datetime.utcnow()
            locations = [
                {
                    **bike_data,
                    "timestamp": timestamp,
                }
                for bike_data in unique_bikes_by_id.values()
            ]
            
            self.db_service.insert_raw_locations(locations)
            print(f"✅ Stored {len(locations)} raw locations")
            
            # 3. Aggregate across all resolutions using unique bikes
            valid_bikes_for_agg = [{"lat": bike["lat"], "lon": bike["lon"]} for bike in unique_bikes_by_id.values()]
            aggregations = self.h3_service.aggregate_multi_resolution(valid_bikes_for_agg)
            
            # 4. Generate all hexagons in bounds and populate with counts
            # This ensures we show hexagons with count=0
            for resolution in self.resolutions:
                # Get all hexagons covering the geographic bounds
                all_hexes_in_bounds = self.h3_service.get_hexagons_in_bounds(
                    settings.MIN_LATITUDE,
                    settings.MAX_LATITUDE,
                    settings.MIN_LONGITUDE,
                    settings.MAX_LONGITUDE,
                    resolution
                )
                
                # Get actual counts (from aggregation, or 0 if not present)
                hexagon_counts = aggregations.get(resolution, {})
                
                # Track active hexagons (count > 0) for next iteration
                current_active = set(h3_idx for h3_idx, count in hexagon_counts.items() if count > 0)
                previous_active = self.previous_active_hexagons.get(resolution, set())
                
                # Service area = hexagons that currently have scooters OR previously had scooters
                service_area = current_active | previous_active
                
                # Build records only for service area hexagons (not empty outskirts)
                agg_records = [
                    {
                        "h3_index": h3_index,
                        "resolution": resolution,
                        "count": hexagon_counts.get(h3_index, 0),
                        "last_updated": timestamp,
                        "window_start": timestamp,
                        "window_end": timestamp,
                    }
                    for h3_index in service_area
                ]
                
                # Clear and insert snapshot
                self.db_service.clear_aggregation(resolution)
                self.db_service.insert_aggregation(resolution, agg_records)
                
                # Update previous active hexagons for next cycle
                self.previous_active_hexagons[resolution] = current_active
                
                total_vehicles = sum(rec["count"] for rec in agg_records)
                hexes_with_vehicles = sum(1 for rec in agg_records if rec["count"] > 0)
                print(f"✅ Resolution {resolution}: {len(agg_records)} service area hexagons ({hexes_with_vehicles} with vehicles), {total_vehicles} vehicles")
            
            # 5. Cleanup old data periodically
            self.db_service.cleanup_old_data()
        
        except Exception as e:
            print(f"❌ Error processing batch: {e}")
            import traceback
            traceback.print_exc()
    
    def get_message_handler(self):
        """Get the message handler function for single message processing"""
        return self.process_single_message
    
    def get_batch_handler(self):
        """Get the batch handler function for batch processing"""
        return self.process_batch


# Singleton instance
aggregation_worker = AggregationWorker()
