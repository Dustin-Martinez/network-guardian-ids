"""One-request inference bridge. JSON stdin/stdout; diagnostics only on stderr."""

from __future__ import annotations

import contextlib
import json
import os
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))  # Needed to unpickle src.encoding wrappers.

import joblib
import numpy as np
import pandas as pd

CLASSES = ["normal", "dos", "probe", "r2l", "u2r"]
MODELS = {"random_forest": "rf_baseline.joblib", "xgboost": "xgb_optuna.joblib", "tabnet": "tabnet_best.zip"}
PROCESSED = Path(os.environ.get("IDS_PROCESSED_DIR", REPO / "data/processed"))
MODEL_DIR = Path(os.environ.get("IDS_MODEL_DIR", REPO / "models"))


def read_json(path: Path):
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def prepare_features(packet: dict, processed: Path = PROCESSED) -> pd.DataFrame:
    names = read_json(processed / "feature_names.json")
    if len(names) != 43 or len(set(names)) != 43:
        raise ValueError("Frozen feature_names.json must contain 43 unique names.")
    frame = pd.DataFrame([{key: value for key, value in packet.items() if key != "model"}])
    for name in ("duration", "src_bytes", "dst_bytes"):
        frame[name] = np.log1p(frame[name].astype(np.float64))
    frequency = joblib.load(processed / "encoder_service.pkl")
    onehot = joblib.load(processed / "encoder_onehot_protocol_flag.pkl")
    frame = onehot.transform(frequency.transform(frame))
    missing = sorted(set(names) - set(frame.columns))
    if missing:
        raise ValueError("Missing engineered features: " + ", ".join(missing))
    frame = frame.loc[:, names].astype(np.float64)
    if not np.isfinite(frame.to_numpy()).all():
        raise ValueError("Engineered features must be finite.")
    return frame


def check_metadata(meta: dict, names: list[str]) -> None:
    if meta.get("class_order") != CLASSES or meta.get("feature_names") != names:
        raise ValueError("Model metadata does not match frozen class and feature ordering.")
    if meta.get("n_features", 43) != 43:
        raise ValueError("Model metadata must declare 43 input features.")


def predict(packet: dict) -> dict:
    model_name = packet.get("model", "xgboost")
    if model_name not in MODELS:
        raise ValueError("Unknown model selection.")
    model_path = MODEL_DIR / MODELS[model_name]
    meta_path = MODEL_DIR / (model_path.stem + ".meta.json")
    if not model_path.is_file() or not meta_path.is_file():
        raise ValueError(f"Model unavailable: provide {model_path.name} and {meta_path.name} from the owner handoff.")
    if read_json(PROCESSED / "class_order.json") != CLASSES:
        raise ValueError("Frozen class ordering is invalid.")
    frame = prepare_features(packet)
    meta = read_json(meta_path)
    check_metadata(meta, list(frame.columns))
    if model_name == "tabnet":
        # The existing trainer uses raw engineered arrays, while the API contract
        # requires scaling. Do not silently serve a mismatched model. Kit must
        # confirm a scaler-trained artifact before enabling this contract path.
        if meta.get("preprocessing", {}).get("scaling") != "standard_scaler":
            raise ValueError("TabNet unavailable: training/inference scaling requires Kit confirmation; see Role 2 Phase 2 report.")
        from pytorch_tabnet.tab_model import TabNetClassifier

        model = TabNetClassifier(device_name="cpu", verbose=0)
        model.load_model(str(model_path))
        matrix = joblib.load(PROCESSED / "scaler_tabnet.pkl").transform(frame.to_numpy())
        probabilities = np.asarray(model.predict_proba(matrix))
        labels = CLASSES
    else:
        model = joblib.load(model_path)
        probabilities = np.asarray(model.predict_proba(frame))
        labels = []
        for value in model.classes_:
            if isinstance(value, (int, np.integer)) and 0 <= value < len(CLASSES):
                labels.append(CLASSES[int(value)])
            elif isinstance(value, str) and value in CLASSES:
                labels.append(value)
            else:
                raise ValueError("Model contains an unsupported class identifier.")
    if len(labels) != 5 or set(labels) != set(CLASSES):
        raise ValueError("Model must contain all five canonical classes.")
    if probabilities.shape != (1, 5) or not np.isfinite(probabilities).all():
        raise ValueError("Model returned invalid class probabilities.")
    if (probabilities < 0).any() or (probabilities > 1).any() or not np.isclose(probabilities.sum(), 1, atol=1e-5):
        raise ValueError("Model returned invalid probability values.")
    index = int(probabilities[0].argmax())
    label = labels[index]
    return {"prediction": label, "confidence": round(float(probabilities[0, index]) * 100, 2), "is_threat": label != "normal", "model": model_name}


def main() -> int:
    try:
        packet = json.loads(sys.stdin.read())
        if not isinstance(packet, dict):
            raise ValueError("Request must be a JSON object.")
        # Some model libraries print during loading. Keep stdout JSON-only.
        with contextlib.redirect_stdout(sys.stderr):
            result = predict(packet)
        print(json.dumps(result, allow_nan=False))
        return 0
    except Exception as exc:
        print(f"BRIDGE_ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
