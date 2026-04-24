from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np
from sklearn.datasets import fetch_lfw_people


def sanitize(name: str) -> str:
    return name.replace(" ", "_").replace(".", "")


def main():
    parser = argparse.ArgumentParser(description="Download LFW subset and export as ImageFolder.")
    parser.add_argument("--output", type=Path, default=Path("datasets/lfw_people"))
    parser.add_argument("--min-faces", type=int, default=20)
    parser.add_argument("--max-per-class", type=int, default=30)
    args = parser.parse_args()

    dataset = fetch_lfw_people(
        min_faces_per_person=args.min_faces,
        resize=1.0,
        color=True,
        download_if_missing=True,
    )

    output_dir = args.output.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    class_counts: dict[int, int] = {}
    total_saved = 0
    for image, target in zip(dataset.images, dataset.target):
        count = class_counts.get(int(target), 0)
        if count >= args.max_per_class:
            continue
        label = sanitize(dataset.target_names[int(target)])
        person_dir = output_dir / label
        person_dir.mkdir(parents=True, exist_ok=True)

        rgb = image.astype(np.uint8)
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        out_path = person_dir / f"{count:04d}.jpg"
        cv2.imwrite(str(out_path), bgr)

        class_counts[int(target)] = count + 1
        total_saved += 1

    print(
        f"LFW exported to {output_dir} with "
        f"{len(class_counts)} identities and {total_saved} images."
    )


if __name__ == "__main__":
    main()
