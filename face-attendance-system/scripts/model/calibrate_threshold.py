from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path

import numpy as np

from _embedding_dataset import build_embeddings


def sample_pairs(by_label: dict[str, list[np.ndarray]], max_pairs_per_class: int, impostor_pairs: int):
    genuine_distances = []
    impostor_distances = []

    labels = list(by_label.keys())
    for label, emb_list in by_label.items():
        if len(emb_list) < 2:
            continue
        pairs = 0
        for i in range(len(emb_list)):
            for j in range(i + 1, len(emb_list)):
                genuine_distances.append(float(np.linalg.norm(emb_list[i] - emb_list[j])))
                pairs += 1
                if pairs >= max_pairs_per_class:
                    break
            if pairs >= max_pairs_per_class:
                break

    for _ in range(impostor_pairs):
        a, b = random.sample(labels, 2)
        ea = random.choice(by_label[a])
        eb = random.choice(by_label[b])
        impostor_distances.append(float(np.linalg.norm(ea - eb)))

    return genuine_distances, impostor_distances


def find_best_threshold(genuine: list[float], impostor: list[float]) -> tuple[float, float]:
    thresholds = np.linspace(0.2, 1.8, 321)
    best_threshold = 1.0
    best_acc = 0.0
    total = len(genuine) + len(impostor)

    for threshold in thresholds:
        tp = sum(1 for d in genuine if d < threshold)
        tn = sum(1 for d in impostor if d >= threshold)
        acc = (tp + tn) / max(total, 1)
        if acc > best_acc:
            best_acc = acc
            best_threshold = float(threshold)

    return best_threshold, float(best_acc)


def main():
    parser = argparse.ArgumentParser(description="Calibrate face match threshold on a dataset.")
    parser.add_argument("--dataset", type=Path, required=True, help="ImageFolder dataset path")
    parser.add_argument("--output", type=Path, default=Path("models/facenet/threshold.json"))
    parser.add_argument("--backend", type=str, default="facenet", choices=["facenet", "fallback"])
    parser.add_argument("--max-per-class", type=int, default=25)
    parser.add_argument("--max-pairs-per-class", type=int, default=100)
    parser.add_argument("--impostor-pairs", type=int, default=5000)
    args = parser.parse_args()

    samples = build_embeddings(args.dataset.resolve(), backend=args.backend, max_per_class=args.max_per_class)
    if len(samples) < 50:
        raise RuntimeError("not enough samples to calibrate threshold")

    by_label: dict[str, list[np.ndarray]] = defaultdict(list)
    for sample in samples:
        by_label[sample.label].append(sample.embedding)

    genuine, impostor = sample_pairs(
        by_label=by_label,
        max_pairs_per_class=args.max_pairs_per_class,
        impostor_pairs=args.impostor_pairs,
    )
    if not genuine or not impostor:
        raise RuntimeError("failed to build genuine/impostor pairs")

    threshold, accuracy = find_best_threshold(genuine, impostor)
    payload = {
        "recommended_threshold": round(threshold, 4),
        "pair_accuracy": round(accuracy, 4),
        "genuine_pairs": len(genuine),
        "impostor_pairs": len(impostor),
    }

    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"threshold calibrated: {payload} -> {output}")


if __name__ == "__main__":
    main()
