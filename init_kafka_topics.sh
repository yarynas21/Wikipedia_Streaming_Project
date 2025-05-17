#!/bin/bash

echo "📦 Створення топіка input..."
docker exec kafka kafka-topics.sh \
  --create --bootstrap-server kafka:9092 \
  --replication-factor 1 --partitions 3 --topic input

echo "📦 Створення топіка processed..."
docker exec kafka kafka-topics.sh \
  --create --bootstrap-server kafka:9092 \
  --replication-factor 1 --partitions 3 --topic processed

echo "✅ Топіки створено успішно."