#!/bin/bash

# Test the API endpoints
BASE_URL="http://localhost:8000"

# Benchmark configuration
BENCH_RESOLUTION="${BENCH_RESOLUTION:-8}"
WARMUP_REQUESTS="${WARMUP_REQUESTS:-30}"
BENCH_REQUESTS="${BENCH_REQUESTS:-200}"

echo "==================================="
echo "🧪 Testing ScooterMap API endpoints"
echo "==================================="
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

echo "==================================="
echo "🧪 Testing aggregation results"
echo "==================================="
echo ""

echo "5. Testing different resolutions..."
for res in 6 7 8 9; do
    echo "   Resolution $res:"
    curl -s "$BASE_URL/api/heatmap?resolution=$res" | jq '.hexagon_count' || echo "   ❌ Failed"
done
echo ""
echo ""

echo "==================================="
echo "🧪 Latency benchmark test"
echo "==================================="
echo ""

echo "6. Benchmarking heatmap query latency (resolution ${BENCH_RESOLUTION})..."
echo "   Warm-up requests: ${WARMUP_REQUESTS}"
echo "   Measured requests: ${BENCH_REQUESTS}"

# Warm up the endpoint to reduce cold-start effects.
for i in $(seq 1 "$WARMUP_REQUESTS"); do
    curl -s -o /dev/null "$BASE_URL/api/heatmap?resolution=$BENCH_RESOLUTION"
done

tmp_ms_file="$(mktemp)"

# Collect latency samples in milliseconds.
for i in $(seq 1 "$BENCH_REQUESTS"); do
    sec=$(curl -s -o /dev/null -w "%{time_total}" "$BASE_URL/api/heatmap?resolution=$BENCH_RESOLUTION")
    awk -v s="$sec" 'BEGIN { printf "%.3f\n", s * 1000 }' >> "$tmp_ms_file"
done

summary=$(sort -n "$tmp_ms_file" | awk '
    {
        a[NR] = $1
        sum += $1
    }
    END {
        if (NR == 0) {
            print "❌ No benchmark samples collected"
            exit 1
        }
        p50_idx = int(NR * 0.50); if (p50_idx < 1) p50_idx = 1
        p95_idx = int(NR * 0.95); if (p95_idx < 1) p95_idx = 1
        p99_idx = int(NR * 0.99); if (p99_idx < 1) p99_idx = 1
        printf "   n=%d avg=%.2fms p50=%.2fms p95=%.2fms p99=%.2fms", NR, sum/NR, a[p50_idx], a[p95_idx], a[p99_idx]
    }
')

echo "$summary"
rm -f "$tmp_ms_file"

echo ""
echo "✅ All tests complete!"
