from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from sklearn.model_selection import train_test_split


@dataclass
class DatasetSplit:
    train: pd.DataFrame
    valid: pd.DataFrame
    test: pd.DataFrame


def split_data(
    frame: pd.DataFrame,
    target_col: str = "Class",
    strategy: str = "temporal",
    test_size: float = 0.15,
    valid_size: float = 0.15,
    random_state: int = 42,
) -> DatasetSplit:
    if strategy not in {"temporal", "stratified"}:
        raise ValueError("strategy must be 'temporal' or 'stratified'")

    if strategy == "temporal" and "Time" in frame.columns:
        ordered = frame.sort_values("Time").reset_index(drop=True)
        test_start = int(len(ordered) * (1 - test_size))
        valid_start = int(len(ordered) * (1 - test_size - valid_size))
        train = ordered.iloc[:valid_start].copy()
        valid = ordered.iloc[valid_start:test_start].copy()
        test = ordered.iloc[test_start:].copy()
        return DatasetSplit(train=train, valid=valid, test=test)

    train_valid, test = train_test_split(
        frame,
        test_size=test_size,
        stratify=frame[target_col],
        random_state=random_state,
    )
    relative_valid_size = valid_size / (1 - test_size)
    train, valid = train_test_split(
        train_valid,
        test_size=relative_valid_size,
        stratify=train_valid[target_col],
        random_state=random_state,
    )
    return DatasetSplit(train=train.copy(), valid=valid.copy(), test=test.copy())


def get_feature_columns(frame: pd.DataFrame, target_col: str = "Class") -> list[str]:
    return [column for column in frame.columns if column != target_col]


def make_sampler(name: str, random_state: int = 42):
    if name == "none":
        return None
    if name == "undersample":
        return RandomUnderSampler(random_state=random_state)
    if name == "smote":
        return SMOTE(random_state=random_state)
    raise ValueError(f"Unsupported sampling strategy: {name}")
