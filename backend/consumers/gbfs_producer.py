"""
GBFS Data Producer - Fetches bike/scooter data and publishes to Kafka
"""
import json
import time
import requests
from kafka import KafkaProducer
from datetime import datetime
from typing import Dict, List
from config import settings


class GBFSProducer:
    """Producer that fetches GBFS data and publishes to Kafka"""
    
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
        )
        self.gbfs_url = settings.GBFS_URL
        self.topic = settings.KAFKA_TOPIC_RAW
        self.fetch_interval = settings.GBFS_FETCH_INTERVAL
        print(f"✅ GBFS Producer initialized - URL: {self.gbfs_url}")
    
    def fetch_gbfs_data(self) -> List[Dict]:
        """Fetch bike/scooter locations from GBFS endpoint"""
        try:
            response = requests.get(self.gbfs_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Extract bikes from GBFS format
            bikes = data.get("data", {}).get("bikes", [])
            
            # Filter bikes within geographic boundaries
            timestamp = datetime.utcnow().isoformat()
            filtered_bikes = []
            
            for bike in bikes:
                lat = bike.get('lat')
                lon = bike.get('lon')
                
                # Check if within Aachen core area
                if (lat and lon and 
                    settings.MIN_LATITUDE <= lat <= settings.MAX_LATITUDE and
                    settings.MIN_LONGITUDE <= lon <= settings.MAX_LONGITUDE):
                    bike["fetch_timestamp"] = timestamp
                    filtered_bikes.append(bike)
            
            if len(filtered_bikes) < len(bikes):
                print(f"🔍 Filtered: {len(filtered_bikes)}/{len(bikes)} bikes within boundaries")
            
            return filtered_bikes
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching GBFS data: {e}")
            return []
        except (KeyError, ValueError) as e:
            print(f"❌ Error parsing GBFS data: {e}")
            return []
    
    def publish_batch(self, bikes: List[Dict]):
        """Publish a batch of bike locations to Kafka"""
        if not bikes:
            print("⚠️  No bikes to publish")
            return
        
        for bike in bikes:
            bike_id = bike.get("bike_id", "unknown")
            
            # Publish to Kafka
            self.producer.send(
                self.topic,
                key=bike_id,
                value=bike
            )
        
        self.producer.flush()
        print(f"✅ Published {len(bikes)} bike locations to {self.topic}")
    
    def run(self):
        """Main loop - fetch and publish GBFS data periodically"""
        print(f"🚀 Starting GBFS Producer (interval: {self.fetch_interval}s)")
        
        try:
            while True:
                print(f"\n⏰ Fetching GBFS data at {datetime.utcnow().isoformat()}")
                
                # Fetch and publish
                bikes = self.fetch_gbfs_data()
                self.publish_batch(bikes)
                
                # Wait for next interval
                time.sleep(self.fetch_interval)
        
        except KeyboardInterrupt:
            print("\n🛑 Stopping GBFS Producer...")
        finally:
            self.producer.close()
            print("✅ Producer closed")


if __name__ == "__main__":
    producer = GBFSProducer()
    producer.run()
