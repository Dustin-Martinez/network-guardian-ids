
"""Generate Phase 4 explainability figures from saved models."""

import json
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
from pytorch_tabnet.tab_model import TabNetClassifier

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / "models"
DATA = ROOT / "data" / "processed"
OUT = ROOT / "outputs" / "03_evaluation"

SEED = 42
SHAP_SAMPLE_SIZE = 1000
TABNET_SAMPLE_SIZE = 1000


def load_json(path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def normalize_shap_values(values, n_samples, n_features, n_classes):
    """Normalize SHAP's list/array formats to (samples, features, classes)."""
    if isinstance(values, list):
        return np.stack(values, axis=-1)

    values = np.asarray(values)

    if values.ndim == 3:
        if values.shape == (n_samples, n_features, n_classes):
            return values
        if values.shape == (n_classes, n_samples, n_features):
            return np.transpose(values, (1, 2, 0))

    raise ValueError(f"Unexpected SHAP value shape: {values.shape}")


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    feature_names = load_json(DATA / "feature_names.json")
    class_order = load_json(DATA / "class_order.json")
    X_test = np.load(DATA / "X_test.npy")
    y_test = np.load(DATA / "y_test.npy")

    if X_test.shape[1] != len(feature_names):
        raise ValueError("Feature count does not match feature_names.json.")

    if not np.isfinite(X_test).all():
        raise ValueError("X_test contains NaN or infinite values.")

    # Use a reproducible subset for global SHAP figures.
    rng = np.random.default_rng(SEED)
    sample_size = min(SHAP_SAMPLE_SIZE, len(X_test))
    sample_indices = np.sort(
        rng.choice(len(X_test), size=sample_size, replace=False)
    )
    X_sample = X_test[sample_indices]

    models = {
        "rf": joblib.load(MODELS / "rf_baseline.joblib"),
        "xgb": joblib.load(MODELS / "xgb_optuna.joblib"),
    }

    # Global SHAP summaries for RF and XGBoost.
    xgb_local_candidate = None

    for key, model in models.items():
        print(f"Computing SHAP values for {key.upper()}...")

        explainer = shap.TreeExplainer(model)
        raw_values = explainer.shap_values(X_sample)
        raw_classes = list(model.classes_)
        class_order = load_json(DATA / "class_order.json")

        # Map numeric model labels to their class names when applicable.
        if all(isinstance(c, (int, np.integer)) for c in raw_classes):
            classes = [class_order[int(c)] for c in raw_classes]
        else:
            classes = [str(c) for c in raw_classes]

        values = normalize_shap_values(
            raw_values,
            len(X_sample),
            X_sample.shape[1],
            len(classes),
        )

        # Explain each sample's predicted class for a global overview.
        predicted = model.predict(X_sample)

        if all(isinstance(c, (int, np.integer)) for c in raw_classes):
            predicted_names = [class_order[int(c)] for c in predicted]
        else:
            predicted_names = [str(c) for c in predicted]

        predicted_indices = np.array(
            [classes.index(label) for label in predicted_names]
        )
        rows = np.arange(len(X_sample))
        predicted_class_values = values[rows, :, predicted_indices]

        plt.figure()
        shap.summary_plot(
            predicted_class_values,
            X_sample,
            feature_names=feature_names,
            show=False,
            max_display=20,
        )
        plt.tight_layout()
        plt.savefig(
            OUT / f"shap_summary_{key}.png",
            dpi=200,
            bbox_inches="tight",
        )
        plt.close("all")

        if key == "xgb":
            xgb_local_candidate = (
                explainer,
                values,
                classes,
                model,
            )

    # Select a correctly predicted, high-confidence rare-class example
    # from existing Phase 3 outputs. Prefer U2R, then R2L if needed.
    predictions = pd.read_csv(OUT / "test_predictions.csv")
    confidences = pd.read_csv(OUT / "test_confidences.csv")

    if len(predictions) != len(y_test) or len(confidences) != len(y_test):
        raise ValueError("Phase 3 CSV row counts do not match X_test.")

    
    class_order = load_json(DATA / "class_order.json")

    def map_labels(values):
        mapped = []
        for value in values:
            text = str(value).strip()
            try:
                number = int(text)
                if str(number) == text and 0 <= number < len(class_order):
                    mapped.append(class_order[number])
                    continue
            except ValueError:
                pass
            mapped.append(text.lower())
        return np.asarray(mapped)

    true_labels = map_labels(predictions["y_true"].to_numpy())
    predicted_labels = map_labels(predictions["xgb_prediction"].to_numpy())

    rare_classes = ["u2r", "r2l"]
    chosen_row = None
    chosen_class = None

    for rare_class in rare_classes:
        column = f"xgb_confidence_{rare_class}"
        if column not in confidences.columns:
            raise ValueError(f"Missing confidence column: {column}")

        candidate_rows = np.flatnonzero(
            (true_labels == rare_class)
            & (predicted_labels == rare_class)
        )

        if len(candidate_rows):
            scores = confidences.iloc[candidate_rows][column].to_numpy()
            chosen_row = int(candidate_rows[np.argmax(scores)])
            chosen_class = rare_class
            break

    if chosen_row is None:
        raise RuntimeError(
            "No correctly predicted U2R or R2L example was found. "
            "Inspect test_predictions.csv before choosing a local example."
        )

    explainer, all_values, classes, model = xgb_local_candidate
    class_index = classes.index(chosen_class)

    # Recompute SHAP for the selected row to keep the waterfall exact.
    local_X = X_test[[chosen_row]]
    local_values = normalize_shap_values(
        explainer.shap_values(local_X),
        1,
        local_X.shape[1],
        len(classes),
    )[0, :, class_index]

    expected = np.asarray(explainer.expected_value)
    base_value = (
        float(expected[class_index])
        if expected.ndim
        else float(expected)
    )

    explanation = shap.Explanation(
        values=local_values,
        base_values=base_value,
        data=local_X[0],
        feature_names=feature_names,
    )

    plt.figure()
    shap.plots.waterfall(explanation, max_display=20, show=False)
    plt.tight_layout()
    plt.savefig(
        OUT / "shap_local_example.png",
        dpi=200,
        bbox_inches="tight",
    )
    plt.close("all")

    # Load the saved TabNet checkpoint and extract attention masks.
    print("Extracting TabNet attention masks...")
    tabnet_meta = load_json(MODELS / "tabnet_best.meta.json")
    tabnet = TabNetClassifier()
    tabnet.load_model(str(MODELS / "tabnet_best.zip"))

    tabnet_indices = np.sort(
        rng.choice(
            len(X_test),
            size=min(TABNET_SAMPLE_SIZE, len(X_test)),
            replace=False,
        )
    )
    X_tabnet = X_test[tabnet_indices].astype(np.float32)

    _, masks = tabnet.explain(X_tabnet)

    if not masks:
        raise RuntimeError("TabNet did not return attention masks.")

    # Average attention across examples and decision steps.
    importance = np.zeros(len(feature_names), dtype=float)
    total_steps = 0

    for step_mask in masks.values():
        importance += np.asarray(step_mask).mean(axis=0)
        total_steps += 1

    importance /= max(total_steps, 1)
    order = np.argsort(importance)[-20:]

    plt.figure(figsize=(10, 8))
    plt.barh(
        np.array(feature_names)[order],
        importance[order],
    )
    plt.xlabel("Mean attention-mask value")
    plt.title("TabNet Feature Attention (Mean Across Decision Steps)")
    plt.tight_layout()
    plt.savefig(
        OUT / "tabnet_attention_mask.png",
        dpi=200,
        bbox_inches="tight",
    )
    plt.close("all")

    print("Phase 4 figure generation finished.")
    print(f"Local example: row {chosen_row}, class={chosen_class}")
    print(f"TabNet architecture: {tabnet_meta['architecture']}")
    for filename in (
        "shap_summary_rf.png",
        "shap_summary_xgb.png",
        "shap_local_example.png",
        "tabnet_attention_mask.png",
    ):
        path = OUT / filename
        print(f"{filename}: {'OK' if path.is_file() else 'MISSING'}")


if __name__ == "__main__":
    main()
