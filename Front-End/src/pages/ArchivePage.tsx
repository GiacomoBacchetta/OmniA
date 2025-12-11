import { useState, useEffect } from 'react'
import { Plus, Search, Filter, FileText, Image, Instagram } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../lib/api'
import { ArchiveItem } from '../types'
import ArchiveItemCard from '../components/ArchiveItemCard'
import CreateArchiveModal from '../components/CreateArchiveModal'
import ArchiveDetailModal from '../components/ArchiveDetailModal'

export default function ArchivePage() {
  const [items, setItems] = useState<ArchiveItem[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedField, setSelectedField] = useState<string>('')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [selectedItem, setSelectedItem] = useState<ArchiveItem | null>(null)

  const fields = ['personal', 'work', 'inspiration', 'learning', 'health', 'finance']

  useEffect(() => {
    fetchItems()
  }, [selectedField])

  const fetchItems = async () => {
    try {
      const params = selectedField ? { field: selectedField } : {}
      const response = await api.get('/archive/items', { params })
      setItems(response.data.items || [])
    } catch (error) {
      toast.error('Failed to fetch archive items')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const filteredItems = items.filter(item =>
    item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.content.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-3xl font-bold text-gray-900">Archive</h1>
        </div>

        {/* Search and Filters */}
        <div className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search your archive..."
              className="w-full pl-10 pr-4 py-2 bg-white border border-gray-300 rounded-full text-gray-900 placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            />
          </div>

          <select
            value={selectedField}
            onChange={(e) => setSelectedField(e.target.value)}
            className="px-4 py-2 bg-white border border-gray-300 rounded-full text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-center"
          >
            <option value="">All Fields</option>
            {fields.map(field => (
              <option key={field} value={field}>
                {field.charAt(0).toUpperCase() + field.slice(1)}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : filteredItems.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full">
            <Filter size={64} className="mb-4 text-gray-300" />
            <p className="text-xl font-semibold text-gray-700">No items found</p>
            <p className="text-sm mt-2 text-gray-500">Try adjusting your search or filters</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredItems.map(item => (
              <ArchiveItemCard 
                key={item.id} 
                item={item} 
                onUpdate={fetchItems}
                onClick={() => setSelectedItem(item)}
              />
            ))}
          </div>
        )}
      </div>

      {showCreateModal && (
        <CreateArchiveModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            setShowCreateModal(false)
            fetchItems()
          }}
        />
      )}

      {selectedItem && (
        <ArchiveDetailModal
          item={selectedItem}
          onClose={() => setSelectedItem(null)}
        />
      )}

      {/* Floating Add Button */}
      <button
        onClick={() => setShowCreateModal(true)}
        className="fixed bottom-6 right-6 bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-full shadow-lg transition-all hover:shadow-xl z-40"
      >
        <Plus size={24} />
      </button>
    </div>
  )
}
