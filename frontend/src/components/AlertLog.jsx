import { useEffect, useRef } from 'react'

function AlertLog({ alerts, resolution }) {
  const logRef = useRef(null)

  // Auto-scroll to bottom when new alerts arrive
  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight
    }
  }, [alerts])

  if (alerts.length === 0) {
    return (
      <div className="absolute bottom-4 right-4 bg-gray-800 text-white p-4 rounded-lg shadow-lg z-10 w-96">
        <h3 className="text-sm font-bold mb-2 flex items-center gap-2">
          <span className="text-green-500">✓</span>
          Alert Log (Res {resolution})
        </h3>
        <div className="text-xs text-gray-400">
          No low-count hexagons detected.
        </div>
      </div>
    )
  }

  return (
    <div className="absolute bottom-4 right-4 bg-gray-800 text-white p-4 rounded-lg shadow-lg z-10 w-96">
      <h3 className="text-sm font-bold mb-2 flex items-center gap-2">
        <span className="text-red-500">⚠</span>
        Alert Log (Res {resolution})
        <span className="ml-auto text-xs font-normal text-gray-400">
          {alerts.length} warning{alerts.length !== 1 ? 's' : ''}
        </span>
      </h3>
      
      <div 
        ref={logRef}
        className="space-y-2 max-h-64 overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-gray-800"
      >
        {alerts.map((alert, idx) => (
          <div 
            key={`${alert.h3_index}-${idx}`}
            className="bg-red-900/30 border border-red-700/50 rounded p-2 text-xs"
          >
            <div className="flex items-start gap-2">
              <span className="text-red-400 font-bold">⚠</span>
              <div className="flex-1">
                <div className="font-mono text-gray-300">
                  {alert.h3_index.slice(0, 12)}...
                </div>
                <div className="text-red-300 mt-1">
                  Low availability: <span className="font-bold">{alert.count}</span> scooter{alert.count !== 1 ? 's' : ''} only
                </div>
                <div className="text-gray-400 text-[10px] mt-1">
                  {new Date(alert.timestamp).toLocaleTimeString()}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default AlertLog
