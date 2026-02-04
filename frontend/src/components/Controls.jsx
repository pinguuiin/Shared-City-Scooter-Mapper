function Controls({ 
  resolution, 
  setResolution, 
  alertThreshold,
  setAlertThreshold,
  autoRefresh,
  setAutoRefresh,
  onRefresh,
  isLoading
}) {
  const resolutions = [
    { value: 6, label: 'District (Res 6)', description: 'District view' },
    { value: 7, label: 'Neighborhood (Res 7)', description: 'Neighborhood' },
    { value: 8, label: 'Street (Res 8)', description: 'Recommended' },
    { value: 9, label: 'Block (Res 9)', description: 'Detailed view' }
  ]

  return (
    <div className="absolute top-4 left-4 bg-gray-800 text-white p-4 rounded-lg shadow-lg z-10 max-w-xs">
      <h2 className="text-lg font-bold mb-4">Free Scooter Map</h2>
      
      {/* Resolution Control */}
      <div className="mb-4">
        <label className="block text-sm font-medium mb-2">
          Resolution Level
        </label>
        <div className="space-y-2">
          {resolutions.map(({ value, label, description }) => (
            <button
              key={value}
              onClick={() => setResolution(value)}
              className={`w-full text-left px-3 py-2 rounded transition-colors ${
                resolution === value 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-700 hover:bg-gray-600 text-gray-200'
              }`}
            >
              <div className="font-medium">{label}</div>
              <div className="text-xs text-gray-400">{description}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Alert Threshold */}
      <div className="mb-4">
        <label className="block text-sm font-medium mb-2">
          Alert Threshold: {alertThreshold}
        </label>
        <input
          type="range"
          min="0"
          max="10"
          value={alertThreshold}
          onChange={(e) => setAlertThreshold(parseInt(e.target.value))}
          className="w-full"
        />
        <div className="flex justify-between text-xs text-gray-400 mt-1">
          <span>0</span>
          <span>10</span>
        </div>
        <div className="text-xs text-gray-400 mt-1">
          Warns when hexagon count ≤ threshold
        </div>
      </div>

      {/* Auto Refresh Toggle */}
      <div className="mb-4 flex items-center justify-between">
        <label className="text-sm font-medium">Auto Refresh (30s)</label>
        <button
          onClick={() => setAutoRefresh(!autoRefresh)}
          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
            autoRefresh ? 'bg-blue-600' : 'bg-gray-600'
          }`}
        >
          <span
            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
              autoRefresh ? 'translate-x-6' : 'translate-x-1'
            }`}
          />
        </button>
      </div>

      {/* Manual Refresh Button */}
      <button
        onClick={onRefresh}
        disabled={isLoading}
        className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-4 py-2 rounded transition-colors flex items-center justify-center gap-2"
      >
        {isLoading ? (
          <>
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            <span>Loading...</span>
          </>
        ) : (
          <>
            <span>🔄</span>
            <span>Refresh Now</span>
          </>
        )}
      </button>
    </div>
  )
}

export default Controls
