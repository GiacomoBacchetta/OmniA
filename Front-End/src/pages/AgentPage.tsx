import { useState } from 'react'
import { Send, Loader } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../lib/api'
import { QueryResponse } from '../types'

export default function AgentPage() {
  const [query, setQuery] = useState('')
  const [selectedField, setSelectedField] = useState('')
  const [conversation, setConversation] = useState<Array<{ role: 'user' | 'assistant'; content: string }>>([])
  const [loading, setLoading] = useState(false)

  const fields = ['personal', 'work', 'inspiration', 'learning', 'health', 'finance']

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return

    const userMessage = query
    setQuery('')
    setConversation(prev => [...prev, { role: 'user', content: userMessage }])
    setLoading(true)

    try {
      const response = await api.post<QueryResponse>('/query', {
        query: userMessage,
        field: selectedField || undefined,
      })

      setConversation(prev => [
        ...prev,
        { role: 'assistant', content: response.data.response },
      ])
    } catch (error) {
      toast.error('Failed to get response from agent')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">AI Agent</h1>
            <p className="text-gray-600 mt-1">Ask questions about your archived content</p>
          </div>
          <select
            value={selectedField}
            onChange={(e) => setSelectedField(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-full focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none text-center"
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

      {/* Chat Container */}
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-4xl mx-auto space-y-6">
          {conversation.length === 0 ? (
            <div className="text-center text-gray-500 mt-20">
              <h2 className="text-2xl font-semibold mb-4">Ask me anything!</h2>
              <p>I can help you search and understand your archived content.</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-8 max-w-2xl mx-auto">
                <button
                  onClick={() => setQuery("What restaurants have I saved?")}
                  className="p-4 bg-white rounded-full border border-gray-200 hover:border-primary-500 text-left transition-colors"
                >
                  <p className="font-medium text-center">Find restaurants</p>
                  <p className="text-sm text-gray-500 mt-1 text-center">What restaurants have I saved?</p>
                </button>
                <button
                  onClick={() => setQuery("Summarize my work notes from this week")}
                  className="p-4 bg-white rounded-full border border-gray-200 hover:border-primary-500 text-left transition-colors"
                >
                  <p className="font-medium text-center">Work summary</p>
                  <p className="text-sm text-gray-500 mt-1 text-center">Summarize my work notes</p>
                </button>
                <button
                  onClick={() => setQuery("Show me all items with locations")}
                  className="p-4 bg-white rounded-full border border-gray-200 hover:border-primary-500 text-left transition-colors"
                >
                  <p className="font-medium text-center">Location search</p>
                  <p className="text-sm text-gray-500 mt-1 text-center">Show items with locations</p>
                </button>
                <button
                  onClick={() => setQuery("What have I learned recently?")}
                  className="p-4 bg-white rounded-full border border-gray-200 hover:border-primary-500 text-left transition-colors"
                >
                  <p className="font-medium text-center">Learning progress</p>
                  <p className="text-sm text-gray-500 mt-1 text-center">What have I learned?</p>
                </button>
              </div>
            </div>
          ) : (
            <>
              {conversation.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-2xl px-6 py-4 rounded-2xl ${
                      message.role === 'user'
                        ? 'bg-primary-600 text-white'
                        : 'bg-white border border-gray-200 text-black'
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{message.content}</p>
                  </div>
                </div>
              ))}
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-white border border-gray-200 px-6 py-4 rounded-2xl">
                    <Loader className="animate-spin text-primary-600" size={24} />
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Input */}
      <div className="bg-white border-t border-gray-200 p-6">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
          <div className="flex gap-4">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask me anything about your archive..."
              className="flex-1 px-6 py-4 border border-gray-300 rounded-full focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="px-8 py-4 bg-primary-600 hover:bg-primary-700 text-white rounded-full transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send size={20} />
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
