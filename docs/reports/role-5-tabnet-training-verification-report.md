# Network Guardian IDS --- Role 5 Technical Report

## TabNet Training Verification and Preliminary Overfitting Assessment

**Prepared by:** Dwyane --- Role 5, TabNet Executor, Evaluation Engineer
& Explainability Contributor\
**Project:** Network Guardian: Detecting Network Intrusions with Machine
Learning\
**Report date:** October 12, 2026\
**Status:** TabNet training completed; artifact verification passed;
preliminary overfitting assessment completed; held-out test evaluation
pending.

------------------------------------------------------------------------

## 1. Executive Summary

The TabNet model training process was completed successfully using the
project's existing training pipeline. The saved model was loaded
successfully, its metadata was inspected, and the training artifacts
were verified without rerunning the computationally expensive training
process.

The recorded cross-validation Macro F1 score was **0.921225**, with a
standard deviation of approximately **0.019250** across three folds. The
best recorded Optuna trial was Trial 16, with a score of approximately
0.921225.

A separate evaluation on the training dataset produced a Macro F1 score
of **0.962640**. This is approximately **0.041415 points, or 4.14
percentage points, higher** than the recorded cross-validation mean.

This difference raises a potential generalization concern, but it does
not independently establish severe overfitting. The training score was
measured using the final refitted model on its training data, while the
cross-validation score was obtained from validation folds during model
selection. The two results therefore measure performance under different
conditions.

The next required step is to evaluate the saved model against the frozen
held-out test set. Until that evaluation is completed, the model's final
test performance and generalization capability remain undetermined.

## 2. Training and Environment Verification

The project environment was verified successfully earlier in the
workflow.

-   Python version: 3.11.9
-   PyTorch version: 2.1.0+cpu
-   Execution device: CPU
-   Phase 1 environment verification: Passed
-   Model artifact loading: Passed
-   TabNet artifact verification: Passed

The final saved model was loaded from:

`models/tabnet_best.zip`

The associated metadata file was:

`models/tabnet_best.meta.json`

The model-loading operation completed successfully. The CPU warning
emitted by PyTorch TabNet was informational and did not indicate a
model-loading failure.

### Training dataset dimensions

  Dataset component   Shape          Data type
  ------------------- -------------- ---------------
  X_train             (109188, 43)   float64
  y_train             (109188,)      String labels

The model uses 43 input features and the following five-class
classification order:

1.  normal
2.  dos
3.  probe
4.  r2l
5.  u2r

## 3. Cross-Validation Results

The saved metadata and the recorded cross-validation results contain the
following values.

  Metric                                 Result
  ---------------------------------- ----------
  Number of cross-validation folds            3
  Optuna trials configured                   20
  Best trial number                          16
  Best recorded CV Macro F1            0.921225
  CV standard deviation                0.019250

### Individual fold scores

  Fold       Macro F1
  -------- ----------
  Fold 1     0.901462
  Fold 2     0.919279
  Fold 3     0.921225

The recorded trial states were:

-   Completed trials: 15
-   Pruned trials: 5

Trial 16 had the highest recorded completed-trial score of approximately
0.921225.

The fold scores show some variation, with Fold 1 performing lower than
Folds 2 and 3. However, three fold results are insufficient to establish
whether the observed variation is statistically significant or
indicative of a systematic generalization problem.

The recorded standard deviation of approximately 0.019250 indicates
variation across the validation folds. It should not be interpreted as a
confidence interval or a direct measurement of the final test-set error.

## 4. Training-Set Evaluation

The saved TabNet model was evaluated on the same training feature and
label arrays used by the training pipeline.

The arrays were loaded from:

-   `data/processed/X_train.npy`
-   `data/processed/y_train.npy`

The saved model generated predictions for the training samples. The
predicted numeric class IDs were mapped back to the corresponding class
labels using the class order recorded in the model metadata.

This evaluation was performed without retraining the model or modifying
the notebook.

### Training metrics

  Metric                           Result
  ---------------------------- ----------
  Training Macro F1              0.962640
  Overall accuracy, rounded          1.00
  Training samples evaluated      109,188

The reported accuracy is rounded to two decimal places, so it should not
be interpreted as proof that every training sample was classified
correctly.

### Per-class training results

  Class             Precision   Recall   F1-score   Support
  --------------- ----------- -------- ---------- ---------
  normal                 1.00     1.00       1.00    65,874
  dos                    1.00     1.00       1.00    40,928
  probe                  0.97     1.00       0.98     1,598
  r2l                    0.89     0.98       0.93       749
  u2r                    0.81     1.00       0.90        39
  Macro average          0.93     1.00       0.96   109,188

The training report shows very high recall across all five classes.
However, precision is lower for R2L and U2R than for the normal and DoS
classes.

For U2R, the model achieved a reported training recall of 1.00 and
precision of 0.81. This indicates that the model recovered all actual
U2R training examples according to the reported recall, but some
predictions classified as U2R were false positives.

The U2R training support is only 39 samples. Performance on this small
training subset is not sufficient to establish reliable detection of
previously unseen U2R attacks.

## 5. Preliminary Training--Validation Gap Assessment

The difference between the training Macro F1 and the recorded
cross-validation mean is:

**Training Macro F1 − CV Macro F1**

**0.962640 − 0.921225 = 0.041415**

The observed difference is approximately 4.14 percentage points.

  Comparison                Macro F1
  ----------------------- ----------
  Training dataset          0.962640
  Cross-validation mean     0.921225
  Absolute difference       0.041415

This result indicates that the model performs better on its training
data than the average recorded validation fold.

This is a reason to investigate generalization, but it is not sufficient
evidence to conclude that the model is severely overfitting.

There are important methodological considerations:

1.  The training Macro F1 was measured using the final refitted model on
    its training data.
2.  The CV Macro F1 represents validation-fold performance during model
    selection.
3.  The training and CV scores were not generated from identical data
    partitions.
4.  The training score is an in-sample metric, while CV estimates
    performance on held-out portions of the training pool.
5.  The current metadata does not contain the expected
    `per_class_recall_cv` field. It contains `per_class_recall_train`
    instead.

The missing `per_class_recall_cv` field is a metadata-schema
discrepancy. It prevents retrieval of the expected per-class CV recall
values from that metadata file, but it is not itself evidence of
overfitting.

The current assessment is therefore:

**A measurable training--validation performance gap exists. Its severity
and cause remain unconfirmed pending held-out test evaluation and
further inspection of the data split and preprocessing pipeline.**

## 6. Data and Evaluation Integrity Considerations

The training pipeline uses a frozen training/test split. The known
dataset dimensions indicate 109,188 training samples and 36,396 test
samples, with 43 features per sample.

The held-out test set must remain independent of model fitting and
hyperparameter selection. The test results should be used to evaluate
the selected model, not to choose new hyperparameters.

The following items should be checked as part of the evaluation audit:

-   Whether all data-dependent preprocessing was fitted on training data
    only.
-   Whether the frozen train/test split was respected throughout model
    selection and final refitting.
-   Whether duplicate or near-duplicate traffic records appear across
    training and test partitions.
-   Whether class distributions differ substantially between the
    training and test sets.
-   Whether the test evaluation reports per-class performance,
    especially for R2L and U2R.
-   Whether independent data from another source or capture period is
    available for a more demanding generalization assessment.

These checks have not all been completed, so no conclusion about data
leakage or duplicate contamination should be drawn at this stage.

## 7. Artifact and Metadata Notes

The saved model loaded successfully, and the artifact verification cell
passed after the model filename was corrected to match the expected
path.

The training process initially saved the model with a duplicated `.zip`
extension. The filename was corrected to:

`models/tabnet_best.zip`

The artifact was renamed rather than retrained.

The metadata contains the selected model parameters, architecture
details, class order, feature names, fold scores, CV mean and standard
deviation, and training recall values.

One issue remains: the metadata does not contain `per_class_recall_cv`,
which was expected by a verification command. The existing metadata key
is `per_class_recall_train`.

This discrepancy should be documented for review. The metadata or
training code should not be changed without approval, because the
existing artifacts and training outputs should remain traceable.

The project also has generated model and output artifacts. These should
not be committed to the repository until the team's artifact-commit
policy is confirmed.

## 8. Required Next Step: Held-Out Test Evaluation

The next step is to evaluate the saved TabNet model using the frozen
test arrays:

-   `X_test.npy`
-   `y_test.npy`

The evaluation should be performed using the project's designated
evaluation notebook, `notebooks/03_Evaluation_and_XAI.ipynb`, following
the applicable instructions in `docs/tasks/5.md`.

The required outputs are:

1.  Test Macro F1.
2.  Per-class precision, recall, and F1.
3.  Confusion matrix.
4.  U2R recall.
5.  R2L recall.

The results should be compared with the training Macro F1 of 0.962640
and the CV Macro F1 of 0.921225.

A substantial drop in test performance would justify further
investigation into overfitting, data distribution differences, or
preprocessing and split integrity. A test score close to the CV mean
would support consistency on the current held-out split, but would not
independently establish generalization to real-world traffic.

The test set must not be used for further hyperparameter tuning or
retraining after its results are observed.

## 9. Conclusion

The TabNet training run and saved model verification completed
successfully. The recorded CV Macro F1 is 0.921225, while the
independently calculated training Macro F1 is 0.962640, producing a gap
of approximately 4.14 percentage points.

This gap is a meaningful observation for model evaluation, but it does
not establish severe overfitting on its own. The training results are
strong, while the low support for U2R and the current lack of per-class
CV recall values require careful interpretation.

The next priority is held-out test evaluation using the existing saved
model and frozen test data, followed by a review of per-class
performance and the integrity of the data split and preprocessing
pipeline.

No training rerun is currently recommended. The existing training
artifacts should be preserved while the remaining evaluation work is
completed.

------------------------------------------------------------------------

## Summary for Review

-   **Training Macro F1:** 0.962640
-   **Cross-validation Macro F1:** 0.921225
-   **Observed gap:** 0.041415
-   **CV standard deviation:** 0.019250
-   **Best Optuna trial:** 16
-   **Model artifact verification:** Passed
-   **Confirmed severe overfitting:** Not established
-   **Held-out test evaluation:** Pending
-   **Metadata discrepancy:** `per_class_recall_cv` is absent;
    `per_class_recall_train` is present
-   **Recommended next action:** Evaluate the saved model on the frozen
    test set without retraining or tuning on that set.
