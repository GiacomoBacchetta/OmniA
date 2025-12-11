# 🗺️ Location Feature - Testing Guide

## Quick Start

### 1. Start the Services
```bash
cd Back-End
docker-compose up --build
```

Wait for all services to start (especially Ollama - it takes ~2-3 minutes to load models).

### 2. Access the Map Viewer
Open your browser and navigate to:
```
http://localhost:8001/static/map.html
```

Or through the API Gateway:
```
http://localhost:8000/map
```

---

## Testing Location Extraction

The location service can automatically extract location data from various formats:

### Test 1: Google Maps URL
```bash
curl -X POST http://localhost:8001/api/v1/archive/text \
  -H "Content-Type: application/json" \
  -d '{
    "field": "personal",
    "title": "Favorite Restaurant",
    "content": "Amazing pizza at Da Michele! https://www.google.com/maps/place/Antica+Pizzeria+da+Michele/@40.8469931,14.2583304,17z/data=!3m1!4b1!4m6!3m5!1s0x133b084a4de021db:0x1d2c1a1c6d0e64c1!8m2!3d40.8469931!4d14.2609053!16s%2Fg%2F11dxfw2vfy"
  }'
```

Expected: Extracts coordinates `40.8469931, 14.2609053` and reverse geocodes to address.

### Test 2: Direct Coordinates
```bash
curl -X POST http://localhost:8001/api/v1/archive/text \
  -H "Content-Type: application/json" \
  -d '{
    "field": "work",
    "title": "Office Location",
    "content": "Our new office is at 45.4642, 9.1900 - right in the city center!"
  }'
```

Expected: Extracts coordinates and geocodes to "Milano, Lombardia, Italia".

### Test 3: Address
```bash
curl -X POST http://localhost:8001/api/v1/archive/text \
  -H "Content-Type: application/json" \
  -d '{
    "field": "inspiration",
    "title": "Beautiful Street",
    "content": "Walked down Via Montenapoleone and saw incredible fashion displays."
  }'
```

Expected: Extracts "Via Montenapoleone" and geocodes to coordinates.

### Test 4: File with Location
```bash
curl -X POST http://localhost:8001/api/v1/archive/file \
  -F "field=personal" \
  -F "title=Vacation Photo" \
  -F "file=@photo.jpg" \
  -F "location_address=Piazza del Duomo, Milano" \
  -F "tags=travel,italy"
```

Expected: Stores address and geocodes to coordinates.

### Test 5: Instagram with Location in Caption
```bash
curl -X POST http://localhost:8001/api/v1/archive/instagram \
  -H "Content-Type: application/json" \
  -d '{
    "field": "inspiration",
    "url": "https://www.instagram.com/p/example/",
    "tags": ["architecture", "travel"],
    "title": "Beautiful Architecture",
    "content": "Amazing cathedral at https://maps.google.com/?q=45.464204,9.191383"
  }'
```

Expected: Extracts coordinates from caption.

---

## Viewing the Map

### Map Features

1. **Filter by Field**: Use the dropdown to show only specific fields
2. **Filter by Tags**: Enter comma-separated tags to filter
3. **Refresh**: Reload markers from the database
4. **Center Map**: Auto-fit all visible markers
5. **Marker Colors**: Each field has a unique color:
   - Personal: Purple (#667eea)
   - Work: Pink (#f093fb)
   - Inspiration: Blue (#4facfe)
   - Learning: Green (#43e97b)
   - Health: Pink-Red (#fa709a)
   - Finance: Yellow (#feca57)

### Interactive Markers

Click any marker to see:
- Title
- Field badge
- Content preview
- Creation date
- Copy coordinates button

---

## API Endpoints

### Get All Map Markers
```bash
curl http://localhost:8001/api/v1/archive/map/all
```

Response:
```json
{
  "markers": [
    {
      "id": "uuid",
      "title": "Favorite Restaurant",
      "latitude": 40.8469931,
      "longitude": 14.2609053,
      "field": "personal",
      "content_preview": "Amazing pizza at Da Michele!...",
      "created_at": "2024-01-15T10:30:00"
    }
  ],
  "total": 1,
  "center_latitude": 40.8469931,
  "center_longitude": 14.2609053
}
```

### Filter by Field
```bash
curl http://localhost:8001/api/v1/archive/map/all?field=personal
```

### Filter by Tags
```bash
curl http://localhost:8001/api/v1/archive/map/all?tags=travel,italy
```

---

## Supported Location Formats

### Google Maps URLs
- `https://www.google.com/maps/place/.../@LAT,LON,...`
- `https://maps.google.com/?q=LAT,LON`
- `https://goo.gl/maps/SHORTCODE`
- `https://maps.app.goo.gl/SHORTCODE`

### Coordinates
- `45.4642, 9.1900`
- `45.4642°N, 9.1900°E`
- `40.7128, -74.0060` (negative for West/South)

### Addresses (Italian Format)
- `Via [Street Name]`
- `Viale [Street Name]`
- `Corso [Street Name]`
- `Piazza [Square Name]`
- `Largo [Area Name]`
- Plus city/country for better geocoding

---

## Troubleshooting

### Map Shows No Markers
1. Check if services are running: `docker-compose ps`
2. Verify data exists: `curl http://localhost:8001/api/v1/archive/items`
3. Check browser console for errors (F12)
4. Ensure items have location data (test with examples above)

### Location Not Extracted
1. Check location service logs: `docker-compose logs archive-service`
2. Verify format matches supported patterns (see above)
3. Try explicit location parameters instead of auto-extraction
4. Check Nominatim API is accessible (geocoding service)

### Geocoding Fails
- Nominatim has rate limits (1 request/second)
- Service uses User-Agent header to comply with usage policy
- Check logs for HTTP errors from Nominatim
- Can provide explicit coordinates instead: `location_latitude`, `location_longitude`

### CORS Errors
- Map viewer should be accessed from same origin as API
- Use `http://localhost:8001/static/map.html` directly
- Or through API Gateway: `http://localhost:8000/map`

---

## Advanced Testing

### Bulk Import with Locations
Create a test script to populate the database:

```bash
#!/bin/bash

# Array of Italian locations
locations=(
  "Via Montenapoleone, Milano"
  "Piazza del Duomo, Milano"
  "Colosseo, Roma"
  "Ponte Vecchio, Firenze"
  "Piazza San Marco, Venezia"
)

fields=("personal" "work" "inspiration" "learning" "health")

for i in {1..20}; do
  location=${locations[$((RANDOM % ${#locations[@]}))]}
  field=${fields[$((RANDOM % ${#fields[@]}))]}
  
  curl -X POST http://localhost:8001/api/v1/archive/text \
    -H "Content-Type: application/json" \
    -d "{
      \"field\": \"$field\",
      \"title\": \"Item $i\",
      \"content\": \"Test content at $location\"
    }"
  
  sleep 1  # Respect Nominatim rate limit
done
```

Save as `test_locations.sh`, make executable, and run:
```bash
chmod +x test_locations.sh
./test_locations.sh
```

Then refresh the map to see all markers!

---

## Performance Notes

- Location extraction is done synchronously during ingestion
- Geocoding adds ~500ms-1s per request (Nominatim API call)
- Map endpoint returns only items with valid coordinates
- Frontend uses Leaflet.js for efficient marker rendering
- Can handle hundreds of markers without performance issues

---

## Next Steps

- [ ] Add location search/autocomplete in ingestion UI
- [ ] Implement marker clustering for dense areas
- [ ] Add heatmap view for location density
- [ ] Support GPX/KML file import for routes
- [ ] Add distance-based search ("within 5km of...")
- [ ] Integrate with Google Maps API for better geocoding (requires API key)
