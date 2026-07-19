from __future__ import annotations

from pyspark.sql import SparkSession, functions as F, types as T

from .dq import apply_dq
from .utils import SILVER_DIR


def build_silver(spark: SparkSession, bronze_path: str, run_id: str):
    raw = spark.read.option("multiline", True).json(bronze_path)
    features = raw.select(F.explode("features").alias("feature"))

    df = features.select(
        F.col("feature.attributes.ChapterID").cast(T.StringType()).alias("chapter_id"),
        F.col("feature.attributes.University_Chapter").cast(T.StringType()).alias("chapter_name"),
        F.col("feature.attributes.City").cast(T.StringType()).alias("city"),
        F.col("feature.attributes.State").cast(T.StringType()).alias("state"),
        F.col("feature.geometry.x").cast(T.DoubleType()).alias("longitude"),
        F.col("feature.geometry.y").cast(T.DoubleType()).alias("latitude"),
        F.col("feature.attributes.OBJECTID").cast(T.StringType()).alias("source_object_id"),
        F.to_json(F.col("feature")).alias("raw_payload"),
    ).filter(F.col("state").isin("CA", "OR", "WA"))

    df = df.dropDuplicates(["chapter_id"]).withColumn("ingest_run_id", F.lit(run_id))

    silver_df, quarantine_df = apply_dq(df)
    silver_df.write.mode("overwrite").parquet(str(SILVER_DIR))
    return silver_df, quarantine_df
