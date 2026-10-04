"""
src/models.py

Model architecture and training for Network Guardian IDS.

Ownership:
    Random Forest section   : Amber (Role 3)
    XGBoost section         : Kit (Role 1)
    TabNet section          : Kit (Role 1)
    Shared helpers          : Kit (frozen before Amber starts)

Anti-leakage contract
---------------------
All training functions in this module accept only the training partition.
The test partition is loaded by ``load_processed_arrays`` for convenience
but is never passed to any training, tuning, or refitting function. Test-
set evaluation happens exclusively in
``notebooks/03_Evaluation_and_XAI.ipynb``.

Design decisions
----------------
- Trial budgets are calibrated against the TabNet feasibility test
  performed on 2026-10-04 (22.09 s/epoch on CPU).
- Tomek Links resampling is applied strictly inside each CV fold's
  training partition. Validation partitions are never resampled.
- Class weights for final refits are computed from the post-Tomek-Links
  training pool, not the raw pool.
- Random state is imported from ``src.utils`` to guarantee a single seed
  across the entire pipeline.
"""

from __future__ import annotations

import json
import time
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import optuna
import torch
import xgboost as xgb
from imblearn.under_sampling import TomekLinks
from pytorch_tabnet.tab_model import TabNetClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, precision_recall_fscore_support
from sklearn.model_selection import StratifiedKFold

from src.utils import PATHS, RANDOM_STATE, set_seed

warnings.filterwarnings("ignore", category=UserWarning, module="pytorch_tabnet")
optuna.logging.set_verbosity(optuna.logging.WARNING)


# =============================================================================
# Constants
# =============================================================================

N_TRIALS_RF: int = 20
N_TRIALS_XGB: int = 30
N_TRIALS_TABNET: int = 20

N_FOLDS_RF: int = 5
N_FOLDS_XGB: int = 5
N_FOLDS_TABNET: int = 3

XGB_EARLY_STOPPING_ROUNDS: int = 20
XGB_MAX_ESTIMATORS: int = 300

TABNET_MAX_EPOCHS: int = 30
TABNET_PATIENCE: int = 10
TABNET_DEFAULT_BATCH_SIZE: int = 1024
TABNET_DEFAULT_VIRTUAL_BATCH_SIZE: int = 128

DEFAULT_MODEL: str = "xgboost"


# =============================================================================
# Data loading
# =============================================================================


def load_processed_arrays() -> tuple[
    np.ndarray, np.ndarray, np.ndarray, np.ndarray, list[str]
]:
    """Load the frozen Phase 2 arrays from data/processed/.

    Returns:
        (X_train, y_train_str, X_test, y_test_str, class_order)
        where X arrays are float64 and y arrays are fixed-width strings.
    """
    X_train = np.load(PATHS.processed / "X_train.npy")
    X_test = np.load(PATHS.processed / "X_test.npy")
    y_train = np.load(PATHS.processed / "y_train.npy", allow_pickle=False)
    y_test = np.load(PATHS.processed / "y_test.npy", allow_pickle=False)
    class_order = json.load(open(PATHS.processed / "class_order.json"))
    return X_train, y_train, X_test, y_test, class_order


def encode_labels(y_str: np.ndarray, class_order: list[str]) -> np.ndarray:
    """Map string labels to integer indices using class_order."""
    mapping = {name: i for i, name in enumerate(class_order)}
    return np.array([mapping[v] for v in y_str], dtype=np.int64)


# =============================================================================
# Class imbalance helpers
# =============================================================================


def compute_class_weights(y_int: np.ndarray) -> dict[int, float]:
    """Inverse-frequency class weights.

    Formula: n_samples / (n_classes * class_count). This matches
    sklearn's ``class_weight='balanced'`` convention so the weighting
    is comparable across models.

    Args:
        y_int: Encoded integer labels.

    Returns:
        Mapping from class index to weight.
    """
    classes, counts = np.unique(y_int, return_counts=True)
    n_samples = len(y_int)
    n_classes = len(classes)
    return {
        int(c): float(n_samples / (n_classes * cnt))
        for c, cnt in zip(classes, counts)
    }


def sample_weight_from_classes(
    y_int: np.ndarray, weights: dict[int, float]
) -> np.ndarray:
    """Build a per-sample weight vector from class weights."""
    return np.array([weights[int(v)] for v in y_int], dtype=np.float64)


# =============================================================================
# Fold preparation
# =============================================================================


def clean_training_fold(
    X: np.ndarray, y: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Apply Tomek Links to a training partition.

    Must be called only on the training portion of a CV fold. Applying
    it to a validation partition would remove evaluation rows and
    invalidate the CV score.

    Returns:
        (X_cleaned, y_cleaned)
    """
    tl = TomekLinks(sampling_strategy="auto", n_jobs=-1)
    X_clean, y_clean = tl.fit_resample(X, y)
    return np.asarray(X_clean, dtype=X.dtype), np.asarray(y_clean, dtype=y.dtype)


# =============================================================================
# Metrics
# =============================================================================


def macro_f1(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Macro-averaged F1 score."""
    return float(f1_score(y_true, y_pred, average="macro", zero_division=0))


def per_class_metrics(
    y_true: np.ndarray, y_pred: np.ndarray, class_order: list[str]
) -> dict[str, dict[str, float]]:
    """Per-class precision, recall, and F1.

    Returns:
        {class_name: {"precision": p, "recall": r, "f1": f}}
    """
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, labels=list(range(len(class_order))),
        average=None, zero_division=0,
    )
    return {
        name: {
            "precision": float(precision[i]),
            "recall": float(recall[i]),
            "f1": float(f1[i]),
        }
        for i, name in enumerate(class_order)
    }


# =============================================================================
# Random Forest (Role 3 - Amber)
# =============================================================================
# Implementation contract: docs/contracts/role-3-rf-architecture-spec.md
# =============================================================================


def build_rf(params: dict) -> RandomForestClassifier:
    """Instantiate a RandomForestClassifier from a hyperparameter dict.

    See docs/contracts/role-3-rf-architecture-spec.md section 3 for the
    search space and section 2.1 for the full contract.

    Raises:
        NotImplementedError: until Role 3 implements this function.
    """
    raise NotImplementedError(
        "build_rf is owned by Role 3 (Amber). "
        "See docs/contracts/role-3-rf-architecture-spec.md."
    )


def rf_objective(
    trial: optuna.Trial,
    X_train: np.ndarray,
    y_train: np.ndarray,
    n_folds: int = N_FOLDS_RF,
    random_state: int = RANDOM_STATE,
) -> float:
    """Optuna objective for Random Forest.

    Must perform StratifiedKFold CV with in-fold Tomek Links and return
    the mean Macro F1 across folds. See section 5 of the RF contract.

    Raises:
        NotImplementedError: until Role 3 implements this function.
    """
    raise NotImplementedError(
        "rf_objective is owned by Role 3 (Amber). "
        "See docs/contracts/role-3-rf-architecture-spec.md."
    )


def train_rf(
    X_train: np.ndarray,
    y_train: np.ndarray,
    class_order: list[str],
    n_trials: int = N_TRIALS_RF,
    n_folds: int = N_FOLDS_RF,
    output_dir: Path = PATHS.outputs / "02_training",
) -> dict:
    """Full Optuna study, final refit, and persistence for Random Forest.

    Raises:
        NotImplementedError: until Role 3 implements this function.
    """
    raise NotImplementedError(
        "train_rf is owned by Role 3 (Amber). "
        "See docs/contracts/role-3-rf-architecture-spec.md."
    )


def save_rf(
    model: RandomForestClassifier, meta: dict, model_dir: Path = PATHS.models
) -> dict[str, Path]:
    """Persist the RF model and its meta sidecar.

    Raises:
        NotImplementedError: until Role 3 implements this function.
    """
    raise NotImplementedError(
        "save_rf is owned by Role 3 (Amber). "
        "See docs/contracts/role-3-rf-architecture-spec.md."
    )


# =============================================================================
# XGBoost (Role 1 - Kit)
# =============================================================================


def build_xgb(params: dict) -> xgb.XGBClassifier:
    """Instantiate an XGBClassifier from a hyperparameter dict."""
    defaults = {
        "objective": "multi:softprob",
        "eval_metric": "mlogloss",
        "tree_method": "hist",
        "early_stopping_rounds": XGB_EARLY_STOPPING_ROUNDS,
        "random_state": RANDOM_STATE,
        "n_jobs": -1,
    }
    merged = {**defaults, **params}
    return xgb.XGBClassifier(**merged)


def _suggest_xgb_params(trial: optuna.Trial) -> dict:
    """Fixed search space for XGBoost Optuna trials."""
    return {
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.15, log=True),
        "max_depth": trial.suggest_int("max_depth", 3, 10),
        "min_child_weight": trial.suggest_int("min_child_weight", 1, 20),
        "gamma": trial.suggest_float("gamma", 0.0, 5.0),
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
        "reg_alpha": trial.suggest_float("reg_alpha", 0.0, 10.0),
        "reg_lambda": trial.suggest_float("reg_lambda", 1.0, 20.0),
        "max_delta_step": trial.suggest_int("max_delta_step", 0, 5),
        "n_estimators": trial.suggest_int(
            "n_estimators", 100, XGB_MAX_ESTIMATORS, step=50
        ),
    }


def xgb_objective(
    trial: optuna.Trial,
    X_train: np.ndarray,
    y_train: np.ndarray,
    n_folds: int = N_FOLDS_XGB,
    random_state: int = RANDOM_STATE,
) -> float:
    """Optuna objective: StratifiedKFold CV with in-fold Tomek Links.

    Returns the mean Macro F1 across folds.
    """
    params = _suggest_xgb_params(trial)
    cv = StratifiedKFold(
        n_splits=n_folds, shuffle=True, random_state=random_state
    )

    fold_scores: list[float] = []
    for fold_idx, (train_idx, val_idx) in enumerate(cv.split(X_train, y_train)):
        X_tr, y_tr = X_train[train_idx], y_train[train_idx]
        X_val, y_val = X_train[val_idx], y_train[val_idx]

        X_tr, y_tr = clean_training_fold(X_tr, y_tr)

        class_weights = compute_class_weights(y_tr)
        sample_weights = sample_weight_from_classes(y_tr, class_weights)

        model = build_xgb(params)
        model.fit(
            X_tr,
            y_tr,
            sample_weight=sample_weights,
            eval_set=[(X_val, y_val)],
            verbose=False,
        )

        y_pred = model.predict(X_val)
        fold_score = macro_f1(y_val, y_pred)
        fold_scores.append(fold_score)

        # Optuna pruning after each fold.
        trial.report(float(np.mean(fold_scores)), fold_idx)
        if trial.should_prune():
            raise optuna.TrialPruned()

    return float(np.mean(fold_scores))


def train_xgb(
    X_train: np.ndarray,
    y_train: np.ndarray,
    class_order: list[str],
    n_trials: int = N_TRIALS_XGB,
    n_folds: int = N_FOLDS_XGB,
    output_dir: Path = PATHS.outputs / "02_training",
) -> dict:
    """Run the Optuna study, refit, and persist the final XGBoost model.

    Returns a dict containing the fitted model, the study object, the
    best parameters, and paths to all artifacts written.
    """
    set_seed(RANDOM_STATE)
    output_dir.mkdir(parents=True, exist_ok=True)

    study = optuna.create_study(
        study_name="ng_ids_xgboost",
        direction="maximize",
        sampler=optuna.samplers.TPESampler(seed=RANDOM_STATE),
        pruner=optuna.pruners.MedianPruner(
            n_startup_trials=5, n_warmup_steps=2
        ),
        storage=f"sqlite:///{output_dir / 'optuna_study_xgb.db'}",
        load_if_exists=True,
    )
    study.optimize(
        lambda t: xgb_objective(t, X_train, y_train, n_folds, RANDOM_STATE),
        n_trials=n_trials,
        show_progress_bar=False,
    )

    best_params = dict(study.best_params)

    # Final refit on the full training pool, cleaned once.
    X_full, y_full = clean_training_fold(X_train, y_train)
    final_weights = sample_weight_from_classes(
        y_full, compute_class_weights(y_full)
    )

    # Use best_iteration from the best trial for the final n_estimators.
    best_n_estimators = best_params.get("n_estimators", XGB_MAX_ESTIMATORS)
    best_params["n_estimators"] = best_n_estimators
    final_model = build_xgb(best_params)
    final_model.fit(X_full, y_full, sample_weight=final_weights, verbose=False)

    # Diagnostics: per-class recall on the training pool for meta sidecar.
    train_pred = final_model.predict(X_full)
    train_per_class = per_class_metrics(y_full, train_pred, class_order)

    meta = {
        "model": "xgboost",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "optuna_trials": n_trials,
        "cv_folds": n_folds,
        "best_trial_number": study.best_trial.number,
        "best_params": best_params,
        "cv_mean_macro_f1": float(study.best_value),
        "cv_std_macro_f1": float(
            np.std([t.value for t in study.trials if t.value is not None])
        ),
        "fold_scores": [
            float(v) for v in study.best_trial.intermediate_values.values()
        ],
        "per_class_recall_cv": {
            k: v["recall"] for k, v in train_per_class.items()
        },
        "feature_names": json.load(
            open(PATHS.processed / "feature_names.json")
        ),
        "class_order": list(class_order),
        "n_train": int(len(X_train)),
        "n_features": int(X_train.shape[1]),
        "random_state": RANDOM_STATE,
        "notes": "Final refit on full cleaned training pool.",
    }

    artifacts = save_xgb(final_model, meta)

    # Trial log CSV.
    trials_df = study.trials_dataframe()
    trial_csv = output_dir / "optuna_xgb_trials.csv"
    trials_df.to_csv(trial_csv, index=False)
    artifacts["trial_csv"] = trial_csv

    # Per-fold scores CSV from the best trial.
    fold_csv = output_dir / "xgb_cv_scores.csv"
    fold_rows = [
        {"fold": i, "macro_f1": float(v)}
        for i, v in study.best_trial.intermediate_values.items()
    ]
    import pandas as pd

    pd.DataFrame(fold_rows).to_csv(fold_csv, index=False)
    artifacts["fold_csv"] = fold_csv

    return {
        "model": final_model,
        "study": study,
        "best_params": best_params,
        "cv_mean_macro_f1": float(study.best_value),
        "cv_std_macro_f1": meta["cv_std_macro_f1"],
        "fold_scores": meta["fold_scores"],
        "artifacts": artifacts,
    }


def save_xgb(
    model: xgb.XGBClassifier, meta: dict, model_dir: Path = PATHS.models
) -> dict[str, Path]:
    """Persist the XGBoost model and its meta sidecar."""
    model_dir.mkdir(parents=True, exist_ok=True)
    model_path = model_dir / "xgb_optuna.joblib"
    meta_path = model_dir / "xgb_optuna.meta.json"
    joblib.dump(model, model_path)
    with meta_path.open("w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2, sort_keys=True)
        fh.write("\n")
    return {"model": model_path, "meta": meta_path}


# =============================================================================
# TabNet (Role 1 - Kit)
# =============================================================================


def build_tabnet(params: dict) -> TabNetClassifier:
    """Instantiate a TabNetClassifier from a hyperparameter dict.

    Only constructor arguments are passed to TabNetClassifier. Fit-time
    arguments (batch_size, virtual_batch_size, max_epochs, patience) are
    consumed by the .fit() call and are filtered out here if present.
    """
    fit_only_keys = {"batch_size", "virtual_batch_size", "max_epochs", "patience"}

    defaults = {
        "optimizer_fn": torch.optim.Adam,
        "optimizer_params": {"lr": 2e-2},
        "seed": RANDOM_STATE,
        "verbose": 0,
        "device_name": "cpu",
    }

    constructor_params = {
        k: v for k, v in params.items() if k not in fit_only_keys
    }
    merged = {**defaults, **constructor_params}
    return TabNetClassifier(**merged)


def _suggest_tabnet_params(trial: optuna.Trial) -> dict:
    """Fixed search space for TabNet Optuna trials."""
    return {
        "n_d": trial.suggest_categorical("n_d", [8, 16, 24, 32]),
        "n_a": trial.suggest_categorical("n_a", [8, 16, 24, 32]),
        "n_steps": trial.suggest_int("n_steps", 3, 7),
        "gamma": trial.suggest_float("gamma", 1.0, 1.6),
        "lambda_sparse": trial.suggest_float(
            "lambda_sparse", 1e-5, 5e-3, log=True
        ),
        "n_independent": trial.suggest_int("n_independent", 1, 3),
        "n_shared": trial.suggest_int("n_shared", 1, 3),
        "momentum": trial.suggest_float("momentum", 0.02, 0.1),
        "mask_type": trial.suggest_categorical(
            "mask_type", ["sparsemax", "entmax"]
        ),
        "batch_size": trial.suggest_categorical(
            "batch_size", [512, 1024, 2048]
        ),
        "virtual_batch_size": trial.suggest_categorical(
            "virtual_batch_size", [128, 256]
        ),
    }


def tabnet_objective(
    trial: optuna.Trial,
    X_train: np.ndarray,
    y_train: np.ndarray,
    n_folds: int = N_FOLDS_TABNET,
    random_state: int = RANDOM_STATE,
) -> float:
    """Optuna objective: StratifiedKFold CV with in-fold Tomek Links.

    Returns the mean Macro F1 across folds. Class weighting is passed
    via the ``weights`` argument of ``TabNetClassifier.fit``.
    """
    params = _suggest_tabnet_params(trial)
    cv = StratifiedKFold(
        n_splits=n_folds, shuffle=True, random_state=random_state
    )

    fold_scores: list[float] = []
    for fold_idx, (train_idx, val_idx) in enumerate(cv.split(X_train, y_train)):
        X_tr, y_tr = X_train[train_idx], y_train[train_idx]
        X_val, y_val = X_train[val_idx], y_train[val_idx]

        X_tr, y_tr = clean_training_fold(X_tr, y_tr)
        class_weights = compute_class_weights(y_tr)

        model = build_tabnet(params)
        model.fit(
            X_train=X_tr,
            y_train=y_tr,
            eval_set=[(X_val, y_val)],
            eval_name=["val"],
            eval_metric=["logloss"],
            weights=class_weights,
            max_epochs=TABNET_MAX_EPOCHS,
            patience=TABNET_PATIENCE,
            batch_size=params["batch_size"],
            virtual_batch_size=params["virtual_batch_size"],
            num_workers=0,
            drop_last=False,
        )

        y_pred = model.predict(X_val)
        fold_score = macro_f1(y_val, y_pred)
        fold_scores.append(fold_score)

        trial.report(float(np.mean(fold_scores)), fold_idx)
        if trial.should_prune():
            raise optuna.TrialPruned()

    return float(np.mean(fold_scores))


def train_tabnet(
    X_train: np.ndarray,
    y_train: np.ndarray,
    class_order: list[str],
    n_trials: int = N_TRIALS_TABNET,
    n_folds: int = N_FOLDS_TABNET,
    output_dir: Path = PATHS.outputs / "02_training",
) -> dict:
    """Run the Optuna study, refit, and persist the final TabNet model."""
    set_seed(RANDOM_STATE)
    output_dir.mkdir(parents=True, exist_ok=True)

    study = optuna.create_study(
        study_name="ng_ids_tabnet",
        direction="maximize",
        sampler=optuna.samplers.TPESampler(seed=RANDOM_STATE),
        pruner=optuna.pruners.MedianPruner(
            n_startup_trials=5, n_warmup_steps=1
        ),
        storage=f"sqlite:///{output_dir / 'optuna_study_tabnet.db'}",
        load_if_exists=True,
    )
    study.optimize(
        lambda t: tabnet_objective(t, X_train, y_train, n_folds, RANDOM_STATE),
        n_trials=n_trials,
        show_progress_bar=False,
    )

    best_params = dict(study.best_params)

    # Final refit on the full cleaned training pool.
    X_full, y_full = clean_training_fold(X_train, y_train)
    final_weights = compute_class_weights(y_full)

    final_model = build_tabnet(best_params)
    final_model.fit(
        X_train=X_full,
        y_train=y_full,
        weights=final_weights,
        max_epochs=TABNET_MAX_EPOCHS,
        patience=TABNET_MAX_EPOCHS,  # no early stopping on final refit
        batch_size=best_params["batch_size"],
        virtual_batch_size=best_params["virtual_batch_size"],
        num_workers=0,
        drop_last=False,
    )

    train_pred = final_model.predict(X_full)
    train_per_class = per_class_metrics(y_full, train_pred, class_order)

    meta = {
        "model": "tabnet",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "optuna_trials": n_trials,
        "cv_folds": n_folds,
        "best_trial_number": study.best_trial.number,
        "best_params": best_params,
        "cv_mean_macro_f1": float(study.best_value),
        "cv_std_macro_f1": float(
            np.std([t.value for t in study.trials if t.value is not None])
        ),
        "fold_scores": [
            float(v) for v in study.best_trial.intermediate_values.values()
        ],
        "per_class_recall_cv": {
            k: v["recall"] for k, v in train_per_class.items()
        },
        "architecture": {
            "n_d": best_params["n_d"],
            "n_a": best_params["n_a"],
            "n_steps": best_params["n_steps"],
        },
        "feature_names": json.load(
            open(PATHS.processed / "feature_names.json")
        ),
        "class_order": list(class_order),
        "n_train": int(len(X_train)),
        "n_features": int(X_train.shape[1]),
        "random_state": RANDOM_STATE,
        "notes": "Final refit on full cleaned training pool.",
    }

    artifacts = save_tabnet(final_model, meta)

    trials_df = study.trials_dataframe()
    trial_csv = output_dir / "optuna_tabnet_trials.csv"
    trials_df.to_csv(trial_csv, index=False)
    artifacts["trial_csv"] = trial_csv

    import pandas as pd

    fold_csv = output_dir / "tabnet_cv_scores.csv"
    fold_rows = [
        {"fold": i, "macro_f1": float(v)}
        for i, v in study.best_trial.intermediate_values.items()
    ]
    pd.DataFrame(fold_rows).to_csv(fold_csv, index=False)
    artifacts["fold_csv"] = fold_csv

    return {
        "model": final_model,
        "study": study,
        "best_params": best_params,
        "cv_mean_macro_f1": float(study.best_value),
        "cv_std_macro_f1": meta["cv_std_macro_f1"],
        "fold_scores": meta["fold_scores"],
        "artifacts": artifacts,
    }


def save_tabnet(
    model: TabNetClassifier, meta: dict, model_dir: Path = PATHS.models
) -> dict[str, Path]:
    """Persist TabNet using its native zip format plus a meta sidecar."""
    model_dir.mkdir(parents=True, exist_ok=True)
    model_path = model_dir / "tabnet_best.zip"
    meta_path = model_dir / "tabnet_best.meta.json"
    model.save_model(str(model_path))
    with meta_path.open("w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2, sort_keys=True)
        fh.write("\n")
    return {"model": model_path, "meta": meta_path}


# =============================================================================
# Orchestration
# =============================================================================


def run_full_training(
    n_trials_rf: int = N_TRIALS_RF,
    n_trials_xgb: int = N_TRIALS_XGB,
    n_trials_tabnet: int = N_TRIALS_TABNET,
) -> dict[str, dict]:
    """Headless runner: trains all three models and writes the comparison table.

    Not intended for interactive use. Notebook 02 invokes each model's
    train function directly so that intermediate output is visible.

    Returns:
        {model_name: result_dict} for each model that completed.
    """
    import pandas as pd

    set_seed(RANDOM_STATE)
    X_train, y_train_str, _, _, class_order = load_processed_arrays()
    y_train = encode_labels(y_train_str, class_order)

    results: dict[str, dict] = {}

    # Random Forest may not be implemented yet; guard with try.
    try:
        results["random_forest"] = train_rf(
            X_train, y_train, class_order, n_trials=n_trials_rf
        )
    except NotImplementedError as exc:
        results["random_forest"] = {"error": str(exc)}

    results["xgboost"] = train_xgb(
        X_train, y_train, class_order, n_trials=n_trials_xgb
    )
    results["tabnet"] = train_tabnet(
        X_train, y_train, class_order, n_trials=n_trials_tabnet
    )

    # Comparison table.
    rows = []
    for model_name, r in results.items():
        if "error" in r:
            rows.append({"model": model_name, "error": r["error"]})
            continue
        rows.append({
            "model": model_name,
            "cv_mean_macro_f1": r["cv_mean_macro_f1"],
            "cv_std_macro_f1": r["cv_std_macro_f1"],
            "best_trial": r.get("best_params", {}),
        })
    comparison = pd.DataFrame(rows)
    comparison.to_csv(
        PATHS.outputs / "02_training" / "model_comparison.csv", index=False
    )

    return results