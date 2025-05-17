#!/bin/bash

echo "📥 Імпортуємо schema.cql в Cassandra..."

docker exec -i cassandra cqlsh < cassandra_init/schema.cql

echo "✅ Схема Cassandra імпортована успішно."