import { useState } from 'react'
import { X, Check } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../lib/api'
import { ArchiveItem } from '../types'

interface Props {
  item: ArchiveItem
  onClose: () => void
  onSuccess: () => void
}

export default function EditArchiveModal({ item, onClose, onSuccess }: Props) {
  const [field, setField] = useState(item.field)
  const [title, setTitle] = useState(item.title)
  const [content, setContent] = useState(item.content || '')
  const [selectedTags, setSelectedTags] = useState<string[]>(item.tags || [])
  const [loading, setLoading] = useState(false)

  const fields = ['personal', 'work', 'inspiration', 'learning', 'health', 'finance']
  
  const availableTags = [
    'travel', 'food', 'fitness', 'coding', 'design', 'music', 
    'photography', 'reading', 'writing', 'art', 'nature', 'family',
    'friends', 'career', 'education', 'technology', 'business', 'finance',
    'health', 'mindfulness', 'productivity', 'entertainment', 'sports', 'hobby'
  ]
  
  const tagColors: Record<string, string> = {
    travel: 'bg-blue-100 text-blue-700 hover:bg-blue-200',
    food: 'bg-orange-100 text-orange-700 hover:bg-orange-200',
    fitness: 'bg-red-100 text-red-700 hover:bg-red-200',
    coding: 'bg-purple-100 text-purple-700 hover:bg-purple-200',
    design: 'bg-pink-100 text-pink-700 hover:bg-pink-200',
    music: 'bg-indigo-100 text-indigo-700 hover:bg-indigo-200',
    photography: 'bg-cyan-100 text-cyan-700 hover:bg-cyan-200',
    reading: 'bg-green-100 text-green-700 hover:bg-green-200',
    writing: 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200',
    art: 'bg-rose-100 text-rose-700 hover:bg-rose-200',
    nature: 'bg-emerald-100 text-emerald-700 hover:bg-emerald-200',
    family: 'bg-amber-100 text-amber-700 hover:bg-amber-200',
    friends: 'bg-teal-100 text-teal-700 hover:bg-teal-200',
    career: 'bg-slate-100 text-slate-700 hover:bg-slate-200',
    education: 'bg-violet-100 text-violet-700 hover:bg-violet-200',
    technology: 'bg-blue-100 text-blue-700 hover:bg-blue-200',
    business: 'bg-gray-100 text-gray-700 hover:bg-gray-200',
    finance: 'bg-green-100 text-green-700 hover:bg-green-200',
    health: 'bg-red-100 text-red-700 hover:bg-red-200',
    mindfulness: 'bg-purple-100 text-purple-700 hover:bg-purple-200',
    productivity: 'bg-indigo-100 text-indigo-700 hover:bg-indigo-200',
    entertainment: 'bg-pink-100 text-pink-700 hover:bg-pink-200',
    sports: 'bg-orange-100 text-orange-700 hover:bg-orange-200',
    hobby: 'bg-teal-100 text-teal-700 hover:bg-teal-200',
  }
  
  const toggleTag = (tag: string) => {
    setSelectedTags(prev => 
      prev.includes(tag) 
        ? prev.filter(t => t !== tag)
        : [...prev, tag]
    )
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      await api.put(`/archive/${item.id}`, {
        field,
        title,
        content: content || undefined,
        tags: selectedTags,
      })

      toast.success('Item updated successfully!')
      onSuccess()
    } catch (error) {
      toast.error('Failed to update item')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200 flex items-center justify-between sticky top-0 bg-white">
          <h2 className="text-2xl font-bold text-gray-900">Edit Archive Item</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-xl transition-colors text-gray-700 hover:text-gray-900"
          >
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Field */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Field
            </label>
            <select
              value={field}
              onChange={(e) => setField(e.target.value)}
              className="w-full px-4 py-2 bg-white border border-gray-300 rounded-xl text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
              required
            >
              {fields.map(f => (
                <option key={f} value={f}>
                  {f.charAt(0).toUpperCase() + f.slice(1)}
                </option>
              ))}
            </select>
          </div>

          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Title
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-4 py-2 bg-white border border-gray-300 rounded-xl text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
              required
            />
          </div>

          {/* Content - only if not file or instagram type */}
          {item.content_type === 'text' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Content
              </label>
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                className="w-full px-4 py-2 bg-white border border-gray-300 rounded-xl text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none min-h-[100px]"
                rows={4}
              />
            </div>
          )}

          {/* Tags */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Tags
            </label>
            <div className="flex flex-wrap gap-2">
              {availableTags.map(tag => (
                <button
                  key={tag}
                  type="button"
                  onClick={() => toggleTag(tag)}
                  className={`px-3 py-1.5 rounded-xl text-sm font-medium transition-colors flex items-center gap-1 ${
                    selectedTags.includes(tag)
                      ? tagColors[tag] || 'bg-gray-200 text-gray-800'
                      : 'bg-gray-50 text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  {selectedTags.includes(tag) && <Check size={14} />}
                  {tag}
                </button>
              ))}
            </div>
          </div>

          {/* Submit */}
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-6 py-3 bg-gray-100 text-gray-700 rounded-xl hover:bg-gray-200 transition-colors font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 text-white rounded-xl hover:shadow-lg transition-all font-medium disabled:opacity-50"
            >
              {loading ? 'Updating...' : 'Update Item'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
