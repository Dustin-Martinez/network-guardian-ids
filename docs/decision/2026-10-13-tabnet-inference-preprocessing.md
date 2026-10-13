# TabNet Inference Preprocessing Decision

**Date:** 2026-10-13
**Raised by:** Markie, Role 2
**Decision owner:** Kit
**Status:** Proposed; confirmation pending

## Question

Should the existing TabNet artifact be served with unscaled engineered features, or should the API contract's StandardScaler pipeline govern a newly verified scaler-trained artifact?

## Evidence

- `docs/contracts/api_data_contract.md`, section 4.2: scale TabNet input at inference.
- `src/models.py`, tabnet_objective and _tabnet_refit: fit directly on the loaded engineered X arrays; no StandardScaler transformation in those functions.
- `notebooks/02_Model_Training.ipynb`: training uses the shared loaded arrays.
- `docs/contracts/role-5-training-execution-spec.md`: model artifact is tabnet_best.zip, while the API contract's general artifact table names tabnet_best.pt.

## Options

1. Confirm the existing model's actual input representation and align the API contract and bridge with it. This preserves the trained artifact when it was trained on unscaled inputs.
2. Require scaler-trained artifacts and keep the scaling contract. This requires verifying the actual training transformation and may require coordinated retraining by the model owner.

## Recommendation

First confirm the existing model's preprocessing from Dwayne's run and inspect its metadata. Prefer aligning inference to the verified training representation, with explicit contract revision if required. Do not scale an unscaled-trained model at inference or relabel metadata without evidence. Use the specific execution contract's native .zip artifact.

## Implemented interim behavior

RF and XGBoost routes work with their artifacts. TabNet returns a clear HTTP 500 readiness error until its preprocessing is confirmed. The current bridge's scaler path accepts an explicit `preprocessing.scaling = standard_scaler` assertion only for an actually scaler-trained artifact. This is a proposed readiness field, not an amendment to the frozen metadata schema.

## Decision

[Kit records the accepted option, any contract update, the artifact identity and the final metadata convention here.]
