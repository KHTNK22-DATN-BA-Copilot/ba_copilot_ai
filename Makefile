# Development shortcuts and automation
.PHONY: help setup clean test test-coverage lint format type-check dev build migrate migration docker-up docker-down

# Default target
help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Setup and Installation
setup: ## Setup development environment
	@echo "Setting up development environment..."
	python -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements/development.txt
	.venv/bin/pre-commit install
	cp .env.template .env
	@echo "✅ Development environment setup complete!"
	@echo "Don't forget to:"
	@echo "  1. Activate virtual environment: source .venv/bin/activate"
	@echo "  2. Edit .env file with your configuration"
	@echo "  3. Start database services: make docker-up"

clean: ## Clean up temporary files and caches
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	@echo "✅ Cleanup complete!"

# Testing
test: ## Run all tests
	@echo "Running tests..."
	pytest tests/ -v

test-unit: ## Run unit tests only
	@echo "Running unit tests..."
	pytest tests/unit/ -v

test-integration: ## Run integration tests only  
	@echo "Running integration tests..."
	pytest tests/integration/ -v

test-e2e: ## Run end-to-end tests only
	@echo "Running e2e tests..."
	pytest tests/e2e/ -v

test-coverage: ## Run tests with coverage report
	@echo "Running tests with coverage..."
	pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/index.html"

test-watch: ## Run tests in watch mode
	@echo "Running tests in watch mode..."
	ptw --runner "pytest tests/ -v"

# Code Quality
lint: ## Run code linting
	@echo "Running linting..."
	flake8 src/ tests/
	pylint src/
	bandit -r src/

format: ## Format code
	@echo "Formatting code..."
	black src/ tests/
	isort src/ tests/
	@echo "✅ Code formatted!"

format-check: ## Check code formatting without making changes
	@echo "Checking code formatting..."
	black --check src/ tests/
	isort --check-only src/ tests/

type-check: ## Run type checking
	@echo "Running type checks..."
	mypy src/

quality: lint format type-check ## Run all code quality checks

# Development
dev: ## Start development server
	@echo "Starting development server..."
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

dev-debug: ## Start development server with debugging
	@echo "Starting development server with debugging..."
	python -m debugpy --listen 0.0.0.0:5678 --wait-for-client -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

worker: ## Start background worker
	@echo "Starting background worker..."
	python -m src.workers.main

# Database
migrate: ## Run database migrations
	@echo "Running database migrations..."
	python scripts/run_migrations.py

migration: ## Generate new migration (usage: make migration name="add_new_table")
	@echo "Generating new migration: $(name)"
	cd src/shared/database/migrations && alembic revision --autogenerate -m "$(name)"

db-reset: ## Reset database (WARNING: This will drop all data!)
	@echo "⚠️  WARNING: This will drop all database data!"
	@read -p "Are you sure you want to continue? [y/N] " confirm && [ "$$confirm" = "y" ]
	python scripts/reset_database.py

db-seed: ## Seed database with sample data
	@echo "Seeding database with sample data..."
	python scripts/populate_test_data.py

# Docker
docker-build: ## Build Docker images
	@echo "Building Docker images..."
	docker-compose build

docker-up: ## Start Docker services (database, cache, etc.)
	@echo "Starting Docker services..."
	docker-compose up -d postgres redis minio

docker-up-full: ## Start all Docker services including the API
	@echo "Starting all Docker services..."
	docker-compose up -d

docker-down: ## Stop Docker services
	@echo "Stopping Docker services..."
	docker-compose down

docker-logs: ## Show Docker logs
	@echo "Showing Docker logs..."
	docker-compose logs -f

docker-clean: ## Clean up Docker resources
	@echo "Cleaning up Docker resources..."
	docker-compose down -v
	docker system prune -f

# Production Build
build: ## Build production images
	@echo "Building production images..."
	docker build -f infrastructure/docker/Dockerfile.api -t bacopilot/api:latest .
	docker build -f infrastructure/docker/Dockerfile.worker -t bacopilot/worker:latest .

# Deployment
deploy-staging: ## Deploy to staging environment
	@echo "Deploying to staging..."
	kubectl apply -f infrastructure/kubernetes/ --context=staging

deploy-prod: ## Deploy to production environment
	@echo "Deploying to production..."
	kubectl apply -f infrastructure/kubernetes/ --context=production

# Health Checks
health: ## Check application health
	@echo "Checking application health..."
	python scripts/health_check.py

# Monitoring
logs: ## Show application logs
	@echo "Showing application logs..."
	docker-compose logs -f api

metrics: ## Show metrics dashboard
	@echo "Opening metrics dashboard..."
	open http://localhost:3000  # Grafana

# Documentation
docs-api: ## Generate API documentation
	@echo "Generating API documentation..."
	python scripts/generate_api_docs.py

docs-serve: ## Serve documentation locally
	@echo "Serving documentation at http://localhost:8080"
	python -m http.server 8080 -d docs/

# Security
security-scan: ## Run security scans
	@echo "Running security scans..."
	bandit -r src/
	safety check

# Dependencies
deps-update: ## Update dependencies
	@echo "Updating dependencies..."
	pip-compile requirements/base.in
	pip-compile requirements/development.in
	pip-compile requirements/testing.in
	pip-compile requirements/production.in

deps-install: ## Install dependencies
	@echo "Installing dependencies..."
	pip install -r requirements/development.txt

# Backup
backup: ## Create database backup
	@echo "Creating database backup..."
	bash scripts/backup_database.sh

restore: ## Restore database from backup (usage: make restore backup="backup_file.sql")
	@echo "Restoring database from backup: $(backup)"
	bash scripts/restore_database.sh $(backup)

# CI/CD
ci-test: ## Run CI test suite
	@echo "Running CI test suite..."
	pytest tests/ --cov=src --cov-report=xml --junitxml=test-results.xml

ci-build: ## Build for CI
	@echo "Building for CI..."
	docker build -f infrastructure/docker/Dockerfile.api -t bacopilot/api:${CI_COMMIT_SHA} .

# Development Helpers
shell: ## Open Python shell with application context
	@echo "Opening Python shell..."
	python -c "from src.api.main import app; import IPython; IPython.embed()"

psql: ## Connect to PostgreSQL database
	@echo "Connecting to PostgreSQL..."
	psql $(DATABASE_URL)

redis-cli: ## Connect to Redis
	@echo "Connecting to Redis..."
	redis-cli -u $(REDIS_URL)

# Full workflow commands
dev-setup: setup docker-up migrate db-seed ## Complete development setup
	@echo "🎉 Development setup complete! You can now run 'make dev' to start the server."

ci: format-check lint type-check test-coverage ## Run full CI pipeline locally

pre-commit: format lint type-check test ## Run pre-commit checks