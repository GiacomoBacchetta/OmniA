# OmniA Backend - Makefile
# Convenient commands for development

.PHONY: help setup start stop restart logs clean build pull-models test

help:
	@echo "OmniA Backend - Available Commands"
	@echo "=================================="
	@echo "make setup        - Initial setup (copy env files)"
	@echo "make start        - Start all services"
	@echo "make stop         - Stop all services"
	@echo "make restart      - Restart all services"
	@echo "make logs         - View logs for all services"
	@echo "make clean        - Stop and remove all containers and volumes"
	@echo "make build        - Rebuild all services"
	@echo "make pull-models  - Pull Ollama models"
	@echo "make infra        - Start only infrastructure services"
	@echo "make app          - Start only application services"
	@echo "make status       - Check service status"
	@echo "make health       - Check API health"

setup:
	@echo "Setting up environment files..."
	@cp -n api-gateway/.env.example api-gateway/.env || true
	@cp -n archive-service/.env.example archive-service/.env || true
	@cp -n embedding-service/.env.example embedding-service/.env || true
	@cp -n vector-db-service/.env.example vector-db-service/.env || true
	@cp -n orchestrator-service/.env.example orchestrator-service/.env || true
	@echo "✓ Environment files created"
	@echo "⚠️  Remember to update JWT_SECRET in api-gateway/.env!"

start:
	@echo "Starting all services..."
	docker-compose up -d
	@echo "✓ All services started"
	@echo "Run 'make logs' to view logs"

stop:
	@echo "Stopping all services..."
	docker-compose down
	@echo "✓ All services stopped"

restart:
	@echo "Restarting all services..."
	docker-compose restart
	@echo "✓ All services restarted"

logs:
	docker-compose logs -f

clean:
	@echo "⚠️  This will remove all containers and volumes!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		echo "✓ Cleaned up"; \
	fi

build:
	@echo "Building all services..."
	docker-compose build --no-cache
	@echo "✓ Build complete"

pull-models:
	@echo "Pulling Ollama models..."
	docker exec -it omnia-ollama ollama pull llama2
	@echo "✓ Models pulled"

infra:
	@echo "Starting infrastructure services..."
	docker-compose up -d postgres redis rabbitmq minio qdrant ollama
	@echo "✓ Infrastructure services started"
	@echo "Waiting for services to be healthy..."
	@sleep 10
	@echo "Run 'make pull-models' to download LLM models"

app:
	@echo "Starting application services..."
	docker-compose up -d api-gateway archive-service embedding-service vector-db-service orchestrator-service
	@echo "✓ Application services started"

status:
	@echo "Service Status:"
	@docker-compose ps

health:
	@echo "Checking service health..."
	@echo "\nAPI Gateway:"
	@curl -s http://localhost:8000/health | jq '.' || echo "❌ Not responding"
	@echo "\nArchive Service:"
	@curl -s http://localhost:8001/health | jq '.' || echo "❌ Not responding"
	@echo "\nVector DB Service:"
	@curl -s http://localhost:8003/health | jq '.' || echo "❌ Not responding"
	@echo "\nOrchestrator Service:"
	@curl -s http://localhost:8004/health | jq '.' || echo "❌ Not responding"

# Individual service commands
logs-gateway:
	docker-compose logs -f api-gateway

logs-archive:
	docker-compose logs -f archive-service

logs-embedding:
	docker-compose logs -f embedding-service

logs-vectordb:
	docker-compose logs -f vector-db-service

logs-orchestrator:
	docker-compose logs -f orchestrator-service

restart-gateway:
	docker-compose restart api-gateway

restart-archive:
	docker-compose restart archive-service

restart-embedding:
	docker-compose restart embedding-service

restart-vectordb:
	docker-compose restart vector-db-service

restart-orchestrator:
	docker-compose restart orchestrator-service
