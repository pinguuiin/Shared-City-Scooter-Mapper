# 🗺️ Real-Time Shared Mobility Heatmap

![alertmap](https://github.com/user-attachments/assets/331085a5-ebd9-4de9-815c-b52728b422c5)

<br>A brief note on AI assistance: This project was developed by the author with assistance from AI agents as a learning exercise to explore stream processing, web development, and deploying FastAPI services. The author retains full responsibility for the final code.

A real-time scooter availability heatmap server combining Kafka-based streaming architecture patterns, batch processed messages, H3 multi-resolution aggregation with embedded DuckDB analytics, a FastAPI backend, and an interactive map frontend with live alert log for urban mobility monitoring and operational insights.

## 🎯 Project Overview

This project demonstrates an ETL data pipeline that:
- **Ingests** scooter location data from GBFS feeds every 60 seconds
- **Processes** geographic coordinates using Uber's H3 hexagonal spatial indexing
- **Aggregates** vehicle density across multiple resolution levels (resolutions 6-9, representing ~3km to ~174m)
- **Serves** heatmap data via FastAPI with 50-200ms query latency
- **Visualizes** density patterns with live alerm system through a React frontend using deck.gl and MapLibre GL

## 🏗️ Architecture

```
┌─────────────┐
│ GBFS Feeds  │ (Public bike-share APIs)
└──────┬──────┘
       │
       ↓ (Every 60s)
┌─────────────┐
│  Producer   │ (Python)
└──────┬──────┘
       │
       ↓ (Kafka Protocol)
┌─────────────┐
│  Redpanda   │ (Streaming Platform)
└──────┬──────┘
       │
       ↓ (Consumer)
┌─────────────┐
│ Aggregation │ (H3 Encoding + Aggregation)
│   Worker    │
└──────┬──────┘
       │
       ↓ (Writes)
┌─────────────┐
│   DuckDB    │ (Embedded Analytics DB)
└──────┬──────┘
       │
       ↓ (Queries)
┌─────────────┐
│  FastAPI    │ (REST API)
└──────┬──────┘
       │
       ↓ (HTTP)
┌─────────────┐
│  Frontend   │ (React + Deck.gl + Nginx)
└─────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Docker** & **Docker Compose**
  - [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/macOS) 
  - [Docker Engine](https://docs.docker.com/engine/install/) (Linux)
- **jq** (for running test script)
  - Linux: `sudo apt-get install jq`
  - macOS: `brew install jq`
  - Windows (WSL): `sudo apt-get install jq`

### Running with Docker

**Start all services:**
```bash
docker compose up -d
```

**Access the application:**
- **Frontend:** http://localhost:3000
- **API Documentation:** http://localhost:8000/docs
- **Redpanda Console:** http://localhost:8080

**View logs:**
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f producer
docker-compose logs -f consumer
```

**Stop all services:**
```bash
docker-compose down
```

**Services included:**
| Service | Description | Port |
|---------|-------------|------|
| frontend | React app with nginx | 3000 |
| backend | FastAPI REST API | 8000 |
| producer | GBFS data fetcher | - |
| consumer | Data aggregation worker | - |
| redpanda | Kafka-compatible broker | 19092 |
| console | Redpanda web UI | 8080 |

### Test the API

```bash
# Health check
curl http://localhost:8000/api/health

# Get heatmap data (resolution 6)
curl http://localhost:8000/api/heatmap?resolution=6

# Get GeoJSON format for deck.gl
curl http://localhost:8000/api/heatmap/geojson?resolution=6

# Get statistics
curl http://localhost:8000/api/stats
```

## 🔧 Configuration

Edit `.env` to customize:

| Variable | Description | Default |
|----------|-------------|---------|
| `GBFS_URL` | GBFS feed endpoint | Aachen Dott scooters |
| `GBFS_FETCH_INTERVAL` | Fetch interval (seconds) | 60 |
| `H3_RESOLUTIONS` | H3 resolution levels | [9, 8, 7, 6] |
| `KAFKA_BOOTSTRAP_SERVERS` | Kafka broker address | redpanda:9092 (Docker) |
| `DUCKDB_PATH` | DuckDB file path | data/mobility.duckdb |
| `WINDOW_SIZE_MINUTES` | Aggregation window | 5 |
| `RETENTION_MINUTES` | Data retention period | 60 |

### H3 Resolution Guide

| Resolution | Avg Hexagon Edge | Use Case |
|------------|------------------|----------|
| 6 | ~3 km | District |
| 7 | ~1 km | Neighborhood |
| 8 | ~461 m | Street-level |
| 9 | ~174 m | Block-level detail |

## 📊 API Endpoints

### `GET /api/heatmap`

Get aggregated vehicle counts per hexagon.

**Query Parameters:**
- `resolution` (int): H3 resolution (6-9, default: 8)
- `min_count` (int): Minimum vehicles per hexagon (default: 1)

**Response:**
```json
{
  "resolution": 6,
  "timestamp": "2026-01-31T12:00:00",
  "hexagons": [
    {
      "h3_index": "862a1073fffffff",
      "center": {"lat": 52.52, "lon": 13.40},
      "boundary": [...],
      "count": 15,
      "last_updated": "2026-01-31T12:00:00"
    }
  ],
  "total_vehicles": 450,
  "hexagon_count": 120
}
```

### `GET /api/heatmap/geojson`

Get heatmap data as GeoJSON FeatureCollection (optimized for deck.gl).

### `GET /api/stats`

Get database and system statistics.

### `GET /api/health`

Health check for all services.

## 🔍 Key Features

### 1. **Multi-Resolution Aggregation**
- Automatically aggregates data at resolutions 6, 7, 8, and 9
- Parent-child hexagon relationships for zoom levels
- Query any resolution without re-computation

### 2. **Sliding Window**
- Configurable time windows (default: 5 minutes)
- Automatic data cleanup (default: 60 minutes retention)
- Real-time updates every 60 seconds

### 3. **Performance Optimizations**
- Batch processing (1000 messages/batch)
- DuckDB for fast analytical queries
- Thread-safe database operations
- Efficient H3 spatial indexing

### 4. **Real-Time Alert System**
- Live alert log on the bottom-right panel
- Configurable alert threshold slider
- Visual highlighting underserved areas on the map
- Only tracking hexagons in active service areas
- Alert log auto-updates with map data every 30 seconds

### 5. **Production-Ready**
- Health checks and monitoring
- CORS support for frontend
- Comprehensive error handling
- Structured logging

## 🧪 Testing

```bash
# Test API endpoints using curl
curl http://localhost:8000/api/health
curl http://localhost:8000/api/heatmap/geojson?resolution=8

# Or use the test script
./test_api.sh
```

## 🐛 Troubleshooting

### Docker Issues

**Services fail to start:**
```bash
# Check logs
docker-compose logs

# Reset everything
docker-compose down -v
docker-compose up -d --build
```

**Port conflicts:**
- Ports 3000, 8000, 8080, 19092 must be available
- Change ports in docker-compose.yml if needed

### Producer not fetching data
- Check GBFS_URL is accessible: `curl $GBFS_URL`
- Verify Redpanda is running: `docker ps`
- Check logs: `docker-compose logs producer`

### Consumer not processing messages
- Check Kafka topic exists: `docker exec -it scootermap-redpanda rpk topic list`
- View consumer group status: `docker exec -it scootermap-redpanda rpk group list`
- Check logs: `docker-compose logs consumer`

### API returns empty heatmap
- Wait 60 seconds for first data fetch
- Check if producer and consumer are running: `docker-compose ps`
- Verify DuckDB has data: `ls -lh data/mobility.duckdb`

### DuckDB errors
- Ensure only ONE process writes to DuckDB
- Check file permissions on `data/` directory
- The `data/` directory is shared via volume mount

## 📈 Performance Characteristics

- **Latency**: ~50-200ms for heatmap queries
- **Throughput**: ~1000 vehicles/second processing
- **Memory**: ~200MB for API + Consumer
- **Storage**: ~10MB per hour of data

## 🔜 Future Enhancements

- [✅] Real-time alarm system for scooter shortage
- [✅] Dockerization with Docker Compose
- [ ] Landscape-based aggregation
- [ ] Redis caching layer
- [ ] WebSocket support for real-time updates
- [ ] Historical data analysis
- [ ] Multiple GBFS feed support
- [ ] Cloud deployment (AWS/GCP)

## 📝 Data Sources

This project uses GBFS (General Bikeshare Feed Specification) data:
- **Default**: Dott Scooters Aachen
- **Format**: https://gbfs.org/
- **Other cities**: https://github.com/MobilityData/gbfs

## 🙏 Acknowledgments

- **GBFS**: Mobility Data collaborative
- **H3**: Uber's Hexagonal Hierarchical Spatial Index
- **Redpanda**: Kafka-compatible streaming platform
- **DuckDB**: Embedded analytical database
- **FastAPI**: Modern Python web framework

---

**Built for Portfolio Demonstration** | Ping | 2026
