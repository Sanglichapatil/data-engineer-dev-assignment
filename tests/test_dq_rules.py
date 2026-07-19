from pyspark.sql import SparkSession
from pyspark.sql import Row

from src.dq import apply_dq


def spark_session():
    return (
        SparkSession.builder.master("local[1]")
        .appName("dq-tests")
        .config("spark.sql.shuffle.partitions", "1")
        .getOrCreate()
    )


def test_quarantine_and_warning_paths():
    spark = spark_session()
    rows = [
        Row(chapter_id="CA-0001", chapter_name="Good Row", city="Los Angeles", state="CA", longitude=-118.25, latitude=34.05),
        Row(chapter_id="CA-0002", chapter_name="Warn Row", city="UNKNOWN", state="CA", longitude=-121.49, latitude=38.58),
        Row(chapter_id="CA-0003", chapter_name="Bad Coord Row", city="San Diego", state="CA", longitude=999.0, latitude=32.71),
    ]
    df = spark.createDataFrame(rows)
    silver_df, quarantine_df = apply_dq(df)

    assert quarantine_df.count() == 1
    assert silver_df.count() == 2
    assert silver_df.filter(silver_df.chapter_id == "CA-0002").collect()[0]["dq_status"] == "WARNING"
    assert silver_df.filter(silver_df.chapter_id == "CA-0003").count() == 0

    spark.stop()
