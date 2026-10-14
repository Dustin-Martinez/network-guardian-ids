# Network Guardian IDS — A Hybrid Machine Learning Approach to Multi-Class Network Intrusion Detection

INTRODUCTION TO INTELLIGENT SYSTEMS
CCINSYSL

Submitted by

Kit Dustin [Complete surname first name and middle initial]

Markie [Complete surname first name and middle initial]

Amber [Complete surname first name and middle initial]

Kenneth [Complete surname first name and middle initial]

Dwayne [Complete surname first name and middle initial]

Submitted to
[Professor full name]
Professor

OCTOBER 2026

## I. Introduction

### 1.1 Background and problem statement

Network intrusion detection requires distinguishing legitimate connections from activity that threatens the confidentiality, integrity, or availability of a system. A machine learning classifier approaches this task by learning relationships between connection attributes and labeled outcomes. Network Guardian IDS investigates this approach through a five class classification problem using network connection records. The project compares alternative learning methods and examines whether their errors differ across common and rare attack families.

The benchmark task concerns connection level classification rather than direct inspection of live packet streams. KDD Cup 1999 draws on a simulated network environment associated with the 1998 DARPA intrusion detection evaluation. This origin provides a reproducible research setting but limits the conclusions that can be drawn about current operational traffic (ACM SIGKDD, n.d.). The project therefore evaluates a research prototype rather than claiming production readiness.

### 1.2 Attack families

The target classes are normal, denial of service, probe, remote to local, and user to root. Denial of service attacks interfere with service availability, probing seeks information about hosts or services, remote to local attacks seek unauthorized access from a remote system, and user to root attacks seek elevated privileges from an existing user context (ACM SIGKDD, n.d.). Each record receives one family label; the project does not infer the full attack sequence from that label alone.

Class imbalance is central to the research problem. The prepared training partition contains 65,874 normal connections but only 39 user to root examples. A model can perform well on frequent classes while failing on the rarest category. Accordingly, the comparison emphasizes Macro F1 and class level recall alongside aggregate measures. The operational significance of a missed attack and the burden of a false alarm must both be considered.

### 1.3 Objectives and research questions

The primary objective is to compare Random Forest, XGBoost, and TabNet using a shared prepared representation and a frozen training and test partition. The study asks how the three approaches differ in overall classification quality, detection of rare attack families, computational requirements, and the explanations available to an analyst. A second objective is to document the preparation decisions and execution difficulties that affect reproducibility.

The comparison is designed around one prepared pipeline. It does not isolate the causal contribution of each transformation because no preprocessing ablation is currently included. Any claim that a particular transformation improves detection will require a separate controlled experiment. Final model recommendations will be based on confirmed training and evaluation artifacts rather than anticipated rankings.

### 1.4 System scope

The prototype comprises a Next.js dashboard, a Node.js Express service, and a Python inference bridge. The bridge preserves the frozen 43-feature order and returns an attack family, confidence percentage, threat indicator, and model identifier. The frontend mock switch was disabled, enabling the dashboard to send raw connection fields to the live API endpoint. The independently reproduced backend smoke test used RF. Complete cross-model deployment verification remains separate from the test-set evaluation (Network Guardian IDS Team, 2026d, 2026g, 2026k).

## II. Data Understanding and Preparation

### 2.1 Data Understanding

The dataset contains 494,021 connection records, 41 predictor variables, and one attack label. Profiling identified no missing values. Protocol type, service, and connection flag are categorical strings, whereas the remaining 38 variables are numerical. The attack manifest defines 22 attack mappings. The normal category is added explicitly, producing 23 observed labels grouped into five classes. These characteristics correspond to the supplied KDD Cup 1999 connection dataset (Network Guardian IDS Team, 2026a).

**Table 1. Class distribution before and after deduplication and in the frozen split**

| Class | Raw | Prepared | Training | Test |
| --- | --- | --- | --- | --- |
| Normal | 97,278 | 87,832 | 65,874 | 21,958 |
| DoS | 391,458 | 54,571 | 40,928 | 13,643 |
| Probe | 4,107 | 2,130 | 1,598 | 532 |
| R2L | 1,126 | 999 | 749 | 250 |
| U2R | 52 | 52 | 39 | 13 |
| Total | 494,021 | 145,584 | 109,188 | 36,396 |

Source: Notebook 01 execution and data/processed/split_indices.json. Removing 348,437 repeated feature vectors reduced the dataset by approximately 70.5 percent. U2R retained only 52 records across the prepared dataset. The small support means that a single incorrect U2R prediction can noticeably change the reported test recall.

### 2.2 Feature Description

Basic connection attributes describe traffic volume and status. Content attributes summarize activity within a connection, while time based and host based traffic attributes describe related connections. All 41 fields in Table 2 are candidate inputs before feature removal; label is the target, not a predictor. Numerical ranges are observed minima and maxima in the supplied raw file, not validation limits for future network traffic. Categories number three for protocol_type, 66 for service, and 11 for flag in this local file.

**Table 2. Raw feature dictionary with locally observed values**

| Feature name | Type and range | Description | Role |
| --- | --- | --- | --- |
| duration | Numeric; 0 to 58,329 | Connection length in seconds | Retained predictor |
| protocol_type | Category; 3 values | Transport or network protocol | Encoded predictor |
| service | Category; 66 values | Destination service category | Encoded predictor |
| flag | Category; 11 values | Connection status category | Encoded predictor |
| src_bytes | Numeric; 0 to 693,375,640 | Bytes toward destination | Retained predictor |
| dst_bytes | Numeric; 0 to 5,155,468 | Bytes toward source | Retained predictor |
| land | Numeric; 0 to 1 | Same host and port indicator | Retained predictor |
| wrong_fragment | Numeric; 0 to 3 | Invalid fragment count | Retained predictor |
| urgent | Numeric; 0 to 3 | Urgent packet count | Retained predictor |
| hot | Numeric; 0 to 30 | Sensitive activity indicator count | Retained predictor |
| num_failed_logins | Numeric; 0 to 5 | Failed authentication count | Retained predictor |
| logged_in | Numeric; 0 to 1 | Successful authentication indicator | Retained predictor |
| num_compromised | Numeric; 0 to 884 | Compromise indicator count | Removed before encoding |
| root_shell | Numeric; 0 to 1 | Root shell indicator | Retained predictor |
| su_attempted | Numeric; 0 to 2 | Superuser command indicator | Retained predictor |
| num_root | Numeric; 0 to 993 | Root access count | Retained predictor |
| num_file_creations | Numeric; 0 to 28 | File creation count | Retained predictor |
| num_shells | Numeric; 0 to 2 | Shell prompt count | Retained predictor |
| num_access_files | Numeric; 0 to 8 | Access control file operation count | Retained predictor |
| num_outbound_cmds | Numeric; 0 to 0 | Outbound FTP command count | Removed before encoding |
| is_host_login | Numeric; 0 to 0 | Host login indicator | Removed before encoding |
| is_guest_login | Numeric; 0 to 1 | Guest login indicator | Retained predictor |
| count | Numeric; 0 to 511 | Recent same host connections | Retained predictor |
| srv_count | Numeric; 0 to 511 | Recent same service connections | Retained predictor |
| serror_rate | Numeric; 0 to 1 | Same host SYN error fraction | Removed before encoding |
| srv_serror_rate | Numeric; 0 to 1 | Same service SYN error fraction | Removed before encoding |
| rerror_rate | Numeric; 0 to 1 | Same host rejection fraction | Removed before encoding |
| srv_rerror_rate | Numeric; 0 to 1 | Same service rejection fraction | Removed before encoding |
| same_srv_rate | Numeric; 0 to 1 | Same host same service fraction | Retained predictor |
| diff_srv_rate | Numeric; 0 to 1 | Same host other service fraction | Retained predictor |
| srv_diff_host_rate | Numeric; 0 to 1 | Same service other host fraction | Retained predictor |
| dst_host_count | Numeric; 0 to 255 | Host window connection count | Retained predictor |
| dst_host_srv_count | Numeric; 0 to 255 | Host window same service count | Removed before encoding |
| dst_host_same_srv_rate | Numeric; 0 to 1 | Host window same service fraction | Retained predictor |
| dst_host_diff_srv_rate | Numeric; 0 to 1 | Host window other service fraction | Retained predictor |
| dst_host_same_src_port_rate | Numeric; 0 to 1 | Host window same source port fraction | Retained predictor |
| dst_host_srv_diff_host_rate | Numeric; 0 to 1 | Service window other host fraction | Retained predictor |
| dst_host_serror_rate | Numeric; 0 to 1 | Host window SYN error fraction | Removed before encoding |
| dst_host_srv_serror_rate | Numeric; 0 to 1 | Host service SYN error fraction | Retained predictor |
| dst_host_rerror_rate | Numeric; 0 to 1 | Host window rejection fraction | Removed before encoding |
| dst_host_srv_rerror_rate | Numeric; 0 to 1 | Host service rejection fraction | Retained predictor |

Source: data/raw/kddcup.names.txt, local profiling of data/raw/kddcup.csv, and the benchmark feature descriptions. The repository spelling is_host_login is retained. The indicators and counts are stored numerically even where their semantic role is categorical or binary.

### 2.3 Data Preparation

#### 2.3.1 Target mapping and duplicate removal

The pipeline parses the raw feature manifest, appends the implicit label column, and maps attack names to their canonical families. Normal is injected into the mapping because it is absent from the attack manifest. Duplicate removal compares the 41 input features rather than the label. When identical feature vectors have different labels, the first record is retained. This policy reduces repeated examples across the subsequent split but also requires scrutiny of any conflicting labels that may be discarded.

#### 2.3.2 Constant and correlated feature removal

Two constant variables, num_outbound_cmds and is_host_login, were removed. Absolute Pearson correlations were then computed among the numerical variables. For pairs with correlation greater than 0.90, the later variable in the original column order was removed. The excluded correlated variables were dst_host_rerror_rate, dst_host_serror_rate, dst_host_srv_count, num_compromised, rerror_rate, serror_rate, srv_rerror_rate, and srv_serror_rate. The resulting representation contained 28 numerical and three categorical variables before encoding.

Constant detection and correlation pruning preceded the training and test split. These transformations therefore used the complete feature pool, including records subsequently assigned to the test partition. Although target labels were not used for these selection steps, this design limits claims of fully isolated preprocessing. Future experiments should estimate data-dependent feature selection within training folds.

#### 2.3.3 Transformation and encoding

The duration, src_bytes, and dst_bytes fields receive log(1 + x) transformations to compress large numerical ranges while retaining zero values. Service is frequency encoded using the training partition, with unseen services mapped to zero. Protocol and flag are one hot encoded using training fitted categories; unknown values produce zeros for the corresponding block. The final representation contains 28 numerical features, one service frequency, three protocol indicators, and 11 flag indicators, totaling 43 ordered inputs.

#### 2.3.4 Split and scaling

A stratified 75 percent training and 25 percent test split uses random state 42. The resulting arrays contain 109,188 training rows and 36,396 test rows. Features are float64 and labels are fixed width Unicode. A StandardScaler is fit on the training partition and saved, but the TabNet training functions do not apply it. The updated inference bridge passes raw engineered features to TabNet to match its training representation; a real TabNet API request remains unverified. Tree models also use the unscaled engineered representation. The saved JSON manifests specify the input order, class order, and frozen split, while saved encoders provide the inference transformation.

The categorical encoders and scaler were fitted to the complete training partition rather than refitted within each cross-validation fold. Validation-fold covariates therefore contributed to preprocessing statistics. The held-out test partition was excluded from their fitting. Cross-validation estimates should be interpreted with this qualification; fold-specific preprocessing would provide a stricter assessment during model selection.

## III. Machine Learning Model Development

### 3.1 Random Forest

#### 3.1.1 Model Description

Random Forest combines decision trees trained with random sampling of records and candidate split features. Aggregation provides a bagging baseline for tabular classification (Breiman, 2001). Bootstrap sampling, out-of-bag estimation, and class weighting are included in the experimental configuration. These mechanisms support comparison without guaranteeing reliable detection of rare attacks.

#### 3.1.2 Model Configuration

**Table 3. Random Forest search space and selected configuration**

| Parameter | Search range | Selected value |
| --- | --- | --- |
| n_estimators | 100 to 500 step 50 | 350 |
| max_depth | 5, 10, 15, 20, 25, 30 or None | 15 |
| min_samples_split | 2 to 20 | 8 |
| min_samples_leaf | 1 to 10 | 3 |
| max_features | sqrt or log2 | sqrt |
| criterion | gini or entropy | entropy |
| class_weight | balanced or balanced_subsample | balanced |

Random Forest hyperparameter optimization used 20 configured Optuna trials and five stratified validation folds. The search space comprised 100 to 500 trees in increments of 50, maximum depths from 5 to 30 or unrestricted depth, minimum split sizes from 2 to 20, and minimum leaf sizes from 1 to 10. Other options included square-root or logarithmic feature sampling, Gini or entropy split criteria, and balanced or balanced-subsample class weighting. Random state 42, parallel execution, bootstrap sampling, and out-of-bag estimation were fixed. Tomek Links was applied only to the training subset within each fold (Network Guardian IDS Team, 2026b).

The selected Random Forest configuration used 350 trees, maximum depth 15, entropy, square-root feature sampling, a minimum split size of 8, a minimum leaf size of 3, and balanced class weighting. Trial 17 produced the selected configuration (Network Guardian IDS Team, 2026f).

#### 3.1.3 Training Procedure

Each trial was assessed with five stratified folds. Tomek Links and class weighting were restricted to the fold training subset; validation predictions were used to calculate Macro F1. After selection, the Random Forest was refitted on the cleaned training pool, with the test partition reserved for subsequent evaluation (Network Guardian IDS Team, 2026b, 2026f).

#### 3.1.4 Model Results

The RF study reports CV Macro F1 of 0.950540 and independently reconstructed fold SD of 0.021178, with OOB Macro F1 of 0.949575. Pooled validation U2R recall was 0.820513. The original RF SD threshold of 0.02 was revised to 0.025 through a documented post-run decision; the observed SD satisfies the revised threshold. This adjustment is disclosed rather than treated as a prespecified criterion.

RF held-out test Macro F1 was 0.933095, weighted F1 0.998905, R2L recall 0.952000, and U2R recall 0.769231. Recorded full-test prediction time was 0.151 seconds. Validation and test recall remain distinct quantities (Network Guardian IDS Team, 2026f, 2026h, 2026j).

### 3.2 XGBoost

#### 3.2.1 Model Description

XGBoost is a regularized gradient tree boosting framework that builds an additive ensemble through sequential optimization (Chen & Guestrin, 2016). The implementation assigns class weighted sample weights and evaluates candidate configurations using five fold stratified validation. The search budget is 30 trials and the objective is the mean Macro F1 across validation folds. Validation based early stopping uses a patience of 20 rounds.

#### 3.2.2 Model Configuration

**Table 4. XGBoost hyperparameter search space**

| Parameter | Search range | Selected value |
| --- | --- | --- |
| learning_rate | 0.01 to 0.15 logarithmic | 0.043473 |
| max_depth | 3 to 10 | 10 |
| min_child_weight | 1 to 20 | 2 |
| gamma | 0 to 5 | 0.00947773 |
| subsample | 0.6 to 1.0 | 0.80875 |
| colsample_bytree | 0.5 to 1.0 | 0.788443 |
| reg_alpha | 0 to 10 | 0.633807 |
| reg_lambda | 1 to 20 | 7.2469 |
| max_delta_step | 0 to 5 | 4 |
| n_estimators | 100 to 300 step 50 | 250 |

The search varies learning rate, tree depth, minimum child weight, split regularization, row and column sampling, L1 and L2 regularization, maximum delta step, and the number of trees. The implemented learning rate range is 0.01 to 0.15 and tree depth ranges from 3 to 10. Candidate ensembles use 100 to 300 trees in steps of 50. After selection, the implementation refits on the cleaned training pool with class weights recalculated after resampling. The final refit does not consult the held out test partition (Network Guardian IDS Team, 2026b).

#### 3.2.3 Training Procedure

The XGBoost study uses a configured budget of 30 trials per invocation. Its saved history contains 90 records: 78 completed and 12 pruned. Trial 81 was selected with mean validation Macro F1 of 0.950842. Five stratified folds, class-weighted fold training, Tomek Links, and validation-based early stopping with patience 20 were retained. Final refitting disables early stopping because no eval_set is supplied; the saved test partition is not used for refit (Network Guardian IDS Team, 2026i).

#### 3.2.4 Model Results

XGBoost trial 81 reports mean CV Macro F1 of 0.950842. Its metadata SD of 0.025954 is trial-value dispersion and is not a fold SD. Held-out test Macro F1 was 0.945134, weighted F1 0.998961, R2L recall 0.992000, and U2R recall 0.769231. Recorded full-test prediction took 0.126 seconds. The execution report records an approximately 1 hour 55 minute training wall time, which is not a controlled cross-device runtime comparison (Network Guardian IDS Team, 2026h, 2026i).

### 3.3 TabNet

#### 3.3.1 Model Description

TabNet applies sequential attention to feature selection in a neural network for tabular data. Its attention masks offer a model specific view of feature usage (Arik & Pfister, 2019). The project implementation uses CPU execution, an Adam optimizer with learning rate 0.02, at most 30 epochs, and validation based early stopping with patience 10. Architecture tuning includes decision and attention widths, decision steps, attention relaxation, sparsity regularization, transformer sharing, momentum, mask type, and batch sizes.

#### 3.3.2 Model Configuration

**Table 5. TabNet architecture and training search space**

| Parameter | Search range | Selected value |
| --- | --- | --- |
| n_d and n_a | Each 8, 16, 24 or 32 | 24 and 32 |
| n_steps | 3 to 7 | 6 |
| gamma | 1.0 to 1.6 | 1.29608 |
| lambda_sparse | 0.00001 to 0.005 logarithmic | 7.91193e-05 |
| n_independent | 1 to 3 | 2 |
| n_shared | 1 to 3 | 1 |
| momentum | 0.02 to 0.10 | 0.0655497 |
| mask_type | sparsemax or entmax | entmax |
| batch_size | 512, 1024 or 2048 | 512 |
| virtual_batch_size | 128 or 256 | 256 |

#### 3.3.3 Training Procedure

TabNet uses 20 configured Optuna trials and three stratified validation folds. With 39 U2R training records, three folds place approximately 13 examples in each validation fold, compared with roughly seven or eight under five folds. This increases support per fold but does not establish that the rare class estimate is stable. The different fold counts must remain visible when comparing the algorithms. Tomek Links is restricted to fold training subsets. The final refit includes an internal 10 percent validation subset for early stopping rather than unrestricted training on the entire pool.

#### 3.3.4 Model Results

TabNet trial 16 reports mean CV Macro F1 of 0.921225. Its exported cumulative means are not independent fold scores, and the metadata SD of 0.019250 describes trial-value dispersion. Held-out test Macro F1 was 0.930622, weighted F1 0.997602, R2L recall 0.976000, and U2R recall 0.769231. Full-test prediction took 1.091 seconds in the reported evaluation environment. Model loading and offline evaluation are verified. The updated bridge passes raw engineered features to match TabNet training, but a real TabNet API request using the model artifact remains unverified (Network Guardian IDS Team, 2026c, 2026g, 2026h).

### 3.4 Common training protocol and imbalance handling

The implementations use a shared random state and persist optimization studies for traceability. Optuna selects configurations according to validation Macro F1; pruning can stop unpromising trials before they consume the full budget (Akiba et al., 2019). Tomek Links removes selected boundary examples from fold training data, while validation subsets are not resampled. Class weights increase the contribution of less frequent classes. The final test partition is reserved for Notebook 03 and is not passed to model tuning functions.

Macro F1 is the arithmetic mean of the five class F1 values. For each class, precision measures how many predicted members are correct, recall measures how many actual members are recovered, and F1 balances precision and recall. Equal class weighting prevents the most frequent category from dominating the summary. Per class support and confusion matrices remain necessary because the same Macro F1 can arise from different error patterns.

### 3.5 Backend implementation and integration verification

The backend implements POST /api/analyze on localhost port 5000. It validates the 31 raw categorical and numerical request fields before starting the repository virtual environment Python interpreter. The bridge applies logarithmic transformations and the frozen encoders, reconstructs the 43 feature columns in their stored order, checks model metadata, and decodes probability columns using the model class identifiers. This avoids dependence on JSON key order and prevents incorrect family decoding when a classifier uses a different probability column order.

Successful requests return a family label, confidence percentage, threat indicator, and model identifier. Invalid requests return HTTP 400. Missing artifacts, bridge failures, invalid model outputs, and timeouts return HTTP 500 with a structured error. The frontend must treat an error envelope as a failed request; its default normal field is not a prediction. The service uses bounded request and response sizes and a per-request timeout.

Functional verification passed 10 Node API tests and three Python bridge tests. A real HTTP inference request using the RF artifact returned a valid response, and reversing the raw JSON key order preserved that response. These checks establish tested interface behavior, not classifier accuracy. No training or test-set evaluation was performed during backend verification (Network Guardian IDS Team, 2026g).

The updated API contract and bridge pass raw engineered features to TabNet, matching the saved model's training representation. Repository tests cover routing with fixtures, but this integration did not verify a real TabNet API request using the model artifact. XGBoost receiving-device verification also remains pending. Offline test evaluation does not establish live-route readiness (Network Guardian IDS Team, 2026g, 2026h, 2026k).

## IV. Model Metadata

All models use the same 43 encoded predictors, target family, random state 42, 109,188 training records before resampling, and 36,396 reserved test records. The metadata table distinguishes configurations, actual study history, and measured results.

**Table 6. Experimental model metadata**

| Metadata | Random Forest | XGBoost | TabNet |
| --- | --- | --- | --- |
| Algorithm | Tree bagging | Gradient boosting | Sequential attention |
| Target | family, five classes | family, five classes | family, five classes |
| Input features | 43 | 43 | 43 |
| Features used | All encoded predictors | All encoded predictors | All encoded predictors |
| Training rows | 109,188 | 109,188 | 109,188 |
| Test rows | 36,396 | 36,396 | 36,396 |
| Random state | 42 | 42 | 42 |
| Validation folds | 5 | 5 | 3 |
| Best trial | 17 | 81 | 16 |
| Configured trial budget | 20 | 30 per invocation | 20 |
| Recorded trials | 20 | 90 | 20 |
| Main measure | Macro F1 | Macro F1 | Macro F1 |
| Test Macro F1 | 0.933095 | 0.945134 | 0.930622 |
| Full-test prediction (s) | 0.151 | 0.126 | 1.091 |
| Training wall time | Not recorded consistently | About 1 h 55 min, reported | Not recorded consistently |
| Model artifact | rf_baseline.joblib | xgb_optuna.joblib | tabnet_best.zip |

Sources: models/*.meta.json, outputs/02_training/optuna_*_trials.csv, and the execution/evaluation reports. The XGBoost trial log contains 90 records, including 78 completed and 12 pruned, whereas 30 is the configured per-invocation budget. The sidecar alone does not describe the accumulated search history (Network Guardian IDS Team, 2026h, 2026i).

## V. Model Comparison and Evaluation

### 5.1 Comparative Results

The selected study objective is the mean validation Macro F1. Five folds were used for the tree models and three for TabNet. Table entries preserve the configured and recorded trial counts separately; repeated study execution can accumulate additional trial indices.

**Table 7. Selected validation objectives and optimization records**

| Model | CV mean | Folds | Best trial | Recorded trials |
| --- | --- | --- | --- | --- |
| Random Forest | 0.950540 | 5 | 17 | 20 (20 complete, 0 pruned) |
| XGBoost | 0.950842 | 5 | 81 | 90 (78 complete, 12 pruned) |
| TabNet | 0.921225 | 3 | 16 | 20 (15 complete, 5 pruned) |

Source: outputs/02_training/model_comparison.csv, model metadata, and optuna_*_trials.csv. Random Forest has independently recorded best-trial fold SD of 0.021178. XGBoost and TabNet metadata values of 0.025954 and 0.019250 come from _safe_cv_std, which computes dispersion across recorded trial values, including non-null pruned values. They are not fold-level standard deviations and are not displayed as comparable CV error bars.

The XGBoost and TabNet *_cv_scores.csv files contain cumulative fold means reported to Optuna. A cumulative mean after successive folds is not an independent fold score. The final cumulative value agrees with the selected objective, but directly taking dispersion across these exports would answer the wrong question. Confirmed independent fold reporting remains a documentation dependency (Network Guardian IDS Team, 2026b, 2026i).

The saved models were evaluated on 36,396 frozen test connections with 43 features and the canonical class order. The exported prediction rows reproduce the reported per-class F1 and Macro F1 values. No training, tuning, or resplitting was performed for this manuscript integration. XGBoost achieved test Macro F1 of 0.945134, followed by Random Forest at 0.933095 and TabNet at 0.930622. (Network Guardian IDS Team, 2026h)

**Table 8. Frozen test-set comparison**

| Measure | Random Forest | XGBoost | TabNet |
| --- | --- | --- | --- |
| Test Macro F1 | 0.933095 | 0.945134 | 0.930622 |
| Test weighted F1 | 0.998905 | 0.998961 | 0.997602 |
| Test accuracy | 0.998901 | 0.998956 | 0.997555 |
| Normal recall | 0.999408 | 0.999044 | 0.996903 |
| DOS recall | 0.999707 | 0.999560 | 0.999414 |
| Probe recall | 0.984962 | 0.988722 | 0.992481 |
| R2L recall | 0.952000 | 0.992000 | 0.976000 |
| U2R recall | 0.769231 | 0.769231 | 0.769231 |
| Full-test prediction time (s) | 0.151 | 0.126 | 1.091 |

Sources: outputs/03_evaluation/test_set_evaluation.json and per_class_metrics.csv; weighted F1 and prediction times are recorded in the evaluation report. Timing covers prediction of the full test matrix in that run, not HTTP response time, model loading, or a repeated deployment benchmark. Complete hardware and repetition details are not supplied (Network Guardian IDS Team, 2026h).

**Table 9. Class precision and recall on the frozen test set**

| Class | Support | RF P | RF R | XGB P | XGB R | Tab P | Tab R |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Normal | 21958 | 0.998998 | 0.999408 | 0.999544 | 0.999044 | 0.999270 | 0.996903 |
| Dos | 13643 | 0.999780 | 0.999707 | 0.999707 | 0.999560 | 0.999707 | 0.999414 |
| Probe | 532 | 0.992424 | 0.984962 | 0.985019 | 0.988722 | 0.953069 | 0.992481 |
| R2L | 250 | 0.975410 | 0.952000 | 0.950192 | 0.992000 | 0.859155 | 0.976000 |
| U2R | 13 | 0.666667 | 0.769231 | 0.769231 | 0.769231 | 0.769231 | 0.769231 |

Source: outputs/03_evaluation/per_class_metrics.csv. P denotes precision and R recall. The normalized CSV adds support_fraction while retaining metrics on the 0–1 scale; its project-wide schema is not yet confirmed. The unambiguous standard metrics are used here.

### 5.2 Error Analysis

All three models missed the same three U2R records, identified at zero-based exported-row positions 20207, 30364, and 32453. RF and TabNet labeled all three normal. XGBoost labeled the first R2L and the other two normal. Equal family recall therefore reflects shared missed records, but the operational threat indicators differ for one case. This agreement does not establish a permanent detection ceiling or prove that the features are intrinsically inseparable.

**Table 10. Attack-family misses and operational detection errors**

| Model | U2R misses | R2L misses | Attack as normal | Normal as attack |
| --- | --- | --- | --- | --- |
| Random Forest | 3 | 12 | 22 | 13 |
| XGBoost | 3 | 2 | 10 | 21 |
| TabNet | 3 | 6 | 16 | 68 |

Source: outputs/03_evaluation/test_predictions.csv; counts reconstructed without refitting. An attack-family miss includes misclassification into another attack family. It differs from an undetected attack classified as normal. Normal-as-attack errors correspond to false alarms under the binary threat indicator.

XGBoost correctly classified 248 of 250 R2L records, compared with 238 for Random Forest and 244 for TabNet. Its R2L precision was 0.950192, below Random Forest at 0.975410 but above TabNet at 0.859155. This tradeoff prevents the higher R2L recall from being interpreted as superiority on every error measure. One U2R test error changes recall by approximately 7.69 percentage points; no significance test or operational error-cost model has been established.

### 5.3 Overfitting Analysis

Cross-validation objectives, in-sample performance, and test performance measure different conditions. The following table reports CV minus test Macro F1; it is not a training-minus-test or training-minus-validation gap.

**Table 11. Validation objective and held-out test difference**

| Model | CV mean | Test Macro F1 | CV minus test |
| --- | --- | --- | --- |
| Random Forest | 0.950540 | 0.933095 | 0.017445 |
| XGBoost | 0.950842 | 0.945134 | 0.005708 |
| TabNet | 0.921225 | 0.930622 | -0.009397 |

Sources: outputs/02_training/model_comparison.csv and outputs/03_evaluation/test_set_evaluation.json. The RF and XGBoost differences are 0.017445 and 0.005708; TabNet test Macro F1 exceeds its CV mean by 0.009397. Unequal fold support and one random test partition qualify interpretation; these differences alone cannot establish absence of overfitting.

A separate TabNet verification report records in-sample Macro F1 of 0.962640. Its difference from the recorded CV mean is 0.041415 and from test Macro F1 is approximately 0.032018. These comparisons are attributed to the report and are not newly generated training evaluations. Comparable full-training Macro F1 for RF and XGBoost remains unavailable (Network Guardian IDS Team, 2026c, 2026h).

### 5.4 Model Recommendation

XGBoost is the preferred candidate for this benchmark, with test Macro F1 of 0.945134, R2L recall of 0.992000, and recorded batch prediction time of 0.126 seconds. Its Macro F1 advantage over RF is 0.012039 and over TabNet 0.014512. No statistical significance or production-readiness claim is established.

All models tie on U2R recall. RF has fewer normal false alarms, so the recommendation depends on error tradeoffs. Independent validation, calibration, and real API checks for XGBoost and TabNet remain deployment requirements.

## VI. Results and Visualizations

The following figures were exported from the completed evaluation. The class-distribution plot uses frozen split counts; the remaining plots describe saved-model predictions on the test partition. They retain the original axes and class ordering. Sampled SHAP summaries, a local explanation, and TabNet attention analysis are presented below.

![Evaluation figure 1](../../outputs/03_evaluation/class_distribution.png)

**Figure 1. Class distribution in the frozen training and test partitions**

Source: outputs/03_evaluation/class_distribution.png.

![Evaluation figure 2](../../outputs/03_evaluation/confusion_matrix_rf.png)

**Figure 2. Random Forest confusion matrix on the frozen test set**

Source: outputs/03_evaluation/confusion_matrix_rf.png.

![Evaluation figure 3](../../outputs/03_evaluation/confusion_matrix_xgb.png)

**Figure 3. XGBoost confusion matrix on the frozen test set**

Source: outputs/03_evaluation/confusion_matrix_xgb.png.

![Evaluation figure 4](../../outputs/03_evaluation/confusion_matrix_tabnet.png)

**Figure 4. TabNet confusion matrix on the frozen test set**

Source: outputs/03_evaluation/confusion_matrix_tabnet.png.

![Evaluation figure 5](../../outputs/03_evaluation/pr_curve_u2r.png)

**Figure 5. U2R precision recall curves for the three saved models**

Source: outputs/03_evaluation/pr_curve_u2r.png.

![Evaluation figure 6](../../outputs/03_evaluation/pr_curve_r2l.png)

**Figure 6. R2L precision recall curves for the three saved models**

Source: outputs/03_evaluation/pr_curve_r2l.png.

![Evaluation figure 7](../../outputs/03_evaluation/model_comparison_visual.png)

**Figure 7. Model comparison from the frozen test evaluation**

Source: outputs/03_evaluation/model_comparison_visual.png.

Precision-recall curves describe probability ranking across thresholds; they do not establish calibration or a deployed alert threshold. The comparison graphic retains its source labels; any cross-validation dispersion shown must be interpreted under the reporting qualifications given in the validation table. (Network Guardian IDS Team, 2026h)

### 6.1 Model Explanations

TreeExplainer was applied to 1,000 sampled frozen-test records using random seed 42. Each observation explains its own predicted class; the combined summaries therefore mix output classes. The plots display the 20 leading features. Positive contributions concern the selected class output for that observation, not a common attack-versus-normal score. Absolute scales are not directly comparable between RF and XGBoost (Network Guardian IDS Team, 2026l).

![Evaluation figure 8](../../outputs/03_evaluation/shap_summary_rf.png)

**Figure 8. Random Forest predicted-class SHAP summary on 1,000 test records**

Source: outputs/03_evaluation/shap_summary_rf.png.

The RF summary ranks service_freq, src_bytes, and dst_bytes highest, followed by count. These fields describe service prevalence and traffic volume in the engineered representation. Because the explained class changes between records, a positive contribution cannot be read as a universal increase in attack probability. The figure summarizes the sampled population rather than establishing rare-class feature effects.

![Evaluation figure 9](../../outputs/03_evaluation/shap_summary_xgb.png)

**Figure 9. XGBoost predicted-class SHAP summary on 1,000 test records**

Source: outputs/03_evaluation/shap_summary_xgb.png.

The XGBoost summary also ranks service_freq first, followed by count and src_bytes. flag_S0 and host statistics contribute to the displayed ordering. Agreement on some leading fields indicates shared use of the prepared representation, not proof that a field causes an intrusion or that the models use identical decision rules. Different model-output units qualify comparisons of SHAP magnitudes.

![Evaluation figure 10](../../outputs/03_evaluation/shap_local_example.png)

**Figure 10. XGBoost U2R explanation for test row 29522**

Source: outputs/03_evaluation/shap_local_example.png.

The local example is a correctly classified U2R record selected for the highest recorded XGBoost U2R confidence among correct candidates. The saved probability is approximately 0.999486. The displayed class-output score is 5.551 relative to a baseline of 0.957; those waterfall values are not probabilities. Duration and dst_bytes show positive contributions of approximately 1.69 and 1.35, while root_shell and num_file_creations also contribute positively. Duration and byte values are log-transformed model inputs, not raw seconds or byte counts (Network Guardian IDS Team, 2026l).

This selected success case cannot explain the three missed U2R records or establish typical U2R behavior. Inspection of failed cases and additional rare-class data remains necessary. Some source waterfall annotations are abbreviated or truncated; the interpretation uses clearly legible values and does not reconstruct missing labels.

![Evaluation figure 11](../../outputs/03_evaluation/tabnet_attention_mask.png)

**Figure 11. TabNet attention averaged over decision steps and 1,000 test records**

Source: outputs/03_evaluation/tabnet_attention_mask.png.

The attention plot averages feature-selection masks across decision steps and a separately drawn 1,000-record test sample. Its leading fields are service_freq, dst_host_diff_srv_rate, same_srv_rate, and protocol_type_tcp. This aggregate describes how the saved model allocates feature selection; it removes variation between individual records and steps. The TabNet sample is drawn after the tree sample from the same seeded generator, so the analysis does not assume identical sampled records.

SHAP contributions and attention-mask averages answer different questions and are not interchangeable importance scores. Predicted-class pooling, finite samples, and selection of a high-confidence correct local example limit conclusions about rare failures. These descriptive outputs provide no causal proof, calibrated risk estimate, preprocessing ablation, or evidence that the shared U2R misses are unavoidable. These offline explanations do not establish live-route readiness for TabNet or XGBoost.

## VII. Discovery Log

The development process revealed issues involving dependency compatibility, source-schema interpretation, label serialization, model persistence, and numerical reporting. These observations informed verification procedures and identified limitations relevant to reproducibility. Historical observations are attributed to the project records; locally reproduced checks are distinguished from reported events.

### 7.1 Environment and schema issues

The initial environment setup encountered an installation failure when the pinned dependencies were used with Python 3.13. Recreating the environment with Python 3.11.9 resolved the compatibility issue. A separate parsing error arose from assuming that the feature manifest explicitly defined the target column. The manifest contains an attack header and 41 feature definitions; the label column is implicit. Appending the label and including the normal class corrected the schema and target coverage (Network Guardian IDS Team, 2026a).

### 7.2 Label serialization and onboarding verification

The preparation workflow initially generated label arrays that could not be loaded with allow_pickle=False. A duplicate export cell overwrote fixed-width Unicode labels with object arrays. Removing the duplicate cell resolved the serialization error. Re-execution produced the expected shapes and Unicode dtypes, and the four reference hashes matched. The incident demonstrates the importance of verifying artifacts after the complete export sequence.

### 7.3 TabNet artifact verification

Model persistence initially produced a duplicated zip extension for the TabNet artifact. Correcting the filename and path-verification code allowed the saved model to load successfully. Metadata inspection also distinguished training recall from validation recall. Persistence verification establishes that an artifact can be accessed; it does not establish its predictive performance on unseen data (Network Guardian IDS Team, 2026c).

### 7.4 Lessons and remaining evidence

A central methodological lesson was to distinguish preparation findings, training diagnostics, validation objectives, and held-out evaluation. Completed test exports now support model comparison. Sampled global explanations and one local success case are now included; explanations of missed attacks, comparable training metrics, corrected fold reporting, and deployment verification remain open. Numerical agreement alone does not resolve these questions.

### 7.5 Backend verification

Backend verification passed 13 functional checks and a real RF request. The frontend now uses real evaluation data and enables the live endpoint. XGBoost receiving-device verification and a real TabNet API request remain open (Network Guardian IDS Team, 2026g, 2026k).

### 7.6 Final refit and metric reporting

The first XGBoost final-refit attempt required an eval_set because early stopping was still enabled. The corrected builder disables early stopping for refit and preserves the optimization study. The saved XGBoost study contains more trials than its per-invocation budget. Source inspection also distinguishes cumulative fold reports and trial-level dispersion from independent validation-fold statistics (Network Guardian IDS Team, 2026i).

## VIII. Executive Summary

### What problem did we set out to solve and why does it matter

We compare three learning methods for distinguishing normal network connections from four attack families. Missed rare attacks and false alarms matter as much as aggregate correctness.

### What did we discover about the data that shaped our decisions

The supplied file contains 494,021 records, substantial duplication, and only 52 U2R examples. Preparation retained 145,584 records, split into 109,188 training and 36,396 test rows with 43 encoded inputs.

### Which approaches did we compare and how did we judge them

Random Forest, XGBoost, and TabNet were evaluated on the same frozen test set. Macro F1 gives each class equal weight. Test scores were 0.933095, 0.945134, and 0.930622, respectively; class recall and measured prediction times describe additional tradeoffs.

### What do we recommend and what evidence supports it

XGBoost is the preferred candidate for this benchmark. It had the highest test Macro F1, R2L recall of 0.992000, and the shortest recorded full-test prediction time of 0.126 seconds. All models detected the same 10 of 13 U2R cases; deployment readiness still requires further checks.

### What are the limitations of our work and what would we do next

The historical simulated benchmark, only 13 U2R test records, preprocessing outside individual validation folds, and unequal optimization budgets limit generalization. Comparable training metrics and complete runtime provenance remain pending. The SHAP summaries and TabNet attention plot use samples of 1,000 test records; the local SHAP plot shows one selected, correctly classified U2R case. Future work should explain missed cases, use newer traffic, fit preprocessing within folds, and conduct controlled ablations.

### What was our biggest mistake or surprise and what did we learn from it

A duplicate notebook export replaced the corrected label format; the fixed notebook now passes verification. Later auditing distinguished cumulative fold means and trial dispersion from independent fold scores. The lesson is to verify both artifact contents and metric definitions.

## IX. Reflection

Individual reflections will address learning about intrusion detection, data preparation, model comparison, encountered challenges, responses to unexpected results, evaluation beyond accuracy, real-world applicability, and possible improvements. Each reflection must represent the corresponding author's own experience.

### Kit Dustin

[Individual reflection to be provided by the corresponding author.]

### Markie

[Individual reflection to be provided by the corresponding author.]

### Amber

[Individual reflection to be provided by the corresponding author.]

### Kenneth

[Individual reflection to be provided by the corresponding author.]

### Dwayne

[Individual reflection to be provided by the corresponding author.]

## X. References

ACM SIGKDD. (n.d.). KDD Cup 1999 computer network intrusion detection. https://www.kdd.org/kdd-cup/view/kdd-cup-1999/Tasks

Akiba, T., Sano, S., Yanase, T., Ohta, T., & Koyama, M. (2019). Optuna: A next-generation hyperparameter optimization framework [Preprint]. arXiv. https://arxiv.org/abs/1907.10902

Arik, S. O., & Pfister, T. (2019). TabNet: Attentive interpretable tabular learning [Preprint]. arXiv. https://arxiv.org/abs/1908.07442

Breiman, L. (2001). Random forests. Machine Learning, 45, 5-32. https://doi.org/10.1023/A:1010933404324

Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, 785-794. https://doi.org/10.1145/2939672.2939785

Lundberg, S. M., & Lee, S.-I. (2017). A unified approach to interpreting model predictions [Preprint]. arXiv. https://arxiv.org/abs/1705.07874

Network Guardian IDS Team. (2026a). Environment and data preparation reports and reproducible artifacts [Project documentation]. docs/reports/role-1-phase-1-kit-environment-setup.md; docs/reports/role-1-phase-2-kit-data-preparation.md; notebooks/01_EDA_and_Data_Prep.ipynb; data/processed/split_indices.json; data/processed/feature_names.json.

Network Guardian IDS Team. (2026b). Model architecture and execution specifications [Project documentation]. src/models.py; docs/contracts/role-3-rf-architecture-spec.md; docs/contracts/role-4-training-execution-spec.md; docs/contracts/role-5-training-execution-spec.md.

Network Guardian IDS Team. (2026c). TabNet execution and artifact verification [Unpublished research record]. docs/reports/role-5-tabnet-training-verification-report.md; outputs/02_training/optuna_tabnet_trials.csv; outputs/02_training/tabnet_cv_scores.csv.

Network Guardian IDS Team. (2026d). Frontend scaffold and API data contract [Project documentation]. docs/reports/role-3-phase-1-amber-frontend-scaffold.md; docs/contracts/api_data_contract.md.

Network Guardian IDS Team. (2026e). Role 2 documentation and setup verification [Project documentation]. docs/reports/role-2-phase-1-markie-documentation-scaffolding.md; docs/reports/discovery_log.md.

Network Guardian IDS Team. (2026f). Random Forest configuration and validation statistics [Unpublished research record]. models/rf_baseline.meta.json; docs/reports/role-3-phase-2-amber-rf-baseline.md.

Network Guardian IDS Team. (2026g). Backend inference implementation and functional verification [Unpublished research record]. docs/reports/role-2-phase-2-markie-backend-bridge.md; server/server.js; server/predict_bridge.py; server/validate.js; server/tests.

Network Guardian IDS Team. (2026h). Frozen test evaluation and saved prediction outputs [Research record]. docs/reports/role-5-phase-3-dwayne-evaluation-suite.md; outputs/03_evaluation/test_set_evaluation.json; outputs/03_evaluation/per_class_metrics.csv; outputs/03_evaluation/test_predictions.csv; outputs/03_evaluation/*.png.

Network Guardian IDS Team. (2026i). XGBoost execution and validation reporting [Research record]. docs/reports/role-4-phase-2-kit-xgboost-execution.md; docs/handoffs/xgboost.md; outputs/02_training/optuna_xgb_trials.csv; src/models.py.

Network Guardian IDS Team. (2026j). Random Forest acceptance threshold decision [Project record]. docs/decision/decision_rf_cv_std_threshold_20261013.md.

Network Guardian IDS Team. (2026k). Frontend connection to the live backend [Project record]. docs/reports/role-3-phase-3-amber-frontend-backend-integration.md; client/src/lib/data.ts.

Network Guardian IDS Team. (2026l). Sampled model explanations and feature attention [Research record]. docs/reports/role-5-phase-4-dwayne-explainability.md; src/explainability.py; outputs/03_evaluation/shap_summary_rf.png; shap_summary_xgb.png; shap_local_example.png; tabnet_attention_mask.png. Repository snapshot 7108f414c049ca265bdd6b305e979abcd7a5c614.

UCI KDD Archive. (1999). KDD Cup 1999 data. https://kdd.ics.uci.edu/databases/kddcup99/kddcup99

### AI Tool Disclosure

OpenAI Codex was used to assist with environment setup, source review, manuscript drafting and formatting, preparation-artifact verification, and backend implementation and functional testing. ChatGPT was also used for troubleshooting and interpretation of execution errors. AI-generated assistance was not used to invent missing measurements or personal reflections. The authors remain responsible for validating the evidence, interpreting the results, and reviewing the final manuscript.
