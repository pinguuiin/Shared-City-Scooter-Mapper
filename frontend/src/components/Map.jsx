import { useState, useMemo, useEffect } from 'react'
import DeckGL from '@deck.gl/react'
import { Map as MapGL } from 'react-map-gl'
import { GeoJsonLayer } from '@deck.gl/layers'
import 'maplibre-gl/dist/maplibre-gl.css'

// Color scale: more saturated, slightly orange-ish progression (low->high)
// Smooth, bright but more transparent gradient (low -> high)
const COLOR_SCALE = [
  [255, 30, 30, 140],   // Vivid red (low, more transparent)
  [255, 70, 40, 150],   // Red-orange
  [255, 110, 30, 155],  // Orange
  [255, 150, 20, 155],  // Orange-yellow
  [255, 200, 30, 160],  // Yellow
  [200, 220, 40, 165],  // Yellow-green
  [120, 210, 70, 170],  // Green
  [60, 200, 90, 180],   // Bright green (high)
]

function getColorForCount(count, maxCount) {
  if (maxCount === 0) return COLOR_SCALE[0]
  
  const normalized = Math.min(count / maxCount, 1)
  const index = Math.floor(normalized * (COLOR_SCALE.length - 1))
  return COLOR_SCALE[index]
}

function Map({ data, resolution, isLoading, alertThreshold, onAlertsUpdate }) {
  const [viewState, setViewState] = useState({
    longitude: 6.0839,
    latitude: 50.7753,
    zoom: 13,
    pitch: 0,
    bearing: 0
  })

  // Calculate max count for color scaling
  const maxCount = useMemo(() => {
    if (!data || !data.features) return 1
    return Math.max(...data.features.map(f => f.properties.count), 1)
  }, [data])

  // Identify low-count hexagons for alerts
  const lowCountHexagons = useMemo(() => {
    if (!data || !data.features) return new Set()
    return new Set(
      data.features
        .filter(f => f.properties.count <= alertThreshold)
        .map(f => f.properties.h3_index)
    )
  }, [data, alertThreshold])

  // Generate alerts and notify parent
  useEffect(() => {
    if (!data || !data.features) {
      onAlertsUpdate([])
      return
    }

    const alerts = data.features
      .filter(f => f.properties.count <= alertThreshold)
      .map(f => ({
        h3_index: f.properties.h3_index,
        count: f.properties.count,
        timestamp: f.properties.last_updated || new Date().toISOString()
      }))

    onAlertsUpdate(alerts)
  }, [data, alertThreshold, onAlertsUpdate])

  // Create deck.gl layer
  const layers = useMemo(() => {
    if (!data || !data.features) return []

    return [
      new GeoJsonLayer({
        id: 'heatmap-layer',
        data: data,
        pickable: true,
        stroked: true,
        filled: true,
        extruded: false,
        lineWidthMinPixels: 1,
        getFillColor: f => {
          const baseColor = getColorForCount(f.properties.count, maxCount)
          // Add red tint to alerted hexagons
          if (lowCountHexagons.has(f.properties.h3_index)) {
            return [
              Math.min(baseColor[0] + 50, 255),
              Math.max(baseColor[1] - 30, 0),
              Math.max(baseColor[2] - 30, 0),
              Math.min(baseColor[3] + 40, 255)
            ]
          }
          return baseColor
        },
        getLineColor: f => {
          // Bright neon red borders for alerted hexagons
          return lowCountHexagons.has(f.properties.h3_index)
            ? [255, 20, 60, 255]  // Vivid neon red, fully opaque
            : [255, 255, 255, 30]  // Subtle white for normal
        },
        getLineWidth: f => {
          // Much thicker borders for alerted hexagons
          return lowCountHexagons.has(f.properties.h3_index) ? 3 : 1
        },
        updateTriggers: {
          getFillColor: [maxCount, lowCountHexagons],
          getLineColor: [lowCountHexagons],
          getLineWidth: [lowCountHexagons]
        }
      })
    ]
  }, [data, maxCount, lowCountHexagons])

  const getTooltip = ({ object }) => {
    if (!object) return null
    
    const { count, h3_index, last_updated } = object.properties
    return {
      html: `
        <div class="p-2">
          <div class="font-bold">${count} vehicle${count !== 1 ? 's' : ''}</div>
          <div class="text-xs text-gray-300 mt-1">H3: ${h3_index.slice(0, 10)}...</div>
          <div class="text-xs text-gray-300">Updated: ${new Date(last_updated).toLocaleTimeString()}</div>
        </div>
      `,
      style: {
        backgroundColor: '#1f2937',
        color: 'white',
        borderRadius: '8px',
        padding: '0',
        fontSize: '14px'
      }
    }
  }

  return (
    <DeckGL
      viewState={viewState}
      onViewStateChange={({ viewState }) => setViewState(viewState)}
      controller={true}
      layers={layers}
      getTooltip={getTooltip}
    >
      <MapGL
        mapLib={import('maplibre-gl')}
        mapStyle="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"
      />
      
      {/* Loading Indicator */}
      {isLoading && (
        <div className="absolute top-20 left-1/2 transform -translate-x-1/2 bg-gray-800 text-white px-4 py-2 rounded-lg shadow-lg z-10">
          <div className="flex items-center gap-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            <span>Loading data...</span>
          </div>
        </div>
      )}
    </DeckGL>
  )
}

export default Map
