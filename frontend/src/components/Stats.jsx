function Stats({ data, error }) {
  if (error) return null
  if (!data || !data.properties) return null

  const { total_vehicles, hexagon_count, timestamp, resolution } = data.properties

  const formatTime = (isoString) => {
    const date = new Date(isoString)
    return date.toLocaleTimeString()
  }

  return (
    <div className="absolute bottom-4 right-4 bg-gray-800 text-white p-4 rounded-lg shadow-lg z-10 min-w-[200px]">
      <h3 className="text-sm font-bold mb-2 text-gray-300">Statistics</h3>
      
      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-400">Vehicles:</span>
          <span className="font-bold">{total_vehicles?.toLocaleString() || 0}</span>
        </div>
        
        <div className="flex justify-between">
          <span className="text-gray-400">Hexagons:</span>
          <span className="font-bold">{hexagon_count?.toLocaleString() || 0}</span>
        </div>
        
        <div className="flex justify-between">
          <span className="text-gray-400">Resolution:</span>
          <span className="font-bold">{resolution}</span>
        </div>

        <div className="border-t border-gray-700 pt-2 mt-2">
          <div className="text-xs text-gray-400">
            Last updated: {timestamp ? formatTime(timestamp) : 'N/A'}
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="mt-4 pt-4 border-t border-gray-700">
        <div className="text-xs font-bold mb-2 text-gray-300">Density</div>
        <div className="flex items-center gap-1">
          <div className="flex-1 h-3 rounded" style={{
            background: 'linear-gradient(to right, rgba(255,30,30,0.55), rgba(255,70,40,0.6), rgba(255,110,30,0.62), rgba(255,150,20,0.62), rgba(255,200,30,0.65), rgba(200,220,40,0.67), rgba(120,210,70,0.68), rgba(60,200,90,0.7))'
          }}></div>
        </div>
        <div className="flex justify-between text-xs text-gray-400 mt-1">
          <span>Low</span>
          <span>High</span>
        </div>
      </div>
    </div>
  )
}

export default Stats
