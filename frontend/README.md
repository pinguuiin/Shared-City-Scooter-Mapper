# ScooterMap Frontend

Real-time visualization of shared mobility data using React, Vite, and deck.gl.

## Features

- 🗺️ **Interactive Map**: Powered by deck.gl and MapLibre GL
- 🔥 **Heatmap Visualization**: H3 hexagonal aggregation with color-coded density
- 🎚️ **Dynamic Resolution**: Switch between 4 resolution levels (city → street)
- 🔄 **Auto-refresh**: Real-time updates every 30 seconds
- 📊 **Statistics Panel**: Live vehicle and hexagon counts
- 🎨 **Modern UI**: Built with Tailwind CSS

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install
```

### Development

```bash
# Start development server
npm run dev
```

The app will be available at `http://localhost:5173`

### Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## Architecture

```
frontend/
├── src/
│   ├── components/
│   │   ├── Map.jsx           # Main map component with deck.gl
│   │   ├── Controls.jsx      # Resolution and filter controls
│   │   └── Stats.jsx         # Statistics panel
│   ├── services/
│   │   └── api.js            # API client functions
│   ├── App.jsx               # Root component
│   ├── main.jsx              # Entry point
│   └── index.css             # Global styles
├── index.html                # HTML template
├── vite.config.js            # Vite configuration
├── tailwind.config.js        # Tailwind CSS configuration
└── package.json              # Dependencies
```

## API Integration

The frontend connects to the backend API:

- **Endpoint**: `/api/heatmap/geojson`
- **Parameters**:
  - `resolution`: H3 resolution level (4-7)
  - `min_count`: Minimum vehicle count filter
- **Response**: GeoJSON FeatureCollection with hexagon polygons

### Proxy Configuration

Vite is configured to proxy API requests from `/api/*` to `http://localhost:8000` during development. See [vite.config.js](vite.config.js).

## Components

### Map Component

Renders the interactive map with deck.gl layers:
- GeoJsonLayer for hexagon visualization
- Color scaling based on vehicle density
- Tooltips showing hexagon details

### Controls Component

User interface for:
- Resolution level selection (4 resolutions)
- Minimum count filter slider
- Auto-refresh toggle
- Manual refresh button

### Stats Component

Displays real-time statistics:
- Total vehicle count
- Number of hexagons
- Current resolution
- Last update timestamp
- Color legend

## Color Scale

The heatmap uses a gradient from green (low density) to red (high density):

```
Green → Yellow-Green → Yellow → Orange → Red-Orange → Red
```

## Technologies

- **React 18**: UI framework
- **Vite**: Build tool and dev server
- **deck.gl 9**: WebGL-powered visualization
- **MapLibre GL**: Base map rendering
- **Tailwind CSS**: Styling
- **react-map-gl**: React wrapper for MapLibre

## Configuration

### Map Style

The default map style is CartoDB Dark Matter. To change it, edit the `mapStyle` prop in [Map.jsx](src/components/Map.jsx):

```jsx
<MapGL
  mapStyle="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"
/>
```

### Initial View State

Default center is Aachen (13.4050°E, 52.5200°N). Modify in [Map.jsx](src/components/Map.jsx):

```jsx
const [viewState, setViewState] = useState({
  longitude: 13.4050,
  latitude: 52.5200,
  zoom: 11,
  // ...
})
```

### Refresh Interval

Auto-refresh interval is 30 seconds. Change in [App.jsx](src/App.jsx):

```jsx
const interval = setInterval(() => {
  loadData()
}, 30000) // milliseconds
```

## Troubleshooting

### API Connection Issues

If you see "Failed to load data" errors:

1. Verify the backend is running on `http://localhost:8000`
2. Check backend health: `curl http://localhost:8000/api/health`
3. Ensure CORS is configured correctly in backend

### No Data Displayed

1. Verify the producer and consumer are running
2. Check that data exists in DuckDB
3. Try a lower `min_count` value
4. Switch to a coarser resolution (e.g., 4 or 5)

### Performance Issues

For large datasets:
- Use coarser resolution (4 or 5)
- Increase `min_count` filter
- Disable auto-refresh during exploration

## Development

### Adding New Features

1. API calls → Add to [src/services/api.js](src/services/api.js)
2. UI components → Add to [src/components/](src/components/)
3. State management → Update [App.jsx](src/App.jsx)

### Linting

```bash
npm run lint
```

## License

Part of the ScooterMap project.
