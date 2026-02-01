"""
Kafka Consumer for GBFS data - reads raw bike locations
"""
import json
from kafka import KafkaConsumer
from typing import Dict, List, Callable
from config import settings


class GBFSConsumer:
    """Consumer that reads raw GBFS data from Kafka"""
    
    def __init__(self, message_handler: Callable[[Dict], None]):
        """
        Initialize consumer with a message handler callback
        
        Args:
            message_handler: Function to process each message
        """
        self.consumer = KafkaConsumer(
            settings.KAFKA_TOPIC_RAW,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id=settings.KAFKA_CONSUMER_GROUP,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',  # Start from latest messages
            enable_auto_commit=True,
        )
        self.message_handler = message_handler
        print(f"✅ GBFS Consumer initialized - Topic: {settings.KAFKA_TOPIC_RAW}")
    
    def run(self):
        """Start consuming messages"""
        print(f"🚀 Starting GBFS Consumer (group: {settings.KAFKA_CONSUMER_GROUP})")
        
        try:
            for message in self.consumer:
                try:
                    # Process the message
                    bike_data = message.value
                    self.message_handler(bike_data)
                
                except Exception as e:
                    print(f"❌ Error processing message: {e}")
                    continue
        
        except KeyboardInterrupt:
            print("\n🛑 Stopping GBFS Consumer...")
        finally:
            self.consumer.close()
            print("✅ Consumer closed")


class BatchGBFSConsumer:
    """Consumer that batches messages before processing"""
    
    def __init__(
        self, 
        batch_handler: Callable[[List[Dict]], None],
        batch_size: int = 100,
        batch_timeout_ms: int = 5000
    ):
        """
        Initialize batch consumer
        
        Args:
            batch_handler: Function to process a batch of messages
            batch_size: Number of messages to batch
            batch_timeout_ms: Max time to wait for batch
        """
        self.consumer = KafkaConsumer(
            settings.KAFKA_TOPIC_RAW,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id=settings.KAFKA_CONSUMER_GROUP,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',
            enable_auto_commit=True,
            max_poll_records=batch_size,
        )
        self.batch_handler = batch_handler
        self.batch_size = batch_size
        self.batch_timeout_ms = batch_timeout_ms
        print(f"✅ Batch GBFS Consumer initialized (batch_size: {batch_size})")
    
    def run(self):
        """Start consuming messages in batches"""
        print(f"🚀 Starting Batch GBFS Consumer")
        
        try:
            batch = []
            
            for message in self.consumer:
                try:
                    batch.append(message.value)
                    
                    # Process batch when full
                    if len(batch) >= self.batch_size:
                        self.batch_handler(batch)
                        batch = []
                
                except Exception as e:
                    print(f"❌ Error processing message: {e}")
                    continue
            
            # Process remaining messages
            if batch:
                self.batch_handler(batch)
        
        except KeyboardInterrupt:
            print("\n🛑 Stopping Batch Consumer...")
        finally:
            self.consumer.close()
            print("✅ Consumer closed")
