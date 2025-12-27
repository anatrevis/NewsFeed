-- Initialize PostgreSQL databases for NewsFeed

-- Create Authentik database (separate from app database)
CREATE DATABASE authentik;

-- Create extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- User keywords table (stores keyword preferences per user)
CREATE TABLE IF NOT EXISTS user_keywords (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    keyword VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, keyword)
);

-- Index for faster queries by user
CREATE INDEX IF NOT EXISTS idx_user_keywords_user_id ON user_keywords(user_id);
CREATE INDEX IF NOT EXISTS idx_user_keywords_created_at ON user_keywords(created_at DESC);

