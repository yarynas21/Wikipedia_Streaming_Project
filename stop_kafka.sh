#!/bin/bash

echo "🛑 Зупинка Kafka та Zookeeper..."

docker stop kafka zookeeper-server >/dev/null 2>&1
docker rm kafka zookeeper-server >/dev/null 2>&1

echo "✅ Контейнери Kafka та Zookeeper зупинено і видалено."

echo "🧹 Також видалення контейнера wikipedia-producer (якщо існує)..."

docker stop wikipedia-producer >/dev/null 2>&1
docker rm wikipedia-producer >/dev/null 2>&1

echo "✅ Контейнер wikipedia-producer зупинено і видалено (якщо існував)."