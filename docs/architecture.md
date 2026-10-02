# System Architecture Specification

## Overview
Network Guardian uses a modular machine learning pipeline built to handle high-cardinality, heavily skewed, and highly imbalanced tabular network telemetry.

```text
Raw CSV Telemetry ──► Deduplication & Cleaning ──► Target Mapping (5 Classes)
                                                               │
                                                               ▼
        ┌──────────────────────────────────────────────────────┴──────────────────────────────────────────────────────┐
        │                                        Stratified 5-Fold Cross Validation                                   │
        └──────────────────────────────────────────────────────┬──────────────────────────────────────────────────────┘
                                                               │
                     ┌─────────────────────────────────────────┼─────────────────────────────────────────┐
                     ▼                                         ▼                                         ▼
            [Feature Engine]                          [Feature Engine]                          [Feature Engine]
         Log-Transform + Hybrid                   Log-Transform + Hybrid                    Log-Transform + Scale
                     │                                         │                                         │
                     ▼                                         ▼                                         ▼
           Random Forest Classifier                    XGBoost Classifier                       PyTorch TabNet Model
             (Tree Bagging Ensemble)                 (Gradient Tree Boosting)                  (Deep Learning + Attention)
                     │                                         │                                         │
                     └─────────────────────────────────────────┼─────────────────────────────────────────┘
                                                               │
                                                               ▼
                                                  Macro F1 Metric Evaluation
                                                               │
                                                               ▼
                                                  SHAP / Attention Explainability
```

# Data Pipeline Mechanics

**Deduplication:** Raw connection records undergo deduplication to eliminate memory inflation and artificial accuracy boosts.

**Feature Pruning:** Pearson correlation analysis removes features with >90% collinearity (e.g., dropping srv_serror_rate in favor of serror_rate).

**Logarithmic Scaling:** Continuous fields (duration, src_bytes, dst_bytes) undergo log(1 + x) transformation to smooth extreme outliers.

**Hybrid Categorical Encoding:**

- High-cardinality feature (service) is Frequency Encoded.
- Low-cardinality features (protocol_type, flag) are One-Hot Encoded[cite: 3].

**In-Fold Resampling:** Tomek Links boundary clearing is executed exclusively on the training folds during cross-validation to prevent data leakage into validation splits.

# Algorithm Selection Rationale

**Random Forest:** Baseline bagging model. Provides non-linear feature interactions and high stability against overfitting out of the box[cite: 1].

**XGBoost:** Primary gradient boosting model. Optimizes objective loss sequentially with built-in regularization and fast execution[cite: 1].

**PyTorch TabNet:** Deep learning architecture designed specifically for tabular data using sparse instance-wise selection attention[cite: 1].

# Hyperparameter Optimization & Stopping

**Optuna Framework:** Executes Bayesian optimization across 50 trials per model, targeting Macro F1-Score.

**Early Stopping:** Monitored against holdout validation splits across 20 iterations to freeze model weights prior to overfitting.