from __future__ import annotations

from pathlib import Path

import pandas as pd


def materialize_main_contract_with_spark(futures_daily: pd.DataFrame, output_path: Path) -> bool:
    try:
        from pyspark.sql import SparkSession, Window
        from pyspark.sql import functions as F
    except ImportError:
        return False

    if futures_daily.empty:
        return False

    spark = (
        SparkSession.builder.appName("cn-futures-analytics")
        .master("local[1]")
        .config("spark.ui.enabled", "false")
        .config("spark.sql.shuffle.partitions", "1")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.driver.host", "127.0.0.1")
        .getOrCreate()
    )
    try:
        sdf = spark.createDataFrame(futures_daily)
        window_spec = Window.partitionBy("trading_date", "product_id").orderBy(
            F.desc("open_interest"),
            F.desc("volume"),
            F.desc("contract_month"),
        )
        main = (
            sdf.withColumn("rank_no", F.row_number().over(window_spec))
            .where(F.col("rank_no") == 1)
            .drop("rank_no")
        )
        main.write.mode("overwrite").parquet(str(output_path))
        return True
    except Exception:  # noqa: BLE001
        return False
    finally:
        spark.stop()
