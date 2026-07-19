from __future__ import annotations

from pyspark.sql import DataFrame, functions as F

from .utils import GOLD_DIR, QUARANTINE_DIR


def publish_gold(silver_df: DataFrame):
    gold_df = silver_df.select(
        "chapter_id",
        "chapter_name",
        "city",
        "state",
        "longitude",
        "latitude",
        "dq_status",
        "dq_warnings",
        "ingest_run_id",
    )
    gold_df.write.mode("overwrite").parquet(str(GOLD_DIR))
    return gold_df


def write_quarantine(quarantine_df: DataFrame, run_id: str):
    path = QUARANTINE_DIR / run_id
    quarantine_df.write.mode("overwrite").parquet(str(path))
    return path


def log_metrics(silver_df: DataFrame, quarantine_df: DataFrame):
    rows_quarantined = quarantine_df.count()
    rows_warned = silver_df.filter(F.col("dq_status") == "WARNING").count()
    rows_ok = silver_df.filter(F.col("dq_status") == "OK").count()
    rows_in = rows_quarantined + rows_warned + rows_ok
    print({
        "rows_in": rows_in,
        "rows_quarantined": rows_quarantined,
        "rows_warned": rows_warned,
        "rows_ok": rows_ok,
    })

    ca_count = silver_df.filter(F.col("state") == "CA").count()
    if ca_count == 0:
        raise RuntimeError("CA dropped to zero unexpectedly; refusing silent success")
