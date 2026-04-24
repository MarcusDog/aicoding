from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app import create_app
from app.services.pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect more live news and keep building the local archive")
    parser.add_argument("--rss-limit", type=int, default=15)
    parser.add_argument("--web-limit", type=int, default=6)
    parser.add_argument("--api-limit", type=int, default=30)
    parser.add_argument("--scenario", choices=["general", "crisis", "policy"], default="general")
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        result = run_pipeline(
            mode="full",
            sample_limit=0,
            rss_limit=args.rss_limit,
            web_limit=args.web_limit,
            api_limit=args.api_limit,
            hot_score_scenario=args.scenario,
            include_sample=False,
            include_batch=False,
            include_rss=True,
            include_web=True,
            include_api=True,
            include_history=True,
        )

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
