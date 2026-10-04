"""
scripts/feasibility_tabnet.py

One-shot TabNet timing test on the real processed data.

Purpose:
    Measure wall-clock time for a single TabNet training run under the
    expected hyperparameter regime, so that the Optuna trial budget for
    Phase 3 can be set based on actual hardware performance rather than
    estimates.

Not part of the production pipeline. Safe to delete after Phase 3
budget is decided.

Usage:
    python scripts/feasibility_tabnet.py
"""

from __future__ import annotations

import sys
import time
import warnings
from pathlib import Path

# Running a script inside scripts/ sets sys.path[0] to scripts/, not the
# repo root. Insert the repo root so `from src import ...` resolves.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import json

import numpy as np
import torch
from pytorch_tabnet.tab_model import TabNetClassifier
from sklearn.metrics import f1_score

from src.utils import PATHS, RANDOM_STATE, set_seed

warnings.filterwarnings("ignore", category=UserWarning, module="pytorch_tabnet")


def load_arrays() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Load the frozen Phase 2 arrays."""
    X_train = np.load(PATHS.processed / "X_train.npy")
    X_test = np.load(PATHS.processed / "X_test.npy")
    y_train_str = np.load(PATHS.processed / "y_train.npy", allow_pickle=False)
    y_test_str = np.load(PATHS.processed / "y_test.npy", allow_pickle=False)
    return X_train, y_train_str, X_test, y_test_str


def encode_labels(y: np.ndarray, class_order: list[str]) -> np.ndarray:
    """Map string labels to integer indices using class_order."""
    mapping = {name: i for i, name in enumerate(class_order)}
    return np.array([mapping[v] for v in y], dtype=np.int64)


def main() -> None:
    set_seed(RANDOM_STATE)

    print("=" * 68)
    print("TabNet Feasibility Test")
    print("=" * 68)

    class_order = json.load(open(PATHS.processed / "class_order.json"))
    X_train, y_train_str, X_test, y_test_str = load_arrays()
    y_train = encode_labels(y_train_str, class_order)
    y_test = encode_labels(y_test_str, class_order)

    print(f"X_train shape   : {X_train.shape}")
    print(f"X_test shape    : {X_test.shape}")
    print(f"y_train classes : {sorted(set(y_train.tolist()))}")
    print(f"Class order     : {class_order}")
    print()

    hyperparams = {
        "n_d": 16,
        "n_a": 16,
        "n_steps": 5,
        "gamma": 1.5,
        "n_independent": 2,
        "n_shared": 2,
        "lambda_sparse": 1e-3,
        "optimizer_fn": torch.optim.Adam,
        "optimizer_params": {"lr": 2e-2},
        "mask_type": "sparsemax",
        "seed": RANDOM_STATE,
        "verbose": 1,
    }

    model = TabNetClassifier(**hyperparams)

    print("Training...")
    print("-" * 68)

    t_start = time.perf_counter()

    model.fit(
        X_train=X_train,
        y_train=y_train,
        eval_set=[(X_test, y_test)],
        eval_name=["val"],
        eval_metric=["accuracy"],
        max_epochs=30,
        patience=10,
        batch_size=1024,
        virtual_batch_size=128,
        num_workers=0,
        drop_last=False,
    )

    t_total = time.perf_counter() - t_start

    # model.history is populated by the automatic History callback.
    n_epochs = len(model.history["loss"])
    mean_epoch = t_total / n_epochs if n_epochs > 0 else 0.0

    print("-" * 68)
    print(f"Total training time : {t_total:.2f} seconds")
    print(f"Epochs completed    : {n_epochs}")
    print(f"Mean epoch time     : {mean_epoch:.2f} seconds")
    print()

    y_pred = model.predict(X_test)
    macro_f1 = f1_score(y_test, y_pred, average="macro")
    print(f"Test Macro F1 (single run) : {macro_f1:.4f}")

    print()
    print("=" * 68)
    print("Feasibility Estimate")
    print("=" * 68)
    assumed_epochs = 25
    per_fold = mean_epoch * assumed_epochs

    for folds, trials in ((3, 15), (5, 15), (5, 30), (5, 50)):
        total_hours = (per_fold * folds * trials) / 3600
        print(
            f"  {trials:>3} trials x {folds}-fold x {assumed_epochs} epochs "
            f"= {total_hours:6.2f} hours"
        )
    print("=" * 68)


if __name__ == "__main__":
    main()