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
- TabNet regularization relies on lambda_sparse, bounded n_steps, ghost
  batch normalization via virtual_batch_size, and validation-based early
  stopping. There is no dropout parameter in pytorch-tabnet 4.1.0.
- The TabNet final refit carves out an internal 10 percent validation
  split for early stopping, matching the protection used during CV.
- The ``per_class_recall_train`` field in each meta sidecar reports
  recall on the training pool, not cross-validated recall. Use the
  test-set evaluation in Notebook 03 for generalization metrics.
"""

from __future__ import annotations

import json
import warnings
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import optuna
import pandas as pd
import torch
import xgboost as xgb
from imblearn.under_sampling import TomekLinks
from pytorch_tabnet.tab_model import TabNetClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, precision_recall_fscore_support
from sklearn.model_selection import StratifiedKFold, train_test_split

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
TABNET_REFIT_VALIDATION_FRACTION: float = 0.10
TABNET_DEFAULT_BATCH_SIZE: int = 1024
TABNET_DEFAULT_VIRTUAL_BATCH_SIZE: int = 128

DEFAULT_MODEL: str = "xgboost"

CANONICAL_CLASS_ORDER: tuple[str, ...] = ("normal", "dos", "probe", "r2l", "u2r")

EXPECTED_TRAIN_ROWS: int = 109_188
EXPECTED_TEST_ROWS: int = 36_396
EXPECTED_FEATURE_COUNT: int = 43


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

    Raises:
        AssertionError: if the loaded arrays do not match the frozen
        shapes recorded in the split contract.
    """
    X_train = np.load(PATHS.processed / "X_train.npy")
    X_test = np.load(PATHS.processed / "X_test.npy")
    y_train = np.load(PATHS.processed / "y_train.npy", allow_pickle=False)
    y_test = np.load(PATHS.processed / "y_test.npy", allow_pickle=False)
    class_order = json.load(open(PATHS.processed / "class_order.json"))

    assert X_train.shape == (EXPECTED_TRAIN_ROWS, EXPECTED_FEATURE_COUNT), (
        f"Unexpected X_train shape: {X_train.shape}. "
        f"Expected ({EXPECTED_TRAIN_ROWS}, {EXPECTED_FEATURE_COUNT})."
    )
    assert X_test.shape == (EXPECTED_TEST_ROWS, EXPECTED_FEATURE_COUNT), (
        f"Unexpected X_test shape: {X_test.shape}. "
        f"Expected ({EXPECTED_TEST_ROWS}, {EXPECTED_FEATURE_COUNT})."
    )
    assert y_train.shape == (EXPECTED_TRAIN_ROWS,), (
        f"Unexpected y_train shape: {y_train.shape}."
    )
    assert y_test.shape == (EXPECTED_TEST_ROWS,), (
        f"Unexpected y_test shape: {y_test.shape}."
    )

    return X_train, y_train, X_test, y_test, class_order


def encode_labels(y_str: np.ndarray, class_order: list[str]) -> np.ndarray:
    """Map string labels to integer indices using class_order.

    The class order is frozen and must match the canonical order. Any
    re-ordering would silently corrupt the integer labels consumed by
    every model.

    Raises:
        ValueError: if class_order does not match the canonical order.
    """
    if list(class_order) != list(CANONICAL_CLASS_ORDER):
        raise ValueError(
            f"class_order mismatch. "
            f"Expected {list(CANONICAL_CLASS_ORDER)}, "
            f"received {list(class_order)}."
        )
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

    Uses ``n_jobs=1`` to avoid a joblib physical-core lookup warning on
    Windows and to guarantee deterministic row ordering across machines.

    Returns:
        (X_cleaned, y_cleaned)
    """
    tl = TomekLinks(sampling_strategy="auto", n_jobs=1)
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


def _safe_cv_std(study: optuna.Study) -> float:
    """Standard deviation of completed trial values, or 0.0 if fewer than 2."""
    values = [t.value for t in study.trials if t.value is not None]
    if len(values) < 2:
        return 0.0
    return float(np.std(values))


# =============================================================================
# Random Forest (Role 3 - Amber)
# =============================================================================
# Implementation contract: docs/contracts/role-3-rf-architecture-spec.md
#
# Ownership boundary (contract section 2):
#   - This section implements build_rf, rf_objective, train_rf, save_rf.
#   - Three private helpers support this section and are not part of the
#     shared interface: _suggest_rf_params, _compute_oob_macro_f1,
#     _collect_best_trial_validation.
#   - Shared helpers (clean_training_fold, compute_class_weights,
#     macro_f1, load_processed_arrays, encode_labels, _safe_cv_std) are
#     owned by Kit and are consumed, not modified.
#   - No XGBoost, TabNet, or bridge code is touched by this section.
# =============================================================================


def build_rf(params: dict) -> RandomForestClassifier:
    """Instantiate a RandomForestClassifier from a hyperparameter dict.

    Contract: docs/contracts/role-3-rf-architecture-spec.md section 3.1.

    Parameters supplied in ``params`` are filtered against the search-space
    keys defined in section 4. Any key outside that set is dropped, and the
    five fixed parameters in section 5 are always forced. This guarantees
    that a caller cannot silently override reproducibility or OOB settings.
    """
    allowed = {
        "n_estimators",
        "max_depth",
        "min_samples_split",
        "min_samples_leaf",
        "max_features",
        "criterion",
        "class_weight",
    }
    filtered = {k: v for k, v in params.items() if k in allowed}

    defaults = {
        "n_estimators": 100,
        "max_depth": None,
        "min_samples_split": 2,
        "min_samples_leaf": 1,
        "max_features": "sqrt",
        "criterion": "gini",
        "class_weight": "balanced",
    }
    merged = {**defaults, **filtered}

    return RandomForestClassifier(
        n_estimators=int(merged["n_estimators"]),
        max_depth=merged["max_depth"],
        min_samples_split=int(merged["min_samples_split"]),
        min_samples_leaf=int(merged["min_samples_leaf"]),
        max_features=str(merged["max_features"]),
        criterion=str(merged["criterion"]),
        class_weight=str(merged["class_weight"]),
        random_state=RANDOM_STATE,
        n_jobs=-1,
        oob_score=True,
        warm_start=False,
        bootstrap=True,
    )


def _suggest_rf_params(trial: optuna.Trial) -> dict:
    """Sample hyperparameters from the RF search space.

    Mirrors docs/contracts/role-3-rf-architecture-spec.md section 4 exactly.
    Do not widen or narrow these ranges without Kit's sign-off (section 15).
    """
    return {
        "n_estimators": trial.suggest_int("n_estimators", 100, 500, step=50),
        "max_depth": trial.suggest_categorical(
            "max_depth", [5, 10, 15, 20, 25, 30, None]
        ),
        "min_samples_split": trial.suggest_int("min_samples_split", 2, 20),
        "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 10),
        "max_features": trial.suggest_categorical(
            "max_features", ["sqrt", "log2"]
        ),
        "criterion": trial.suggest_categorical(
            "criterion", ["gini", "entropy"]
        ),
        "class_weight": trial.suggest_categorical(
            "class_weight", ["balanced", "balanced_subsample"]
        ),
    }


def rf_objective(
    trial: optuna.Trial,
    X_train: np.ndarray,
    y_train: np.ndarray,
    n_folds: int = N_FOLDS_RF,
    random_state: int = RANDOM_STATE,
) -> float:
    """Optuna objective for Random Forest.

    Contract: docs/contracts/role-3-rf-architecture-spec.md sections 3.2, 7.

    Runs StratifiedKFold cross-validation with in-fold Tomek Links boundary
    clearing and returns the mean Macro F1 across folds.

    In addition to the scalar score, this objective persists each fold's
    validation targets and predictions on the trial via ``set_user_attr``.
    That persistence lets ``train_rf`` reconstruct per-class recall without
    refitting any model after the study completes. The persisted arrays are
    small (a fold's worth of integer labels) and are read back only from the
    best trial.

    Anti-leakage rules enforced by this function (section 7):
        Rule 1: X_fold_val is never passed to clean_training_fold.
        Rule 2: X_test and y_test are never accepted as parameters.
    """
    params = _suggest_rf_params(trial)

    cv = StratifiedKFold(
        n_splits=n_folds, shuffle=True, random_state=random_state
    )

    fold_scores: list[float] = []
    for fold_idx, (train_idx, val_idx) in enumerate(cv.split(X_train, y_train)):
        X_fold_train = X_train[train_idx]
        y_fold_train = y_train[train_idx]
        X_fold_val = X_train[val_idx]
        y_fold_val = y_train[val_idx]

        # Rule 1: Tomek Links touches the training portion only.
        X_fold_train, y_fold_train = clean_training_fold(
            X_fold_train, y_fold_train
        )

        model = build_rf(params)
        # class_weight handles imbalance; do not also pass sample_weight.
        model.fit(X_fold_train, y_fold_train)

        y_pred = model.predict(X_fold_val)
        fold_score = macro_f1(y_fold_val, y_pred)
        fold_scores.append(float(fold_score))

        # Persist fold-level arrays for downstream meta construction. Stored
        # as plain lists so Optuna's JSON-backed storage round-trips cleanly.
        trial.set_user_attr(f"val_true_fold_{fold_idx}", y_fold_val.tolist())
        trial.set_user_attr(f"val_pred_fold_{fold_idx}", y_pred.tolist())

        trial.report(float(np.mean(fold_scores)), fold_idx)
        if trial.should_prune():
            raise optuna.TrialPruned()

    return float(np.mean(fold_scores))


def _collect_best_trial_validation(
    trial: optuna.Trial,
    n_folds: int,
    class_order: list[str],
) -> tuple[dict[str, float], list[float]]:
    """Reconstruct per-class recall and per-fold scores from a completed trial.

    Reads the arrays persisted by ``rf_objective`` via ``set_user_attr`` and
    aggregates them into a single confusion matrix across all folds.

    Returns:
        (per_class_recall, fold_scores)
        per_class_recall : {class_name: recall}
        fold_scores      : per-fold Macro F1, ordered by fold index

    Raises:
        RuntimeError: if the trial is missing persisted fold arrays. This
        indicates the trial was pruned before completion and is not the
        best trial. ``train_rf`` only calls this on ``study.best_trial``.
    """
    n_classes = len(class_order)
    confusion = np.zeros((n_classes, n_classes), dtype=np.int64)
    fold_scores: list[float] = []

    for fold_idx in range(n_folds):
        true_key = f"val_true_fold_{fold_idx}"
        pred_key = f"val_pred_fold_{fold_idx}"
        if true_key not in trial.user_attrs or pred_key not in trial.user_attrs:
            raise RuntimeError(
                f"Best trial {trial.number} is missing persisted validation "
                f"arrays for fold {fold_idx}. A completed trial must expose "
                f"all {n_folds} folds."
            )
        y_true_fold = np.asarray(trial.user_attrs[true_key], dtype=np.int64)
        y_pred_fold = np.asarray(trial.user_attrs[pred_key], dtype=np.int64)

        for t, p in zip(y_true_fold, y_pred_fold):
            confusion[int(t), int(p)] += 1

        fold_scores.append(macro_f1(y_true_fold, y_pred_fold))

    per_class_recall: dict[str, float] = {}
    for i, name in enumerate(class_order):
        row_sum = int(confusion[i].sum())
        per_class_recall[name] = (
            float(confusion[i, i] / row_sum) if row_sum > 0 else 0.0
        )
    return per_class_recall, fold_scores


def _compute_oob_macro_f1(
    model: RandomForestClassifier, y_full: np.ndarray
) -> float:
    """Compute Macro F1 from out-of-bag predictions.

    Contract: section 8 step 5. Rows that were never out-of-bag appear as
    NaN rows in ``oob_decision_function_`` and are excluded from the score.

    Raises:
        RuntimeError: if the model has no OOB decision function (oob_score
        was disabled) or if no rows are scorable.
    """
    if not hasattr(model, "oob_decision_function_") or \
            model.oob_decision_function_ is None:
        raise RuntimeError(
            "Model has no oob_decision_function_. build_rf must keep "
            "oob_score=True (contract section 5)."
        )

    oob_proba = np.asarray(model.oob_decision_function_)
    if oob_proba.ndim != 2 or oob_proba.shape[0] != len(y_full):
        raise RuntimeError(
            f"oob_decision_function_ shape {oob_proba.shape} does not match "
            f"y_full length {len(y_full)}."
        )

    valid_mask = ~np.isnan(oob_proba).any(axis=1)
    if not valid_mask.any():
        raise RuntimeError(
            "No scorable out-of-bag rows. Increase n_estimators or check "
            "that bootstrap=True."
        )

    oob_pred = np.argmax(oob_proba[valid_mask], axis=1)
    y_valid = y_full[valid_mask]
    return macro_f1(y_valid, oob_pred)


def train_rf(
    X_train: np.ndarray,
    y_train: np.ndarray,
    class_order: list[str],
    n_trials: int = N_TRIALS_RF,
    n_folds: int = N_FOLDS_RF,
    output_dir: Path = PATHS.outputs / "02_training",
) -> dict:
    """Full Optuna study, final refit, and persistence for Random Forest.

    Contract: docs/contracts/role-3-rf-architecture-spec.md sections 3.3,
    6, 7, 8, 9, 10.

    Order of operations:
        1. Create or load the Optuna study (section 6).
        2. Optimize with rf_objective over n_trials.
        3. Read per-class recall and fold scores from the best trial's
           persisted validation arrays (section 9).
        4. Refit the best parameters once on the full cleaned training pool.
        5. Extract OOB Macro F1 from the refitted model.
        6. Call save_rf with the fitted model and the section-9 meta dict.
        7. Write the trial log and per-fold metrics (section 10).

    Returns:
        dict with keys: model, study, best_params, cv_mean_macro_f1,
        cv_std_macro_f1, fold_scores, artifacts.
    """
    set_seed(RANDOM_STATE)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    study = optuna.create_study(
        study_name="ng_ids_random_forest",
        direction="maximize",
        sampler=optuna.samplers.TPESampler(seed=RANDOM_STATE),
        pruner=optuna.pruners.MedianPruner(
            n_startup_trials=5, n_warmup_steps=2
        ),
        storage=f"sqlite:///{output_dir / 'optuna_study_rf.db'}",
        load_if_exists=True,
    )
    study.optimize(
        lambda t: rf_objective(t, X_train, y_train, n_folds, RANDOM_STATE),
        n_trials=n_trials,
        show_progress_bar=False,
    )

    best_params = dict(study.best_params)
    best_trial = study.best_trial

    # Step 3: reconstruct per-class recall and per-fold scores from the
    # persisted validation arrays. No refitting happens here.
    per_class_recall_cv, fold_scores = _collect_best_trial_validation(
        trial=best_trial,
        n_folds=n_folds,
        class_order=class_order,
    )

    # Section 8 step 2: a single Tomek Links pass on the full training pool.
    X_full, y_full = clean_training_fold(X_train, y_train)

    # Section 8 steps 3 and 4: instantiate and fit once on the cleaned pool.
    final_model = build_rf(best_params)
    final_model.fit(X_full, y_full)

    # Section 8 step 5: OOB Macro F1.
    oob_macro_f1 = _compute_oob_macro_f1(final_model, y_full)

    feature_names = json.load(open(PATHS.processed / "feature_names.json"))

    meta = {
        "model": "random_forest",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "optuna_trials": int(n_trials),
        "cv_folds": int(n_folds),
        "best_trial_number": int(best_trial.number),
        "best_params": {
            "n_estimators": int(best_params["n_estimators"]),
            "max_depth": (
                None if best_params["max_depth"] is None
                else int(best_params["max_depth"])
            ),
            "min_samples_split": int(best_params["min_samples_split"]),
            "min_samples_leaf": int(best_params["min_samples_leaf"]),
            "max_features": str(best_params["max_features"]),
            "criterion": str(best_params["criterion"]),
            "class_weight": str(best_params["class_weight"]),
        },
        "cv_mean_macro_f1": float(study.best_value),
        "cv_std_macro_f1": float(np.std(fold_scores)),
        "oob_macro_f1": float(oob_macro_f1),
        "fold_scores": [float(s) for s in fold_scores],
        "per_class_recall_cv": per_class_recall_cv,
        "feature_names": feature_names,
        "class_order": list(class_order),
        "n_train": int(len(X_train)),
        "n_features": int(X_train.shape[1]),
        "random_state": int(RANDOM_STATE),
        "notes": (
            "Final model refit on the full cleaned training pool after one "
            "Tomek Links pass. per_class_recall_cv and fold_scores are "
            "reconstructed from the best trial's persisted validation arrays "
            "(set_user_attr in rf_objective); no models are refit for the "
            "meta sidecar. cv_std_macro_f1 is the standard deviation across "
            "the best trial's fold scores."
        ),
    }

    artifacts = save_rf(final_model, meta)

    trials_df = study.trials_dataframe()
    trial_csv = output_dir / "optuna_rf_trials.csv"
    trials_df.to_csv(trial_csv, index=False)
    artifacts["trial_csv"] = trial_csv

    fold_csv = output_dir / "rf_cv_scores.csv"
    pd.DataFrame(
        [{"fold": int(i), "macro_f1": float(s)} for i, s in enumerate(fold_scores)]
    ).to_csv(fold_csv, index=False)
    artifacts["fold_csv"] = fold_csv

    artifacts["study_db"] = output_dir / "optuna_study_rf.db"

    return {
        "model": final_model,
        "study": study,
        "best_params": best_params,
        "cv_mean_macro_f1": float(study.best_value),
        "cv_std_macro_f1": meta["cv_std_macro_f1"],
        "fold_scores": [float(s) for s in fold_scores],
        "artifacts": artifacts,
    }


def save_rf(
    model: RandomForestClassifier,
    meta: dict,
    model_dir: Path = PATHS.models,
) -> dict[str, Path]:
    """Persist the RF model and its meta sidecar.

    Contract: docs/contracts/role-3-rf-architecture-spec.md section 3.4.

    Writes:
        models/rf_baseline.joblib
        models/rf_baseline.meta.json

    Returns:
        {"model": Path, "meta": Path}
    """
    model_dir = Path(model_dir)
    model_dir.mkdir(parents=True, exist_ok=True)
    model_path = model_dir / "rf_baseline.joblib"
    meta_path = model_dir / "rf_baseline.meta.json"

    joblib.dump(model, model_path)
    with meta_path.open("w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2, sort_keys=True)
        fh.write("\n")

    return {"model": model_path, "meta": meta_path} 


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

    X_full, y_full = clean_training_fold(X_train, y_train)
    final_weights = sample_weight_from_classes(
        y_full, compute_class_weights(y_full)
    )

    best_n_estimators = best_params.get("n_estimators", XGB_MAX_ESTIMATORS)
    best_params["n_estimators"] = best_n_estimators
    final_model = build_xgb(best_params)
    final_model.fit(X_full, y_full, sample_weight=final_weights, verbose=False)

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
        "cv_std_macro_f1": _safe_cv_std(study),
        "fold_scores": [
            float(v) for v in study.best_trial.intermediate_values.values()
        ],
        "per_class_recall_train": {
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

    trials_df = study.trials_dataframe()
    trial_csv = output_dir / "optuna_xgb_trials.csv"
    trials_df.to_csv(trial_csv, index=False)
    artifacts["trial_csv"] = trial_csv

    fold_csv = output_dir / "xgb_cv_scores.csv"
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

    Regularization is controlled through lambda_sparse, bounded n_steps,
    and ghost batch normalization via virtual_batch_size. pytorch-tabnet
    4.1.0 does not expose a dropout constructor argument.
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


def _tabnet_refit(
    params: dict,
    X_full: np.ndarray,
    y_full: np.ndarray,
    random_state: int = RANDOM_STATE,
) -> TabNetClassifier:
    """Fit the final TabNet model on the full cleaned pool.

    Carves out an internal stratified validation split (10 percent) for
    early stopping during the refit. Class weights are computed from the
    full cleaned pool before the split, so the weight scale matches the
    CV folds.
    """
    weights = compute_class_weights(y_full)

    X_tr, X_val, y_tr, y_val = train_test_split(
        X_full,
        y_full,
        test_size=TABNET_REFIT_VALIDATION_FRACTION,
        random_state=random_state,
        stratify=y_full,
    )

    model = build_tabnet(params)
    model.fit(
        X_train=X_tr,
        y_train=y_tr,
        eval_set=[(X_val, y_val)],
        eval_name=["val"],
        eval_metric=["logloss"],
        weights=weights,
        max_epochs=TABNET_MAX_EPOCHS,
        patience=TABNET_PATIENCE,
        batch_size=params["batch_size"],
        virtual_batch_size=params["virtual_batch_size"],
        num_workers=0,
        drop_last=False,
    )
    return model


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

    X_full, y_full = clean_training_fold(X_train, y_train)

    final_model = _tabnet_refit(best_params, X_full, y_full, RANDOM_STATE)

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
        "cv_std_macro_f1": _safe_cv_std(study),
        "fold_scores": [
            float(v) for v in study.best_trial.intermediate_values.values()
        ],
        "per_class_recall_train": {
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
        "notes": (
            "Final refit on full cleaned training pool with an internal "
            "10 percent validation split for early stopping."
        ),
    }

    artifacts = save_tabnet(final_model, meta)

    trials_df = study.trials_dataframe()
    trial_csv = output_dir / "optuna_tabnet_trials.csv"
    trials_df.to_csv(trial_csv, index=False)
    artifacts["trial_csv"] = trial_csv

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
    set_seed(RANDOM_STATE)
    X_train, y_train_str, _, _, class_order = load_processed_arrays()
    y_train = encode_labels(y_train_str, class_order)

    results: dict[str, dict] = {}

    trainers = [
        ("random_forest", lambda: train_rf(
            X_train, y_train, class_order, n_trials=n_trials_rf, n_folds=N_FOLDS_RF
        )),
        ("xgboost", lambda: train_xgb(
            X_train, y_train, class_order, n_trials=n_trials_xgb, n_folds=N_FOLDS_XGB
        )),
        ("tabnet", lambda: train_tabnet(
            X_train, y_train, class_order, n_trials=n_trials_tabnet, n_folds=N_FOLDS_TABNET
        )),
    ]

    for name, trainer in trainers:
        try:
            results[name] = trainer()
        except NotImplementedError as exc:
            results[name] = {"error": f"not implemented: {exc}"}
        except Exception as exc:
            results[name] = {"error": f"{type(exc).__name__}: {exc}"}

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