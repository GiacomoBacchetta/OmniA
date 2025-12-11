# OmniA
This is the official repository for the development of the OmniA app.

## Overview

OmniA is a self-management application with intelligent content archiving and retrieval powered by agentic RAG (Retrieval-Augmented Generation). The app allows users to:

- **Archive diverse content**: text notes, files, Instagram links, and more
- **Organize by fields**: categorize content into personal, work, inspiration, etc.
- **Intelligent search**: query your archive using natural language
- **Agentic RAG**: specialized agents for each field provide context-aware responses

## Architecture

OmniA uses a microservices architecture with the following components:

### Core Services
- **API Gateway** - Entry point, authentication, routing
- **Archive Service** - Content ingestion (text, files, Instagram)
- **Embedding Service** - Generate embeddings using Ollama/HuggingFace
- **Vector DB Service** - Qdrant vector database wrapper
- **Orchestrator Service** - Agentic RAG orchestration
- **Field Agents** - Specialized RAG agents per field

### Infrastructure
- **PostgreSQL** - Metadata storage
- **Redis** - Caching and session management
- **RabbitMQ** - Message queue for async processing
- **MinIO** - S3-compatible file storage
- **Qdrant** - Open-source vector database
- **Ollama** - Local LLM inference

## Technology Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Vector Database**: Qdrant
- **LLM**: Ollama (llama2)
- **Embeddings**: HuggingFace sentence-transformers
- **Deployment**: Docker + Docker Compose

## Quick Start

See [Back-End/QUICKSTART.md](Back-End/QUICKSTART.md) for detailed setup instructions.

```bash
# Navigate to backend
cd Back-End

# Start infrastructure services
docker-compose up -d postgres redis rabbitmq minio qdrant ollama

# Pull LLM model
docker exec -it omnia-ollama ollama pull llama2

# Start application services
docker-compose up -d

# Check health
curl http://localhost:8000/health
```

## Project Structure

```
OmniA/
├── README.md
├── Back-End/
│   ├── README.md                    # Architecture documentation
│   ├── QUICKSTART.md               # Quick start guide
│   ├── ARCHITECTURE_DIAGRAM.txt    # Visual architecture
│   ├── docker-compose.yml          # Docker orchestration
│   ├── api-gateway/                # API Gateway service
│   ├── archive-service/            # Content ingestion
│   ├── embedding-service/          # Embedding generation
│   ├── vector-db-service/          # Vector DB wrapper
│   ├── orchestrator-service/       # Agentic orchestrator
│   ├── agents/
│   │   └── field-agent-template/   # Template for field agents
│   └── shared/                     # Shared utilities
└── Front-End/                      # (To be implemented)
```

## Features

### Content Ingestion
- Archive text notes
- Upload files (PDF, DOCX, images, etc.)
- Import Instagram posts/reels
- Automatic embedding generation
- Field-based organization

### Intelligent Retrieval
- Natural language queries
- Vector similarity search
- Field-specific agents
- Context-aware responses
- Source attribution

### Agentic RAG
- Orchestrator routes queries to appropriate agents
- Each field has a specialized agent
- Agents perform vector search + RAG
- Responses synthesized with LLM

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/register` - Register

### Archive
- `POST /api/v1/archive/text` - Archive text
- `POST /api/v1/archive/file` - Upload file
- `POST /api/v1/archive/instagram` - Archive Instagram link
- `GET /api/v1/archive/{field}` - List items in field
- `DELETE /api/v1/archive/{id}` - Delete item

### Query
- `POST /api/v1/query` - Query with agentic RAG
- `GET /api/v1/query/{id}` - Get query status

### Agents
- `POST /api/v1/agents/register` - Register field agent
- `GET /api/v1/agents` - List agents
- `GET /api/v1/agents/{field}` - Get agent info

## Development Status

✅ **Completed**
- Microservices architecture design
- API Gateway with authentication
- Archive service (text, file, Instagram)
- Embedding service (HuggingFace + Ollama)
- Vector DB service (Qdrant)
- Orchestrator service
- Field agent template
- Docker Compose configuration
- Documentation and guides

🚧 **In Progress**
- Front-End development
- Advanced file content extraction
- Enhanced authentication system

📋 **Planned**
- User management UI
- Advanced query interfaces
- Analytics dashboard
- Mobile application
- Cloud deployment options

## Contributing

This is a private development project. For questions or suggestions, please contact the repository owner.

## License

All rights reserved.
