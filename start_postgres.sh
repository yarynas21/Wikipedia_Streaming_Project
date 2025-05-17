#!/bin/bash

echo "🐘 Створення контейнера PostgreSQL у мережі streaming-net..."

docker run -d \
  --name postgres \
  --network streaming-net \
  -e POSTGRES_DB=postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -v "$(pwd)/postgres_init:/docker-entrypoint-initdb.d" \
  postgres:15

echo "⏳ Очікування 10 секунд поки PostgreSQL ініціалізується..."
sleep 10

echo "✅ PostgreSQL запущено."