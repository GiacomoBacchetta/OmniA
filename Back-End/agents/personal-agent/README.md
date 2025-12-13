# Field-Specific Agent Template

This directory contains the base template for creating field-specific RAG agents.

## Overview

Each field-specific agent:
- Handles queries for a specific field/category
- Performs vector search in its field-specific index
- Applies RAG with retrieved context
- Returns structured responses with sources

## Creating a New Field Agent

1. Copy this template to a new directory:
   ```bash
   cp -r agents/field-agent-template agents/field-agent-{field-name}
   ```

2. Update the configuration:
   - Edit `.env.example` with field-specific settings
   - Set `FIELD_NAME` to your field name
   - Set `PORT` to a unique port (8010+)

3. Customize behavior:
   - Modify `services/rag_service.py` for field-specific logic
   - Add custom prompt templates in `prompts/`
   - Implement field-specific preprocessing

4. Build and run:
   ```bash
   docker build -t field-agent-{field-name} .
   docker run -p 8010:8010 field-agent-{field-name}
   ```

## API Endpoints

### POST /query
Query the field agent with RAG

**Request:**
```json
{
  "query": "user question",
  "max_results": 5
}
```

**Response:**
```json
{
  "field": "field-name",
  "answer": "generated answer",
  "sources": [
    {
      "id": "item-id",
      "content": "relevant content",
      "score": 0.95,
      "metadata": {}
    }
  ],
  "confidence": 0.9
}
```

## Architecture

```
Field Agent
├── Vector Search (via Vector DB Service)
├── Context Retrieval
├── Prompt Construction
├── LLM Generation (via Ollama)
└── Response Formatting
```

## Customization Points

1. **Vector Search Strategy**: Adjust search parameters, filters
2. **Context Selection**: Customize how sources are ranked/selected
3. **Prompt Engineering**: Field-specific prompt templates
4. **Post-processing**: Format responses for specific use cases
