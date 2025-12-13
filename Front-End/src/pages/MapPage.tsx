import { useEffect, useState } from 'react'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import { Icon } from 'leaflet'
import { Map as MapIcon } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../lib/api'
import { MapMarker } from '../types'
import 'leaflet/dist/leaflet.css'

// Fix for default marker icons in production
delete (Icon.Default.prototype as any)._getIconUrl
Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

const fieldColors: Record<string, string> = {
  personal: '#667eea',
  work: '#f093fb',
  inspiration: '#4facfe',
  learning: '#43e97b',
  health: '#fa709a',
  finance: '#feca57',
}

export default function MapPage() {
  const [markers, setMarkers] = useState<MapMarker[]>([])
  const [selectedField, setSelectedField] = useState('')
  const [loading, setLoading] = useState(true)
  const [center, setCenter] = useState<[number, number]>([45.4642, 9.1900]) // Milan default

  const fields = ['personal', 'work', 'inspiration', 'learning', 'health', 'finance']

  useEffect(() => {
    fetchMarkers()
  }, [selectedField])

  const fetchMarkers = async () => {
    try {
      const params = selectedField ? { field: selectedField } : {}
      const response = await api.get('/archive/map/all', { params })
      setMarkers(response.data.markers || [])
      
      if (response.data.center_latitude && response.data.center_longitude) {
        setCenter([response.data.center_latitude, response.data.center_longitude])
      }
    } catch (error) {
      toast.error('Failed to fetch map markers')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const createCustomIcon = (field: string) => {
    const color = fieldColors[field] || '#667eea'
    return new Icon({
      iconUrl: `data:image/svg+xml;base64,${btoa(`
        <svg width="25" height="41" viewBox="0 0 25 41" xmlns="http://www.w3.org/2000/svg">
          <path d="M12.5 0C5.596 0 0 5.596 0 12.5c0 9.375 12.5 28.125 12.5 28.125S25 21.875 25 12.5C25 5.596 19.404 0 12.5 0z" fill="${color}"/>
          <circle cx="12.5" cy="12.5" r="7" fill="white"/>
        </svg>
      `)}`,
      iconSize: [25, 41],
      iconAnchor: [12, 41],
      popupAnchor: [1, -34],
    })
  }

  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-md border-b border-gray-200/50 shadow-sm">
        <div className="px-8 py-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              {/* <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
                Map View
              </h1> */}
            <p className="text-purple-600 font-medium mt-2">{markers.length} locations found</p>
            </div>
            
            <select
              value={selectedField}
              onChange={(e) => setSelectedField(e.target.value)}
              className="px-6 py-3 bg-white/90 backdrop-blur-sm border border-purple-200 rounded-full text-gray-900 focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none text-center font-medium shadow-sm transition-all cursor-pointer hover:border-purple-300"
            >
              <option value="">All Fields</option>
              {fields.map(field => (
                <option key={field} value={field}>
                  {field.charAt(0).toUpperCase() + field.slice(1)}
                </option>
              ))}
            </select>
          </div>

          {/* Legend */}
          <div className="flex gap-4 flex-wrap">
            {fields.map(field => (
              <div key={field} className="flex items-center gap-2 px-3 py-1.5 bg-white/60 backdrop-blur-sm rounded-full shadow-sm border border-purple-100">
                <div 
                  className="w-3 h-3 rounded-full shadow-sm" 
                  style={{ backgroundColor: fieldColors[field] }}
                />
                <span className="text-sm text-gray-700 capitalize font-medium">{field}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Map */}
      <div className="flex-1 relative">
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50">
            <div className="relative">
              <div className="animate-spin rounded-full h-16 w-16 border-4 border-purple-200"></div>
              <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-purple-600 absolute top-0"></div>
            </div>
          </div>
        ) : markers.length === 0 ? (
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <div className="bg-gradient-to-br from-purple-100 to-pink-100 p-6 rounded-full mb-4">
              <MapIcon className="text-purple-600" size={64} />
            </div>
            <p className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              No locations found
            </p>
            <p className="text-sm mt-2 text-gray-500">Archive items with location data will appear here</p>
          </div>
        ) : (
          <MapContainer
            center={center}
            zoom={10}
            style={{ height: '100%', width: '100%' }}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {markers.map(marker => (
              <Marker
                key={marker.id}
                position={[marker.latitude, marker.longitude]}
                icon={createCustomIcon(marker.field)}
              >
                <Popup>
                  <div className="min-w-[200px]">
                    <h3 className="font-semibold text-lg mb-2">{marker.title}</h3>
                    <span 
                      className="inline-block px-2 py-1 rounded-full text-xs text-white mb-2"
                      style={{ backgroundColor: fieldColors[marker.field] }}
                    >
                      {marker.field}
                    </span>
                    <p className="text-sm text-gray-600 mb-2">{marker.content_preview}</p>
                    <p className="text-xs text-gray-400">
                      {new Date(marker.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        )}
      </div>
    </div>
  )
}
