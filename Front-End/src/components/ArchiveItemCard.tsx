import { ArchiveItem } from '../types'
import { Calendar, MapPin, Tag } from 'lucide-react'

interface Props {
  item: ArchiveItem
  onUpdate: () => void
  onClick: () => void
}

export default function ArchiveItemCard({ item, onClick }: Props) {
  const fieldColors: Record<string, string> = {
    personal: 'bg-purple-100 text-purple-800',
    work: 'bg-pink-100 text-pink-800',
    inspiration: 'bg-blue-100 text-blue-800',
    learning: 'bg-green-100 text-green-800',
    health: 'bg-red-100 text-red-800',
    finance: 'bg-yellow-100 text-yellow-800',
  }

  return (
    <div 
      onClick={onClick}
      className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-lg transition-shadow cursor-pointer"
    >
      <div className="flex items-start justify-between mb-3">
        <h3 className="text-lg font-semibold text-gray-900">{item.title}</h3>
        <span className={`px-3 py-1 rounded-full text-xs font-medium ${fieldColors[item.field] || 'bg-gray-100 text-gray-800'}`}>
          {item.field}
        </span>
      </div>

      <p className="text-gray-600 text-sm mb-4 line-clamp-3">{item.content}</p>

      <div className="flex flex-wrap gap-2 mb-4">
        {item.tags && item.tags.map(tag => (
          <span key={tag} className="flex items-center gap-1 px-2 py-1 bg-gray-100 text-gray-700 rounded-md text-xs">
            <Tag size={12} />
            {tag}
          </span>
        ))}
      </div>

      <div className="flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1">
            <Calendar size={14} />
            {new Date(item.created_at).toLocaleDateString()}
          </span>
          {item.location?.latitude && (
            <span className="flex items-center gap-1 text-primary-600">
              <MapPin size={14} />
              Location
            </span>
          )}
        </div>
      </div>
    </div>
  )
}
