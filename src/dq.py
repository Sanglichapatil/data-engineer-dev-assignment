from __future__ import annotations

from pyspark.sql import functions as F


def apply_dq(df):
    df = df.withColumn(
        "is_invalid_coordinates",
        (
            F.col("longitude").isNull()
            | F.col("latitude").isNull()
            | (F.col("longitude") < F.lit(-180.0))
            | (F.col("longitude") > F.lit(180.0))
            | (F.col("latitude") < F.lit(-90.0))
            | (F.col("latitude") > F.lit(90.0))
        ),
    )

    city_norm = F.upper(F.trim(F.coalesce(F.col("city"), F.lit(""))))
    df = df.withColumn(
        "has_city_warning",
        (F.col("city").isNull()) | (F.trim(F.col("city")) == "") | (city_norm == F.lit("UNKNOWN")),
    )

    df = df.withColumn(
        "dq_status",
        F.when(F.col("has_city_warning"), F.lit("WARNING")).otherwise(F.lit("OK")),
    ).withColumn(
        "dq_warnings",
        F.when(F.col("has_city_warning"), F.array(F.lit("MISSING_OR_UNKNOWN_CITY"))).otherwise(F.array()),
    )

    quarantine_df = df.filter(F.col("is_invalid_coordinates")).withColumn(
        "dq_reason_code", F.lit("INVALID_COORDINATES")
    )

    silver_df = df.filter(~F.col("is_invalid_coordinates"))
    return silver_df, quarantine_df
