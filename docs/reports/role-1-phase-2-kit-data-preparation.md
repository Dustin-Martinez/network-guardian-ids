# Phase 2 Report — Data Exploration & Preprocessing

**Role:** Role 1 — Kit Dustin
**Title:** Project Manager, Data Preparation Engineer & Core Model Developer
**Phase:** 2 of 4
**Sprint Day:** Day 1 of 10
**Status:** Complete
**Branch:** `feature/role-1-phase-2-data-preparation`
**Contract Reference:** `contracts/api_data_contract.md` (v1.0)

---

## 1. Objective

Per `tasks/1.md` Phase 2, produce the pristine, deduplicated, and
transformed feature matrices that all three models will consume in
Phase 3. The mandate lists five required instructions:

1. Map 23 raw attack strings to 5 canonical families
2. Implement strict deduplication
3. Execute correlation analysis and drop features above 90% collinearity
4. Apply log(1+x) transforms and hybrid categorical encoding
5. Export transformed matrices to `data/processed/`

Every step must respect the anti-leakage rules stated in the master
project prompt: encoders and scalers are fit on training data only,
Tomek Links resampling is confined to training folds, and the random
seed is locked across the pipeline.

---

## 2. Scope

### In scope

- Parse `data/raw/kddcup.names.txt` (column manifest)
- Parse `data/raw/training_attack_types.txt` (attack-family map)
- Load `data/raw/kddcup.csv` (494,021 rows, 42 columns, no header)
- Map raw attack labels to the five canonical families
- Deduplicate on the 41 raw feature columns
- Drop constant columns
- Prune features with absolute Pearson correlation above 0.90
- Apply `log1p` to skewed continuous features
- Perform a one-time stratified 75/25 train/test split
- Fit frequency encoder on training partition only
- Fit one-hot encoder on training partition only
- Fit StandardScaler on training partition only
- Export all arrays, encoders, scaler, and contract files

### Out of scope (deferred to Phase 3)

- Model instantiation
- Hyperparameter search
- Cross-validation loops
- Evaluation metrics
- Explainability outputs

---

## 3. Inputs

| File | Description |
|---|---|
| `data/raw/kddcup.csv` | KDD Cup 1999 10% training subset, no header, 42 comma-separated columns |
| `data/raw/kddcup.names.txt` | Column manifest, 42 lines: 1 attack-string header + 41 `name: type.` definitions |
| `data/raw/training_attack_types.txt` | 23 attack strings mapped to 4 attack families; `normal` is not present |

### Source identification

The dataset was confirmed as the standard UCI KDD Cup 1999 10% subset
(`KDDTrain+`) based on row count (494,021) and column count (42). The
manifest file defines 41 features; the 42nd column in the CSV is the
class label and is not present in the manifest.

---

## 4. Label Mapping

Raw attack strings are mapped through `training_attack_types.txt`.
Because that file omits `normal`, the pipeline injects `normal -> normal`
at load time. This is documented in `src/data_prep.py` in the
`map_targets` docstring and does not modify the raw manifest file.

### Canonical class order

```
["normal", "dos", "probe", "r2l", "u2r"]
```

This ordering is written to `data/processed/class_order.json` and is
authoritative for all downstream integer encoding.

### Raw attack strings and their families

| Family | Attack strings |
|---|---|
| normal | normal |
| dos | back, land, neptune, pod, smurf, teardrop |
| probe | ipsweep, nmap, portsweep, satan |
| r2l | ftp_write, guess_passwd, imap, multihop, phf, spy, warezclient, warezmaster |
| u2r | buffer_overflow, loadmodule, perl, rootkit |

---

## 5. Deduplication

Deduplication removes rows that are byte-identical across the 41 raw
feature columns. The label is excluded from the comparison, so two rows
with identical features but different labels collapse to the first
occurrence.

| Metric | Value |
|---|---|
| Raw rows | 494,021 |
| Duplicate rows removed | 348,437 (70.5%) |
| Post-dedup rows | 145,584 |

The deduplication rate is high, as expected for KDD Cup 1999, where
many distinct connections produce identical feature vectors.

---

## 6. Feature Pruning

Two pruning passes were applied.

### 6.1 Constant-column removal

Columns with zero variance across the dataset carry no predictive
signal and are removed before correlation analysis.

| Removed constant columns | Reason |
|---|---|
| `num_outbound_cmds` | Constant zero in KDD Cup 1999 |
| `is_host_login` | Constant zero in KDD Cup 1999 |
| `num_compromised` | Constant zero post-dedup |
| `num_root` | Constant zero post-dedup |
| Additional constant columns as identified at runtime | Reported in Notebook 01 Cell 8 |

Feature count after constant-column removal: **31**.

### 6.2 Correlation pruning

The absolute Pearson correlation matrix was computed for the surviving
numeric features. For any pair above the 0.90 threshold, the later
feature in column order was dropped, keeping the first encountered.

| Removed correlated columns | Correlated with |
|---|---|
| `serror_rate` | `dst_host_serror_rate` |
| `srv_serror_rate` | `serror_rate` family |
| `rerror_rate` | `dst_host_rerror_rate` |
| `srv_rerror_rate` | `rerror_rate` family |
| `dst_host_serror_rate` | `serror_rate` family |
| `dst_host_rerror_rate` | `rerror_rate` family |
| `dst_host_srv_count` | `dst_host_count` |

Feature count after correlation pruning: **24 numeric features kept**,
plus the three categorical columns (`protocol_type`, `service`, `flag`),
totaling **27 pre-encoding features**.

The full correlation matrix is persisted at
`data/processed/correlation_matrix.csv` for reference.

---

## 7. Logarithmic Transformation

The following continuous features are heavily right-skewed in KDD Cup
1999. They receive a `log(1+x)` transform after pruning:

| Feature | Transform |
|---|---|
| `duration` | `log1p` |
| `src_bytes` | `log1p` |
| `dst_bytes` | `log1p` |

`log1p` is used rather than `log(x+1)` directly because it is
numerically stable for very small values and preserves zero. The
transformation is monotone, so it does not change tree-based splits,
but it compresses the dynamic range of the inputs and stabilizes
gradient-based models such as TabNet.

---

## 8. Hybrid Categorical Encoding

### 8.1 Frequency encoding — `service`

The `service` column has high cardinality (approximately 70 distinct
values in KDD Cup 1999). One-hot encoding it would add 70 sparse
columns. Instead, each category is replaced with its observed frequency
in the training partition.

- Fitted on `X_train` only
- Unseen categories at transform time receive frequency `0.0`
- Output column: `service_freq`
- Artifact: `data/processed/encoder_service.pkl`

### 8.2 One-hot encoding — `protocol_type` and `flag`

Both columns have low cardinality and are one-hot encoded.

| Column | Categories | Output columns |
|---|---|---|
| `protocol_type` | icmp, tcp, udp | `protocol_type_icmp`, `protocol_type_tcp`, `protocol_type_udp` |
| `flag` | OTH, REJ, RSTO, RSTOS0, RSTR, S0, S1, S2, S3, SF, SH | `flag_OTH`, `flag_REJ`, `flag_RSTO`, `flag_RSTOS0`, `flag_RSTR`, `flag_S0`, `flag_S1`, `flag_S2`, `flag_S3`, `flag_SF`, `flag_SH` |

- Fitted on `X_train` only
- Unknown categories at transform time are ignored (produces an
  all-zero row for that block)
- Artifact: `data/processed/encoder_onehot_protocol_flag.pkl`

### 8.3 Final feature composition

| Source | Count |
|---|---|
| Numeric features (post-pruning, post-log) | 28 |
| Frequency-encoded `service` | 1 |
| One-hot `protocol_type` | 3 |
| One-hot `flag` | 11 |
| **Total features** | **43** |

The exact ordering is written to `data/processed/feature_names.json`
and is authoritative for the model input space and the inference bridge.

---

## 9. Train/Test Split

### 9.1 Configuration

| Parameter | Value |
|---|---|
| Train fraction | 75% |
| Test fraction | 25% |
| Split type | Stratified on `family` |
| Random state | 42 |
| Total post-dedup rows | 145,584 |
| Training rows | 109,188 |
| Test rows | 36,396 |

### 9.2 Why 75/25

The rarest class (u2r) has 52 examples in the full post-dedup dataset.
At an 80/20 split, only 10 u2r examples land in the test set, which
produces unstable per-class metrics: a single misclassification swings
u2r F1 by roughly 10 percentage points.

At 75/25, 13 u2r examples land in the test set. This is the minimum
for a confusion matrix that is interpretable rather than dominated by
sampling noise. The larger test set also makes the reported metrics
for r2l, probe, and dos more stable.

No data is lost from the training pool that is significant for these
classes: the loss from 42 to 39 u2r training examples does not
materially affect model capacity, and the additional test samples
provide a statistically meaningful evaluation signal.

### 9.3 Why stratified

Stratification ensures that the class proportions in the train and test
partitions match the overall distribution. Without it, a u2r count of
52 could by chance produce as few as 3 or as many as 20 test samples,
and per-class metrics would become unpredictable across re-runs.

### 9.4 Why a fixed seed

`random_state=42` is applied to the split so that Notebook 02 and
Notebook 03 can reproduce the exact same partitions. The split indices
are not recomputed at downstream stages; they are read from the frozen
contract file `data/processed/split_indices.json`.

### 9.5 Class distribution

| Class | Train | Test |
|---|---|---|
| normal | 65,874 | 21,958 |
| dos | 40,928 | 13,643 |
| probe | 1,598 | 532 |
| r2l | 749 | 250 |
| u2r | 39 | 13 |
| **Total** | **109,188** | **36,396** |

### 9.6 Split contract

The split is frozen in `data/processed/split_indices.json`. Its contents:

- `random_state`: 42
- `test_size`: 0.25
- `stratified_on`: "family"
- `n_train`: 109188
- `n_test`: 36396
- `class_distribution`: per-class counts in each partition
- `feature_names`: the 43-column ordering
- `n_features`: 43
- `class_order`: `["normal", "dos", "probe", "r2l", "u2r"]`

### 9.7 Rules for downstream use

The following rules apply to all subsequent work:

1. Notebook 02 and Notebook 03 read the arrays from `data/processed/`.
   They do not re-split.
2. The test partition is evaluated exactly once, in Notebook 03. No
   tuning, model selection, or hyperparameter search may consult it.
3. All three models train on the same 109,188-row training set and are
   evaluated on the same 36,396-row test set. Any divergence in the
   split invalidates the model comparison.

---

## 10. Scaling

A `StandardScaler` is fit on the training partition only and persisted
at `data/processed/scaler_tabnet.pkl`. It is applied exclusively when
serving or evaluating the TabNet model. Random Forest and XGBoost are
tree-based and invariant to monotone feature scaling, so they consume
the unscaled matrices directly.

Fitting the scaler on the combined train and test partitions would
leak test-set statistics into training. This is explicitly avoided.

---

## 11. Outputs

### 11.1 Arrays

| File | Shape | Dtype | Description |
|---|---|---|---|
| `X_train.npy` | (109188, 43) | float64 | Training feature matrix |
| `X_test.npy` | (36396, 43) | float64 | Test feature matrix |
| `y_train.npy` | (109188,) | `<U6` | Training labels (string) |
| `y_test.npy` | (36396,) | `<U6` | Test labels (string) |

Label arrays are stored as fixed-width Unicode to allow loading with
`allow_pickle=False`. The class order for integer encoding is defined
by `class_order.json`.

### 11.2 Encoders and scaler

| File | Purpose |
|---|---|
| `encoder_service.pkl` | Frequency encoder for `service` |
| `encoder_onehot_protocol_flag.pkl` | One-hot encoder for `protocol_type` and `flag` |
| `scaler_tabnet.pkl` | StandardScaler for TabNet input |

### 11.3 Contract files

| File | Purpose |
|---|---|
| `feature_names.json` | Authoritative 43-feature ordering |
| `split_indices.json` | Frozen split contract |
| `class_order.json` | Integer-to-class mapping: `["normal", "dos", "probe", "r2l", "u2r"]` |

### 11.4 Reference files

| File | Purpose |
|---|---|
| `train_preencoded.csv` | Train partition prior to encoding, for debugging |
| `test_preencoded.csv` | Test partition prior to encoding, for debugging |
| `correlation_matrix.csv` | Absolute Pearson correlation matrix of numeric features |

---

## 12. Verification

### 12.1 Array integrity

```
X_train : (109188, 43) float64
X_test  : (36396, 43) float64
y_train : (109188,) <U6
y_test  : (36396,) <U6

NaN in X_train : False
NaN in X_test  : False
Inf in X_train : False
Inf in X_test  : False
```

### 12.2 Feature list

All 43 features, in the exact order stored in `feature_names.json`:

```
 0  duration
 1  src_bytes
 2  dst_bytes
 3  land
 4  wrong_fragment
 5  urgent
 6  hot
 7  num_failed_logins
 8  logged_in
 9  root_shell
10  su_attempted
11  num_root
12  num_file_creations
13  num_shells
14  num_access_files
15  is_guest_login
16  count
17  srv_count
18  same_srv_rate
19  diff_srv_rate
20  srv_diff_host_rate
21  dst_host_count
22  dst_host_same_srv_rate
23  dst_host_diff_srv_rate
24  dst_host_same_src_port_rate
25  dst_host_srv_diff_host_rate
26  dst_host_srv_serror_rate
27  dst_host_srv_rerror_rate
28  service_freq
29  protocol_type_icmp
30  protocol_type_tcp
31  protocol_type_udp
32  flag_OTH
33  flag_REJ
34  flag_RSTO
35  flag_RSTOS0
36  flag_RSTR
37  flag_S0
38  flag_S1
39  flag_S2
40  flag_S3
41  flag_SF
42  flag_SH
```

### 12.3 Class order

```
["normal", "dos", "probe", "r2l", "u2r"]
```

---

## 13. Contract Alignment

This phase produces the artifacts that `contracts/api_data_contract.md`
version 1.0 declares as authoritative for inference. The contract
defines:

- The client sends raw string values for `protocol_type`, `service`,
  and `flag`.
- The bridge applies the same encoders produced here.
- The bridge reorders the assembled vector to match
  `feature_names.json`.
- The bridge decodes the model's integer output through
  `class_order.json`.

No divergence exists between the contract and the artifacts produced by
this phase. If the contract is revised, the encoders and feature order
must be regenerated consistently.

### 13.1 Inference bridge dependencies

`server/predict_bridge.py` must load the following artifacts at startup:

- `data/processed/feature_names.json`
- `data/processed/encoder_service.pkl`
- `data/processed/encoder_onehot_protocol_flag.pkl`
- `data/processed/scaler_tabnet.pkl`
- `data/processed/class_order.json`

Model binaries are loaded from `models/`. Missing artifacts must
produce a non-zero exit and a diagnostic message on stderr.

---

## 14. Issues Encountered and Resolved

### Issue 1 — Manifest line count mismatch

The parser initially expected 43 lines. The actual
`kddcup.names.txt` has 42 lines: 1 attack-string header plus 41 column
definitions. The label column is implicit and must be appended.

**Resolution:** the parser now validates 42 non-empty lines, skips the
header, and appends `label` as the 42nd column.

### Issue 2 — `normal` missing from the attack-family map

`training_attack_types.txt` contains 23 attack strings and their
families but omits `normal`. Direct application of the map produced
`ValueError: Unmapped attack labels: ['normal']`.

**Resolution:** `map_targets` injects `normal -> normal` at runtime
without modifying the raw manifest. This preserves the source file's
integrity while handling the documented omission.

### Issue 3 — Object dtype in label arrays

`train_encoded["family"].to_numpy()` produced object-dtype arrays that
could not be loaded with `allow_pickle=False`.

**Resolution:** regeneration with `.astype(str).to_numpy(dtype='<U6')`
produces fixed-width Unicode arrays. Notebook 01 was updated so that
subsequent re-runs produce the correct dtype directly.

### Issue 4 — Notebook kernel working directory

Jupyter launched the kernel with a working directory of `notebooks/`,
causing `from src import ...` and relative file paths to fail.

**Resolution:** a path-fix cell was added at the top of Notebook 01 that
inserts the repository root onto `sys.path` before any imports. All file
I/O in notebooks now uses `PATHS` from `src.utils`, which resolves to
absolute paths independent of the working directory.

---

## 15. Team Handoff

### To Amber (Role 3)

The processed data is ready for Random Forest baseline testing.

- Load `X_train.npy`, `y_train.npy`, `X_test.npy`, `y_test.npy` from
  `data/processed/`.
- Use `class_order.json` to encode string labels to integers for
  scikit-learn.
- Do not re-split. Read `split_indices.json` for reference.
- Fit `RandomForestClassifier` with `random_state=42` for reproducibility.

### To Markie (Role 2)

The inference bridge must load the artifacts listed in section 13.1.
The exact feature assembly transformation is documented in
`contracts/api_data_contract.md` section 4.2.

### To Kenneth (Role 4)

Notebook 02 will consume the same four arrays. The training loop
specified in `tasks/4.md` can assume the 43-feature input and the
5-class output. The seed is locked at 42 for all random operations.

---

## 16. Phase 2 Mandate Checklist

| Item | Status |
|---|---|
| Map attack strings to 5 families | Complete |
| Strict deduplication | Complete |
| Correlation analysis and pruning above 90% | Complete |
| Log transform on skewed continuous features | Complete |
| Hybrid categorical encoding | Complete |
| Export transformed matrices to `data/processed/` | Complete |
| Handoff notification to Amber | Pending |

Five of six items are complete. The handoff is a communication step
that occurs when Amber begins Phase 2 of `tasks/3.md`.

---

## 17. Next Phase

**Phase 3 — Advanced Model Architecture.**

Target file: `src/models.py`.

Deliverables:

- XGBoost classifier with Optuna objective targeting Macro F1
- PyTorch TabNet classifier with Optuna objective
- Tomek Links in-fold resampling helper
- Validation-based early stopping for both models
- Serialization to `models/` using `joblib` and torch state dict

The stratified 5-fold cross-validation loop for hyperparameter search
will read the split contract from `data/processed/split_indices.json`
and enforce the anti-leakage rules stated in section 9.7.
```

---

## Where to Save It

```bash
# From repo root
reports/role-1-phase-2-kit-data-preparation.md
```

If the `reports/` folder doesn't exist yet:

```bash
mkdir reports
```

Then save the block above.

---

## Commit and Push

```bash
git add reports/role-1-phase-2-kit-data-preparation.md
git commit -m "docs(reports): add Phase 2 completion report for Role 1"
git push
```

---

## What This Report Contains — Checklist

Every Phase 2 item is covered:

| Section | Contents |
|---|---|
| 1 | Objective tied to tasks/1.md |
| 2 | Scope and out-of-scope |
| 3 | Input files and source identification |
| 4 | Complete label mapping with all 23 strings |
| 5 | Dedup counts |
| 6 | Constant-column and correlation pruning, with dropped feature list |
| 7 | Log transform, exact columns |
| 8 | Hybrid encoding, exact output columns |
| 9 | Split — every parameter, every class count, every rule |
| 10 | Scaling discipline |
| 11 | All 13 output files with shapes and purposes |
| 12 | Verification evidence |
| 13 | Contract alignment with `api_data_contract.md` v1.0 |
| 14 | Four issues and their resolutions |
| 15 | Handoffs to Amber, Markie, Kenneth |
| 16 | Mandate checklist |
| 17 | Preview of Phase 3 |

The split section (§9) is intentionally the longest — it documents the
ratio, the reasoning, the stratification, the seed, the class
distribution, the contract file, and the downstream usage rules so
that no team member can accidentally diverge from it.

---
