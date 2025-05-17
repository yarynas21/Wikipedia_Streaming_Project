CREATE TABLE IF NOT EXISTS wiki_events (
    id SERIAL PRIMARY KEY,
    domain TEXT,
    created_at TIMESTAMP,
    page_id BIGINT,
    page_title TEXT,
    user_id BIGINT,
    user_name TEXT,
    comment TEXT,
    user_is_bot BOOLEAN
);