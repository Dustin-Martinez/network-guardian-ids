"""
Phase 3 evaluation pipeline for Network Guardian IDS.

Evaluates the three already-trained models on the frozen Phase 2 test set.
This script DOES NOT train, tune, or modify any model.

Run from the repository root with the project's virtual environment active:
    python src/evaluate.py

Required inputs:
    data/processed/X_test.npy
    data/processed/y_test.npy
    data/processed/class_order.json
    data/processed/feature_names.json
    models/rf_baseline.joblib
    models/rf_baseline.meta.json
    models/xgb_optuna.joblib
    models/xgb_optuna.meta.json
    models/tabnet_best.zip
    models/tabnet_best.meta.json

Outputs are written to outputs/03_evaluation/.
"""

from __future__ import annotations

import json
import sys
import time
import warnings
from pathlib import Path
from typing import Any

import joblib
import matplotlib

# Headless-safe backend so the script works in PowerShell and CI.
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
)

# Support both `python src/evaluate.py` and `python -m src.evaluate`.
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.utils import PATHS, load_json, save_json  # noqa: E402


MODEL_CONFIGS = {
    "rf": {
        "display_name": "Random Forest",
        "model_path": PATHS.models / "rf_baseline.joblib",
        "meta_path": PATHS.models / "rf_baseline.meta.json",
        "kind": "joblib",
    },
    "xgb": {
        "display_name": "XGBoost",
        "model_path": PATHS.models / "xgb_optuna.joblib",
        "meta_path": PATHS.models / "xgb_optuna.meta.json",
        "kind": "joblib",
    },
    "tabnet": {
        "display_name": "TabNet",
        "model_path": PATHS.models / "tabnet_best.zip",
        "meta_path": PATHS.models / "tabnet_best.meta.json",
        "kind": "tabnet",
    },
}

EXPECTED_CLASS_ORDER = ["normal", "dos", "probe", "r2l", "u2r"]
RARE_ATTACK_CLASSES = ("u2r", "r2l")


def _require_file(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"Required Phase 3 input is missing: {path}")


def _load_model(model_key: str, config: dict[str, Any]) -> Any:
    """Load an existing model without fitting or changing it."""
    _require_file(config["model_path"])
    _require_file(config["meta_path"])

    if config["kind"] == "joblib":
        return joblib.load(config["model_path"])

    # Import lazily: RF/XGBoost loading should not depend on TabNet imports.
    try:
        from pytorch_tabnet.tab_model import TabNetClassifier
    except ImportError as exc:
        raise ImportError(
            "Cannot import pytorch_tabnet. Activate the project's .venv "
            "before running this script."
        ) from exc

    model = TabNetClassifier()
    model.load_model(str(config["model_path"]))
    return model


def _validate_metadata(
    model_key: str,
    config: dict[str, Any],
    class_order: list[str],
    feature_names: list[str],
    n_features: int,
) -> dict[str, Any]:
    meta = load_json(config["meta_path"])
    meta_classes = meta.get("class_order")
    meta_features = meta.get("feature_names")

    if meta_classes is not None and list(meta_classes) != class_order:
        raise ValueError(
            f"{config['meta_path']} class_order does not match "
            "data/processed/class_order.json."
        )
    if meta_features is not None and list(meta_features) != feature_names:
        raise ValueError(
            f"{config['meta_path']} feature_names does not match "
            "data/processed/feature_names.json."
        )
    if int(meta.get("n_features", n_features)) != n_features:
        raise ValueError(
            f"{config['meta_path']} declares {meta.get('n_features')} "
            f"features, but X_test has {n_features}."
        )
    if meta.get("model") not in (None, model_key, config["display_name"].lower().replace(" ", "_")):
        # Metadata model names are informative; don't silently ignore a mismatch.
        expected_aliases = {
            "rf": {"random_forest", "rf"},
            "xgb": {"xgboost", "xgb"},
            "tabnet": {"tabnet"},
        }[model_key]
        if meta.get("model") not in expected_aliases:
            raise ValueError(
                f"Unexpected model identifier {meta.get('model')!r} "
                f"in {config['meta_path']}."
            )
    return meta


def _numeric_predictions_to_labels(
    predictions: np.ndarray, class_order: list[str], model_name: str
) -> np.ndarray:
    predictions = np.asarray(predictions).reshape(-1)
    if predictions.dtype.kind in "iu":
        ids = predictions.astype(int)
        if np.any(ids < 0) or np.any(ids >= len(class_order)):
            raise ValueError(f"{model_name} predicted class IDs outside class_order.")
        return np.asarray([class_order[i] for i in ids], dtype=str)

    # Some estimator wrappers may return numeric-looking floats.
    try:
        numeric = predictions.astype(int)
        if np.all(predictions.astype(float) == numeric):
            if np.any(numeric < 0) or np.any(numeric >= len(class_order)):
                raise ValueError(f"{model_name} predicted class IDs outside class_order.")
            return np.asarray([class_order[i] for i in numeric], dtype=str)
    except (TypeError, ValueError):
        pass

    labels = predictions.astype(str)
    unknown = sorted(set(labels.tolist()) - set(class_order))
    if unknown:
        raise ValueError(f"{model_name} produced unknown class labels: {unknown}")
    return labels


def _get_probabilities(
    model: Any,
    X: np.ndarray,
    class_order: list[str],
    model_name: str,
) -> np.ndarray:
    """Return probability columns in canonical class_order.

    The current repository contract encodes classes as indices of class_order.
    For sklearn models, classes_ is checked explicitly before using columns.
    TabNet's predict_proba follows the encoded class indices used at training.
    """
    if not hasattr(model, "predict_proba"):
        raise TypeError(f"{model_name} does not expose predict_proba().")

    probabilities = np.asarray(model.predict_proba(X), dtype=float)
    expected_shape = (len(X), len(class_order))
    if probabilities.shape != expected_shape:
        raise ValueError(
            f"{model_name} predict_proba shape {probabilities.shape}; "
            f"expected {expected_shape}."
        )
    if not np.isfinite(probabilities).all():
        raise ValueError(f"{model_name} returned non-finite probabilities.")
    if np.any(probabilities < -1e-8) or np.any(probabilities > 1.0 + 1e-8):
        raise ValueError(f"{model_name} returned probabilities outside [0, 1].")
    if not np.allclose(probabilities.sum(axis=1), 1.0, atol=1e-4):
        raise ValueError(f"{model_name} probability rows do not sum to 1.")

    classes = getattr(model, "classes_", None)
    if classes is not None:
        classes = np.asarray(classes)
        expected_ids = np.arange(len(class_order))
        if classes.shape != expected_ids.shape or not np.array_equal(classes, expected_ids):
            raise ValueError(
                f"{model_name} classes_={classes.tolist()} does not match encoded "
                f"class IDs {expected_ids.tolist()}; probability columns cannot be "
                "safely aligned."
            )
    return probabilities


def _plot_confusion_matrix(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    class_order: list[str],
    title: str,
    destination: Path,
) -> np.ndarray:
    cm = confusion_matrix(y_true, y_pred, labels=class_order)
    fig, ax = plt.subplots(figsize=(8, 7))
    display = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_order)
    display.plot(ax=ax, cmap="Blues", values_format="d", colorbar=False)
    ax.set_title(title)
    ax.set_xlabel("Predicted label")
    ax.set_ylabel("True label")
    fig.tight_layout()
    fig.savefig(destination, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return cm


def _compute_error_counts(
    cm: np.ndarray, class_order: list[str]
) -> dict[str, dict[str, int]]:
    """For each class, count false negatives and false positives one-vs-rest."""
    total = int(cm.sum())
    result: dict[str, dict[str, int]] = {}
    for idx, label in enumerate(class_order):
        tp = int(cm[idx, idx])
        fn = int(cm[idx, :].sum() - tp)
        fp = int(cm[:, idx].sum() - tp)
        tn = int(total - tp - fn - fp)
        result[label] = {
            "true_positive": tp,
            "false_negative": fn,
            "false_positive": fp,
            "true_negative": tn,
            "support": int(cm[idx, :].sum()),
            "predicted_count": int(cm[:, idx].sum()),
        }
    return result


def main() -> None:
    output_dir = PATHS.outputs / "03_evaluation"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load the frozen test data and schema.
    for filename in (
        "X_test.npy",
        "y_test.npy",
        "class_order.json",
        "feature_names.json",
    ):
        _require_file(PATHS.processed / filename)

    X_test = np.load(PATHS.processed / "X_test.npy", allow_pickle=False)
    y_test = np.load(PATHS.processed / "y_test.npy", allow_pickle=False).astype(str)
    class_order = load_json(PATHS.processed / "class_order.json")
    feature_names = load_json(PATHS.processed / "feature_names.json")

    if list(class_order) != EXPECTED_CLASS_ORDER:
        raise ValueError(
            f"Frozen class order {class_order} differs from the required "
            f"canonical order {EXPECTED_CLASS_ORDER}."
        )
    if X_test.ndim != 2 or X_test.shape[1] != len(feature_names):
        raise ValueError(
            f"X_test shape {X_test.shape} does not match "
            f"{len(feature_names)} feature names."
        )
    if y_test.ndim != 1 or len(y_test) != len(X_test):
        raise ValueError("X_test and y_test row counts/shapes do not match.")
    unknown_true_labels = sorted(set(y_test.tolist()) - set(class_order))
    if unknown_true_labels:
        raise ValueError(f"Frozen test labels contain unknown classes: {unknown_true_labels}")
    if not np.isfinite(X_test).all():
        raise ValueError("X_test contains NaN or infinite feature values.")

    print("Frozen test data:", X_test.shape)
    print("Class order:", class_order)
    print("Output directory:", output_dir)

    all_metric_rows: list[dict[str, Any]] = []
    evaluation: dict[str, Any] = {
        "evaluation_type": "frozen_holdout_test",
        "test_samples": int(len(y_test)),
        "n_features": int(X_test.shape[1]),
        "class_order": class_order,
        "feature_names_file": "data/processed/feature_names.json",
        "test_inputs": {
            "X_test": "data/processed/X_test.npy",
            "y_test": "data/processed/y_test.npy",
        },
        "models": {},
        "notes": [
            "Models were loaded from existing artifacts; this script does not train or tune.",
            "Macro F1 is the primary aggregate metric because class support is imbalanced.",
            "Per-class false negatives represent missed examples of that class; "
            "for U2R/R2L these are particularly important missed-attack errors.",
            "Per-class false positives represent other classes incorrectly flagged as the class.",
            "Error counts are one-vs-rest counts derived from each confusion matrix.",
        ],
    }
    model_macro_f1: dict[str, float] = {}
    model_predictions: dict[str, np.ndarray] = {}
    model_probabilities: dict[str, np.ndarray] = {}
    model_confusion_matrices: dict[str, np.ndarray] = {}

    for model_key, config in MODEL_CONFIGS.items():
        print(f"\nEvaluating {config['display_name']}...")
        metadata = _validate_metadata(
            model_key, config, class_order, feature_names, X_test.shape[1]
        )
        model = _load_model(model_key, config)

        # Check feature count when the estimator exposes it.
        n_features_in = getattr(model, "n_features_in_", None)
        if n_features_in is not None and int(n_features_in) != X_test.shape[1]:
            raise ValueError(
                f"{config['display_name']} expects {n_features_in} features, "
                f"but X_test has {X_test.shape[1]}."
            )

        start = time.perf_counter()
        raw_predictions = model.predict(X_test)
        prediction_seconds = time.perf_counter() - start
        y_pred = _numeric_predictions_to_labels(
            raw_predictions, class_order, config["display_name"]
        )
        probabilities = _get_probabilities(
            model, X_test, class_order, config["display_name"]
        )

        if len(y_pred) != len(y_test):
            raise ValueError(f"{config['display_name']} prediction count does not match y_test.")

        macro_f1 = float(f1_score(
            y_test, y_pred, labels=class_order, average="macro", zero_division=0
        ))
        weighted_f1 = float(f1_score(
            y_test, y_pred, labels=class_order, average="weighted", zero_division=0
        ))
        accuracy = float(accuracy_score(y_test, y_pred))
        per_class_precision = precision_score(
            y_test, y_pred, labels=class_order, average=None, zero_division=0
        )
        per_class_recall = recall_score(
            y_test, y_pred, labels=class_order, average=None, zero_division=0
        )
        per_class_f1 = f1_score(
            y_test, y_pred, labels=class_order, average=None, zero_division=0
        )
        support = np.asarray([(y_test == label).sum() for label in class_order], dtype=int)

        cm_path = output_dir / f"confusion_matrix_{model_key}.png"
        cm = _plot_confusion_matrix(
            y_test,
            y_pred,
            class_order,
            f"{config['display_name']} — Frozen Test Set",
            cm_path,
        )
        error_counts = _compute_error_counts(cm, class_order)

        for idx, label in enumerate(class_order):
            all_metric_rows.append({
                "model": model_key,
                "class": label,
                "precision": float(per_class_precision[idx]),
                "recall": float(per_class_recall[idx]),
                "f1": float(per_class_f1[idx]),
                "support": int(support[idx]),
                "support_fraction": float(support[idx] / len(y_test)),
                "macro_f1": macro_f1,
                "weighted_f1": weighted_f1,
            })

        model_macro_f1[model_key] = macro_f1
        model_predictions[model_key] = y_pred
        model_probabilities[model_key] = probabilities
        model_confusion_matrices[model_key] = cm

        evaluation["models"][model_key] = {
            "display_name": config["display_name"],
            "model_file": str(config["model_path"].relative_to(PATHS.repo_root)),
            "metadata_file": str(config["meta_path"].relative_to(PATHS.repo_root)),
            "test_accuracy": accuracy,
            "test_macro_f1": macro_f1,
            "test_weighted_f1": weighted_f1,
            "test_per_class": {
                label: {
                    "precision": float(per_class_precision[idx]),
                    "recall": float(per_class_recall[idx]),
                    "f1": float(per_class_f1[idx]),
                    "support": int(support[idx]),
                }
                for idx, label in enumerate(class_order)
            },
            "confusion_matrix": cm.tolist(),
            "confusion_matrix_labels": class_order,
            "error_counts_one_vs_rest": error_counts,
            "false_negatives_u2r": error_counts["u2r"]["false_negative"],
            "false_negatives_r2l": error_counts["r2l"]["false_negative"],
            "false_positives_total_one_vs_rest": int(sum(
                item["false_positive"] for item in error_counts.values()
            )),
            "prediction_seconds": float(prediction_seconds),
            "prediction_seconds_per_sample": float(prediction_seconds / len(X_test)),
            "cv_mean_macro_f1_from_metadata": metadata.get("cv_mean_macro_f1"),
            "cv_std_macro_f1_from_metadata": metadata.get("cv_std_macro_f1"),
            "cv_folds_from_metadata": metadata.get("cv_folds"),
            "train_macro_f1_from_metadata": metadata.get("train_macro_f1"),
            "train_vs_cv_gap_from_metadata": (
                float(metadata["train_macro_f1"] - metadata["cv_mean_macro_f1"])
                if isinstance(metadata.get("train_macro_f1"), (int, float))
                and isinstance(metadata.get("cv_mean_macro_f1"), (int, float))
                else None
            ),
            "overfitting_gap_note": (
                "Not calculated because the metadata does not contain train_macro_f1."
                if metadata.get("train_macro_f1") is None
                else "train_macro_f1 minus cv_mean_macro_f1; inspect alongside held-out test performance."
            ),
        }

        print(
            f"  Test Macro F1={macro_f1:.6f}; "
            f"weighted F1={weighted_f1:.6f}; "
            f"prediction time={prediction_seconds:.3f}s"
        )
        print(
            "  U2R recall={:.6f} (FN={}); R2L recall={:.6f} (FN={})".format(
                float(per_class_recall[class_order.index("u2r")]),
                error_counts["u2r"]["false_negative"],
                float(per_class_recall[class_order.index("r2l")]),
                error_counts["r2l"]["false_negative"],
            )
        )

    # Standard per-class table. All metrics are already proportions in [0, 1].
    metrics_df = pd.DataFrame(all_metric_rows)
    metrics_path = output_dir / "per_class_metrics.csv"
    metrics_df.drop(columns=["support_fraction"]).to_csv(metrics_path, index=False)

    # Contract does not define "normalized"; this explicit interpretation keeps
    # the same metrics and adds class support as a fraction of the test set.
    normalized_path = output_dir / "per_class_metrics_normalized.csv"
    metrics_df.to_csv(normalized_path, index=False)

    # Precision-recall curves for U2R and R2L, one line per model.
    for target_class in RARE_ATTACK_CLASSES:
        class_idx = class_order.index(target_class)
        y_binary = (y_test == target_class).astype(int)
        fig, ax = plt.subplots(figsize=(8, 6))
        for model_key, config in MODEL_CONFIGS.items():
            precision, recall, _ = precision_recall_curve(
                y_binary, model_probabilities[model_key][:, class_idx]
            )
            ax.plot(
                recall,
                precision,
                linewidth=2,
                label=f"{config['display_name']} (AP not shown)",
            )
        ax.set_title(f"Precision–Recall Curve: {target_class.upper()}")
        ax.set_xlabel("Recall")
        ax.set_ylabel("Precision")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1.02)
        ax.grid(True, alpha=0.3)
        ax.legend(loc="best")
        fig.tight_layout()
        fig.savefig(output_dir / f"pr_curve_{target_class}.png", dpi=180, bbox_inches="tight")
        plt.close(fig)

    # Test Macro F1 comparison.
    fig, ax = plt.subplots(figsize=(8, 5))
    keys = list(MODEL_CONFIGS)
    labels = [MODEL_CONFIGS[key]["display_name"] for key in keys]
    values = [model_macro_f1[key] for key in keys]
    bars = ax.bar(labels, values)
    ax.set_title("Model Comparison — Test Macro F1")
    ax.set_ylabel("Macro F1")
    ax.set_ylim(0, min(1.0, max(values) + 0.12))
    ax.grid(axis="y", alpha=0.3)
    ax.bar_label(bars, fmt="%.4f", padding=3)
    fig.tight_layout()
    fig.savefig(output_dir / "model_comparison_visual.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    # The paper's overall class-distribution figure is specified to come from
    # split_indices.json. It is intentionally not generated here from y_test
    # alone, which would depict only the held-out test split.
    evaluation["metrics_csv"] = str(metrics_path.relative_to(PATHS.repo_root))
    evaluation["normalized_metrics_csv"] = str(normalized_path.relative_to(PATHS.repo_root))
    evaluation["macro_f1_comparison"] = model_macro_f1
    evaluation["outputs"] = [
        f"outputs/03_evaluation/confusion_matrix_{key}.png" for key in MODEL_CONFIGS
    ] + [
        "outputs/03_evaluation/per_class_metrics.csv",
        "outputs/03_evaluation/per_class_metrics_normalized.csv",
        "outputs/03_evaluation/pr_curve_u2r.png",
        "outputs/03_evaluation/pr_curve_r2l.png",
        "outputs/03_evaluation/model_comparison_visual.png",
        "outputs/03_evaluation/test_set_evaluation.json",
    ]

    json_path = output_dir / "test_set_evaluation.json"
    save_json(evaluation, json_path)

    print("\n=== Phase 3 evaluation complete ===")
    print("Metrics:", metrics_path)
    print("Normalized metrics:", normalized_path)
    print("Evaluation summary:", json_path)
    print("Figures saved to:", output_dir)
    print("\nReminder: this script does not calculate a train-vs-CV gap when train_macro_f1")
    print("is absent from a model's metadata. Do not infer that gap from test scores.")


if __name__ == "__main__":
    main()
