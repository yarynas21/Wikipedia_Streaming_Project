from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, LongType, BooleanType
from pyspark.sql.functions import col, from_json, to_json, struct

spark = SparkSession.builder \
    .appName("WikipediaCleanStream") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

schema = StructType([
    StructField("meta", StructType([
        StructField("domain", StringType()),
        StructField("dt", StringType())
    ])),
    StructField("page_id", LongType()),
    StructField("page_title", StringType()),
    StructField("comment", StringType()),
    StructField("page_is_redirect", BooleanType()),
    StructField("performer", StructType([
        StructField("user_id", LongType()),
        StructField("user_text", StringType()),
        StructField("user_is_bot", BooleanType())
    ]))
])

df_raw = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "input") \
    .option("startingOffsets", "latest") \
    .load()

df_parsed = df_raw.selectExpr("CAST(value AS STRING) as json_str") \
    .withColumn("data", from_json(col("json_str"), schema)) \
    .select(
        col("data.meta.domain").alias("domain"),
        col("data.meta.dt").alias("created_at"),
        col("data.page_id").alias("page_id"),
        col("data.page_title").alias("page_title"),
        col("data.comment").alias("comment"),
        col("data.page_is_redirect").alias("is_redirect"),
        col("data.performer.user_id").alias("user_id"),
        col("data.performer.user_text").alias("user_name"),
        col("data.performer.user_is_bot").alias("user_is_bot")
    )

# Видаляємо лише null-и, не фільтруємо ботів
filtered_df = df_parsed.dropna(subset=[
    "domain", "created_at", "user_id", "page_id", "page_title"
])

# Об’єднуємо всі потрібні поля
output_df = filtered_df.select(to_json(struct(
    col("domain"),
    col("created_at"),
    col("page_id"),
    col("page_title"),
    col("comment"),
    col("is_redirect"),
    col("user_id"),
    col("user_name"),
    col("user_is_bot")
)).alias("value"))

# Запис у Kafka
query = output_df.writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("topic", "processed") \
    .option("checkpointLocation", "/tmp/wiki-stream-clean-checkpoint") \
    .start()

query.awaitTermination()