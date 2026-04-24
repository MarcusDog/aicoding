from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]):
    print(">", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main():
    parser = argparse.ArgumentParser(description="One-command model data prep + projection + threshold calibration.")
    parser.add_argument("--dataset", type=Path, default=Path("datasets/lfw_people"))
    parser.add_argument("--skip-download", action="store_true")
    parser.add_argument("--backend", type=str, default="facenet")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    dataset = args.dataset.resolve()

    if not args.skip_download:
        run(
            [
                sys.executable,
                str(root / "download_lfw.py"),
                "--output",
                str(dataset),
                "--min-faces",
                "20",
                "--max-per-class",
                "30",
            ]
        )

    run(
        [
            sys.executable,
            str(root / "train_projection.py"),
            "--dataset",
            str(dataset),
            "--backend",
            args.backend,
            "--output",
            str(Path("models/facenet/projection_head.npz").resolve()),
        ]
    )
    run(
        [
            sys.executable,
            str(root / "calibrate_threshold.py"),
            "--dataset",
            str(dataset),
            "--backend",
            args.backend,
            "--output",
            str(Path("models/facenet/threshold.json").resolve()),
        ]
    )

    print("model pipeline completed")


if __name__ == "__main__":
    main()
