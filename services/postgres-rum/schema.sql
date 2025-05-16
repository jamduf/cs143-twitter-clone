CREATE EXTENSION IF NOT EXISTS rum;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

DROP TABLE IF EXISTS urls;
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(128) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE urls (
    id SERIAL PRIMARY KEY,
    tweet_id INTEGER NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    expanded_url TEXT NOT NULL
);

-- Indexes
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_urls_tweet_id ON urls(tweet_id);

-- RUM index for full-text search on messages
CREATE INDEX idx_messages_fts_rum
ON messages USING rum (to_tsvector('english', content));

CREATE INDEX idx_messages_trgm
ON messages USING GIN (content gin_trgm_ops);
