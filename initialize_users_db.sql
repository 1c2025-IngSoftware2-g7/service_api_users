-- Crear el usuario solo si no existe
DO
$$
BEGIN
   IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'user_db') THEN
      CREATE USER user_db WITH PASSWORD 'classconect-users';
   END IF;
END
$$;

-- Crear la base de datos solo si no existe
DO
$$
BEGIN
   IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'classconnect_users') THEN
      CREATE DATABASE classconnect_users;
   END IF;
END
$$;

-- Grant privileges on the database
GRANT ALL PRIVILEGES ON DATABASE classconnect_users TO user_db;

-- Connect to the database
\c classconnect_users

-- Grant privileges on all tables and sequences in the public schema
-- Sequences: for the auto-incrementing id
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO user_db;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO user_db;

-- Set default privileges for future tables and sequences
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO user_db;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO user_db;

-- Enable the uuid-ossp extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create the 'courses' table
CREATE TABLE IF NOT EXISTS users (
    uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name text,
    surname text,
    password text,
    email text,
    status text,
    role text
);

-- Create the 'user_locations' table
CREATE TABLE IF NOT EXISTS user_locations (
    uuid UUID PRIMARY KEY,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    FOREIGN KEY (uuid) REFERENCES users(uuid) ON DELETE CASCADE
);
