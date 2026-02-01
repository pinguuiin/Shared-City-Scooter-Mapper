"""
Aggregation Worker - Processes GBFS data and creates H3 aggregations
"""
from datetime import datetime
from typing import Dict, List
from app.services.h3_service import h3_service
from app.services.duckdb_service import get_db_service
from app.config import settings


class AggregationWorker:
    """Worker that aggregates bike locations into H3 hexagons"""
    
    def __init__(self):
        self.h3_service = h3_service
        self.db_service = get_db_service()
        self.resolutions = settings.H3_RESOLUTIONS
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
            # 1. Store raw locations
            locations = []
            valid_bikes = []
            
            for bike in bike_batch:
                lat = bike.get("lat")
                lon = bike.get("lon")
                
                if lat is None or lon is None:
                    continue
                
                locations.append({
                    "bike_id": bike.get("bike_id", "unknown"),
                    "lat": lat,
                    "lon": lon,
                    "timestamp": datetime.utcnow(),
                    "is_reserved": bike.get("is_reserved", False),
                    "is_disabled": bike.get("is_disabled", False),
                    "vehicle_type_id": bike.get("vehicle_type_id"),
                })
                
                valid_bikes.append({"lat": lat, "lon": lon})
            
            if not valid_bikes:
                print("⚠️  No valid bikes in batch")
                return
            
            # Insert raw locations
            self.db_service.insert_raw_locations(locations)
            print(f"✅ Stored {len(locations)} raw locations")
            
            # 2. Aggregate across all resolutions
            aggregations = self.h3_service.aggregate_multi_resolution(valid_bikes)
            
            # 3. Store aggregations for each resolution
            timestamp = datetime.utcnow()
            
            for resolution, hexagon_counts in aggregations.items():
                agg_records = [
                    {
                        "h3_index": h3_index,
                        "resolution": resolution,
                        "count": count,
                        "last_updated": timestamp,
                        "window_start": timestamp,
                        "window_end": timestamp,
                    }
                    for h3_index, count in hexagon_counts.items()
                ]
                
                self.db_service.upsert_aggregation(resolution, agg_records)
                print(f"✅ Resolution {resolution}: {len(hexagon_counts)} hexagons")
            
            # 4. Cleanup old data periodically
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
