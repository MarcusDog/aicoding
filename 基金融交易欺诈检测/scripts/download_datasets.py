from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from fraud_detection.data import download_creditcard_dataset, download_latest_sec_nmfp  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Download project datasets.")
    parser.add_argument("--force", action="store_true", help="Redownload files even if they exist.")
    parser.add_argument(
        "--download-sec-nmfp",
        action="store_true",
        help="Download the latest SEC Form N-MFP archive as an extension dataset.",
    )
    args = parser.parse_args()

    dataset_path, metadata = download_creditcard_dataset(force=args.force)
    print(f"Downloaded credit card fraud dataset to: {dataset_path}")
    print(json.dumps(metadata, indent=2, ensure_ascii=False))

    if args.download_sec_nmfp:
        try:
            sec_path = download_latest_sec_nmfp(force=args.force)
            print(f"Downloaded SEC N-MFP archive to: {sec_path}")
        except Exception as exc:  # noqa: BLE001
            print(f"SEC N-MFP download skipped: {exc}")


if __name__ == "__main__":
    main()
