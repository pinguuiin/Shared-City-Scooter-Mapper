# ScooterMap Frontend

Real-time visualization of shared mobility data using React, Vite, and deck.gl.

> **Note**: See the [main README](../README.md) for full project setup including backend services.

## Quick Start

```bash
# Install dependencies
npm install

# Start development server (backend must be running on port 8000)
npm run dev
```

The app will be available at `http://localhost:5173`

## Features

- 🗺️ **Interactive Map**: Powered by deck.gl and MapLibre GL
- 🔥 **Heatmap Visualization**: H3 hexagonal aggregation with color-coded density
- 🎚️ **Dynamic Resolution**: Switch between resolution levels 6-9 (neighborhood → block)
- 🔄 **Auto-refresh**: Real-time updates every 30 seconds
- 📊 **Statistics Panel**: Live vehicle and hexagon counts with legend
- ⚠️ **Alert System**: Configurable alerts for low-availability hexagons
- 🎨 **Modern UI**: Built with Tailwind CSS

## Architecture

```
frontend/
├── src/
│   ├── components/
│   │   ├── Map.jsx           # Main map component with deck.gl and MapLibre
│   │   ├── Controls.jsx      # Resolution and filter controls
│   │   ├── Stats.jsx         # Statistics panel
│   │   └── AlertLog.jsx      # Live alert log panel
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

The frontend connects to the backend at `/api/heatmap/geojson`:

**Parameters:**
- `resolution`: H3 resolution (6-9)
- `min_count`: Minimum vehicles per hexagon (default: 0)

Vite proxies `/api/*` to `http://localhost:8000` during development (see [vite.config.js](vite.config.js)).

## Components

### Map.jsx
- deck.gl GeoJsonLayer for hexagon rendering
- Color scaling by vehicle density
- Alert highlighting (red borders for low counts)
- Interactive tooltips

### Controls.jsx
- Resolution selector (6-9)
- Alert threshold slider
- Auto-refresh toggle
- Manual refresh button

### Stats.jsx
- Real-time statistics display
- Color gradient legend
- Update timestamp

### AlertLog.jsx
- Bottom-right panel showing low-availability alerts
- Clears on resolution change
- Auto-scrolls to new entries

## Color Scale

Gradient from red (low density/count=0) to green (high density), with higher opacity for better visibility.

## Technologies

- **React 18** + **Vite** - Fast modern dev environment
- **deck.gl 9** - WebGL-powered hexagon visualization
- **MapLibre GL** + **react-map-gl** - Base map rendering
- **Tailwind CSS** - Utility-first styling

## Configuration

### Map Center & Style

Edit initial view in [Map.jsx](src/components/Map.jsx):
```jsx
longitude: 6.0839, latitude: 50.7753, zoom: 13  // Aachen
mapStyle: "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"
```

### Refresh Interval

Change auto-refresh in [App.jsx](src/App.jsx):
```jsx
setInterval(() => loadData(), 30000)  // 30s default
```

## Troubleshooting

**No data displayed:**
- Verify backend is running: `curl http://localhost:8000/api/health`
- Check producer/consumer are processing data
- Try resolution 6 or 7 (coarser view)

**Performance issues:**
- Use coarser resolution (6-7 vs 8-9)
- Disable auto-refresh during exploration

**API connection errors:**
- Backend must run on port 8000
- Check CORS configuration in backend

## Development

Add new features:
- API calls → [src/services/api.js](src/services/api.js)
- Components → [src/components/](src/components/)
- State → [App.jsx](src/App.jsx)

```bash
npm run lint  # Check code style
npm run build # Production build
```
