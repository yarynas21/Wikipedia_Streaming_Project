CREATE KEYSPACE IF NOT EXISTS wikipedia
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

USE wikipedia;

CREATE TABLE IF NOT EXISTS domains_created (
    domain TEXT,
    created_at TIMESTAMP,
    PRIMARY KEY (domain)
);

CREATE TABLE IF NOT EXISTS pages_by_user (
    user_id BIGINT,
    page_id BIGINT,
    dt TIMESTAMP,
    PRIMARY KEY (user_id, page_id)
);

CREATE TABLE IF NOT EXISTS domain_page_counts (
    domain TEXT,
    page_count COUNTER,
    PRIMARY KEY (domain)
);

CREATE TABLE IF NOT EXISTS pages_by_id (
    page_id BIGINT,
    page_title TEXT,
    domain TEXT,
    dt TIMESTAMP,
    PRIMARY KEY (page_id)
);

CREATE TABLE IF NOT EXISTS user_page_counts_by_date (
    dt DATE,
    user_id BIGINT,
    page_count COUNTER,
    PRIMARY KEY ((dt), user_id)
);

CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    user_name TEXT
);

CREATE TABLE IF NOT EXISTS domain_stats_by_hour (
    time_start TIMESTAMP,
    domain TEXT,
    page_count INT,
    PRIMARY KEY ((time_start), domain)
);

CREATE TABLE IF NOT EXISTS bot_stats_last_6h (
    time_start TIMESTAMP,
    domain TEXT,
    created_by_bots INT,
    PRIMARY KEY ((time_start), domain)
);

CREATE TABLE IF NOT EXISTS top_users_last_6h (
    time_start TIMESTAMP,
    user_id BIGINT,
    user_name TEXT,
    page_count INT,
    page_titles LIST<TEXT>,
    PRIMARY KEY ((time_start), page_count, user_id)
) WITH CLUSTERING ORDER BY (page_count DESC);