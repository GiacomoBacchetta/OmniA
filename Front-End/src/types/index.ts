export interface ArchiveItem {
  id: string
  field: string
  content_type: string
  title: string
  content: string
  file_url?: string
  file_name?: string
  tags: string[]
  location?: Location
  created_at: string
  updated_at?: string
}

export interface Location {
  address?: string
  google_maps_url?: string
  latitude?: number
  longitude?: number
}

export interface MapMarker {
  id: string
  title: string
  latitude: number
  longitude: number
  field: string
  content_preview: string
  created_at: string
}

export interface QueryRequest {
  query: string
  field?: string
}

export interface QueryResponse {
  query: string
  response: string
  sources: string[]
  field?: string
}
