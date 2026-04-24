from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app import create_app
from app.services.pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Run news monitor collection and analysis pipeline")
    parser.add_argument("--mode", choices=["sample", "rss", "batch", "web", "hybrid", "full"], default="hybrid")
    parser.add_argument("--sample-limit", type=int, default=80)
    parser.add_argument("--rss-limit", type=int, default=20)
    parser.add_argument("--web-limit", type=int, default=0)
    parser.add_argument("--api-limit", type=int, default=50)
    parser.add_argument("--hot-score-scenario", choices=["general", "crisis", "policy"], default="general")
    parser.add_argument("--source-config-path", type=str, default="")
    parser.add_argument("--dataset-dir", type=str, default="")
    parser.add_argument("--dataset-path", dest="dataset_paths", action="append", default=[])
    parser.add_argument("--no-sample", action="store_true")
    parser.add_argument("--no-batch", action="store_true")
    parser.add_argument("--no-rss", action="store_true")
    parser.add_argument("--include-web", action="store_true")
    parser.add_argument("--include-api", action="store_true")
    parser.add_argument("--no-history", action="store_true")
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        result = run_pipeline(
            mode=args.mode,
            sample_limit=args.sample_limit,
            rss_limit=args.rss_limit,
            api_limit=args.api_limit,
            hot_score_scenario=args.hot_score_scenario,
            web_limit=args.web_limit,
            source_config_path=args.source_config_path or None,
            dataset_dir=args.dataset_dir or None,
            dataset_paths=args.dataset_paths or None,
            include_sample=False if args.no_sample else None,
            include_batch=False if args.no_batch else None,
            include_rss=False if args.no_rss else None,
            include_web=True if args.include_web else None,
            include_api=True if args.include_api else None,
            include_history=not args.no_history,
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
