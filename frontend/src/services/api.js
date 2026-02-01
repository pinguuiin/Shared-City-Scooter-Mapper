const API_BASE_URL = '/api'

export async function fetchHeatmapData(resolution = 6, minCount = 1) {
  try {
    const response = await fetch(
      `${API_BASE_URL}/heatmap/geojson?resolution=${resolution}&min_count=${minCount}`
    )
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    return data
  } catch (error) {
    console.error('Error fetching heatmap data:', error)
    throw error
  }
}

export async function fetchStats() {
  try {
    const response = await fetch(`${API_BASE_URL}/stats`)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    return data
  } catch (error) {
    console.error('Error fetching stats:', error)
    throw error
  }
}

export async function fetchHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    return data
  } catch (error) {
    console.error('Error fetching health:', error)
    throw error
  }
}
