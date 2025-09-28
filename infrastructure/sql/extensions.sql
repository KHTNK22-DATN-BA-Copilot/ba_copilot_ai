-- PostgreSQL Extensions Setup
-- BA Copilot AI Services

-- Full-text search support
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- UUID generation functions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Performance monitoring extension
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Additional useful extensions for production (commented for now)

-- Advanced JSON operations (if needed)
-- CREATE EXTENSION IF NOT EXISTS "jsonb_plperl";

-- Cryptographic functions
-- CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- PostGIS for geospatial data (if needed for location features)
-- CREATE EXTENSION IF NOT EXISTS "postgis";

-- HStore for key-value storage (alternative to JSONB)
-- CREATE EXTENSION IF NOT EXISTS "hstore";

-- Fuzzy string matching
-- CREATE EXTENSION IF NOT EXISTS "fuzzystrmatch";

-- Tablespace and partition management (if needed for large datasets)
-- CREATE EXTENSION IF NOT EXISTS "pg_partman";

-- Additional performance extensions
-- CREATE EXTENSION IF NOT EXISTS "auto_explain";
-- CREATE EXTENSION IF NOT EXISTS "pg_buffercache";

COMMIT;