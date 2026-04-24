from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import pandas as pd
from kafka import KafkaProducer


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from fraud_detection.settings import PROCESSED_DATA_DIR  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay test data to Kafka.")
    parser.add_argument("--topic", default="fraud-transactions")
    parser.add_argument("--bootstrap-servers", default="127.0.0.1:9092")
    parser.add_argument("--rows", type=int, default=300)
    parser.add_argument("--delay", type=float, default=0.05, help="Delay between messages in seconds.")
    args = parser.parse_args()

    source_path = PROCESSED_DATA_DIR / "splits" / "test.csv"
    frame = pd.read_csv(source_path).head(args.rows).copy()
    frame["transaction_id"] = [f"txn-{idx:06d}" for idx in range(len(frame))]
    frame["event_time"] = pd.Timestamp.utcnow().isoformat()
    frame = frame.rename(columns={"Class": "label"})

    producer = KafkaProducer(
        bootstrap_servers=args.bootstrap_servers,
        value_serializer=lambda payload: json.dumps(payload).encode("utf-8"),
    )

    for row in frame.to_dict(orient="records"):
        producer.send(args.topic, row)
        if args.delay > 0:
            time.sleep(args.delay)
    producer.flush()
    producer.close()
    print(f"Published {len(frame)} events to topic {args.topic}")


if __name__ == "__main__":
    main()
