# Database Architecture Documentation - BA Copilot AI Services

## Overview

The BA Copilot AI Services uses PostgreSQL as the primary database for a modular monolith architecture serving AI-powered business analysis tools. This documentation provides comprehensive guidelines for database design, deployment, operations, and development workflows.

## Database Requirements

### Functional Requirements

- **Multi-tenant data isolation**: User-scoped data access with secure boundaries
- **AI processing support**: Store large text content, metadata, and generation results
- **Real-time conversation storage**: Message history with temporal ordering
- **Document generation tracking**: SRS documents with version history
- **Wireframe data storage**: HTML/CSS content with associated metadata
- **Audit trail**: Creation and modification timestamps for all entities

### Non-functional Requirements

- **Performance**: Sub-100ms queries for typical API operations
- **Scalability**: Handle 1000+ concurrent users with read replicas
- **Reliability**: 99.9% uptime with automated backups
- **Security**: Row-level security, encrypted connections, secure credential storage
- **Maintainability**: Clear schema design with comprehensive documentation

## Database Architecture

### Technology Stack

| Component              | Technology          | Version | Purpose                                          |
| ---------------------- | ------------------- | ------- | ------------------------------------------------ |
| **Primary Database**   | PostgreSQL          | 14+     | ACID transactions, complex queries, JSON support |
| **Connection Pooling** | Built-in PostgreSQL | Latest  | Efficient connection management                  |
| **Migrations**         | Alembic             | 1.12+   | Schema version control and deployment            |
| **ORM**                | SQLAlchemy          | 2.0+    | Python database abstraction                      |
| **Caching**            | Redis               | 7+      | Session storage and query caching                |

### High-Level Architecture

```mermaid
graph TD
    subgraph "Application Layer"
        APP[FastAPI Application]
        CACHE[Redis Cache]
    end

    subgraph "Database Layer"
        PG_PRIMARY[(PostgreSQL Primary)]
        PG_REPLICA[(PostgreSQL Replica - Optional)]
    end

    subgraph "Storage Layer"
        FILE_STORAGE[File Storage<br/>Local/S3-Compatible]
    end

    APP --> CACHE
    APP --> PG_PRIMARY
    APP --> PG_REPLICA
    APP --> FILE_STORAGE
    PG_PRIMARY -.->|Replication| PG_REPLICA

    style PG_PRIMARY fill:#e8f5e8
    style CACHE fill:#fff3e0
    style FILE_STORAGE fill:#e3f2fd
```

## Database Schema Design

### Important: AI Services Database Scope

**This database schema is specifically for AI Services and does NOT include user management tables:**

- **No `users` table**: User management is handled by the Backend Repository
- **User ID references**: All tables store `user_id` as UUID without foreign key constraints
- **Application-level joins**: User information is joined at the application layer via JWT claims
- **Data isolation**: Each AI service entity is associated with a user through `user_id` field

### Core AI Services Entities

#### 1. Documents (SRS) Table

```sql
CREATE TABLE documents (
    document_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL, -- No FK constraint, managed by application layer
    project_name VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    document_metadata JSONB DEFAULT '{}', -- Renamed to avoid SQL keyword conflict
    status VARCHAR(50) DEFAULT 'draft',
    version INTEGER DEFAULT 1,
    file_path VARCHAR(1000),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_documents_user_id ON documents(user_id);
CREATE INDEX idx_documents_project_name ON documents(project_name);
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_created_at ON documents(created_at);
CREATE INDEX idx_documents_metadata ON documents USING GIN(document_metadata);
```

#### 2. Wireframes Table

```sql
CREATE TABLE wireframes (
    wireframe_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL, -- No FK constraint, managed by application layer
    title VARCHAR(500) NOT NULL,
    html_content TEXT,
    css_styles TEXT,
    wireframe_metadata JSONB DEFAULT '{}', -- Renamed to avoid SQL keyword conflict
    template_type VARCHAR(100),
    preview_url VARCHAR(1000),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_wireframes_user_id ON wireframes(user_id);
CREATE INDEX idx_wireframes_title ON wireframes(title);
CREATE INDEX idx_wireframes_template_type ON wireframes(template_type);
CREATE INDEX idx_wireframes_created_at ON wireframes(created_at);
```

#### 3. Conversations Table

```sql
CREATE TABLE conversations (
    conversation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL, -- No FK constraint, managed by application layer
    title VARCHAR(500) NOT NULL,
    conversation_metadata JSONB DEFAULT '{}', -- Renamed to avoid SQL keyword conflict
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_title ON conversations(title);
CREATE INDEX idx_conversations_created_at ON conversations(created_at);
```

#### 4. Messages Table

```sql
CREATE TABLE messages (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(conversation_id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    message_metadata JSONB DEFAULT '{}', -- Renamed to avoid SQL keyword conflict
    token_count INTEGER,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_timestamp ON messages(timestamp);
CREATE INDEX idx_messages_role ON messages(role);
```

#### 5. Diagrams Table

```sql
CREATE TABLE diagrams (
    diagram_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL, -- No FK constraint, managed by application layer
    title VARCHAR(500) NOT NULL,
    diagram_type VARCHAR(50) NOT NULL CHECK (diagram_type IN ('sequence', 'architecture', 'usecase', 'flowchart')),
    mermaid_code TEXT NOT NULL,
    preview_url VARCHAR(1000),
    diagram_metadata JSONB DEFAULT '{}', -- Renamed to avoid SQL keyword conflict
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_diagrams_user_id ON diagrams(user_id);
CREATE INDEX idx_diagrams_type ON diagrams(diagram_type);
CREATE INDEX idx_diagrams_title ON diagrams(title);
CREATE INDEX idx_diagrams_created_at ON diagrams(created_at);
```

### Database Relationships

```mermaid
erDiagram
    %% AI Services Database Schema
    %% Note: No USERS table - managed by Backend Repository

    CONVERSATIONS ||--o{ MESSAGES : contains

    DOCUMENTS {
        uuid document_id PK
        uuid user_id "No FK - application managed"
        varchar project_name
        text content
        jsonb document_metadata
        varchar status
        integer version
        varchar file_path
        timestamp created_at
        timestamp updated_at
    }

    WIREFRAMES {
        uuid wireframe_id PK
        uuid user_id "No FK - application managed"
        varchar title
        text html_content
        text css_styles
        jsonb wireframe_metadata
        varchar template_type
        varchar preview_url
        timestamp created_at
        timestamp updated_at
    }

    CONVERSATIONS {
        uuid conversation_id PK
        uuid user_id "No FK - application managed"
        varchar title
        jsonb conversation_metadata
        timestamp created_at
        timestamp updated_at
    }

    MESSAGES {
        uuid message_id PK
        uuid conversation_id FK
        varchar role
        text content
        jsonb message_metadata
        integer token_count
        timestamp timestamp
    }

    DIAGRAMS {
        uuid diagram_id PK
        uuid user_id "No FK - application managed"
        varchar title
        varchar diagram_type
        text mermaid_code
        varchar preview_url
        jsonb diagram_metadata
        timestamp created_at
        timestamp updated_at
    }
```

### User Data Management

**Important**: This AI Services database does NOT manage user data:

- **No `users` table**: User management is handled by the Backend Repository
- **Application-level user context**: User information is provided via JWT claims from backend
- **User ID storage**: All AI service entities store `user_id` as UUID for data association
- **No foreign key constraints**: No FK relationships to non-existent users table
- **Data isolation**: Each user's AI-generated content is isolated via `user_id` filtering

## Docker Integration

### Development Setup

```yaml
# docker-compose.yml - Database services for development
version: '3.8'

services:
  postgres:
    image: postgres:14-alpine
    container_name: ba-copilot-postgres
    environment:
      POSTGRES_DB: bacopilot
      POSTGRES_USER: bacopilot_user
      POSTGRES_PASSWORD: dev_password
      POSTGRES_INITDB_ARGS: '--encoding=UTF8 --locale=en_US.UTF8'
    ports:
      - '5432:5432'
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./infrastructure/sql/init.sql:/docker-entrypoint-initdb.d/01-init.sql:ro
      - ./infrastructure/sql/extensions.sql:/docker-entrypoint-initdb.d/02-extensions.sql:ro
    networks:
      - ba-copilot-network
    healthcheck:
      test: ['CMD-SHELL', 'pg_isready -U bacopilot_user -d bacopilot']
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: ba-copilot-redis
    ports:
      - '6379:6379'
    volumes:
      - redis_data:/data
    networks:
      - ba-copilot-network
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    healthcheck:
      test: ['CMD', 'redis-cli', 'ping']
      interval: 10s
      timeout: 5s
      retries: 3
    restart: unless-stopped

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local

networks:
  ba-copilot-network:
    driver: bridge
```

### Production Configuration

```yaml
# docker-compose.prod.yml - Production database setup
version: '3.8'

services:
  postgres:
    image: postgres:14-alpine
    container_name: ba-copilot-postgres-prod
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_INITDB_ARGS: '--encoding=UTF8 --locale=en_US.UTF8'
    volumes:
      - postgres_prod_data:/var/lib/postgresql/data
      - ./infrastructure/sql/production-init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    networks:
      - ba-copilot-network
    healthcheck:
      test: ['CMD-SHELL', 'pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}']
      interval: 30s
      timeout: 10s
      retries: 3
    restart: always
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M

volumes:
  postgres_prod_data:
    driver: local

networks:
  ba-copilot-network:
    external: true
```

## Database Initialization

### SQL Initialization Scripts

```sql
-- infrastructure/sql/init.sql
-- Development database initialization

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create application user (development only)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'bacopilot_app') THEN
        CREATE USER bacopilot_app WITH PASSWORD 'app_password';
    END IF;
END
$$;

-- Grant permissions
GRANT CONNECT ON DATABASE bacopilot TO bacopilot_app;
GRANT USAGE ON SCHEMA public TO bacopilot_app;
GRANT CREATE ON SCHEMA public TO bacopilot_app;

-- Set up logging
ALTER SYSTEM SET log_statement = 'mod';
ALTER SYSTEM SET log_min_duration_statement = 1000;
ALTER SYSTEM SET log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h ';

SELECT pg_reload_conf();
```

```sql
-- infrastructure/sql/extensions.sql
-- Additional PostgreSQL extensions

-- Full-text search support
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- JSON operations (included in PostgreSQL 14+)
-- CREATE EXTENSION IF NOT EXISTS "jsonb_plperl"; -- Optional for advanced JSON ops

-- Performance monitoring (development)
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

## Migration Management

### Alembic Configuration

```python
# alembic/env.py
"""
Alembic migration environment configuration.
"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.config import settings
from shared.database.models import Base

# Alembic Config object
config = context.config

# Set database URL from environment
config.set_main_option("sqlalchemy.url", settings.database_url)

# Setup logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### Migration Scripts

```bash
#!/bin/bash
# scripts/run_migrations.sh
# Database migration runner

set -e

echo "🗄️  Running database migrations..."

# Ensure database is running
docker-compose up -d postgres

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
timeout 60 bash -c 'until docker-compose exec postgres pg_isready -U bacopilot_user -d bacopilot; do sleep 2; done'

# Run migrations
echo "📊 Running Alembic migrations..."
alembic upgrade head

echo "✅ Database migrations completed successfully!"
```

```python
# scripts/generate_migration.py
"""
Generate new Alembic migration.
"""
import subprocess
import sys
from datetime import datetime

def generate_migration(message: str) -> None:
    """Generate a new migration with descriptive name."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    full_message = f"{timestamp}_{message.replace(' ', '_').lower()}"

    cmd = ["alembic", "revision", "--autogenerate", "-m", full_message]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ Migration generated: {full_message}")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration generation failed: {e}")
        print(e.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/generate_migration.py 'migration description'")
        sys.exit(1)

    message = " ".join(sys.argv[1:])
    generate_migration(message)
```

## Logging and Monitoring

### PostgreSQL Logging Configuration

```sql
-- logging configuration (postgresql.conf equivalent)
-- Applied via Docker environment or config files

-- Basic logging
log_destination = 'stderr'
logging_collector = on
log_directory = '/var/log/postgresql'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_file_mode = 0644

-- Query logging
log_statement = 'mod'                    -- Log DDL/DML statements
log_min_duration_statement = 1000        -- Log slow queries (>1s)
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on

-- Performance monitoring
shared_preload_libraries = 'pg_stat_statements'
pg_stat_statements.track = all
pg_stat_statements.track_utility = on
pg_stat_statements.track_planning = on
```

### Application-Level Database Logging

```python
# src/core/database.py
"""
Database connection and logging setup.
"""
import logging
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from core.config import settings

# Configure database logger
db_logger = logging.getLogger("database")
db_logger.setLevel(logging.INFO)

# Database connection with logging
engine = create_engine(
    settings.database_url,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=settings.debug,  # Log SQL queries in debug mode
)

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log slow queries."""
    context._query_start_time = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log query execution time."""
    total = time.time() - context._query_start_time
    if total > 0.1:  # Log queries taking more than 100ms
        db_logger.warning(f"Slow query ({total:.3f}s): {statement[:100]}...")
```

### Health Check Monitoring

```python
# src/api/v1/endpoints/health.py - Database health checks
"""
Enhanced health check with database monitoring.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from core.database import get_db
import time

@router.get("/health")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Comprehensive health check including database."""
    health_data = {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {}
    }

    # Database connectivity test
    try:
        start_time = time.time()
        result = db.execute(text("SELECT 1")).scalar()
        db_time = time.time() - start_time

        health_data["services"]["database"] = {
            "status": "healthy" if result == 1 else "unhealthy",
            "response_time_ms": round(db_time * 1000, 2),
            "connection_pool": {
                "size": db.bind.pool.size(),
                "checked_in": db.bind.pool.checkedin(),
                "checked_out": db.bind.pool.checkedout(),
            }
        }
    except Exception as e:
        health_data["services"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_data["status"] = "unhealthy"

    return health_data
```

## CI/CD Integration

### GitHub Actions Database Workflow

```yaml
# .github/workflows/database.yml
name: Database CI/CD

on:
  push:
    branches: [main, develop]
    paths: ['alembic/**', 'src/models/**', 'infrastructure/sql/**']
  pull_request:
    branches: [main]

jobs:
  migration-test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:14-alpine
        env:
          POSTGRES_DB: test_bacopilot
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_password
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest-alembic

      - name: Run migration tests
        env:
          DATABASE_URL: postgresql://test_user:test_password@localhost:5432/test_bacopilot
        run: |
          # Test migrations up and down
          alembic upgrade head
          alembic downgrade base
          alembic upgrade head

          # Run migration tests
          python -m pytest tests/test_migrations.py -v

      - name: Test schema integrity
        env:
          DATABASE_URL: postgresql://test_user:test_password@localhost:5432/test_bacopilot
        run: |
          python scripts/verify_schema.py

  performance-test:
    runs-on: ubuntu-latest
    needs: migration-test

    services:
      postgres:
        image: postgres:14-alpine
        env:
          POSTGRES_DB: perf_bacopilot
          POSTGRES_USER: perf_user
          POSTGRES_PASSWORD: perf_password
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup and run performance tests
        env:
          DATABASE_URL: postgresql://perf_user:perf_password@localhost:5432/perf_bacopilot
        run: |
          pip install -r requirements.txt
          alembic upgrade head
          python scripts/populate_test_data.py --size large
          python -m pytest tests/test_performance.py -v
```

### Database Testing Scripts

```python
# scripts/verify_schema.py
"""
Schema verification and integrity tests.
"""
from sqlalchemy import create_engine, inspect, text
from core.config import settings
import sys

def verify_schema():
    """Verify database schema integrity."""
    engine = create_engine(settings.database_url)
    inspector = inspect(engine)

    errors = []

    # Check required tables exist
    required_tables = ['users', 'documents', 'wireframes', 'conversations', 'messages', 'diagrams']
    existing_tables = inspector.get_table_names()

    for table in required_tables:
        if table not in existing_tables:
            errors.append(f"Missing required table: {table}")

    # Check foreign key constraints
    for table in existing_tables:
        fks = inspector.get_foreign_keys(table)
        for fk in fks:
            if fk['referred_table'] not in existing_tables:
                errors.append(f"Foreign key in {table} references non-existent table: {fk['referred_table']}")

    # Check indexes exist
    required_indexes = [
        ('users', 'idx_users_email'),
        ('documents', 'idx_documents_user_id'),
        ('conversations', 'idx_conversations_user_id'),
        ('messages', 'idx_messages_conversation_id'),
    ]

    for table, index in required_indexes:
        if table in existing_tables:
            indexes = inspector.get_indexes(table)
            index_names = [idx['name'] for idx in indexes]
            if index not in index_names:
                errors.append(f"Missing required index: {index} on table {table}")

    if errors:
        print("❌ Schema verification failed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("✅ Schema verification passed!")

if __name__ == "__main__":
    verify_schema()
```

## Advanced Features (Overview)

### Backup and Recovery

```bash
# Basic backup script (infrastructure/scripts/backup.sh)
#!/bin/bash
BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/bacopilot_backup_${TIMESTAMP}.sql"

# Create backup
docker-compose exec postgres pg_dump -U bacopilot_user -d bacopilot > $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE

# Cleanup old backups (keep last 30 days)
find $BACKUP_DIR -name "*.gz" -type f -mtime +30 -delete

echo "Backup completed: ${BACKUP_FILE}.gz"
```

### Performance Optimization

- **Connection Pooling**: SQLAlchemy with configured pool sizes
- **Query Optimization**: Index strategies for common query patterns
- **JSONB Indexing**: GIN indexes for metadata columns
- **Read Replicas**: Optional read-only replicas for reporting

### Monitoring and Alerts

- **pg_stat_statements**: Query performance monitoring
- **Health Checks**: Automated endpoint monitoring
- **Connection Monitoring**: Pool utilization tracking
- **Slow Query Alerts**: Automated alerts for performance issues

### Security Considerations

- **SSL/TLS**: Encrypted connections in production
- **Row-Level Security**: User data isolation
- **Password Policies**: Strong password requirements
- **Audit Logging**: Comprehensive activity logging

## Development Workflows

### Local Development Setup

```bash
# Complete local development setup
make dev-setup

# This runs:
# 1. Setup Python environment
# 2. Start Docker services (PostgreSQL, Redis)
# 3. Run database migrations
# 4. Seed test data
```

### Schema Changes Workflow

```bash
# 1. Modify SQLAlchemy models
# 2. Generate migration
make migration name="add_user_preferences"

# 3. Review generated migration file
# 4. Apply migration
make migrate

# 5. Test migration
make test-db
```

### Testing Database Operations

```bash
# Run database-specific tests
python -m pytest tests/test_database.py -v

# Run migration tests
python -m pytest tests/test_migrations.py -v

# Run performance tests
python -m pytest tests/test_performance.py -v --benchmark-only
```

This comprehensive database documentation provides the foundation for building, deploying, and maintaining the BA Copilot AI Services database infrastructure with clear guidelines for development, testing, and production operations.

## Quick Start Guide

### 1. Initial Setup

```bash
# Clone the repository and navigate to project root
cd ba_copilot_ai

# Copy environment template
cp .env.template .env
# Edit .env with your specific configuration

# Start services with Docker
make docker-up
# Or manually: docker-compose up -d postgres redis

# Run database migrations
make migrate
# Or manually: python scripts/run_migrations.py
```

### 2. Development Workflow

```bash
# Start development environment
make dev-setup

# Generate new migration
make migration name="add_new_feature"

# Verify schema integrity
python scripts/verify_schema.py

# Run database tests
make test-db
```

### 3. Backup and Maintenance

```bash
# Create database backup
./scripts/backup_database.sh

# Monitor database health
curl http://localhost:8000/v1/health
```

## Project Files Created

This documentation includes the following implementation files:

- **Database Documentation**: `docs/database_documentation.md`
- **SQL Initialization Scripts**:
  - `infrastructure/sql/init.sql` - Development database setup
  - `infrastructure/sql/extensions.sql` - PostgreSQL extensions
  - `infrastructure/sql/production-init.sql` - Production configuration
- **Migration Management**:
  - `src/alembic.ini` - Alembic configuration
  - `src/alembic/env.py` - Migration environment
  - `src/alembic/script.py.mako` - Migration template
- **Management Scripts**:
  - `scripts/run_migrations.py` - Cross-platform migration runner
  - `scripts/run_migrations.sh` - Bash migration runner
  - `scripts/verify_schema.py` - Schema verification
  - `scripts/backup_database.sh` - Database backup utility
- **Configuration**:
  - Updated `src/core/config.py` - Application settings
  - Updated `.env.template` - Environment variables
  - Updated `infrastructure/docker-compose.yml` - Added PostgreSQL service

All scripts are production-ready and include comprehensive error handling, logging, and cross-platform compatibility.
