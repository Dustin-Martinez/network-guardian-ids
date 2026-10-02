# Project Structure & Directory Guidelines

```text
network-guardian-ids/
├── .venv/                         # Isolated Python virtual environment
├── data/
│   ├── raw/                       # Original raw CSV files and definition manifests
│   └── processed/                 # Cleaned, deduplicated, and mapped datasets
├── docs/                          # System documentation and architecture specifications
|   ├──contracts/                  # Governance, team agreements, and academic rubric mappings
|   ├──tasks/                      # Task delegation and milestone tracking (empty / reserved)
├── src/                           # Reusable production Python source code
│   ├── __init__.py
│   ├── data_prep.py               # Target mapping, deduplication, correlation pruning
│   ├── encoding.py                # Frequency encoding, One-Hot transformers, scaling
│   ├── models.py                  # Model instantiations, wrappers, Optuna search spaces
│   ├── evaluate.py                # Confusion matrices, Macro F1 calculations, SHAP routines
│   └── utils.py                   # Reproducibility seed locking & artifact export helpers
├── notebooks/                     # Sequential execution environment
│   ├── 01_EDA_and_Data_Prep.ipynb # Data discovery, transformation, and validation
│   ├── 02_Model_Training.ipynb    # K-Fold training loops, Optuna tuning, early stopping
│   └── 03_Evaluation_and_XAI.ipynb# Model comparison, error analysis, SHAP visualizer
├── models/                        # Serialized model binaries (.joblib / .pt)
├── outputs/                       # Rendered evaluation figures, confusion matrices, logs
├── .gitignore                     # Repository access exclusions
└── requirements.txt               # Locked environment dependencies
```

# Subsystem Responsibilities

**src/:** Contains pure, tested Python functions. Code must not be duplicated inside Jupyter notebooks; notebooks import directly from src/.

**notebooks/:** Serves as the execution and report presentation layer. Must run top-to-bottom sequentially without error.

**contracts/:** Documents compliance with course rubrics, team governance, and academic integrity policies[cite: 1, 2].

**tasks/:** Maintained for future work allocation and sprint tracking.

**models/ & outputs/:** Stores non-text output artifacts generated during notebook execution.