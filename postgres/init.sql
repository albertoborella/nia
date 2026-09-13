-- NIA Database Initialization
-- This runs automatically when the container starts for the first time

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- The actual schema is managed by Alembic migrations.
-- This file only ensures the database and extensions are ready.
