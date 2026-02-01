#!/bin/bash

# Test the API endpoints

BASE_URL="http://localhost:8000"

echo "🧪 Testing ScooterMap API"
echo "========================="
echo ""

echo "1. Testing health endpoint..."
curl -s "$BASE_URL/api/health" | jq '.' || echo "❌ Health check failed"
echo ""
echo ""

echo "2. Testing heatmap endpoint (resolution 6)..."
curl -s "$BASE_URL/api/heatmap?resolution=6" | jq '.resolution, .total_vehicles, .hexagon_count' || echo "❌ Heatmap failed"
echo ""
echo ""

echo "3. Testing GeoJSON endpoint..."
curl -s "$BASE_URL/api/heatmap/geojson?resolution=6" | jq '.type, .properties' || echo "❌ GeoJSON failed"
echo ""
echo ""

echo "4. Testing stats endpoint..."
curl -s "$BASE_URL/api/stats" | jq '.database' || echo "❌ Stats failed"
echo ""
echo ""

echo "5. Testing different resolutions..."
for res in 4 5 6 7; do
    echo "   Resolution $res:"
    curl -s "$BASE_URL/api/heatmap?resolution=$res" | jq '.hexagon_count' || echo "   ❌ Failed"
done
echo ""

echo "========================="
echo "✅ Testing complete!"
