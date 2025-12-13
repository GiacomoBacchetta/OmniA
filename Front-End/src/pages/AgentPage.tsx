import { useState, useEffect } from 'react'
import { Send, Loader, Sparkles } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../lib/api'
import { QueryResponse } from '../types'

export default function AgentPage() {
  const [query, setQuery] = useState('')
  const [selectedField, setSelectedField] = useState('')
  const [conversation, setConversation] = useState<Array<{ role: 'user' | 'assistant'; content: string }>>([])
  const [loading, setLoading] = useState(false)
  const [showFieldSuggestions, setShowFieldSuggestions] = useState(false)
  const [filteredFields, setFilteredFields] = useState<string[]>([])
  const [selectedSuggestionIndex, setSelectedSuggestionIndex] = useState(0)

  const fields = ['personal', 'work', 'inspiration', 'learning', 'health', 'finance']

  // Detect @ symbol for field tagging and filter suggestions
  useEffect(() => {
    const lastAtIndex = query.lastIndexOf('@')
    if (lastAtIndex !== -1) {
      const textAfterAt = query.substring(lastAtIndex + 1)
      const hasSpace = textAfterAt.includes(' ')
      
      if (!hasSpace) {
        setShowFieldSuggestions(true)
        // Filter fields based on what's typed after @
        const filtered = fields.filter(field => 
          field.toLowerCase().startsWith(textAfterAt.toLowerCase())
        )
        setFilteredFields(filtered)
        setSelectedSuggestionIndex(0)
      } else {
        setShowFieldSuggestions(false)
      }
    } else {
      setShowFieldSuggestions(false)
    }
  }, [query])

  const handleFieldSelect = (field: string) => {
    const lastAtIndex = query.lastIndexOf('@')
    if (lastAtIndex !== -1) {
      const beforeAt = query.substring(0, lastAtIndex)
      setQuery(beforeAt + '@' + field + ' ')
      setSelectedField(field)
    }
    setShowFieldSuggestions(false)
    setSelectedSuggestionIndex(0)
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Tab' && showFieldSuggestions && filteredFields.length > 0) {
      e.preventDefault()
      
      if (filteredFields.length === 1) {
        // Auto-complete with the only option
        handleFieldSelect(filteredFields[0])
      } else {
        // Cycle through options
        const nextIndex = (selectedSuggestionIndex + 1) % filteredFields.length
        setSelectedSuggestionIndex(nextIndex)
        
        // Update the query with the selected field
        const lastAtIndex = query.lastIndexOf('@')
        if (lastAtIndex !== -1) {
          const beforeAt = query.substring(0, lastAtIndex)
          setQuery(beforeAt + '@' + filteredFields[nextIndex])
        }
      }
    } else if (e.key === 'Enter' && showFieldSuggestions && filteredFields.length > 0) {
      // Complete with currently highlighted suggestion on Enter
      e.preventDefault()
      handleFieldSelect(filteredFields[selectedSuggestionIndex])
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return

    // Extract field from @mention if present
    let finalQuery = query
    let finalField = selectedField
    const fieldMatch = query.match(/@(\w+)/)
    if (fieldMatch) {
      const mentionedField = fieldMatch[1].toLowerCase()
      if (fields.includes(mentionedField)) {
        finalField = mentionedField
        finalQuery = query.replace(`@${mentionedField}`, '').trim()
      }
    }

    const userMessage = query
    setQuery('')
    setSelectedField('')
    setConversation(prev => [...prev, { role: 'user', content: userMessage }])
    setLoading(true)

    try {
      const response = await api.post<QueryResponse>('/query', {
        query: finalQuery,
        field: finalField || undefined,
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

  const handleQuickQuery = (quickQuery: string) => {
    setQuery(quickQuery)
  }

  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-md border-b border-gray-200/50 shadow-sm">
        {/* <div className="px-8 py-6"> */}
          {/* <div className="flex items-center gap-3">
            <div className="bg-gradient-to-br from-blue-100 to-purple-100 p-3 rounded-3xl">
              <Sparkles className="text-purple-600" size={28} />
            </div> */}
            {/* <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
                AI Agent
              </h1>
              <p className="text-purple-600 font-medium mt-1">Ask questions about your archived content</p>
            </div> */}
          {/* </div> */}
        {/* </div> */}
      </div>

      {/* Chat Container */}
      <div className="flex-1 overflow-auto p-8">
        <div className="max-w-4xl mx-auto space-y-6">
          {conversation.length === 0 ? (
            <div className="text-center mt-20">
              <div className="inline-block bg-gradient-to-br from-blue-100 to-purple-100 p-6 rounded-2xl mb-6">
                <Sparkles className="text-purple-600 mx-auto" size={64} />
              </div>
              <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
                Ask me anything!
              </h2>
              <p className="text-gray-600 mb-4">I can help you search and understand your archived content.</p>
              <p className="text-sm text-purple-600 font-medium mb-8">💡 Tip: Use @field to search specific categories (e.g., @work or @personal)</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-8 max-w-2xl mx-auto">
                <button
                  onClick={() => handleQuickQuery("What restaurants have I saved?")}
                  className="p-4 bg-white/80 backdrop-blur-sm rounded-2xl border border-purple-200 hover:border-purple-400 hover:shadow-lg transition-all group"
                >
                  <p className="font-semibold text-gray-800 text-center group-hover:text-purple-600 transition-colors">Find restaurants</p>
                  <p className="text-sm text-gray-500 mt-1 text-center">What restaurants have I saved?</p>
                </button>
                <button
                  onClick={() => handleQuickQuery("@work Summarize my notes from this week")}
                  className="p-4 bg-white/80 backdrop-blur-sm rounded-2xl border border-purple-200 hover:border-purple-400 hover:shadow-lg transition-all group"
                >
                  <p className="font-semibold text-gray-800 text-center group-hover:text-purple-600 transition-colors">Work summary</p>
                  <p className="text-sm text-gray-500 mt-1 text-center">@work Summarize my notes</p>
                </button>
                <button
                  onClick={() => handleQuickQuery("Show me all items with locations")}
                  className="p-4 bg-white/80 backdrop-blur-sm rounded-2xl border border-purple-200 hover:border-purple-400 hover:shadow-lg transition-all group"
                >
                  <p className="font-semibold text-gray-800 text-center group-hover:text-purple-600 transition-colors">Location search</p>
                  <p className="text-sm text-gray-500 mt-1 text-center">Show items with locations</p>
                </button>
                <button
                  onClick={() => handleQuickQuery("@learning What have I learned recently?")}
                  className="p-4 bg-white/80 backdrop-blur-sm rounded-2xl border border-purple-200 hover:border-purple-400 hover:shadow-lg transition-all group"
                >
                  <p className="font-semibold text-gray-800 text-center group-hover:text-purple-600 transition-colors">Learning progress</p>
                  <p className="text-sm text-gray-500 mt-1 text-center">@learning What have I learned?</p>
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
                    className={`max-w-2xl px-6 py-4 rounded-2xl shadow-md ${
                      message.role === 'user'
                        ? 'bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 text-white'
                        : 'bg-white/90 backdrop-blur-sm border border-purple-200 text-gray-800'
                    }`}
                  >
                    <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
                  </div>
                </div>
              ))}
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-white/90 backdrop-blur-sm border border-purple-200 px-6 py-4 rounded-2xl shadow-md">
                    <div className="flex items-center gap-3">
                      <Loader className="animate-spin text-purple-600" size={24} />
                      <span className="text-gray-600">Thinking...</span>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Input */}
      <div className="bg-white/80 backdrop-blur-md border-t border-gray-200/50 shadow-lg p-6">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto relative">
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask me anything... (use @field to search specific categories)"
                className="w-full px-6 py-4 bg-white/90 backdrop-blur-sm border border-purple-200 rounded-full text-gray-900 placeholder-gray-400 focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none shadow-sm transition-all"
                disabled={loading}
              />
              {/* Field Suggestions Dropdown */}
              {showFieldSuggestions && filteredFields.length > 0 && (
                <div className="absolute bottom-full left-0 mb-2 w-full bg-white/95 backdrop-blur-md rounded-2xl shadow-xl border border-purple-200 p-2 z-10">
                  <div className="text-xs text-gray-500 px-3 py-2 font-medium">
                    Select a field: {filteredFields.length > 1 && <span className="text-purple-600">(Press Tab to cycle)</span>}
                  </div>
                  {filteredFields.map((field, index) => (
                    <button
                      key={field}
                      type="button"
                      onClick={() => handleFieldSelect(field)}
                      className={`w-full text-left px-3 py-2 rounded-lg transition-colors flex items-center gap-2 ${
                        index === selectedSuggestionIndex 
                          ? 'bg-purple-100 border border-purple-300' 
                          : 'hover:bg-purple-50'
                      }`}
                    >
                      <span className="text-purple-600 font-bold">@</span>
                      <span className="font-medium text-gray-700 capitalize">{field}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="px-8 py-4 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 hover:from-blue-700 hover:via-purple-700 hover:to-pink-700 text-white rounded-full transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl disabled:hover:shadow-lg group"
            >
              <Send size={20} className="group-hover:translate-x-0.5 transition-transform" />
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
