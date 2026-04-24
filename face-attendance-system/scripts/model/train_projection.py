from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

from _embedding_dataset import build_embeddings


def main():
    parser = argparse.ArgumentParser(description="Train embedding projection matrix on a face dataset.")
    parser.add_argument("--dataset", type=Path, required=True, help="ImageFolder dataset path")
    parser.add_argument("--output", type=Path, default=Path("models/facenet/projection_head.npz"))
    parser.add_argument("--backend", type=str, default="facenet", choices=["facenet", "fallback"])
    parser.add_argument("--max-per-class", type=int, default=30)
    parser.add_argument("--pca-dim", type=int, default=64)
    args = parser.parse_args()

    samples = build_embeddings(
        dataset_dir=args.dataset.resolve(),
        backend=args.backend,
        max_per_class=args.max_per_class,
    )
    if len(samples) < 30:
        raise RuntimeError("not enough samples to train projection")

    labels = [sample.label for sample in samples]
    label_to_id = {label: idx for idx, label in enumerate(sorted(set(labels)))}
    y = np.array([label_to_id[label] for label in labels], dtype=np.int32)
    x = np.stack([sample.embedding for sample in samples]).astype(np.float32)

    if len(label_to_id) < 3:
        raise RuntimeError("need at least 3 identities to train projection")

    pca_dim = min(args.pca_dim, x.shape[1], len(samples) - 1)
    pca = PCA(n_components=pca_dim, random_state=42)
    x_pca = pca.fit_transform(x)

    lda_dim = min(len(label_to_id) - 1, x_pca.shape[1])
    lda = LinearDiscriminantAnalysis(solver="svd")
    lda.fit(x_pca, y)

    scalings = lda.scalings_[:, :lda_dim]
    matrix = pca.components_.T @ scalings
    matrix = matrix.astype(np.float32)
    bias = np.zeros((matrix.shape[1],), dtype=np.float32)

    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    np.savez(output, matrix=matrix, bias=bias)
    print(
        f"projection trained: samples={len(samples)}, classes={len(label_to_id)}, "
        f"input_dim={x.shape[1]}, output_dim={matrix.shape[1]}, file={output}"
    )


if __name__ == "__main__":
    main()
