# Section V — Model Comparison and Evaluation

## V.1 Comparative Results

The three evaluated models—Random Forest, XGBoost, and TabNet—were assessed using a frozen held-out test set containing 36,396 records and 43 input features. The target variable consists of five traffic classes: normal, denial of service (DoS), probe, remote-to-local (R2L), and user-to-root (U2R). Evaluation used the same test partition across the three models to support a consistent comparison.

Macro F1 was treated as the primary comparison metric. Unlike accuracy, Macro F1 gives equal weight to the F1 score of each class, making it more informative when a dataset contains substantial class imbalance. This is particularly important for intrusion detection because a model can classify the majority classes accurately while performing poorly on less frequent attack categories.

The recorded test-set Macro F1 scores were 0.9451 for XGBoost, 0.9331 for Random Forest, and 0.9306 for TabNet. XGBoost achieved the highest Macro F1 among the three evaluated models, exceeding Random Forest by approximately 0.0120 and TabNet by approximately 0.0145. Random Forest exceeded TabNet by approximately 0.0025. These differences indicate that XGBoost provided the strongest overall balance of class-level F1 performance on this test set. However, the Macro F1 comparison alone does not establish that XGBoost was the best model for every individual attack class.

The confusion matrices provide the class-level view needed to interpret the aggregate scores. Each matrix compares actual labels against predicted labels, allowing correct classifications and misclassifications to be examined by class. The diagonal entries represent correct classifications, while off-diagonal entries show the classes into which traffic was incorrectly assigned. These errors have different operational implications: a benign record classified as malicious can create an unnecessary alert, while an attack record classified as normal can remain undetected.

**Figure 1.** Random Forest confusion matrix on the frozen test set. Source file: `outputs/03_evaluation/confusion_matrix_rf.png`.

**Figure 2.** XGBoost confusion matrix on the frozen test set. Source file: `outputs/03_evaluation/confusion_matrix_xgb.png`.

**Figure 3.** TabNet confusion matrix on the frozen test set. Source file: `outputs/03_evaluation/confusion_matrix_tabnet.png`.

The per-class precision, recall, and F1 scores should be interpreted alongside these matrices. Precision measures the proportion of predictions for a class that were correct, while recall measures the proportion of actual instances of that class that were detected. F1 combines precision and recall into a single measure. For an intrusion detection system, recall is particularly important for assessing how many attacks are detected, but it must be considered alongside precision because excessive false positives can burden security analysts.

The test partition is imbalanced. It contains 21,958 normal records, 13,643 DoS records, 532 probe records, 250 R2L records, and only 13 U2R records. Consequently, performance on U2R traffic is estimated from a very small number of test examples. Even a small number of missed or correctly classified U2R records can substantially change its measured recall and F1 score. The R2L class also has considerably less representation than normal and DoS traffic. The per-class metrics and precision–recall curves are therefore necessary complements to the overall Macro F1 comparison.

**Table 1.** Per-class precision, recall, F1, support, and model Macro F1. Source file: `outputs/03_evaluation/per_class_metrics.csv`.

**Table 2.** Per-class metrics with class support expressed as a fraction of the test set. Source file: `outputs/03_evaluation/per_class_metrics_normalized.csv`.

Precision–recall curves provide an additional view of model behavior for the two rare attack categories, U2R and R2L. These curves show the trade-off between precision and recall as the classification threshold varies. They are useful when the objective is to assess detection behavior for classes that represent a small proportion of all records. The curves should be examined together with the confusion matrices and per-class metrics rather than interpreted as standalone evidence of overall model superiority.

**Figure 4.** Precision–recall curves for U2R detection. Source file: `outputs/03_evaluation/pr_curve_u2r.png`.

**Figure 5.** Precision–recall curves for R2L detection. Source file: `outputs/03_evaluation/pr_curve_r2l.png`.

**Figure 6.** Comparison of test-set Macro F1 across Random Forest, XGBoost, and TabNet. Source file: `outputs/03_evaluation/model_comparison_visual.png`.

## V.2 Error Analysis

The evaluation should be interpreted in terms of both aggregate performance and the consequences of individual classification errors. Macro F1 identifies the model with the strongest average class-level performance, while confusion matrices reveal where the models confuse one traffic family with another. The per-class metrics clarify whether a class's results are limited by missed detections, incorrect positive predictions, or both.

The rare-class support counts require particular caution. U2R has only 13 examples in the held-out test set, so its observed performance should not be treated as a precise estimate of performance on future U2R traffic. R2L has 250 examples and provides a larger, though still comparatively small, basis for evaluation. The precision–recall curves offer further information about threshold-dependent behavior, but the selected operating threshold should ultimately reflect the deployment context and the relative costs of missed attacks and false alarms.

The recorded Macro F1 comparison supports selecting XGBoost as the leading candidate for further consideration. That recommendation should remain conditional on review of the actual U2R and R2L precision, recall, F1, and confusion-matrix entries. A model with the highest Macro F1 may not necessarily have the highest recall for every high-severity attack category. Operational selection should therefore account for rare-class detection, false-positive burden, interpretability, and inference cost rather than relying on one aggregate score.

Finally, the results apply to the evaluated dataset, feature representation, saved model checkpoints, and frozen test partition. They do not by themselves demonstrate equivalent performance on live network traffic or on traffic distributions that differ from the evaluation data. Deployment claims should be supported by additional testing under realistic operational conditions.