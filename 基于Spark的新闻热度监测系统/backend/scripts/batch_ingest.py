from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app import create_app
from app.services.pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch import local news datasets and refresh analysis outputs")
    parser.add_argument("--dataset-dir", type=str, default="../data/raw/imports")
    parser.add_argument("--dataset-path", dest="dataset_paths", action="append", default=[])
    parser.add_argument("--source-config-path", type=str, default="")
    parser.add_argument("--include-rss", action="store_true")
    parser.add_argument("--rss-limit", type=int, default=20)
    parser.add_argument("--include-sample", action="store_true")
    parser.add_argument("--sample-limit", type=int, default=30)
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        result = run_pipeline(
            mode="batch",
            sample_limit=args.sample_limit if args.include_sample else 0,
            rss_limit=args.rss_limit if args.include_rss else 0,
            dataset_dir=args.dataset_dir,
            dataset_paths=args.dataset_paths or None,
            source_config_path=args.source_config_path or None,
            include_sample=args.include_sample,
            include_batch=True,
            include_rss=args.include_rss,
            include_web=False,
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
