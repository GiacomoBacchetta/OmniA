import { useState } from 'react'
import { X, FileText, Upload, Link as LinkIcon, Check } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../lib/api'

interface Props {
  onClose: () => void
  onSuccess: () => void
}

export default function CreateArchiveModal({ onClose, onSuccess }: Props) {
  const [contentType, setContentType] = useState<'text' | 'file' | 'instagram'>('text')
  const [field, setField] = useState('personal')
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [url, setUrl] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [selectedTags, setSelectedTags] = useState<string[]>([])
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
    productivity: 'bg-orange-100 text-orange-700 hover:bg-orange-200',
    entertainment: 'bg-pink-100 text-pink-700 hover:bg-pink-200',
    sports: 'bg-lime-100 text-lime-700 hover:bg-lime-200',
    hobby: 'bg-cyan-100 text-cyan-700 hover:bg-cyan-200',
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
      if (contentType === 'text') {
        await api.post('/archive/text', {
          field,
          title,
          content,
          tags: selectedTags,
        })
      } else if (contentType === 'file' && file) {
        const formData = new FormData()
        formData.append('field', field)
        formData.append('title', title)
        formData.append('file', file)
        if (selectedTags.length > 0) formData.append('tags', JSON.stringify(selectedTags))

        await api.post('/archive/file', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        })
      } else if (contentType === 'instagram') {
        await api.post('/archive/instagram', {
          field,
          url,
          title,
          tags: selectedTags,
        })
      }

      toast.success('Item added successfully!')
      onSuccess()
    } catch (error) {
      toast.error('Failed to add item')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200 flex items-center justify-between sticky top-0 bg-white">
          <h2 className="text-2xl font-bold text-gray-900">Add to Archive</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-xl transition-colors text-gray-700 hover:text-gray-900"
          >
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Content Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Content Type
            </label>
            <div className="grid grid-cols-3 gap-4">
              {[
                { type: 'text', icon: FileText, label: 'Text' },
                { type: 'file', icon: Upload, label: 'File' },
                { type: 'instagram', icon: LinkIcon, label: 'Instagram' },
              ].map(({ type, icon: Icon, label }) => (
                <button
                  key={type}
                  type="button"
                  onClick={() => setContentType(type as any)}
                  className={`p-4 border-2 rounded-xl flex flex-col items-center gap-2 transition-colors ${
                    contentType === type
                      ? 'border-blue-600 bg-blue-50 text-blue-700'
                      : 'border-gray-200 hover:border-gray-300 text-gray-700 bg-white'
                  }`}
                >
                  <Icon size={24} />
                  <span className="text-sm font-medium">{label}</span>
                </button>
              ))}
            </div>
          </div>

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
              className="w-full px-4 py-2 bg-white border border-gray-300 rounded-xl text-gray-900 placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
              required
            />
          </div>

          {/* Content based on type */}
          {contentType === 'text' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Content
              </label>
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                rows={6}
                className="w-full px-4 py-2 bg-white border border-gray-300 rounded-xl text-gray-900 placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none resize-none"
                placeholder="Include location data like addresses or Google Maps URLs for automatic map marking..."
                required
              />
            </div>
          )}

          {contentType === 'file' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                File
              </label>
              <input
                type="file"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="w-full px-4 py-2 bg-white border border-gray-300 rounded-xl text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                required
              />
            </div>
          )}

          {contentType === 'instagram' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Instagram URL
              </label>
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://www.instagram.com/p/..."
                className="w-full px-4 py-2 bg-white border border-gray-300 rounded-xl text-gray-900 placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                required
              />
            </div>
          )}

          {/* Tags */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tags
            </label>
            <div className="flex flex-wrap gap-2 p-3 bg-gray-50 border border-gray-300 rounded-xl max-h-48 overflow-y-auto">
              {availableTags.map(tag => (
                <button
                  key={tag}
                  type="button"
                  onClick={() => toggleTag(tag)}
                  className={`px-3 py-1.5 rounded-xl text-sm font-medium transition-all ${
                    selectedTags.includes(tag)
                      ? `${tagColors[tag] || 'bg-gray-200 text-gray-800'} ring-2 ring-offset-1 ring-blue-500`
                      : `${tagColors[tag] || 'bg-gray-100 text-gray-600'} hover:shadow-sm`
                  }`}
                >
                  {selectedTags.includes(tag) && <Check size={14} className="inline mr-1" />}
                  {tag}
                </button>
              ))}
            </div>
            {selectedTags.length > 0 && (
              <p className="text-xs text-gray-500 mt-2">
                {selectedTags.length} tag{selectedTags.length !== 1 ? 's' : ''} selected
              </p>
            )}
          </div>

          {/* Actions */}
          <div className="flex gap-4 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-6 py-3 bg-white border border-gray-300 rounded-xl text-gray-700 font-medium hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl transition-colors shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Adding...' : 'Add to Archive'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
