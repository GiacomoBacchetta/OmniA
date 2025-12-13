import { ArchiveItem } from '../types'
import { Calendar, MapPin, Tag, Pencil, Trash2 } from 'lucide-react'

interface Props {
  item: ArchiveItem
  onUpdate: () => void
  onClick: () => void
  onEdit: (item: ArchiveItem) => void
  onDelete: (id: string) => void
}

export default function ArchiveItemCard({ item, onClick, onEdit, onDelete }: Props) {
  const fieldColors: Record<string, string> = {
    personal: 'bg-purple-100 text-purple-800',
    work: 'bg-pink-100 text-pink-800',
    inspiration: 'bg-blue-100 text-blue-800',
    learning: 'bg-green-100 text-green-800',
    health: 'bg-red-100 text-red-800',
    finance: 'bg-yellow-100 text-yellow-800',
  }

  return (
    <div className="bg-white rounded-3xl border border-gray-200 p-6 hover:shadow-lg transition-shadow relative group">
      {/* Main card content - clickable */}
      <div onClick={onClick} className="cursor-pointer">
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

      {/* Action buttons - bottom right on hover */}
      <div className="absolute bottom-4 right-4 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        <button
          onClick={(e) => {
            e.stopPropagation()
            onEdit(item)
          }}
          className="p-2 bg-blue-500 text-white rounded-xl hover:bg-blue-600 transition-colors shadow-lg"
          title="Edit"
        >
          <Pencil size={14} />
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation()
            if (confirm('Are you sure you want to delete this item?')) {
              onDelete(item.id)
            }
          }}
          className="p-2 bg-red-500 text-white rounded-xl hover:bg-red-600 transition-colors shadow-lg"
          title="Delete"
        >
          <Trash2 size={14} />
        </button>
      </div>
    </div>
  )
}
