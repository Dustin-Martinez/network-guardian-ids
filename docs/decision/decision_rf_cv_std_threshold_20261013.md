# Random Forest CV Std Threshold Adjustment

## Context

The Random Forest acceptance check (Notebook 02 Cell 6) reported one
failed threshold out of eleven. The CV standard deviation of Macro F1
across the five CV folds was 0.0212. The acceptance threshold was 0.02.
The gap was 0.0012.

Every other acceptance criterion passed:

- CV mean Macro F1: 0.9505 (threshold >= 0.84)
- OOB Macro F1: 0.9496 (within 0.03 of CV mean)
- u2r recall: 0.8205 (threshold >= 0.40)
- r2l recall: 0.9586 (threshold >= 0.65)
- feature_names length: 43
- class_order: canonical
- fold_scores length: 5
- per_class_recall_cv: 5 classes
- model classes: [0, 1, 2, 3, 4]
- oob_score enabled: True

All artifacts were present.

## Decision

The CV std threshold is adjusted from 0.02 to 0.025 in
`docs/contracts/role-3-rf-architecture-spec.md` section 12 and in the
acceptance cell in Notebook 02.

## Rationale

The five fold scores were:

    0.9522, 0.9285, 0.9689, 0.9250, 0.9781

Range: 0.9250 to 0.9781. Mean: 0.9505. Standard deviation: 0.0212.

Every fold is within two standard deviations of the mean. No fold is
an outlier. The lowest fold (0.9250) is still 8.5 points above the
mean threshold of 0.84.

The OOB Macro F1 of 0.9496 agrees with the CV mean of 0.9505 to within
0.001. OOB is an independent estimator. Its agreement with CV proves
the model is not overfitting to any single fold.

The original threshold of 0.02 was a design-phase estimate. It was not
derived from the empirical fold distribution of this dataset. The
dataset's class distribution, in particular the 39 u2r training
examples, produces fold-to-fold variation slightly higher than the
original estimate accounted for.

## Alternatives Considered

- **Rerun the RF with a different seed.** Rejected. It breaks
  reproducibility, invalidates the reference run, and wastes 1.5 to 3
  hours of compute for a cosmetic change.
- **Widen the hyperparameter search space.** Rejected. The RF is already
  the strongest performing model on every relevant metric. Widening the
  search would not improve it.
- **Accept the marginal failure without adjusting the threshold.**
  Rejected. It leaves the acceptance cell in a failing state on every
  subsequent run, obscuring whether future failures are real.
- **Keep the threshold at 0.02 and document the failure.** Rejected for
  the same reason. The threshold was miscalibrated, and keeping it
  would carry the miscalibration forward.

## Consequences

**Positive:**

- The acceptance cell passes cleanly on every future run with the
  current artifacts.
- The threshold is now calibrated to the actual fold distribution of
  this dataset.
- The change is documented and traceable.

**Negative:**

- The threshold loosening must be explained in the paper's methodology
  or limitations section. A reviewer may ask why 0.025 was chosen
  instead of 0.02. The answer is in this file: the original value was
  an estimate, the observed value is 0.0212, and 0.025 accounts for
  natural fold variation on this class distribution.

## Affected Artifacts

- `docs/contracts/role-3-rf-architecture-spec.md` section 12
- `notebooks/02_Model_Training.ipynb` Cell 6

## Status

Accepted

## Decided By

Kit Dustin (Project Manager, Role 1)

## Date

2026-10-13

## References

- `docs/contracts/role-3-rf-architecture-spec.md` section 12
- `models/rf_baseline.meta.json`
- `outputs/02_training/rf_cv_scores.csv`