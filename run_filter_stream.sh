#!/bin/bash

echo "🚀 Копіюємо Spark Streaming скрипт у spark-master..."
docker cp stream_processor/kafka_filter_stream.py spark-master:/opt/bitnami/spark/kafka_filter_stream.py

echo "🧠 Запускаємо Spark Streaming job усередині контейнера spark-master..."
docker exec -it spark-master /opt/bitnami/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --conf spark.executor.cores=1 \
  --conf spark.executor.memory=1G \
  --conf spark.cores.max=1 \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0 \
  /opt/bitnami/spark/kafka_filter_stream.py

echo "✅ Потік запущено з контейнера spark-master (input → processed)."SELECT * FROM user_page_counts_by_date LIMIT 5;