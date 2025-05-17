#!/bin/bash

echo "🔄 Створення Docker-мережі 'streaming-net' (якщо ще не існує)..."
docker network create streaming-net 2>/dev/null || echo "Мережа вже існує"

echo "🧨 Видалення попередніх kafka/zookeeper (якщо існують)..."
docker rm -f kafka zookeeper-server 2>/dev/null

echo "🟢 Запуск Zookeeper..."
docker run -d --name zookeeper-server \
  --network streaming-net \
  -e ALLOW_ANONYMOUS_LOGIN=yes \
  bitnami/zookeeper:latest

echo "🟢 Запуск Kafka..."

docker run -d --name kafka \
  --network streaming-net \
  -p 9092:9092 \
  -e KAFKA_CFG_ZOOKEEPER_CONNECT=zookeeper-server:2181 \
  -e ALLOW_PLAINTEXT_LISTENER=yes \
  bitnami/kafka:3.4.0

echo "✅ Kafka кластер запущено."