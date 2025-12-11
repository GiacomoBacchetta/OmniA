# OmniA Backend - Microservices Architecture

## Overview
Self-management application with intelligent archive and agentic RAG system for personalized content retrieval.

## Architecture

### Microservices Structure
```
Back-End/
├── api-gateway/           # Entry point, routing, authentication
├── archive-service/       # Content ingestion (text, files, Instagram links)
├── embedding-service/     # Ollama + HuggingFace embeddings generation
├── vector-db-service/     # Qdrant vector database wrapper
├── orchestrator-service/  # Agentic RAG orchestrator
├── agents/
│   ├── agent-base/       # Shared agent logic
│   └── field-agents/     # Field-specific RAG agents
├── shared/               # Shared utilities, models, configs
└── docker-compose.yml    # Local deployment orchestration
```

## Technology Stack

### Core Technologies
- **Language**: Python 3.11+
- **API Framework**: FastAPI
- **Vector Database**: Qdrant (open-source)
- **Embeddings**: Ollama + HuggingFace models
- **Message Queue**: RabbitMQ (async processing)
- **Cache**: Redis
- **API Gateway**: Kong or custom FastAPI gateway

### Storage
- **Metadata DB**: PostgreSQL
- **File Storage**: MinIO (S3-compatible)
- **Vector Storage**: Qdrant

## Service Descriptions

### 1. API Gateway
- Single entry point for all client requests
- JWT authentication & authorization
- Rate limiting
- Request routing to appropriate services
- **Port**: 8000

### 2. Archive Service
- Handles content ingestion
- Supports: text, files, Instagram links
- Extracts metadata and content
- Publishes to embedding queue
- **Port**: 8001

### 3. Embedding Service
- Consumes content from queue
- Generates embeddings using Ollama/HuggingFace
- Stores embeddings in Vector DB by field
- **Port**: 8002

### 4. Vector DB Service
- Qdrant wrapper/manager
- Field-specific index management
- Vector search operations
- **Port**: 8003

### 5. Orchestrator Service
- Receives user queries
- Determines which field agent(s) to invoke
- Aggregates responses from multiple agents
- Generates final response
- **Port**: 8004

### 6. Field-Specific Agents
- Each agent handles queries for specific field
- Performs vector search in field-specific index
- Applies RAG with retrieved context
- **Ports**: 8010-8019 (per agent)

## Data Flow

### Ingestion Flow
```
Client → API Gateway → Archive Service → RabbitMQ → Embedding Service → Vector DB
                                ↓
                          PostgreSQL (metadata)
                                ↓
                          MinIO (file storage)
```

### Query Flow
```
Client → API Gateway → Orchestrator → Field Agent(s) → Vector DB
                                            ↓
                                       LLM (Ollama)
                                            ↓
                                    Orchestrator → Client
```

## API Endpoints

### Archive Service
- `POST /api/v1/archive/text` - Add text content
- `POST /api/v1/archive/file` - Upload file
- `POST /api/v1/archive/instagram` - Add Instagram link
- `GET /api/v1/archive/{field}` - List items in field
- `DELETE /api/v1/archive/{id}` - Delete item

### Orchestrator Service
- `POST /api/v1/query` - Submit query for agentic RAG
- `GET /api/v1/query/{id}` - Get query status
- `POST /api/v1/agents/register` - Register new field agent

### Vector DB Service
- `POST /api/v1/index/{field}` - Create field index
- `POST /api/v1/search/{field}` - Search in field index
- `GET /api/v1/index/{field}/stats` - Get index statistics

## Field Management

Fields are dynamically configurable:
- Personal notes
- Work documents
- Inspirations (Instagram, etc.)
- Learning materials
- Health & fitness
- Finance
- Custom fields...

Each field has:
- Dedicated vector index
- Specific embedding strategy
- Field-specialized agent

## Environment Variables

See each service's `.env.example` for specific configurations.

Common variables:
- `POSTGRES_URL`
- `REDIS_URL`
- `RABBITMQ_URL`
- `QDRANT_URL`
- `OLLAMA_URL`
- `JWT_SECRET`
- `MINIO_ENDPOINT`

## Development Setup

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild after changes
docker-compose up -d --build
```

## Security Considerations

- JWT-based authentication
- API rate limiting
- Input validation on all endpoints
- File type validation and scanning
- Secure file storage with MinIO
- Network isolation between services
- Environment-based secrets management

## Scalability

- Each service can be scaled independently
- Message queue for async processing
- Redis caching for frequent queries
- Connection pooling for databases
- Horizontal scaling via Docker replicas

## Monitoring & Logging

- Centralized logging (to be implemented)
- Health check endpoints on all services
- Metrics collection (Prometheus/Grafana)
- Distributed tracing (OpenTelemetry)

## Next Steps

1. Implement each microservice
2. Setup Docker configurations
3. Create shared libraries
4. Implement authentication
5. Build agent framework
6. Setup CI/CD pipeline
