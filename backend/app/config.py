"""
Configuration management for the Real-Time Shared Mobility Heatmap
"""
import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "ScooterMap"
    DEBUG: bool = True
    
    # Kafka/Redpanda
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_RAW: str = "gbfs.raw"
    KAFKA_TOPIC_AGGREGATED: str = "gbfs.aggregated"
    KAFKA_CONSUMER_GROUP: str = "h3-aggregator"
    
    # GBFS
    GBFS_URL: str = "https://gbfs.api.ridedott.com/public/v2/berlin/free_bike_status.json"
    GBFS_FETCH_INTERVAL: int = 60  # seconds
    
    # DuckDB
    DUCKDB_PATH: str = "data/mobility.duckdb"
    
    # H3 Configuration
    H3_RESOLUTIONS: List[int] = [7, 6, 5, 4]  # From finest to coarsest
    H3_DEFAULT_RESOLUTION: int = 6
    
    # Sliding Window
    WINDOW_SIZE_MINUTES: int = 5
    RETENTION_MINUTES: int = 60
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
