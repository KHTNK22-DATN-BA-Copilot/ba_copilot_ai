#!/bin/bash
# Database migration runner script
# BA Copilot AI Services

set -e

echo "🗄️  Running database migrations..."

# Check if we're in the correct directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Load environment variables if .env exists
if [ -f ".env" ]; then
    echo "📋 Loading environment variables from .env"
    export $(cat .env | grep -v '^#' | xargs)
fi

# Ensure database is running (Docker)
if command -v docker-compose &> /dev/null; then
    echo "🐳 Starting PostgreSQL container..."
    docker-compose up -d postgres
    
    # Wait for PostgreSQL to be ready
    echo "⏳ Waiting for PostgreSQL to be ready..."
    timeout 60 bash -c 'until docker-compose exec postgres pg_isready -U ${POSTGRES_USER:-bacopilot_user} -d ${POSTGRES_DB:-bacopilot}; do sleep 2; done'
    
    if [ $? -eq 0 ]; then
        echo "✅ PostgreSQL is ready"
    else
        echo "❌ PostgreSQL failed to start within timeout"
        exit 1
    fi
elif command -v docker &> /dev/null; then
    echo "🐳 Using standalone Docker..."
    # Check if postgres container is running
    if ! docker ps | grep -q postgres; then
        echo "❌ PostgreSQL container is not running. Please start it first."
        exit 1
    fi
else
    echo "ℹ️  No Docker found, assuming PostgreSQL is running externally"
fi

# Check if Alembic is available
if ! command -v alembic &> /dev/null; then
    echo "❌ Alembic not found. Installing dependencies..."
    pip install -r requirements.txt
fi

# Verify database connection
echo "🔌 Testing database connection..."
python -c "
import sys
import os
sys.path.insert(0, 'src')
try:
    from core.config import settings
    from sqlalchemy import create_engine
    engine = create_engine(settings.database_url if hasattr(settings, 'database_url') else 'postgresql://bacopilot_user:dev_password@localhost:5432/bacopilot')
    with engine.connect() as conn:
        conn.execute('SELECT 1')
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Database connection test failed"
    exit 1
fi

# Run Alembic migrations
echo "📊 Running Alembic migrations..."
cd src
alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ Database migrations completed successfully!"
else
    echo "❌ Database migrations failed!"
    exit 1
fi

# Return to project root
cd ..

echo "🎉 Migration process completed!"