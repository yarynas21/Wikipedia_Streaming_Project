# Wikipedia_Streaming_Project

## 🧪 Full System Startup Instructions

This guide will help you run the entire Wikipedia Streaming Project stack from scratch.

---

### ✅ 1. Start Cassandra
```bash
./start_cassandra.sh
```

Wait ~20 seconds or run:
```bash
docker logs -f cassandra
```
until you see `Startup complete`.

---

### ✅ 2. Initialize Cassandra Schema
```bash
./init_cassandra.sh
```

---

### ✅ 3. Start PostgreSQL
```bash
./start_postgres.sh
```

---

### ✅ 4. Start Kafka + Zookeeper
```bash
./start_kafka.sh
```

---

### ✅ 5. Initialize Kafka Topics
```bash
./init_kafka_topics.sh
```

---

### ✅ 6. Start Spark (Master + Worker)
```bash
docker compose up -d
```

---

### ✅ 7. Run Wikipedia Producer
```bash
./run_wikipedia_producer.sh
```

```bash
docker exec -it kafka kafka-console-consumer.sh \
  --bootstrap-server kafka:9092 \
  --topic input \
  --from-beginning
```
---

### ✅ 8. Run Stream: input → processed
```bash
./run_filter_stream.sh
```

```bash
docker exec -it kafka kafka-console-consumer.sh \
  --bootstrap-server kafka:9092 \
  --topic processed \
  --from-beginning
```
---

#### How To Check Cassandra

```bash
docker exec -it cassandra cqlsh
USE wikipedia;
SELECT * FROM pages_by_id LIMIT 5;
SELECT * FROM domains_created LIMIT 5;
```

#### How To Check Postgres
```bash
docker exec -it postgres bash
psql -U postgres -d postgres
SELECT * FROM wiki_events ORDER BY created_at DESC LIMIT 1;
SELECT * FROM wiki_events ORDER BY created_at DESC LIMIT 10;
```


### ✅ 10. Run Aggregation file
```bash
./batch_jobs/run_aggregator.sh
```

### ✅ 11. Build & Run FastAPI for Category B API
```bash
cd fastapi_api
docker build -t fastapi-api .
docker run -d --name fastapi-api --network streaming-net -p 8000:8000 fastapi-api
```
---

### 📍 API Available At
[http://localhost:8000/docs](http://localhost:8000/docs)