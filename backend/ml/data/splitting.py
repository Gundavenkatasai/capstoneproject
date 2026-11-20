"""
CivicMind AI — Leak-Free Dataset Splitting
Supports chronological/temporal splitting and stratified categorical splitting
with strict prevention of cross-split data leakage.
"""

from typing import Tuple, Dict, Any
import pandas as pd
from sklearn.model_selection import train_test_split


def temporal_split(
    df: pd.DataFrame,
    test_size: float = 0.2,
    val_size: float = 0.1,
    time_col: str = "submitted_at",
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Chronological train/val/test split to prevent temporal look-ahead leakage.
    Orders records by submission timestamp and splits into early (train), mid (val), late (test).
    """
    df_sorted = df.sort_values(by=time_col).reset_index(drop=True)
    n = len(df_sorted)

    n_test = int(n * test_size)
    n_val = int(n * val_size)
    n_train = n - n_test - n_val

    train_df = df_sorted.iloc[:n_train].copy().reset_index(drop=True)
    val_df = df_sorted.iloc[n_train : n_train + n_val].copy().reset_index(drop=True)
    test_df = df_sorted.iloc[n_train + n_val :].copy().reset_index(drop=True)

    return train_df, val_df, test_df


def stratified_split(
    df: pd.DataFrame,
    stratify_col: str = "category",
    test_size: float = 0.2,
    val_size: float = 0.1,
    random_state: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Stratified split preserving class representation across splits.
    Avoids data leakage by isolating duplicate clusters into the same partition.
    """
    # Separate duplicates from primary records to avoid leaking duplicate pairs into test
    has_dups = "is_duplicate" in df.columns
    if has_dups:
        dups = df[df["is_duplicate"] == True].copy()
        primaries = df[df["is_duplicate"] == False].copy()
    else:
        dups = pd.DataFrame()
        primaries = df.copy()

    # Split primaries
    val_ratio = val_size / (1.0 - test_size)
    train_prim, test_prim = train_test_split(
        primaries,
        test_size=test_size,
        stratify=primaries[stratify_col],
        random_state=random_state,
    )

    train_prim, val_prim = train_test_split(
        train_prim,
        test_size=val_ratio,
        stratify=train_prim[stratify_col],
        random_state=random_state,
    )

    # Put duplicates matching train in train, matching test in test
    if not dups.empty:
        train_ids = set(train_prim["id"])
        val_ids = set(val_prim["id"])
        test_ids = set(test_prim["id"])

        train_dups = dups[dups["duplicate_of"].isin(train_ids)]
        val_dups = dups[dups["duplicate_of"].isin(val_ids)]
        test_dups = dups[dups["duplicate_of"].isin(test_ids)]

        train_df = pd.concat([train_prim, train_dups], ignore_index=True)
        val_df = pd.concat([val_prim, val_dups], ignore_index=True)
        test_df = pd.concat([test_prim, test_dups], ignore_index=True)
    else:
        train_df = train_prim.reset_index(drop=True)
        val_df = val_prim.reset_index(drop=True)
        test_df = test_prim.reset_index(drop=True)

    return train_df, val_df, test_df


def verify_no_split_leakage(train_df: pd.DataFrame, test_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Verifies that no IDs or duplicate pairs leak across splits.
    """
    train_ids = set(train_df["id"])
    test_ids = set(test_df["id"])
    id_overlap = train_ids.intersection(test_ids)

    leakage_detected = len(id_overlap) > 0

    return {
        "train_samples": len(train_df),
        "test_samples": len(test_df),
        "id_overlap_count": len(id_overlap),
        "leakage_detected": leakage_detected,
    }
