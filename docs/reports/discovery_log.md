# Team Discovery Log: Network Guardian IDS

This log documents our actual development journey, capturing questions, wrong turns, failures, and key insights discovered throughout the project lifecycle[cite: 1, 2].

## 1. Initial Exploration & Data Surprises
* **Question:** How clean is the KDD-style network dataset when first loaded?
* **Observation:** We discovered thousands of duplicate records and extreme skewness in continuous fields like `src_bytes` and `duration`[cite: 3]. Leaving duplicates caused models to artificially inflate accuracy by memorizing identical rows.
* **Action Taken:** Implemented a deduplication function and applied logarithmic scaling ($log(1+x)$) to stabilize numerical ranges[cite: 2, 3].

## 2. Categorical Encoding Challenges
* **Problem:** Standard One-Hot Encoding on the `service` feature created an unmanageable sparse matrix with dozens of columns, causing memory spikes.
* **Failed Approach:** Dropping the `service` column entirely (caused a severe drop in model sensitivity to `r2l` and `u2r` attacks).
* **Solution Found:** Implemented a hybrid approach—Frequency Encoding for high-cardinality `service` features and One-Hot Encoding for low-cardinality flags and protocols[cite: 3].

## 3. Class Imbalance & Model Bias
* **Issue:** Default models achieved 99% accuracy by simply guessing `normal` traffic, completely missing rare, high-severity `u2r` attacks (like `buffer_overflow`)[cite: 3, 4].
* **Wrong Turn:** Blindly applying SMOTE caused synthetic overlapping data points, increasing false positives.
* **Correction:** Switched our primary optimization metric to **Macro F1-Score** and applied Tomek Links boundary cleaning exclusively inside training folds during Stratified K-Fold cross-validation[cite: 1, 2].

## 4. Deep Learning Tuning & Early Stopping
* **Observation:** PyTorch TabNet initially overfitted rapidly when trained over too many epochs without validation monitoring.
* **Solution:** Integrated a validation-based early stopping monitor with a patience threshold, which successfully froze model weights the moment validation loss plateaued[cite: 2].