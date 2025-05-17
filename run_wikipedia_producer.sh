#!/bin/bash

echo "Запуск Wikipedia продюсера у Docker-контейнері..."

NETWORK_NAME=streaming-net

CONTAINER_NAME=wikipedia-producer

docker rm -f $CONTAINER_NAME 2>/dev/null

docker run -d \
  --name $CONTAINER_NAME \
  --network $NETWORK_NAME \
  -v "$(pwd)/wikipedia_producer/wikipedia_producer.py:/app/wikipedia_producer.py" \
  python:3.9-slim \
  bash -c "pip install requests sseclient kafka-python && python /app/wikipedia_producer.py"

echo "Контейнер $CONTAINER_NAME запущено. Потік Wikimedia → Kafka активний."