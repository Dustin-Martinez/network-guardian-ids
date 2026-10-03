"""
src/encoding.py

Feature encoding for Network Guardian IDS.

Encoders are fit strictly on the training partition to prevent test-set
information from leaking into the model input space.

Encoders produced:
    - FrequencyEncoder for 'service' (high-cardinality categorical)
    - OneHotEncoder for 'protocol_type' and 'flag' (low-cardinality)
    - StandardScaler for TabNet input (not applied to tree models)

Serialization follows the project's data/processed convention. Each
encoder is written to data/processed/encoder_<name>.pkl.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.utils import PATHS

# ---------------------------------------------------------------------------
# Column groupings (import-consistent with src/data_prep.py)
# ---------------------------------------------------------------------------

FREQUENCY_ENCODE_COLUMNS: tuple[str, ...] = ("service",)
ONEHOT_ENCODE_COLUMNS: tuple[str, ...] = ("protocol_type", "flag")


# ---------------------------------------------------------------------------
# Frequency encoder
# ---------------------------------------------------------------------------


class FrequencyEncoder:
    """Maps each category to its observed frequency in the fitting set.

    Unseen categories at transform time are assigned a frequency of zero.
    This is deliberate: the model has no evidence that an unseen category
    is common, so it should not be assigned an arbitrary nonzero value.
    """

    def __init__(self, column: str) -> None:
        self.column = column
        self.frequencies_: dict[str, float] | None = None
        self.default_: float = 0.0

    def fit(self, df: pd.DataFrame) -> "FrequencyEncoder":
        if self.column not in df.columns:
            raise KeyError(f"Column {self.column!r} not present in fitting frame.")
        counts = df[self.column].value_counts(normalize=True)
        self.frequencies_ = counts.to_dict()
        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.frequencies_ is None:
            raise RuntimeError("FrequencyEncoder must be fit before transform.")
        out = df.copy()
        out[self.column + "_freq"] = (
            out[self.column].map(self.frequencies_).fillna(self.default_).astype(np.float64)
        )
        out = out.drop(columns=[self.column])
        return out

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return self.fit(df).transform(df)


# ---------------------------------------------------------------------------
# One-hot encoder wrapper
# ---------------------------------------------------------------------------


class MultiColumnOneHotEncoder:
    """Wrapper around sklearn OneHotEncoder for multiple named columns.

    Output columns are named '<column>_<category>' to keep the feature
    ordering deterministic and inspectable in saved artifacts.
    """

    def __init__(self, columns: Iterable[str]) -> None:
        self.columns = list(columns)
        self.encoder_: OneHotEncoder | None = None
        self.output_columns_: list[str] | None = None

    def fit(self, df: pd.DataFrame) -> "MultiColumnOneHotEncoder":
        missing = [c for c in self.columns if c not in df.columns]
        if missing:
            raise KeyError(f"Columns not present in fitting frame: {missing}")

        self.encoder_ = OneHotEncoder(
            sparse_output=False,
            handle_unknown="ignore",
            dtype=np.float64,
        )
        self.encoder_.fit(df[self.columns])

        # Build the output column names in the same order sklearn produces.
        self.output_columns_ = []
        for col, categories in zip(self.columns, self.encoder_.categories_):
            for cat in categories:
                self.output_columns_.append(f"{col}_{cat}")
        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.encoder_ is None or self.output_columns_ is None:
            raise RuntimeError("MultiColumnOneHotEncoder must be fit before transform.")

        encoded = self.encoder_.transform(df[self.columns])
        encoded_df = pd.DataFrame(encoded, columns=self.output_columns_, index=df.index)

        out = df.drop(columns=self.columns).copy()
        out = pd.concat([out, encoded_df], axis=1)
        return out

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return self.fit(df).transform(df)


# ---------------------------------------------------------------------------
# Scaling
# ---------------------------------------------------------------------------


def fit_scaler_on_train(
    train_df: pd.DataFrame,
    feature_columns: Iterable[str],
) -> StandardScaler:
    """Fit StandardScaler on the training partition only.

    The caller is responsible for using the same scaler to transform both
    train and test partitions. Fitting on the combined set would leak test
    statistics into training.
    """
    scaler = StandardScaler()
    scaler.fit(train_df[list(feature_columns)].to_numpy(dtype=np.float64))
    return scaler


def apply_scaler(scaler: StandardScaler, df: pd.DataFrame) -> np.ndarray:
    """Return a standardized NumPy matrix for the columns seen at fit time."""
    return scaler.transform(df.to_numpy(dtype=np.float64))


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def fit_and_apply_encoders(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    frequency_columns: Iterable[str] = FREQUENCY_ENCODE_COLUMNS,
    onehot_columns: Iterable[str] = ONEHOT_ENCODE_COLUMNS,
    output_dir: str | Path = PATHS.processed,
) -> dict[str, object]:
    """Fit encoders on train, apply to both partitions, persist artifacts.

    Returns:
        Dictionary containing:
            train_encoded (DataFrame),
            test_encoded (DataFrame),
            frequency_encoder (FrequencyEncoder),
            onehot_encoder (MultiColumnOneHotEncoder),
            encoder_paths (dict of str -> Path),
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    train_encoded = train_df.copy()
    test_encoded = test_df.copy()

    frequency_encoders: dict[str, FrequencyEncoder] = {}
    for column in frequency_columns:
        encoder = FrequencyEncoder(column)
        encoder.fit(train_encoded)
        train_encoded = encoder.transform(train_encoded)
        test_encoded = encoder.transform(test_encoded)
        frequency_encoders[column] = encoder

    onehot_encoder = MultiColumnOneHotEncoder(onehot_columns)
    onehot_encoder.fit(train_encoded)
    train_encoded = onehot_encoder.transform(train_encoded)
    test_encoded = onehot_encoder.transform(test_encoded)

    encoder_paths: dict[str, Path] = {}
    for column, encoder in frequency_encoders.items():
        path = output_dir / f"encoder_{column}.pkl"
        joblib.dump(encoder, path)
        encoder_paths[f"frequency_{column}"] = path

    onehot_path = output_dir / "encoder_onehot_protocol_flag.pkl"
    joblib.dump(onehot_encoder, onehot_path)
    encoder_paths["onehot_protocol_flag"] = onehot_path

    return {
        "train_encoded": train_encoded,
        "test_encoded": test_encoded,
        "frequency_encoders": frequency_encoders,
        "onehot_encoder": onehot_encoder,
        "encoder_paths": encoder_paths,
    }


def fit_and_persist_scaler(
    train_encoded: pd.DataFrame,
    feature_columns: Iterable[str],
    output_dir: str | Path = PATHS.processed,
) -> tuple[StandardScaler, Path]:
    """Fit StandardScaler on the training partition and persist it.

    Returns the fitted scaler and the path it was written to.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    scaler = fit_scaler_on_train(train_encoded, feature_columns)
    path = output_dir / "scaler_tabnet.pkl"
    joblib.dump(scaler, path)
    return scaler, path