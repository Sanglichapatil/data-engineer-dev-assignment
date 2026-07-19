from __future__ import annotations

from pyspark.sql import SparkSession

from .ingest import ingest_bronze
from .publish_gold import log_metrics, publish_gold, write_quarantine
from .transform_silver import build_silver


def main():
    spark = (
        SparkSession.builder.appName("university-chapters-medallion")
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", "1")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    run_id, bronze_path = ingest_bronze()
    silver_df, quarantine_df = build_silver(spark, bronze_path, run_id)
    write_quarantine(quarantine_df, run_id)
    publish_gold(silver_df)
    log_metrics(silver_df, quarantine_df)
    spark.stop()


if __name__ == "__main__":
    main()
