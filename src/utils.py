"""
src/utils.py

Reproducibility and artifact helpers for Network Guardian IDS.

Centralizes seed locking, project path constants, and JSON/NumPy
serialization so that all pipeline stages behave identically.

Import surface:
    from src.utils import (
        SEED, RANDOM_STATE, PATHS,
        set_seed, ensure_dirs,
        save_json, load_json,
        save_array, load_array,
        compute_file_sha256,
    )
"""

from __future__ import annotations

import hashlib
import json
import os
import random
from pathlib import Path
from typing import Any

import numpy as np

# ---------------------------------------------------------------------------
# Reproducibility constants
# ---------------------------------------------------------------------------

# Single source of truth for every random operation in the project.
# Do not redefine in other modules. Import from here.
SEED: int = 42
RANDOM_STATE: int = SEED  # alias for sklearn compatibility

# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------


class _Paths:
    """Resolved filesystem paths rooted at the repository top level.

    The repository root is inferred from this file's location:
    src/utils.py -> parent of src/.
    """

    def __init__(self) -> None:
        self.repo_root: Path = Path(__file__).resolve().parent.parent
        self.data: Path = self.repo_root / "data"
        self.raw: Path = self.data / "raw"
        self.processed: Path = self.data / "processed"
        self.models: Path = self.repo_root / "models"
        self.outputs: Path = self.repo_root / "outputs"
        self.notebooks: Path = self.repo_root / "notebooks"
        self.src: Path = self.repo_root / "src"

        # Named raw data files, per team agreement.
        self.raw_csv: Path = self.raw / "kddcup.csv"
        self.raw_names: Path = self.raw / "kddcup.names.txt"
        self.raw_attack_types: Path = self.raw / "training_attack_types.txt"

    def as_dict(self) -> dict[str, str]:
        return {
            "repo_root": str(self.repo_root),
            "data": str(self.data),
            "raw": str(self.raw),
            "processed": str(self.processed),
            "models": str(self.models),
            "outputs": str(self.outputs),
            "notebooks": str(self.notebooks),
            "src": str(self.src),
        }


PATHS = _Paths()


def ensure_dirs() -> None:
    """Create the writable directories the pipeline expects if missing."""
    for path in (PATHS.processed, PATHS.models, PATHS.outputs):
        path.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Seed locking
# ---------------------------------------------------------------------------


def set_seed(seed: int = SEED) -> None:
    """Lock random state across Python, NumPy, and (optionally) PyTorch.

    Torch is imported lazily so that scripts not requiring it do not pay
    the import cost. If torch is present, deterministic algorithms are
    enabled where feasible on CPU; CUDA determinism is left off because
    this project targets CPU training only.
    """
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)

    try:
        import torch

        torch.manual_seed(seed)
        torch.use_deterministic_algorithms(True, warn_only=True)
    except ImportError:
        pass


# ---------------------------------------------------------------------------
# JSON helpers
# ---------------------------------------------------------------------------


def save_json(obj: Any, path: str | Path, indent: int = 2) -> None:
    """Serialize obj to UTF-8 JSON with deterministic key ordering."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=indent, sort_keys=True, default=_json_default)
        fh.write("\n")


def load_json(path: str | Path) -> Any:
    """Load JSON from disk."""
    path = Path(path)
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _json_default(obj: Any) -> Any:
    """Fallback encoder for NumPy scalar and array types."""
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


# ---------------------------------------------------------------------------
# NumPy array helpers
# ---------------------------------------------------------------------------


def save_array(arr: np.ndarray, path: str | Path) -> None:
    """Persist a NumPy array to .npy format."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.save(path, arr)


def load_array(path: str | Path) -> np.ndarray:
    """Load a NumPy array from .npy format."""
    return np.load(Path(path))


# ---------------------------------------------------------------------------
# File hashing
# ---------------------------------------------------------------------------


def compute_file_sha256(path: str | Path, chunk_size: int = 1 << 20) -> str:
    """Return hex SHA256 of a file, streamed to avoid loading it into memory."""
    sha = hashlib.sha256()
    with Path(path).open("rb") as fh:
        while True:
            chunk = fh.read(chunk_size)
            if not chunk:
                break
            sha.update(chunk)
    return sha.hexdigest()