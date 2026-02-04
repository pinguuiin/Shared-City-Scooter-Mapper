import { useState, useEffect, useCallback } from 'react'
import Map from './components/Map'
import Controls from './components/Controls'
import Stats from './components/Stats'
import AlertLog from './components/AlertLog'
import { fetchHeatmapData } from './services/api'

function App() {
  const [resolution, setResolution] = useState(8)
  const [alertThreshold, setAlertThreshold] = useState(3)
  const [heatmapData, setHeatmapData] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [alerts, setAlerts] = useState([])

  // Callback to receive alerts from Map
  const handleAlertsUpdate = useCallback((newAlerts) => {
    setAlerts(newAlerts)
  }, [])

  // Fetch heatmap data
  const loadData = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const data = await fetchHeatmapData(resolution, 0)
      setHeatmapData(data)
    } catch (err) {
      console.error('Failed to load heatmap data:', err)
      setError(err.message || 'Failed to load data')
    } finally {
      setIsLoading(false)
    }
  }

  // Initial load
  useEffect(() => {
    loadData()
  }, [resolution])

  // Auto-refresh every 30 seconds
  useEffect(() => {
    if (!autoRefresh) return

    const interval = setInterval(() => {
      loadData()
    }, 30000) // 30 seconds

    return () => clearInterval(interval)
  }, [autoRefresh, resolution])

  return (
    <div className="relative w-full h-full">
      {/* Map */}
      <Map 
        data={heatmapData} 
        resolution={resolution}
        isLoading={isLoading}
        alertThreshold={alertThreshold}
        onAlertsUpdate={handleAlertsUpdate}
      />

      {/* Controls Panel */}
      <Controls
        resolution={resolution}
        setResolution={setResolution}
        alertThreshold={alertThreshold}
        setAlertThreshold={setAlertThreshold}
        autoRefresh={autoRefresh}
        setAutoRefresh={setAutoRefresh}
        onRefresh={loadData}
        isLoading={isLoading}
      />

      {/* Stats Panel */}
      <Stats 
        data={heatmapData}
        error={error}
      />

      {/* Alert Log */}
      <AlertLog 
        alerts={alerts}
        resolution={resolution}
      />

      {/* Error Toast */}
      {error && (
        <div className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50">
          <div className="flex items-center gap-2">
            <span className="text-xl">⚠️</span>
            <span>{error}</span>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
