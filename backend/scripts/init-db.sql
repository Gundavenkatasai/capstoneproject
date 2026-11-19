-- ==============================================================================
-- CivicMind AI — PostgreSQL Initialization Script
-- Executed on container creation in /docker-entrypoint-initdb.d/
-- ==============================================================================

-- Enable vector extension for 768-dimensional dense semantic embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable UUID extension for cryptographic UUIDv4 generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Enable pg_trgm for full-text search indexing on grievance titles & descriptions
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Verify vector extension is loaded
DO $$
BEGIN
    RAISE NOTICE 'CivicMind AI: Extensions successfully loaded into %', current_database();
END $$;
