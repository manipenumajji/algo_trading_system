CREATE TABLE IF NOT EXISTS news_raw (
    id SERIAL PRIMARY KEY,
    asset VARCHAR(10) NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    url TEXT,
    source VARCHAR(100),
    published_at TIMESTAMP NOT NULL,
    fetched_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(url)
);