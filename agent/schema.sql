-- Run this in the Supabase SQL Editor (https://app.supabase.com → SQL Editor)

-- Users table: stores registered phone numbers and their target language
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  phone TEXT UNIQUE NOT NULL,
  language TEXT NOT NULL,
  level TEXT NOT NULL DEFAULT 'A1',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Messages table: full conversation history per user
-- This replaces the old `memory` table
CREATE TABLE IF NOT EXISTS messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  phone TEXT NOT NULL REFERENCES users(phone) ON DELETE CASCADE,
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast history lookup by phone, ordered by time
CREATE INDEX IF NOT EXISTS messages_phone_created_at_idx
  ON messages (phone, created_at ASC);

-- Tracks words/phrases the user has practised
CREATE TABLE IF NOT EXISTS user_progress (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  phone TEXT NOT NULL REFERENCES users(phone) ON DELETE CASCADE,
  word TEXT NOT NULL,
  language TEXT NOT NULL,
  times_seen INTEGER DEFAULT 1,
  times_correct INTEGER DEFAULT 0,
  last_seen TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (phone, word)
);

-- Drop the old memory table if it exists
DROP TABLE IF EXISTS memory;
