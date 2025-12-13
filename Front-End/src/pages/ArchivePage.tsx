import { useState, useEffect } from 'react'
import { Plus, Search, Filter, FileText, Image, Instagram } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../lib/api'
import { ArchiveItem } from '../types'
import ArchiveItemCard from '../components/ArchiveItemCard'
import CreateArchiveModal from '../components/CreateArchiveModal'
import ArchiveDetailModal from '../components/ArchiveDetailModal'
import EditArchiveModal from '../components/EditArchiveModal'

export default function ArchivePage() {
  const [items, setItems] = useState<ArchiveItem[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedField, setSelectedField] = useState<string>('')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [selectedItem, setSelectedItem] = useState<ArchiveItem | null>(null)
  const [editingItem, setEditingItem] = useState<ArchiveItem | null>(null)

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

  const handleDelete = async (id: string) => {
    try {
      await api.delete(`/archive/${id}`)
      toast.success('Item deleted successfully')
      fetchItems()
    } catch (error) {
      toast.error('Failed to delete item')
      console.error(error)
    }
  }

  const filteredItems = items.filter(item =>
    item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.content.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-md border-b border-gray-200/50 shadow-sm">
        <div className="px-8 py-6">
          {/* <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent mb-6">
            Archive
          </h1> */}

          {/* Search and Filters */}
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-purple-400" size={20} />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search your archive..."
                className="w-full pl-12 pr-4 py-3 bg-white/90 backdrop-blur-sm border border-purple-200 rounded-full text-gray-900 placeholder-gray-400 focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none shadow-sm transition-all"
              />
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
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-8">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="relative">
              <div className="animate-spin rounded-full h-16 w-16 border-4 border-purple-200"></div>
              <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-purple-600 absolute top-0"></div>
            </div>
          </div>
        ) : filteredItems.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full">
            <div className="bg-gradient-to-br from-purple-100 to-pink-100 p-6 rounded-full mb-4">
              <Filter size={64} className="text-purple-600" />
            </div>
            <p className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              No items found
            </p>
            <p className="text-sm mt-2 text-gray-500">Try adjusting your search or filters</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredItems.map(item => (
              <ArchiveItemCard 
                key={item.id} 
                item={item} 
                onUpdate={fetchItems}
                onClick={() => setSelectedItem(item)}
                onEdit={(item) => setEditingItem(item)}
                onDelete={handleDelete}
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

      {editingItem && (
        <EditArchiveModal
          item={editingItem}
          onClose={() => setEditingItem(null)}
          onSuccess={() => {
            setEditingItem(null)
            fetchItems()
          }}
        />
      )}

      {/* Floating Add Button */}
      <button
        onClick={() => setShowCreateModal(true)}
        className="fixed bottom-8 right-8 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 hover:from-blue-700 hover:via-purple-700 hover:to-pink-700 text-white p-5 rounded-full shadow-2xl transition-all hover:shadow-purple-500/50 hover:scale-110 z-40 group"
      >
        <Plus size={28} className="group-hover:rotate-90 transition-transform duration-300" />
      </button>
    </div>
  )
}
