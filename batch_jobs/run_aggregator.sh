#!/bin/bash

echo "🚀 Запуск Aggregator у Docker-контейнері..."

NETWORK_NAME=streaming-net

CONTAINER_NAME=postgres-cassandra-aggregator

docker rm -f $CONTAINER_NAME 2>/dev/null

docker run -d \
  --name $CONTAINER_NAME \
  --network $NETWORK_NAME \
  -v "$(pwd)/batch_jobs/aggregator.py:/app/batch_jobs/aggregator.py" \
  python:3.9-slim \
  bash -c "pip install psycopg2-binary pandas cassandra-driver && python /app/batch_jobs/aggregator.py"

echo "✅ Контейнер $CONTAINER_NAME запущено. Агрегація запущена."