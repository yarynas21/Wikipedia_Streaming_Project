from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, LongType

import psycopg2
from cassandra.cluster import Cluster
from datetime import datetime
import time

# Spark Session
spark = SparkSession.builder \
    .appName("KafkaToCassandraPostgres") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Kafka schema
schema = StructType([
    StructField("domain", StringType()),
    StructField("created_at", StringType()),
    StructField("page_id", LongType()),
    StructField("page_title", StringType()),
    StructField("user_id", LongType()),
    StructField("user_name", StringType()),
    StructField("comment", StringType(), True),
    StructField("user_is_bot", StringType(), True)
])

# Kafka source
df_raw = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "processed") \
    .option("startingOffsets", "earliest") \
    .load()

# Parse JSON
parsed_df = df_raw.selectExpr("CAST(value AS STRING) as json_str") \
    .withColumn("data", from_json(col("json_str"), schema)) \
    .select("data.*")

# Row-level write logic
def process_row(row):
    try:
        created_at = datetime.fromisoformat(row.created_at.replace("Z", "+00:00"))
        dt_date = created_at.date()

        # PostgreSQL insert
        pg_conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="postgres",
            host="postgres",
            port="5432"
        )
        pg_cur = pg_conn.cursor()
        pg_cur.execute("""
            INSERT INTO wiki_events (domain, created_at, page_id, page_title, user_id, user_name, comment, user_is_bot)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            row.domain,
            created_at,
            row.page_id,
            row.page_title,
            row.user_id,
            row.user_name,
            row.comment or "",
            row.user_is_bot.lower() == "true" if isinstance(row.user_is_bot, str) else bool(row.user_is_bot)
        ))
        pg_conn.commit()
        pg_cur.close()
        pg_conn.close()

        # Cassandra insert (з retry)
        cassandra_connected = False
        retry_attempts = 5
        for attempt in range(retry_attempts):
            try:
                cluster = Cluster(["cassandra"])
                session = cluster.connect("wikipedia")

                session.execute("""
                    INSERT INTO pages_by_user (user_id, page_id, dt)
                    VALUES (%s, %s, %s)
                """, (row.user_id, row.page_id, created_at))

                session.execute("""
                    INSERT INTO pages_by_id (page_id, page_title, domain, dt)
                    VALUES (%s, %s, %s, %s)
                """, (row.page_id, row.page_title, row.domain, created_at))

                session.execute("""
                    INSERT INTO domains_created (domain, created_at)
                    VALUES (%s, %s)
                    IF NOT EXISTS
                """, (row.domain, created_at))

                session.execute("""
                    UPDATE domain_page_counts
                    SET page_count = page_count + 1
                    WHERE domain = %s
                """, (row.domain,))

                session.execute("""
                    UPDATE user_page_counts_by_date
                    SET page_count = page_count + 1
                    WHERE dt = %s AND user_id = %s
                """, (dt_date, row.user_id))

                session.execute("""
                    INSERT INTO users (user_id, user_name)
                    VALUES (%s, %s)
                """, (row.user_id, row.user_name))

                cassandra_connected = True
                break

            except Exception as cassandra_error:
                print(f"❌ Cassandra помилка (спроба {attempt + 1}): {cassandra_error}")
                time.sleep(3)

        if not cassandra_connected:
            print(f"🚫 Cassandra недоступна. Пропускаємо page_id={row.page_id}")
        else:
            print(f"✔️ Оброблено: page_id={row.page_id}")

    except Exception as e:
        print(f"❌ Помилка обробки: {e}")

def process_batch(df, batch_id):
    rows = df.collect()
    print(f"📦 Отримано {len(rows)} записів у batch {batch_id}")
    for row in rows:
        process_row(row)

parsed_df.writeStream \
    .foreachBatch(process_batch) \
    .start() \
    .awaitTermination()