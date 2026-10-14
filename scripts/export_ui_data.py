"""
scripts/export_ui_data.py

Reads the trained models and the evaluation outputs and writes four
JSON files into client/public/data/. The frontend loads these files
as static assets. No live backend call is required for the dashboard
panels.

Regenerate this file's outputs whenever the following change:
    models/*.joblib, models/*.zip
    outputs/03_evaluation/test_predictions.csv
    data/processed/split_indices.json

Usage:
    python scripts/export_ui_data.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from src.utils import PATHS  # noqa: E402

CLASSES = ["normal", "dos", "probe", "r2l", "u2r"]
UI_DATA_DIR = PATHS.repo_root / "client" / "public" / "data"
UI_DATA_DIR.mkdir(parents=True, exist_ok=True)

MODEL_KEYS = ("rf", "xgb", "tabnet")


def _write(name: str, payload) -> Path:
    path = UI_DATA_DIR / name
    with path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
        fh.write("\n")
    print(f"  wrote {path.relative_to(PATHS.repo_root)}  ({path.stat().st_size:,} bytes)")
    return path


def export_class_distribution() -> None:
    print("[1/4] class_distribution.json")
    split = json.load(open(PATHS.processed / "split_indices.json", encoding="utf-8"))
    out = {
        "train": split["class_distribution"]["train"],
        "test": split["class_distribution"]["test"],
    }
    _write("class_distribution.json", out)


def _resolve_predictions(pred: pd.DataFrame) -> dict[str, pd.Series]:
    """Return a dict mapping model key -> predicted label Series.

    Handles the actual column layout used by Notebook 03:
        y_true, rf_prediction, xgb_prediction, tabnet_prediction

    Also handles a wide layout with prefix naming and a long layout with
    a 'model' column, in case the evaluation notebook changes.
    """
    # Preferred layout: <model>_prediction columns.
    suffix_map = {
        "rf": "rf_prediction",
        "xgb": "xgb_prediction",
        "tabnet": "tabnet_prediction",
    }
    if all(col in pred.columns for col in suffix_map.values()):
        return {key: pred[col] for key, col in suffix_map.items()}

    # Fallback 1: prefix naming (pred_rf, pred_xgb, pred_tabnet).
    prefix_map = {
        "rf": "pred_rf",
        "xgb": "pred_xgb",
        "tabnet": "pred_tabnet",
    }
    if any(col in pred.columns for col in prefix_map.values()):
        return {key: pred[col] for key, col in prefix_map.items() if col in pred.columns}

    # Fallback 2: long layout with a 'model' column.
    if "model" in pred.columns:
        pred_col = next(
            (c for c in ("y_pred", "prediction", "pred", "label_pred") if c in pred.columns),
            None,
        )
        if pred_col is None:
            raise ValueError(
                "test_predictions.csv has a 'model' column but no recognizable prediction column."
            )
        out: dict[str, pd.Series] = {}
        for key in MODEL_KEYS:
            aliases = {key}
            if key == "rf":
                aliases.update({"random_forest"})
            elif key == "xgb":
                aliases.update({"xgboost"})
            subset = pred[pred["model"].isin(aliases)]
            if len(subset):
                out[key] = subset[pred_col]
        return out

    raise ValueError(
        "Unrecognized test_predictions.csv layout. "
        f"Columns are: {list(pred.columns)}. Update _resolve_predictions()."
    )


def export_confusion_matrices() -> None:
    print("[2/4] confusion_matrices.json")
    pred_path = PATHS.outputs / "03_evaluation" / "test_predictions.csv"
    if not pred_path.is_file():
        raise FileNotFoundError(f"Missing {pred_path}. Run Notebook 03 first.")
    pred = pd.read_csv(pred_path)

    true_col = next(
        (c for c in ("y_true", "true", "label_true", "actual", "y_test") if c in pred.columns),
        None,
    )
    if true_col is None:
        raise ValueError(
            f"No ground-truth column found in test_predictions.csv. Columns: {list(pred.columns)}"
        )

    predictions = _resolve_predictions(pred)

    # Map the short keys from _resolve_predictions to the long names
    # the frontend expects (matching ModelName in client/src/types).
    KEY_MAP = {"rf": "random_forest", "xgb": "xgboost", "tabnet": "tabnet"}

    out = {}
    for key, series in predictions.items():
        y_true = pred.loc[series.index, true_col]
        cm = confusion_matrix(y_true, series, labels=CLASSES)
        out[KEY_MAP[key]] = cm.tolist()
        print(f"  {KEY_MAP[key]}: {int(cm.sum())} rows")

    _write("confusion_matrices.json", out)

def export_feature_importances() -> None:
    print("[3/4] features.json")
    names = json.load(open(PATHS.processed / "feature_names.json", encoding="utf-8"))
    out: dict[str, list[dict]] = {"random_forest": [], "xgboost": [], "tabnet": []}

    rf_path = PATHS.models / "rf_baseline.joblib"
    if rf_path.is_file():
        rf = joblib.load(rf_path)
        importances = rf.feature_importances_
        order = np.argsort(importances)[::-1][:8]
        out["random_forest"] = [
            {"name": names[i], "value": float(importances[i])} for i in order
        ]

    xgb_path = PATHS.models / "xgb_optuna.joblib"
    if xgb_path.is_file():
        xgb = joblib.load(xgb_path)
        importances = xgb.feature_importances_
        order = np.argsort(importances)[::-1][:8]
        out["xgboost"] = [
            {"name": names[i], "value": float(importances[i])} for i in order
        ]

    tabnet_path = PATHS.models / "tabnet_best.zip"
    if tabnet_path.is_file():
        try:
            from pytorch_tabnet.tab_model import TabNetClassifier

            model = TabNetClassifier()
            model.load_model(str(tabnet_path))
            X_test = np.load(PATHS.processed / "X_test.npy")[:512]
            result = model.explain(X_test)

            # pytorch-tabnet 4.1.0 explain() returns a 2-tuple:
            #   result[0] : ndarray, shape (n_rows, n_features)  -> aggregated
            #               importance per row, per feature
            #   result[1] : dict of per-step details
            #
            # We use result[0] directly. Average over the rows axis to get
            # one importance per feature. Handle 3D shapes as a fallback in
            # case a different pytorch-tabnet version returns per-step masks.
            if isinstance(result, tuple):
                masks = np.asarray(result[0])
            else:
                masks = np.asarray(result)

            n_features = len(names)
            if masks.ndim == 2:
                # (n_rows, n_features)
                importance = masks.mean(axis=0)
            elif masks.ndim == 3:
                # (n_rows, n_features, n_steps) or a permutation
                if masks.shape[1] == n_features:
                    importance = masks.mean(axis=(0, 2))
                elif masks.shape[0] == n_features:
                    importance = masks.mean(axis=(1, 2))
                elif masks.shape[2] == n_features:
                    importance = masks.mean(axis=(0, 1))
                else:
                    raise ValueError(f"Unexpected mask shape: {masks.shape}")
            else:
                raise ValueError(f"Unexpected mask ndim: {masks.ndim}")

            order = np.argsort(importance)[::-1][:8]
            out["tabnet"] = [
                {"name": names[i], "value": float(importance[i])} for i in order
            ]
        except Exception as exc:
            print(f"  TabNet importance extraction skipped: {exc}")

    _write("features.json", out)


def export_evaluation() -> None:
    print("[4/4] evaluation.json")
    src = PATHS.outputs / "03_evaluation" / "test_set_evaluation.json"
    if not src.is_file():
        raise FileNotFoundError(f"Missing {src}. Run Notebook 03 first.")
    payload = json.load(open(src, encoding="utf-8"))

    # Remap model keys from the short names used by test_set_evaluation.json
    # to the long names the frontend expects (matching ModelName in
    # client/src/types). Otherwise ModelsView and the panel lookups fail.
    KEY_MAP = {"rf": "random_forest", "xgb": "xgboost", "tabnet": "tabnet"}
    if "models" in payload:
        payload["models"] = {
            KEY_MAP.get(k, k): v for k, v in payload["models"].items()
        }

    _write("evaluation.json", payload)


def main() -> int:
    print("Exporting UI data from real artifacts...")
    print()
    export_class_distribution()
    export_confusion_matrices()
    export_feature_importances()
    export_evaluation()
    print()
    print("Done. Files are in client/public/data/.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())