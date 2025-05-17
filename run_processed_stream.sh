#!/bin/bash

echo "🚀 Копіюємо Spark Streaming скрипт у spark-master..."
docker cp stream_processor/spark_kafka_to_db.py spark-master:/opt/bitnami/spark/spark_kafka_to_db.py

echo "🧠 Запускаємо Spark Streaming job (processed → PostgreSQL + Cassandra)..."
docker exec -it spark-master /opt/bitnami/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,com.datastax.spark:spark-cassandra-connector_2.12:3.3.0,org.postgresql:postgresql:42.2.24 \
  /opt/bitnami/spark/spark_kafka_to_db.py

echo "✅ Потік з Kafka (processed) до БД запущено з контейнера spark-master."