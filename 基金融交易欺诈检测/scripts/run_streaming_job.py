from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd
import requests
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import DoubleType, IntegerType, StringType, StructField, StructType


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from fraud_detection.settings import STREAMING_DIR, ensure_directories  # noqa: E402
from fraud_detection.streaming import persist_stream_results  # noqa: E402


def build_schema(feature_columns: list[str]) -> StructType:
    fields = [
        StructField("transaction_id", StringType(), True),
        StructField("event_time", StringType(), True),
        StructField("label", IntegerType(), True),
    ]
    fields.extend(StructField(column, DoubleType(), True) for column in feature_columns)
    return StructType(fields)


def fetch_feature_columns(api_base_url: str) -> list[str]:
    response = requests.get(f"{api_base_url}/schema", timeout=30)
    response.raise_for_status()
    return response.json()["feature_columns"]


def score_batch_via_api(frame: pd.DataFrame, api_base_url: str) -> pd.DataFrame:
    records = []
    meta_columns = {"transaction_id", "event_time", "label"}
    feature_columns = [column for column in frame.columns if column not in meta_columns]
    for row in frame.to_dict(orient="records"):
        records.append(
            {
                "transaction_id": row.get("transaction_id"),
                "features": {column: row[column] for column in feature_columns},
            }
        )
    response = requests.post(f"{api_base_url}/predict/batch", json={"records": records}, timeout=60)
    response.raise_for_status()
    scored = pd.DataFrame(response.json()["results"])
    scored = scored.drop(columns=["transaction_id"], errors="ignore")
    return pd.concat([frame.reset_index(drop=True), scored.reset_index(drop=True)], axis=1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Spark Structured Streaming scoring job.")
    parser.add_argument("--bootstrap-servers", default="127.0.0.1:9092")
    parser.add_argument("--topic", default="fraud-transactions")
    parser.add_argument("--trigger-seconds", type=int, default=5)
    parser.add_argument("--timeout-seconds", type=int, default=90)
    parser.add_argument("--api-base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()

    ensure_directories()
    feature_columns = fetch_feature_columns(args.api_base_url)
    schema = build_schema(feature_columns)
    checkpoint_dir = STREAMING_DIR / "checkpoint"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    spark = (
        SparkSession.builder.master("local[2]")
        .appName("FraudDetectionStreaming")
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.5")
        .config("spark.sql.shuffle.partitions", "2")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    stream_df = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", args.bootstrap_servers)
        .option("subscribe", args.topic)
        .option("startingOffsets", "latest")
        .load()
    )

    parsed = stream_df.select(from_json(col("value").cast("string"), schema).alias("payload")).select("payload.*")

    def process_batch(batch_df, batch_id: int) -> None:
        pdf = batch_df.toPandas()
        if pdf.empty:
            return
        merged = score_batch_via_api(pdf, args.api_base_url)
        summary = persist_stream_results(merged, STREAMING_DIR, batch_id=batch_id)
        print(json.dumps(summary, ensure_ascii=False))

    query = (
        parsed.writeStream.outputMode("append")
        .foreachBatch(process_batch)
        .option("checkpointLocation", str(checkpoint_dir))
        .trigger(processingTime=f"{args.trigger_seconds} seconds")
        .start()
    )

    query.awaitTermination(args.timeout_seconds)
    query.stop()
    spark.stop()


if __name__ == "__main__":
    main()
