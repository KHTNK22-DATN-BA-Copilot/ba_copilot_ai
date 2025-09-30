-- Production Database Initialization Script
-- BA Copilot AI Services

-- Enable required PostgreSQL extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create application user with limited privileges
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'bacopilot_app') THEN
        CREATE USER bacopilot_app WITH PASSWORD 'CHANGE_THIS_PASSWORD_IN_PRODUCTION';
    END IF;
END
$$;

-- Grant minimal required permissions
GRANT CONNECT ON DATABASE bacopilot TO bacopilot_app;
GRANT USAGE ON SCHEMA public TO bacopilot_app;
GRANT CREATE ON SCHEMA public TO bacopilot_app;

-- Note: Table permissions will be granted via Alembic migrations in production
-- DO NOT create tables directly in production - use migrations instead

-- Configure production logging
ALTER SYSTEM SET log_destination = 'stderr';
ALTER SYSTEM SET logging_collector = on;
ALTER SYSTEM SET log_directory = '/var/log/postgresql';
ALTER SYSTEM SET log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log';
ALTER SYSTEM SET log_file_mode = 0644;
ALTER SYSTEM SET log_rotation_age = '1d';
ALTER SYSTEM SET log_rotation_size = '100MB';

-- Production logging settings
ALTER SYSTEM SET log_statement = 'ddl';  -- Only log DDL in production
ALTER SYSTEM SET log_min_duration_statement = 2000;  -- Log queries taking more than 2 seconds
ALTER SYSTEM SET log_checkpoints = on;
ALTER SYSTEM SET log_connections = off;  -- Disable connection logging in production
ALTER SYSTEM SET log_disconnections = off;
ALTER SYSTEM SET log_lock_waits = on;
ALTER SYSTEM SET log_temp_files = 10240;  -- Log temp files larger than 10MB

-- Performance settings
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET pg_stat_statements.track = 'all';
ALTER SYSTEM SET pg_stat_statements.track_utility = on;
ALTER SYSTEM SET pg_stat_statements.track_planning = on;
ALTER SYSTEM SET pg_stat_statements.max = 10000;

-- Connection settings
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET work_mem = '4MB';

-- WAL settings for better performance
ALTER SYSTEM SET wal_level = 'replica';
ALTER SYSTEM SET max_wal_size = '1GB';
ALTER SYSTEM SET min_wal_size = '80MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;

-- Security settings
ALTER SYSTEM SET ssl = on;
ALTER SYSTEM SET ssl_cert_file = 'server.crt';
ALTER SYSTEM SET ssl_key_file = 'server.key';
ALTER SYSTEM SET password_encryption = 'scram-sha-256';

-- Reload configuration
SELECT pg_reload_conf();

COMMIT;