# 🎯 OmniA Quick Reference

## 📡 Service URLs

| Service | URL | Description |
|---------|-----|-------------|
| **API Gateway** | http://localhost:8000 | Main entry point |
| **Archive Service** | http://localhost:8001 | Content ingestion |
| **Map Viewer** | http://localhost:8001/static/map.html | Interactive map |
| **Archive API Docs** | http://localhost:8001/docs | Swagger UI |
| **Vector DB** | http://localhost:8003 | Vector search |
| **Orchestrator** | http://localhost:8004 | Agentic RAG |
| **RabbitMQ UI** | http://localhost:15672 | Queue management (guest/guest) |
| **MinIO Console** | http://localhost:9001 | File storage (minioadmin/minioadmin) |

## 🚀 Quick Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f archive-service

# Restart a service
docker-compose restart archive-service

# Check service health
make health

# Run test suite
./test_all.sh

# Pull Ollama models (first time only)
docker exec -it omnia-ollama ollama pull llama2
docker exec -it omnia-ollama ollama pull nomic-embed-text
```

## 📝 Ingest Content Examples

### Text with Location
```bash
curl -X POST http://localhost:8001/api/v1/archive/text \
  -H "Content-Type: application/json" \
  -d '{
    "field": "personal",
    "title": "My Favorite Place",
    "content": "Love this spot at Via Montenapoleone, Milano!",
    "tags": ["travel", "italy"]
  }'
```

### File with Location
```bash
curl -X POST http://localhost:8001/api/v1/archive/file \
  -F "field=work" \
  -F "title=Meeting Notes" \
  -F "file=@document.pdf" \
  -F "location_address=Piazza del Duomo, Milano"
```

### Instagram Link
```bash
curl -X POST http://localhost:8001/api/v1/archive/instagram \
  -H "Content-Type: application/json" \
  -d '{
    "field": "inspiration",
    "url": "https://www.instagram.com/p/example/",
    "title": "Beautiful Photo",
    "tags": ["art"]
  }'
```

## 🔍 Query Examples

### List All Items
```bash
curl http://localhost:8001/api/v1/archive/items
```

### Filter by Field
```bash
curl "http://localhost:8001/api/v1/archive/items?field=personal"
```

### Filter by Tags
```bash
curl "http://localhost:8001/api/v1/archive/items?tags=travel,italy"
```

### Get Map Markers
```bash
curl http://localhost:8001/api/v1/archive/map/all
```

### Query with Agentic RAG
```bash
curl -X POST http://localhost:8004/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What restaurants have I saved?",
    "field": "personal"
  }'
```

## 🗺️ Location Formats Supported

The system automatically extracts location from:

1. **Google Maps URLs**
   - `https://www.google.com/maps/place/.../@LAT,LON`
   - `https://maps.google.com/?q=LAT,LON`
   - `https://goo.gl/maps/SHORTCODE`

2. **Direct Coordinates**
   - `45.4642, 9.1900`
   - `40.7128°N, 74.0060°W`

3. **Italian Addresses**
   - `Via Montenapoleone, Milano`
   - `Piazza del Duomo`
   - `Corso Buenos Aires, 25`

## 🐛 Troubleshooting

### Services not starting
```bash
docker-compose down
docker-compose up --build
```

### Check specific service
```bash
docker-compose logs archive-service --tail=100
```

### Database issues
```bash
# Reset database (⚠️ deletes all data)
docker-compose down -v
docker-compose up -d
```

### Can't access map viewer
1. Check if archive service is running: `docker-compose ps`
2. Try direct URL: http://localhost:8001/static/map.html
3. Check browser console for errors (F12)

### Geocoding slow or failing
- Nominatim has rate limits (1 request/second)
- Provide explicit coordinates instead:
```bash
curl -X POST http://localhost:8001/api/v1/archive/text \
  -H "Content-Type: application/json" \
  -d '{
    "field": "personal",
    "title": "My Place",
    "content": "Great location!",
    "location_latitude": 45.4642,
    "location_longitude": 9.1900
  }'
```

## 📚 API Documentation

- **Archive Service**: http://localhost:8001/docs
- **Vector DB Service**: http://localhost:8003/docs  
- **Orchestrator Service**: http://localhost:8004/docs

## 🎨 Field Types

Available fields for categorization:
- `personal` - Personal notes and memories
- `work` - Work-related content
- `inspiration` - Creative inspiration
- `learning` - Educational content
- `health` - Health and wellness
- `finance` - Financial information

## 📦 Data Locations

- **PostgreSQL Data**: `postgres_data` volume
- **File Uploads**: `archive_uploads` volume
- **Vector DB**: `qdrant_data` volume
- **Ollama Models**: `ollama_data` volume
- **Redis Cache**: `redis_data` volume

## 🔐 Default Credentials

| Service | Username | Password |
|---------|----------|----------|
| PostgreSQL | omnia | omnia_password |
| RabbitMQ | guest | guest |
| MinIO | minioadmin | minioadmin |

## 🚨 Important Notes

1. **First Time Setup**: Pull Ollama models before using RAG:
   ```bash
   docker exec -it omnia-ollama ollama pull llama2
   ```

2. **Rate Limits**: Nominatim geocoding is rate-limited to 1 req/sec

3. **Production**: Change all default passwords in docker-compose.yml

4. **Backup**: Regularly backup Docker volumes:
   ```bash
   docker run --rm -v back-end_postgres_data:/data \
     -v $(pwd)/backups:/backup \
     alpine tar czf /backup/postgres-$(date +%Y%m%d).tar.gz /data
   ```
