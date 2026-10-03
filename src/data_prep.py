"""
src/data_prep.py

Data preparation for Network Guardian IDS.

Responsibilities (Phase 2 of tasks/1.md):
    1. Parse the column manifest (data/raw/kddcup.names.txt).
    2. Parse the attack-family map (data/raw/training_attack_types.txt).
    3. Load the raw KDD Cup 1999 dataset with explicit column names.
    4. Map 23 raw attack strings to 5 canonical families.
    5. Deduplicate on the 41 feature columns.
    6. Prune features with Pearson correlation above a threshold.
    7. Apply log(1+x) to skewed continuous features.
    8. Perform a one-time stratified 75/25 train/test split.
    9. Write processed arrays, feature names, split indices, and a
       split contract to data/processed/.

All functions are pure with respect to global state and accept explicit
arguments. Randomness is locked to src.utils.SEED.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from src.utils import (
    PATHS,
    RANDOM_STATE,
    load_json,
    save_json,
)

# ---------------------------------------------------------------------------
# Constants derived from project context (not assumptions)
# ---------------------------------------------------------------------------

# Continuous columns identified in tasks/1.md Phase 2 step 4 for log(1+x).
LOG_TRANSFORM_COLUMNS: tuple[str, ...] = ("duration", "src_bytes", "dst_bytes")

# Columns treated as categorical and encoded in src/encoding.py.
FREQUENCY_ENCODE_COLUMNS: tuple[str, ...] = ("service",)
ONEHOT_ENCODE_COLUMNS: tuple[str, ...] = ("protocol_type", "flag")

# Split configuration confirmed on Day 1 of the sprint.
TEST_SIZE: float = 0.25
STRATIFY_ON_LABEL: bool = True

# Correlation pruning threshold per architecture spec.
CORRELATION_THRESHOLD: float = 0.90

# Canonical family ordering used everywhere downstream.
CLASS_ORDER: tuple[str, ...] = ("normal", "dos", "probe", "r2l", "u2r")


# ---------------------------------------------------------------------------
# Manifest and label-map parsing
# ---------------------------------------------------------------------------


def parse_column_manifest(path: str | Path) -> list[str]:
    """Parse data/raw/kddcup.names.txt and return the 42 column names.

    The file has 42 non-empty lines:
        Line 1    : comma-separated attack-string header (not a column).
        Lines 2-42: 41 column definitions of the form '<name>: <type>.'.

    The label column is not defined in the file. It is the 42nd column
    of the CSV and is appended here under the name 'label'.

    Returns:
        List of 41 feature names followed by 'label'.

    Raises:
        ValueError: if the file does not match the expected format.
    """
    path = Path(path)
    lines = [
        ln.rstrip("\n").rstrip("\r")
        for ln in path.read_text(encoding="utf-8").splitlines()
        if ln.strip()
    ]

    if len(lines) != 42:
        raise ValueError(
            f"{path.name} must contain exactly 42 non-empty lines "
            f"(1 attack-string header + 41 column definitions). "
            f"Found {len(lines)}."
        )

    header = lines[0]
    if "," not in header or ":" in header:
        raise ValueError(
            f"Line 1 of {path.name} is not a valid attack-string header: "
            f"{header!r}"
        )

    column_lines = lines[1:]
    if len(column_lines) != 41:
        raise ValueError(
            f"Expected 41 column definitions in {path.name}, "
            f"found {len(column_lines)}."
        )

    feature_names: list[str] = []
    for ln in column_lines:
        if ":" not in ln:
            raise ValueError(
                f"Malformed column line in {path.name}: {ln!r}. "
                "Expected format '<name>: <type>.'"
            )
        name = ln.split(":", 1)[0].strip()
        if not name:
            raise ValueError(f"Empty column name in line: {ln!r}")
        feature_names.append(name)

    # The label column is the 42nd CSV column and is not present in the
    # manifest. Append it manually so downstream code sees the full schema.
    feature_names.append("label")
    return feature_names


def parse_attack_family_map(path: str | Path) -> dict[str, str]:
    """Parse training_attack_types.txt into a raw-label -> family mapping.

    File format: one '<attack_string> <family>' pair per line. Whitespace
    separated. Family strings are one of: normal, dos, probe, r2l, u2r.

    Returns:
        Dict mapping each attack string to its canonical family.
    """
    path = Path(path)
    mapping: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) != 2:
            raise ValueError(f"Malformed line in {path.name}: {raw!r}")
        attack, family = parts
        family = family.lower().strip().rstrip(".")
        if family not in CLASS_ORDER:
            raise ValueError(
                f"Family {family!r} for attack {attack!r} is not in {CLASS_ORDER}."
            )
        mapping[attack] = family
    return mapping


# ---------------------------------------------------------------------------
# Dataset loading and target mapping
# ---------------------------------------------------------------------------


def load_raw_dataset(csv_path: str | Path, columns: list[str]) -> pd.DataFrame:
    """Load the KDD Cup 1999 CSV with explicit column names.

    The CSV has no header row. Each row contains 42 comma-separated values:
    the 41 features followed by the raw attack label. The label carries a
    trailing period (e.g. 'normal.'), which is stripped here so that
    downstream mapping operates on the bare string.
    """
    df = pd.read_csv(
        csv_path,
        header=None,
        names=columns,
        dtype=str,
        skipinitialspace=True,
    )
    df["label"] = df["label"].str.strip().str.rstrip(".")
    return df


def map_targets(df: pd.DataFrame, family_map: dict[str, str]) -> pd.DataFrame:
    """Add a 'family' column by mapping raw labels through family_map.

    The file data/raw/training_attack_types.txt maps the 23 attack strings
    to four attack families. It deliberately excludes the 'normal' class,
    which is not an attack and maps to itself. That entry is injected here
    before applying the map.

    Raises if any raw label remains unmapped after the injection, which
    prevents silent NaN propagation into the training pipeline.
    """
    # Inject the self-map for 'normal' if it is not already present.
    effective_map = dict(family_map)
    effective_map.setdefault("normal", "normal")

    unmapped = set(df["label"].unique()) - set(effective_map.keys())
    if unmapped:
        raise ValueError(f"Unmapped attack labels: {sorted(unmapped)}")

    df = df.copy()
    df["family"] = df["label"].map(effective_map)
    df["family"] = pd.Categorical(
        df["family"], categories=list(CLASS_ORDER), ordered=True
    )
    return df


# ---------------------------------------------------------------------------
# Deduplication and feature pruning
# ---------------------------------------------------------------------------


def deduplicate(df: pd.DataFrame, feature_columns: Iterable[str]) -> pd.DataFrame:
    """Drop rows that are byte-identical across the feature columns.

    The label is excluded from the comparison, so two rows with identical
    features but different labels will collapse to the first occurrence.
    """
    feature_columns = list(feature_columns)
    return df.drop_duplicates(subset=feature_columns, keep="first").reset_index(drop=True)


def prune_correlated_features(
    df: pd.DataFrame,
    feature_columns: Iterable[str],
    threshold: float = CORRELATION_THRESHOLD,
) -> tuple[list[str], pd.DataFrame]:
    """Drop features whose absolute Pearson correlation exceeds threshold.

    Operates on numeric feature columns only. Categorical columns are
    passed through untouched and returned in the kept list.

    Returns:
        (kept_feature_columns, correlation_table)
        where correlation_table is the full absolute correlation matrix
        of the numeric features considered.
    """
    feature_columns = list(feature_columns)
    numeric_cols = [
        c for c in feature_columns
        if pd.api.types.is_numeric_dtype(df[c])
    ]
    categorical_cols = [c for c in feature_columns if c not in numeric_cols]

    if len(numeric_cols) < 2:
        return feature_columns, pd.DataFrame()

    corr_matrix = df[numeric_cols].corr(numeric_only=True).abs()

    # Upper triangle mask, excluding the diagonal.
    upper = corr_matrix.where(
        np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
    )

    to_drop: set[str] = set()
    for column in upper.columns:
        if column in to_drop:
            continue
        high_corr_partners = upper.index[upper[column] > threshold].tolist()
        for partner in high_corr_partners:
            # Keep the first encountered feature in original order, drop the later one.
            if partner not in to_drop and partner != column:
                to_drop.add(partner)

    kept = [c for c in feature_columns if c not in to_drop]
    return kept, corr_matrix


# ---------------------------------------------------------------------------
# Skew transforms
# ---------------------------------------------------------------------------


def apply_log_transform(
    df: pd.DataFrame,
    columns: Iterable[str] = LOG_TRANSFORM_COLUMNS,
) -> pd.DataFrame:
    """Apply log(1+x) to the listed columns, after coercing to float.

    Uses np.log1p, which is numerically stable for very small x. The
    transformation is monotone and preserves ordering, so it does not
    distort tree-based splits; it compresses the dynamic range of skewed
    continuous features, which stabilizes distance- and gradient-based
    models such as TabNet.
    """
    df = df.copy()
    for col in columns:
        if col not in df.columns:
            raise KeyError(f"Log-transform column {col!r} not present in DataFrame.")
        df[col] = np.log1p(df[col].astype(np.float64))
    return df


# ---------------------------------------------------------------------------
# Type casting
# ---------------------------------------------------------------------------


def cast_feature_dtypes(
    df: pd.DataFrame,
    feature_columns: Iterable[str],
) -> pd.DataFrame:
    """Cast categorical columns to string and everything else to float64.

    Categorical columns are the union of FREQUENCY_ENCODE_COLUMNS and
    ONEHOT_ENCODE_COLUMNS defined above. All other feature columns are
    cast to float64 for downstream numeric operations.
    """
    df = df.copy()
    categorical = set(FREQUENCY_ENCODE_COLUMNS) | set(ONEHOT_ENCODE_COLUMNS)
    for col in feature_columns:
        if col in categorical:
            df[col] = df[col].astype(str)
        else:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype(np.float64)
    return df


# ---------------------------------------------------------------------------
# Split
# ---------------------------------------------------------------------------


def stratified_split(
    df: pd.DataFrame,
    test_size: float = TEST_SIZE,
    random_state: int = RANDOM_STATE,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Stratified 75/25 train/test split, performed exactly once.

    Stratification is on the 'family' column so that rare attack families
    appear in both partitions in proportion to their prevalence.
    """
    train_df, test_df = train_test_split(
        df,
        test_size=test_size,
        random_state=random_state,
        stratify=df["family"],
        shuffle=True,
    )
    return train_df.reset_index(drop=True), test_df.reset_index(drop=True)


# ---------------------------------------------------------------------------
# Split contract
# ---------------------------------------------------------------------------


def write_split_contract(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    feature_names: list[str],
    contract_path: str | Path,
) -> None:
    """Write a machine-readable split contract to disk.

    Contract contents include the split configuration, the exact class
    distribution in each partition, the frozen feature ordering, and a
    hash of the configuration. Notebooks 02 and 03 must consume this file
    rather than re-splitting.
    """
    contract = {
        "random_state": RANDOM_STATE,
        "test_size": TEST_SIZE,
        "stratified_on": "family",
        "n_train": int(len(train_df)),
        "n_test": int(len(test_df)),
        "class_distribution": {
            "train": train_df["family"].value_counts().sort_index().to_dict(),
            "test": test_df["family"].value_counts().sort_index().to_dict(),
        },
        "feature_names": feature_names,
        "n_features": len(feature_names),
        "class_order": list(CLASS_ORDER),
    }
    save_json(contract, contract_path)


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def run_data_prep(
    raw_csv: str | Path = PATHS.raw_csv,
    raw_names: str | Path = PATHS.raw_names,
    raw_attack_types: str | Path = PATHS.raw_attack_types,
    processed_dir: str | Path = PATHS.processed,
    correlation_threshold: float = CORRELATION_THRESHOLD,
) -> dict[str, Path]:
    """Execute the full Phase 2 data preparation pipeline end to end.

    Returns:
        Dict mapping artifact name to the path written.
    """
    processed_dir = Path(processed_dir)
    processed_dir.mkdir(parents=True, exist_ok=True)

    # 1. Parse manifests.
    columns = parse_column_manifest(raw_names)
    family_map = parse_attack_family_map(raw_attack_types)

    feature_columns = [c for c in columns if c != "label"]

    # 2. Load and map.
    df = load_raw_dataset(raw_csv, columns)
    df = map_targets(df, family_map)

    # 3. Deduplicate on the raw feature set before any transformation.
    df = deduplicate(df, feature_columns)

    # 4. Drop features that are constant across the dataset; they carry no signal.
    constant_cols = [c for c in feature_columns if df[c].nunique(dropna=False) <= 1]
    if constant_cols:
        df = df.drop(columns=constant_cols)
        feature_columns = [c for c in feature_columns if c not in constant_cols]

    # 5. Cast dtypes before correlation analysis.
    df = cast_feature_dtypes(df, feature_columns)

    # 6. Correlation pruning on numeric features only.
    kept_features, corr_matrix = prune_correlated_features(
        df, feature_columns, threshold=correlation_threshold
    )

    # 7. Log-transform skewed continuous features (only those that survived pruning).
    log_columns = [c for c in LOG_TRANSFORM_COLUMNS if c in kept_features]
    if log_columns:
        df = apply_log_transform(df, columns=log_columns)

    # 8. Reduce the frame to the kept features plus the family label.
    df = df[kept_features + ["family"]]

    # 9. Split once.
    train_df, test_df = stratified_split(df)

    # 10. Emit artifacts.
    feature_names = list(kept_features)
    artifacts: dict[str, Path] = {}

    artifacts["feature_names"] = processed_dir / "feature_names.json"
    save_json(feature_names, artifacts["feature_names"])

    artifacts["split_contract"] = processed_dir / "split_indices.json"
    write_split_contract(train_df, test_df, feature_names, artifacts["split_contract"])

    artifacts["class_order"] = processed_dir / "class_order.json"
    save_json(list(CLASS_ORDER), artifacts["class_order"])

    # Persist the pre-encoding frames. Encoding is applied in a separate
    # module so that each encoder can be fit on the training partition only.
    artifacts["train_preencoded"] = processed_dir / "train_preencoded.csv"
    train_df.to_csv(artifacts["train_preencoded"], index=False)

    artifacts["test_preencoded"] = processed_dir / "test_preencoded.csv"
    test_df.to_csv(artifacts["test_preencoded"], index=False)

    # Correlation matrix for the EDA notebook to render.
    if not corr_matrix.empty:
        artifacts["correlation_matrix"] = processed_dir / "correlation_matrix.csv"
        corr_matrix.to_csv(artifacts["correlation_matrix"])

    return artifacts