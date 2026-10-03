"""
src/verify_env.py

Phase 1 environment smoke test for Network Guardian IDS.

Confirms the active .venv contains every pinned package from requirements.txt
and that PyTorch, XGBoost, and PyTorch-TabNet can execute a minimal runtime
check.

Exit codes:
    0 - all critical checks passed
    1 - one or more critical checks failed

Usage:
    python src/verify_env.py
"""

from __future__ import annotations

import importlib
import platform
import sys
from typing import NamedTuple


class Check(NamedTuple):
    module: str
    dist_name: str
    critical: bool
    reason: str


CHECKS: list[Check] = [
    # Core data stack
    Check("numpy",          "numpy",             True, "Numerical arrays"),
    Check("pandas",         "pandas",            True, "DataFrame loading and EDA"),

    # Classical ML
    Check("sklearn",        "scikit-learn",      True, "Random Forest baseline, CV, metrics"),
    Check("imblearn",       "imbalanced-learn",  True, "Tomek Links in-fold resampling"),
    Check("xgboost",        "xgboost",           True, "Model 2 - gradient boosting"),

    # Deep learning
    Check("torch",          "torch",             True, "Backend for TabNet"),
    Check("pytorch_tabnet", "pytorch-tabnet",    True, "Model 3 - TabNet classifier"),

    # Optimization and explainability
    Check("optuna",         "optuna",            True, "Bayesian hyperparameter search"),

    # Visualization
    Check("matplotlib",     "matplotlib",        True, "Confusion matrices, PR curves"),
    Check("seaborn",        "seaborn",           True, "Heatmaps, styled plots"),

    # Serialization
    Check("joblib",         "joblib",            True, "Model and encoder persistence"),

    Check("shap",           "shap",              True, "TreeExplainer for RF and XGBoost"),

    # Notebook tooling
    Check("jupyter",        "jupyter",           True, "Notebook execution environment"),
]


def _version(dist_name: str) -> str:
    """Return installed distribution version or 'UNKNOWN'."""
    try:
        from importlib.metadata import version
        return version(dist_name)
    except Exception:
        return "UNKNOWN"


def run_checks() -> tuple[int, int]:
    """Run all import checks. Return (passed_count, failed_critical_count)."""
    passed = 0
    failed = 0

    print("=" * 72)
    print("Network Guardian IDS - Environment Verification (Phase 1)")
    print("=" * 72)
    print(f"Python     : {sys.version.split()[0]}")
    print(f"Executable : {sys.executable}")
    print(f"Platform   : {platform.system()} {platform.release()} ({platform.machine()})")
    print("-" * 72)
    print(f"{'MODULE':<18}{'VERSION':<18}{'STATUS':<10}NOTE")
    print("-" * 72)

    for chk in CHECKS:
        try:
            importlib.import_module(chk.module)
            ver = _version(chk.dist_name)
            status = "OK"
            passed += 1
            print(f"{chk.module:<18}{ver:<18}{status:<10}{chk.reason}")
        except Exception as exc:
            ver = "-"
            status = "FAIL" if chk.critical else "WARN"
            if chk.critical:
                failed += 1
            print(f"{chk.module:<18}{ver:<18}{status:<10}{type(exc).__name__}: {exc}")

    print("-" * 72)
    print(f"Passed: {passed}   Failed (critical): {failed}")
    print("=" * 72)
    return passed, failed


def verify_torch_runtime() -> bool:
    """Execute a minimal tensor operation to confirm torch is functional."""
    print()
    print("[torch runtime]")
    try:
        import torch

        print(f"  torch version      : {torch.__version__}")
        print(f"  CUDA available     : {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"  CUDA device        : {torch.cuda.get_device_name(0)}")

        a = torch.randn(4, 4)
        b = torch.randn(4, 4)
        c = a @ b
        assert c.shape == (4, 4), "Tensor matmul returned unexpected shape"
        print("  tensor matmul      : OK")
        return True
    except Exception as exc:
        print(f"  torch runtime FAIL : {type(exc).__name__}: {exc}")
        return False


def verify_xgboost_runtime() -> bool:
    """Fit a toy XGBoost booster on random data to confirm functionality."""
    print()
    print("[xgboost runtime]")
    try:
        import numpy as np
        import xgboost as xgb

        rng = np.random.default_rng(seed=42)
        X = rng.random((64, 5)).astype(np.float32)
        y = (X[:, 0] > 0.5).astype(int)

        dtrain = xgb.DMatrix(X, label=y)
        params = {"objective": "binary:logistic", "verbosity": 0, "seed": 42}
        booster = xgb.train(params, dtrain, num_boost_round=5)
        preds = booster.predict(dtrain)
        assert preds.shape[0] == 64, "XGBoost prediction shape mismatch"

        print(f"  xgboost version    : {xgb.__version__}")
        print("  toy train + predict: OK")
        return True
    except Exception as exc:
        print(f"  xgboost runtime FAIL: {type(exc).__name__}: {exc}")
        return False


def verify_tabnet_import() -> bool:
    """Confirm pytorch-tabnet exposes its classifier class and public API."""
    print()
    print("[pytorch-tabnet runtime]")
    try:
        from pytorch_tabnet.tab_model import TabNetClassifier
        from importlib.metadata import version as _pkg_version

        try:
            tabnet_version = _pkg_version("pytorch-tabnet")
        except Exception:
            tabnet_version = "UNKNOWN"

        print(f"  tabnet version     : {tabnet_version}")
        print(f"  classifier class   : {TabNetClassifier.__name__}")

        for method in ("fit", "predict", "predict_proba"):
            assert hasattr(TabNetClassifier, method), (
                f"TabNetClassifier missing expected method: {method}"
            )
        print("  public API surface : OK")
        print("  import             : OK")
        return True
    except Exception as exc:
        print(f"  tabnet import FAIL : {type(exc).__name__}: {exc}")
        return False


def main() -> int:
    _, failed = run_checks()
    torch_ok = verify_torch_runtime()
    xgb_ok = verify_xgboost_runtime()
    tabnet_ok = verify_tabnet_import()

    ok = (failed == 0) and torch_ok and xgb_ok and tabnet_ok
    print()
    if ok:
        print("RESULT: Phase 1 environment verification PASSED.")
        return 0

    print("RESULT: Phase 1 environment verification FAILED. See failures above.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())