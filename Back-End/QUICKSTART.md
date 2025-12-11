# OmniA Backend - Quick Start Guide

## Prerequisites

- Docker and Docker Compose installed
- At least 8GB RAM available
- 20GB free disk space

## Initial Setup

### 1. Clone and Navigate
```bash
cd Back-End
```

### 2. Configure Environment Variables

Copy example env files and update as needed:
```bash
# API Gateway
cp api-gateway/.env.example api-gateway/.env

# Archive Service
cp archive-service/.env.example archive-service/.env

# Embedding Service
cp embedding-service/.env.example embedding-service/.env

# Vector DB Service
cp vector-db-service/.env.example vector-db-service/.env

# Orchestrator Service
cp orchestrator-service/.env.example orchestrator-service/.env
```

**Important**: Change the `JWT_SECRET` in `api-gateway/.env` for production!

### 3. Start Infrastructure Services

Start only infrastructure services first:
```bash
docker-compose up -d postgres redis rabbitmq minio qdrant ollama
```

Wait for services to be healthy (~30 seconds):
```bash
docker-compose ps
```

### 4. Pull Ollama Models

```bash
# Pull the LLM model (this may take several minutes)
docker exec -it omnia-ollama ollama pull llama2

# Optional: Pull smaller model for testing
docker exec -it omnia-ollama ollama pull llama2:7b
```

### 5. Start Application Services

```bash
docker-compose up -d api-gateway archive-service embedding-service vector-db-service orchestrator-service
```

### 6. Check Service Health

```bash
# Check all services
docker-compose ps

# Check API Gateway health
curl http://localhost:8000/health

# Check individual services
curl http://localhost:8001/health  # Archive
curl http://localhost:8003/health  # Vector DB
curl http://localhost:8004/health  # Orchestrator
```

## Usage Examples

### 1. Get Access Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password"
  }'
```

Save the returned `access_token`.

### 2. Archive Text Content

```bash
curl -X POST http://localhost:8000/api/v1/archive/text \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "field": "personal",
    "title": "My first note",
    "content": "This is a test note about my personal goals.",
    "tags": ["goals", "personal-development"]
  }'
```

### 3. Upload a File

```bash
curl -X POST http://localhost:8000/api/v1/archive/file \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "field=work" \
  -F "title=Project Document" \
  -F "file=@/path/to/your/file.pdf" \
  -F "tags=project,documentation"
```

### 4. Archive Instagram Link

```bash
curl -X POST http://localhost:8000/api/v1/archive/instagram \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "field": "inspiration",
    "title": "Cool Design",
    "instagram_url": "https://www.instagram.com/p/ABC123/",
    "tags": ["design", "inspiration"]
  }'
```

### 5. Create Field Agents

Uncomment agent services in `docker-compose.yml` and start them:
```bash
docker-compose up -d field-agent-personal field-agent-work
```

### 6. Query with Agentic RAG

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "query": "What are my personal goals?",
    "fields": ["personal"],
    "max_results": 5
  }'
```

## Service URLs

- **API Gateway**: http://localhost:8000
- **Archive Service**: http://localhost:8001
- **Vector DB Service**: http://localhost:8003
- **Orchestrator Service**: http://localhost:8004
- **RabbitMQ Management**: http://localhost:15672 (guest/guest)
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)

## Adding New Field Agents

1. Copy the template:
```bash
cp -r agents/field-agent-template agents/field-agent-myfield
```

2. Update `docker-compose.yml` with new agent service

3. Start the agent:
```bash
docker-compose up -d field-agent-myfield
```

The agent will auto-register with the orchestrator!

## Monitoring

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api-gateway
docker-compose logs -f embedding-service
```

### Check Resource Usage
```bash
docker stats
```

## Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes all data)
docker-compose down -v
```

## Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs SERVICE_NAME

# Rebuild
docker-compose build --no-cache SERVICE_NAME
docker-compose up -d SERVICE_NAME
```

### Ollama model not found
```bash
# Pull model again
docker exec -it omnia-ollama ollama pull llama2
```

### Port conflicts
Edit the ports in `docker-compose.yml` to use different host ports.

### Database connection issues
```bash
# Check postgres is healthy
docker-compose ps postgres

# Restart postgres
docker-compose restart postgres
```

## Development

### Hot Reload
The services are configured with `--reload` flag for development. Changes to Python files will auto-reload.

### Rebuild After Code Changes
```bash
docker-compose up -d --build SERVICE_NAME
```

## Production Deployment

For production:
1. Change all default passwords and secrets
2. Use proper TLS/SSL certificates
3. Configure proper backup strategies
4. Use managed services for PostgreSQL, Redis, etc.
5. Implement proper monitoring and logging
6. Set up CI/CD pipeline
7. Remove `--reload` flags from CMD in Dockerfiles

## Next Steps

1. Implement user authentication with a real database
2. Add more field agents for your specific needs
3. Customize RAG prompts for better responses
4. Implement file content extraction for various formats
5. Add monitoring with Prometheus/Grafana
6. Implement rate limiting and security measures
