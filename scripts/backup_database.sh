#!/bin/bash
# Database backup script for BA Copilot AI Services

set -e

# Configuration
BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
POSTGRES_USER="${POSTGRES_USER:-bacopilot_user}"
POSTGRES_DB="${POSTGRES_DB:-bacopilot}"
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Backup filename
BACKUP_FILE="${BACKUP_DIR}/bacopilot_backup_${TIMESTAMP}.sql"

echo "🗄️  Starting database backup..."
echo "📋 Database: $POSTGRES_DB"
echo "👤 User: $POSTGRES_USER"
echo "🏠 Host: $POSTGRES_HOST:$POSTGRES_PORT"
echo "📁 Backup file: $BACKUP_FILE"

# Check if we're using Docker
if command -v docker-compose &> /dev/null && [ -f "docker-compose.yml" ]; then
    echo "🐳 Using Docker Compose..."
    
    # Create backup using docker-compose exec
    if docker-compose exec -T postgres pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" > "$BACKUP_FILE"; then
        echo "✅ Database backup created successfully"
    else
        echo "❌ Database backup failed"
        exit 1
    fi
    
elif command -v docker &> /dev/null; then
    echo "🐳 Using Docker..."
    
    # Find the postgres container
    CONTAINER_ID=$(docker ps --filter "name=postgres" --format "table {{.ID}}" | tail -n +2 | head -1)
    
    if [ -z "$CONTAINER_ID" ]; then
        echo "❌ PostgreSQL container not found"
        exit 1
    fi
    
    # Create backup using docker exec
    if docker exec "$CONTAINER_ID" pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" > "$BACKUP_FILE"; then
        echo "✅ Database backup created successfully"
    else
        echo "❌ Database backup failed"
        exit 1
    fi
    
else
    echo "💻 Using local PostgreSQL..."
    
    # Create backup using local pg_dump
    if pg_dump -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" > "$BACKUP_FILE"; then
        echo "✅ Database backup created successfully"
    else
        echo "❌ Database backup failed"
        exit 1
    fi
fi

# Compress the backup
echo "🗜️  Compressing backup..."
if gzip "$BACKUP_FILE"; then
    echo "✅ Backup compressed: ${BACKUP_FILE}.gz"
    BACKUP_FILE="${BACKUP_FILE}.gz"
else
    echo "⚠️  Failed to compress backup, keeping uncompressed version"
fi

# Get backup size
BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
echo "📊 Backup size: $BACKUP_SIZE"

# Cleanup old backups (keep last 30 days by default)
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"
echo "🧹 Cleaning up backups older than $RETENTION_DAYS days..."

OLD_BACKUPS=$(find "$BACKUP_DIR" -name "bacopilot_backup_*.gz" -type f -mtime +$RETENTION_DAYS)
if [ -n "$OLD_BACKUPS" ]; then
    echo "$OLD_BACKUPS" | while read -r backup; do
        echo "🗑️  Removing old backup: $(basename "$backup")"
        rm "$backup"
    done
    echo "✅ Old backups cleaned up"
else
    echo "ℹ️  No old backups to clean up"
fi

# List remaining backups
echo "📋 Available backups:"
ls -lah "$BACKUP_DIR"/bacopilot_backup_*.gz 2>/dev/null | tail -10 || echo "No backups found"

echo "🎉 Backup process completed successfully!"
echo "💾 Backup saved to: $BACKUP_FILE"