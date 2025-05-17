#!/bin/bash

echo "🔄 Створення контейнера Cassandra..."
docker run -d --name cassandra \
  --network streaming-net \
  -p 9042:9042 \
  cassandra:4

echo "⏳ Очікуємо готовності Cassandra (через cqlsh)..."
until docker exec cassandra cqlsh -e "SHOW VERSION" >/dev/null 2>&1; do
  echo "⏱️  Cassandra ще не готова, чекаємо..."
  sleep 5
done

echo "✅ Cassandra запущено."