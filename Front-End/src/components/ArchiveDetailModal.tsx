import { X, Calendar, MapPin, Tag, FileText, ExternalLink } from 'lucide-react'
import { ArchiveItem } from '../types'

interface Props {
  item: ArchiveItem
  onClose: () => void
}

export default function ArchiveDetailModal({ item, onClose }: Props) {
  const fieldColors: Record<string, string> = {
    personal: 'bg-purple-100 text-purple-800',
    work: 'bg-pink-100 text-pink-800',
    inspiration: 'bg-blue-100 text-blue-800',
    learning: 'bg-green-100 text-green-800',
    health: 'bg-red-100 text-red-800',
    finance: 'bg-yellow-100 text-yellow-800',
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl max-w-3xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-start justify-between p-6 border-b border-gray-200">
          <div className="flex-1 pr-4">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">{item.title}</h2>
            <div className="flex items-center gap-3">
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${fieldColors[item.field] || 'bg-gray-100 text-gray-800'}`}>
                {item.field}
              </span>
              <span className="flex items-center gap-1 text-sm text-gray-500">
                <Calendar size={14} />
                {new Date(item.created_at).toLocaleDateString('en-US', { 
                  year: 'numeric', 
                  month: 'long', 
                  day: 'numeric' 
                })}
              </span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Content Type */}
          <div className="mb-6">
            <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
              <FileText size={16} />
              <span className="font-medium">Content Type:</span>
              <span className="capitalize">{item.content_type}</span>
            </div>
          </div>

          {/* File Preview */}
          {item.file_url && (
            <div className="mb-6">
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Attached File</h3>
              {item.content_type === 'file' && item.file_name?.match(/\.(jpg|jpeg|png|gif|webp)$/i) ? (
                <img 
                  src={item.file_url} 
                  alt={item.title}
                  className="w-full rounded-full border border-gray-200"
                />
              ) : (
                <a
                  href={item.file_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 text-blue-600 hover:text-blue-700 text-sm"
                >
                  <ExternalLink size={16} />
                  {item.file_name || 'View File'}
                </a>
              )}
            </div>
          )}

          {/* Content */}
          <div className="mb-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-2">Content</h3>
            <p className="text-gray-900 whitespace-pre-wrap leading-relaxed">{item.content}</p>
          </div>

          {/* Tags */}
          {item.tags && item.tags.length > 0 && (
            <div className="mb-6">
              <h3 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                <Tag size={16} />
                Tags
              </h3>
              <div className="flex flex-wrap gap-2">
                {item.tags.map(tag => (
                  <span 
                    key={tag} 
                    className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Location */}
          {item.location && (item.location.latitude || item.location.address) && (
            <div className="mb-6">
              <h3 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                <MapPin size={16} />
                Location
              </h3>
              <div className="bg-gray-50 rounded-full p-4 border border-gray-200">
                {item.location.address && (
                  <p className="text-gray-900 mb-2">{item.location.address}</p>
                )}
                {item.location.latitude && item.location.longitude && (
                  <p className="text-sm text-gray-600 mb-2">
                    Coordinates: {item.location.latitude.toFixed(6)}, {item.location.longitude.toFixed(6)}
                  </p>
                )}
                {item.location.google_maps_url && (
                  <a
                    href={item.location.google_maps_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 text-blue-600 hover:text-blue-700 text-sm"
                  >
                    <ExternalLink size={14} />
                    Open in Google Maps
                  </a>
                )}
              </div>
            </div>
          )}

          {/* Metadata */}
          <div className="pt-4 border-t border-gray-200">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-500">Created:</span>
                <p className="text-gray-900 font-medium">
                  {new Date(item.created_at).toLocaleString('en-US', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </p>
              </div>
              {item.updated_at && (
                <div>
                  <span className="text-gray-500">Updated:</span>
                  <p className="text-gray-900 font-medium">
                    {new Date(item.updated_at).toLocaleString('en-US', {
                      year: 'numeric',
                      month: 'short',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-200 bg-gray-50">
          <button
            onClick={onClose}
            className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-full transition-colors font-medium"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
