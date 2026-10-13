# Network Guardian IDS — A Comparative Study of Bagging, Boosting, and Deep Attention Architectures for Multi-Class Network Intrusion Detection

Kit Dustin, Markie, Amber, Kenneth, and Dwayne

[Full author names and institutional affiliations to be completed]

Corresponding author: [Full name and email to be completed]

OCTOBER 2026

## Abstract

Background. Network intrusion detection requires reliable classification of common and rare attacks. Historical connection benchmarks support reproducible experiments, although strong aggregate performance may conceal failures on underrepresented categories.

Objective. This study compares bagging, gradient boosting, and deep tabular attention through Random Forest, XGBoost, and TabNet, emphasizing five-class prediction, rare-attack recall, reproducibility, and deployment requirements.

Methods. The supplied KDD Cup 1999 file contains 494,021 records and 41 predictors. Duplicate removal yields 145,584 records. A stratified 75 percent training and 25 percent test partition produces 109,188 and 36,396 records, respectively. Transformation and categorical encoding yield 43 ordered inputs. Optimization uses Macro F1, class weighting, and Tomek Links within training folds. Tree ensembles use five validation folds; TabNet uses three because only 39 U2R records occur in training.

Results. The available Random Forest study reports validation Macro F1 of 0.950540 with standard deviation 0.021178 and out-of-bag Macro F1 of 0.949575. Pooled validation U2R recall is 0.820513. These values describe validation rather than held-out performance. Preparation artifacts were reproduced, and 13 backend functional checks passed. Complete XGBoost results, reconciled TabNet validation statistics, test metrics, runtime measurements, and explanation figures remain unavailable.

Conclusion. The evidence supports a reproducible preparation pipeline and an initial validation baseline. It does not establish a preferred classifier. Rare-class support, preprocessing outside individual folds, and inconsistent TabNet training and inference transformations constrain interpretation. Complete evaluation and stricter preprocessing isolation are required before comparative conclusions or operational deployment claims can be justified. The reported evidence remains provisional until these analyses are completed.

### Keywords

Intrusion Detection; Machine Learning; KDD Cup 1999; Explainable AI; Tabular Deep Learning; Anomaly Detection.

## 1. Introduction

### 1.1 Motivation

Network intrusion detection requires distinguishing legitimate connections from activity that threatens the confidentiality, integrity, or availability of a system. A machine learning classifier approaches this task by learning relationships between connection attributes and labeled outcomes. Network Guardian IDS investigates this approach through a five class classification problem using network connection records. The project compares alternative learning methods and examines whether their errors differ across common and rare attack families.

The benchmark task concerns connection level classification rather than direct inspection of live packet streams. KDD Cup 1999 draws on a simulated network environment associated with the 1998 DARPA intrusion detection evaluation. This origin provides a reproducible research setting but limits the conclusions that can be drawn about current operational traffic (ACM SIGKDD, n.d.-a). The project therefore evaluates a research prototype rather than claiming production readiness.

### 1.2 Problem Statement

The target classes are normal, denial of service, probe, remote to local, and user to root. Denial of service attacks interfere with service availability, probing seeks information about hosts or services, remote to local attacks seek unauthorized access from a remote system, and user to root attacks seek elevated privileges from an existing user context (ACM SIGKDD, n.d.-a). Each record receives one family label; the project does not infer the full attack sequence from that label alone.

Class imbalance is central to the research problem. The prepared training partition contains 65,874 normal connections but only 39 user to root examples. A model can perform well on frequent classes while failing on the rarest category. Accordingly, the comparison emphasizes Macro F1 and class level recall alongside aggregate measures. The operational significance of a missed attack and the burden of a false alarm must both be considered.

The research problem is to assign a connection to normal, DoS, probe, R2L, or U2R using an engineered tabular representation. The class distribution creates unequal statistical support: 13 U2R examples are reserved for testing, while normal traffic has 21,958. Reliable interpretation requires class-level counts and recall, rather than reliance on accuracy alone.

### 1.3 Research Questions

The primary objective is to compare Random Forest, XGBoost, and TabNet using a shared prepared representation and a frozen training and test partition. The study asks how the three approaches differ in overall classification quality, detection of rare attack families, computational requirements, and the explanations available to an analyst. A second objective is to document the preparation decisions and execution difficulties that affect reproducibility.

The comparison is designed around one prepared pipeline. It does not isolate the causal contribution of each transformation because no preprocessing ablation is currently included. Any claim that a particular transformation improves detection will require a separate controlled experiment. Final model recommendations will be based on confirmed training and evaluation artifacts rather than anticipated rankings.

### 1.4 Contributions

The study contributes a documented comparison protocol for three learning families, a reproducible preparation snapshot with explicit feature ordering, and a prototype inference interface. The current manuscript also identifies limitations in validation reporting and preprocessing isolation. Comparative superiority and operational effectiveness remain empirical questions until the complete evaluation is available.

### 1.5 Paper Organization

Section 2 establishes the background and related work. Section 3 describes the data and preparation, followed by methodology in Section 4 and experimental conditions in Section 5. Section 6 separates available results from pending measurements. Section 7 defines the explainability analysis, Section 8 discusses interpretation and validity, and Section 9 presents conclusions and future work. The appendices retain configuration tables, evaluation inventory, and reproducibility instructions.

## 2. Background and Related Work

### 2.1 Intrusion Detection Systems

Intrusion detection examines system or network activity for indications of security violations. Network-based, host-based, and network behavior analysis systems differ in observation points and available context. This project operates on already extracted connection features and does not implement the full acquisition and response functions of an operational detection system (Scarfone & Mell, 2007).

#### 2.1.1 Signature based Detection

Signature-based methods compare observed activity with representations of known threats. They provide a direct basis for recognizing previously characterized patterns, while coverage depends on the signatures available. The present classifier uses labeled connection records rather than a rule database (Scarfone & Mell, 2007).

#### 2.1.2 Anomaly based Detection

Anomaly-based methods compare activity with an expected behavioral profile. A deviation may indicate an attack or an unusual legitimate event, making false alarms relevant to interpretation. Supervised attack-family classification should not automatically be described as detection of unseen attack types (Scarfone & Mell, 2007).

#### 2.1.3 Hybrid Approaches

Complementary detection methods can be combined within a security architecture (Scarfone & Mell, 2007). In this project, the compared algorithms are separate candidates. No stacked ensemble, fused probability model, or combined signature-and-anomaly detector has been evaluated; the system title alone does not establish such a capability.

### 2.2 Machine Learning for Tabular Classification

The selected methods represent different ways to learn from the same ordered feature vector. Their evaluation shares the target definition and test partition, while retaining differences in validation-fold count and configured optimization budget. These differences prevent the study from being interpreted as a controlled comparison of equal training cost.

#### 2.2.1 Bagging Ensembles

Breiman (2001) describes Random Forest as an ensemble of randomized tree predictors. Random sampling and feature selection produce diverse trees whose predictions are aggregated. Out-of-bag estimates use records omitted from an individual tree bootstrap sample. These estimates provide an internal diagnostic, while the independent test partition remains necessary for the project comparison.

#### 2.2.2 Gradient Boosting

Chen and Guestrin (2016) present XGBoost as a scalable tree boosting system with sparse-data handling and regularized tree learning. Sequential tree construction differs from the aggregation of independently randomized trees. The method motivates a boosting candidate in this study, but its published engineering advantages do not determine its ranking on the prepared intrusion dataset.

#### 2.2.3 Deep Tabular Architectures

Arik and Pfister (2019) introduce TabNet, which uses sequential attention to select features during processing of tabular records. Its architecture supplies feature-selection masks as part of the network computation. A shared input dimension permits comparison with the tree models, but optimization, stopping, and representation choices must still be accounted for.

### 2.3 Explainable AI in Security

#### 2.3.1 SHAP

Lundberg and Lee (2017) define an additive feature-attribution framework that assigns contributions to a particular prediction. In security analysis, such attributions can describe which encoded fields influenced a classifier response. Their interpretation depends on the explained class and reference distribution; they do not establish an attack cause.

#### 2.3.2 Attention based Interpretability

TabNet attention masks describe the features selected by the model at its decision steps (Arik & Pfister, 2019). They address a different question from additive SHAP contributions. The study will interpret each explanation according to its construction and will avoid treating the two outputs as interchangeable quantitative importance scores.

### 2.4 The KDD Cup 1999 Benchmark

#### 2.4.1 Dataset Description

KDD Cup 1999 poses a predictive task distinguishing normal connections from intrusions. Its records derive from a simulated environment associated with the 1998 DARPA evaluation. The supplied file is treated as the project input snapshot; its size and class counts are verified locally rather than assumed to describe every benchmark release (ACM SIGKDD, n.d.-a; Network Guardian IDS Team, 2026a).

#### 2.4.2 Known Limitations

The historical simulated origin limits transfer to present-day traffic. Local profiling also shows extensive duplication and few U2R records. Duplicate removal changes the relative class frequencies, while random stratification evaluates a different condition from time-based transfer or entirely unseen attack families. No contemporary operational detection claim follows from this benchmark alone.

#### 2.4.3 Published Baselines

The official archive identifies the original competition winners and preserves the historical evaluation context (ACM SIGKDD, n.d.-b). Those outcomes are not numerical baselines for the present split. Before comparing a published score, the analysis must establish matching target definitions, duplicate treatment, training and test files, and metric definitions. No literature-derived performance number is presented as a directly comparable baseline in this draft.

## 3. Dataset and Preprocessing

### 3.1 Data Source and Schema

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

### 3.2 Target Definition

Twenty-two attack names and the explicitly added normal category are mapped to five canonical families. The class manifest controls decoding. Predictor fields contain connection attributes; the original label is excluded from the model input vector. Label spelling and punctuation normalization are handled by the preparation code.

### 3.3 Class Balance and Rare Classes

Before duplicate removal, DoS accounts for 391,458 records compared with 97,278 normal connections. Afterwards normal records number 87,832 and DoS records number 54,571. U2R retains 52 examples across the complete prepared dataset. These counts motivate stratification and equal class weighting in the objective, but do not remove the uncertainty caused by sparse support.

### 3.4 Feature Description

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

### 3.5 Cleaning and Duplicate Removal

The pipeline parses the raw feature manifest, appends the implicit label column, and maps attack names to their canonical families. Normal is injected into the mapping because it is absent from the attack manifest. Duplicate removal compares the 41 input features rather than the label. When identical feature vectors have different labels, the first record is retained. This policy reduces repeated examples across the subsequent split but also requires scrutiny of any conflicting labels that may be discarded.

### 3.6 Constant and Correlated Feature Removal

Two constant variables, num_outbound_cmds and is_host_login, were removed. Absolute Pearson correlations were then computed among the numerical variables. For pairs with correlation greater than 0.90, the later variable in the original column order was removed. The excluded correlated variables were dst_host_rerror_rate, dst_host_serror_rate, dst_host_srv_count, num_compromised, rerror_rate, serror_rate, srv_rerror_rate, and srv_serror_rate. The resulting representation contained 28 numerical and three categorical variables before encoding.

Constant detection and correlation pruning preceded the training and test split. These transformations therefore used the complete feature pool, including records subsequently assigned to the test partition. Although target labels were not used for these selection steps, this design limits claims of fully isolated preprocessing. Future experiments should estimate data-dependent feature selection within training folds.

### 3.7 Transformation and Categorical Encoding

The duration, src_bytes, and dst_bytes fields receive log(1 + x) transformations to compress large numerical ranges while retaining zero values. Service is frequency encoded using the training partition, with unseen services mapped to zero. Protocol and flag are one hot encoded using training fitted categories; unknown values produce zeros for the corresponding block. The final representation contains 28 numerical features, one service frequency, three protocol indicators, and 11 flag indicators, totaling 43 ordered inputs.

### 3.8 Partitioning and Scaling

A stratified 75 percent training and 25 percent test split uses random state 42. The resulting arrays contain 109,188 training rows and 36,396 test rows. Features are float64 and labels are fixed width Unicode. A StandardScaler is fit on the training partition and saved for the intended TabNet inference pipeline. The current TabNet training functions receive the loaded engineered arrays without applying that saved scaler. Training and inference transformations must be reconciled before integration. Tree models use the unscaled engineered representation. The saved JSON manifests specify the input order, class order, and frozen split, while saved encoders provide the inference transformation.

The categorical encoders and scaler were fitted to the complete training partition rather than refitted within each cross-validation fold. Validation-fold covariates therefore contributed to preprocessing statistics. The held-out test partition was excluded from their fitting. Cross-validation estimates should be interpreted with this qualification; fold-specific preprocessing would provide a stricter assessment during model selection.

### 3.9 Imbalance Handling and Artifact Verification

Tomek Links is applied to each fold training subset, followed by class weighting. Validation and test records are not resampled. Frozen arrays are accompanied by feature and class manifests, fitted encoders, a saved scaler, and split indices. Re-execution verified the expected array shapes, Unicode label representation, and four reference hashes (Network Guardian IDS Team, 2026a, 2026e).

## 4. Methodology

### 4.1 Task Definition and Formal Notation

Let D = {(x_i, y_i)} contain the prepared observations, where x_i is a vector of 43 ordered inputs and y_i belongs to C = {normal, dos, probe, r2l, u2r}. A model f_theta maps x_i to five class probabilities; the predicted family is the class with the highest probability. The stored model class identifiers determine probability-column decoding. A probability percentage is a classifier output and has not been established as a calibrated operational risk estimate.

For class c, precision P_c = TP_c / (TP_c + FP_c), recall R_c = TP_c / (TP_c + FN_c), and F1_c = 2 P_c R_c / (P_c + R_c). Macro F1 = (1/5) sum_c F1_c. Reported class support is the number of true observations for that family. The evaluation must state its treatment of zero denominators and preserve the complete class order.

### 4.2 Candidate Models

#### 4.2.1 Random Forest

Random Forest combines decision trees trained with random sampling of records and candidate split features. Aggregation provides a bagging baseline for tabular classification (Breiman, 2001). Bootstrap sampling, out-of-bag estimation, and class weighting are included in the experimental configuration. These mechanisms support comparison without guaranteeing reliable detection of rare attacks.

#### 4.2.2 XGBoost

XGBoost is a regularized gradient tree boosting framework that builds an additive ensemble through sequential optimization (Chen & Guestrin, 2016). The implementation assigns class weighted sample weights and evaluates candidate configurations using five fold stratified validation. The search budget is 30 trials and the objective is the mean Macro F1 across validation folds. Validation based early stopping uses a patience of 20 rounds.

#### 4.2.3 TabNet

TabNet applies sequential attention to feature selection in a neural network for tabular data. Its attention masks offer a model specific view of feature usage (Arik & Pfister, 2019). The project implementation uses CPU execution, an Adam optimizer with learning rate 0.02, at most 30 epochs, and validation based early stopping with patience 10. Architecture tuning includes decision and attention widths, decision steps, attention relaxation, sparsity regularization, transformer sharing, momentum, mask type, and batch sizes.

Table 3 summarizes the experimental configuration. Random Forest selected parameters are described in Appendix A. Execution times and unavailable performance values remain unreported. Training recall, validation recall, and test recall are treated as distinct quantities.

**Table 3. Experimental model configuration**

| Item | Random Forest | XGBoost | TabNet |
| --- | --- | --- | --- |
| Family | Bagging | Gradient boosting | Tabular attention |
| Input features | 43 | 43 | 43 |
| Training rows before resampling | 109,188 | 109,188 | 109,188 |
| Reserved test rows | 36,396 | 36,396 | 36,396 |
| Configured trials | 20 | 30 | 20 |
| Validation folds | 5 | 5 | 3 |
| Random state | 42 | 42 | 42 |
| Selected parameters | Trial 17 | Not available | Under verification |
| Model artifact | rf_baseline.joblib | xgb_optuna.joblib | tabnet_best.zip |
| Measured runtime | Not available | Not available | Not available |
| Test metrics | Not available | Not available | Not available |

Sources: model configuration records, prepared-data manifests, and documented execution results (Network Guardian IDS Team, 2026b, 2026c, 2026f). Configured budgets describe the intended study and must not be substituted for the actual completed and pruned trial counts.

### 4.3 Hyperparameter Optimization

Optuna searches bounded model-specific spaces using validation Macro F1 (Akiba et al., 2019). The configured trial budgets are 20 for Random Forest, 30 for XGBoost, and 20 for TabNet. Search ranges and available selected configurations appear in Appendix A. These budgets cannot be used as measured completed-trial counts, and optimization cost is not equalized across architectures.

### 4.4 Cross Validation and Final Refit

The implementations use a shared random state and persist optimization studies for traceability. Optuna selects configurations according to validation Macro F1; pruning can stop unpromising trials before they consume the full budget (Akiba et al., 2019). Tomek Links removes selected boundary examples from fold training data, while validation subsets are not resampled. Class weights increase the contribution of less frequent classes. The final test partition is reserved for Notebook 03 and is not passed to model tuning functions.

Macro F1 is the arithmetic mean of the five class F1 values. For each class, precision measures how many predicted members are correct, recall measures how many actual members are recovered, and F1 balances precision and recall. Equal class weighting prevents the most frequent category from dominating the summary. Per class support and confusion matrices remain necessary because the same Macro F1 can arise from different error patterns.

Each trial was assessed with five stratified folds. Tomek Links and class weighting were restricted to the fold training subset; validation predictions were used to calculate Macro F1. After selection, the Random Forest was refitted on the cleaned training pool, with the test partition reserved for subsequent evaluation (Network Guardian IDS Team, 2026b, 2026f).

The configured study uses 30 Optuna trials and five stratified folds. Weighted fold training uses Tomek Links followed by class weights, and validation-based early stopping has a patience of 20 rounds. The selected configuration is refitted on the cleaned training pool. Actual execution counts and selected parameters require the completed training record; configured budgets are not completed-run measurements (Network Guardian IDS Team, 2026b).

TabNet uses 20 configured Optuna trials and three stratified validation folds. With 39 U2R training records, three folds place approximately 13 examples in each validation fold, compared with roughly seven or eight under five folds. This increases support per fold but does not establish that the rare class estimate is stable. The different fold counts must remain visible when comparing the algorithms. Tomek Links is restricted to fold training subsets. The final refit includes an internal 10 percent validation subset for early stopping rather than unrestricted training on the entire pool.

### 4.5 Evaluation and Error Analysis

Error analysis will distinguish missed attacks, false alarms, and confusion between attack families. A false negative occurs when an attack is classified as normal; a false positive occurs when normal traffic is classified as an attack. Rates will be accompanied by counts and class support, particularly for the 13 U2R test examples.

Observed error counts and confusion patterns will be reported after completion of held-out evaluation.

The held-out evaluation will report Macro F1, weighted F1, per-class precision, recall and F1, confusion matrices, and execution measurements. False-negative and false-positive counts must be interpreted with class support. With 13 U2R test records, one additional error changes recall by approximately 0.0769, or 7.69 percentage points. A fine-grained ranking based on this category therefore requires caution.

### 4.6 Inference Architecture

The backend implements POST /api/analyze on localhost port 5000. It validates the 31 raw categorical and numerical request fields before starting the repository virtual environment Python interpreter. The bridge applies logarithmic transformations and the frozen encoders, reconstructs the 43 feature columns in their stored order, checks model metadata, and decodes probability columns using the model class identifiers. This avoids dependence on JSON key order and prevents incorrect family decoding when a classifier uses a different probability column order.

Successful requests return a family label, confidence percentage, threat indicator, and model identifier. Invalid requests return HTTP 400. Missing artifacts, bridge failures, invalid model outputs, and timeouts return HTTP 500 with a structured error. The frontend must treat an error envelope as a failed request; its default normal field is not a prediction. The service uses bounded request and response sizes and a per-request timeout.

Functional verification passed 10 Node API tests and three Python bridge tests. A real HTTP inference request using the RF artifact returned a valid response, and reversing the raw JSON key order preserved that response. These checks establish tested interface behavior, not classifier accuracy. No training or test-set evaluation was performed during backend verification (Network Guardian IDS Team, 2026g).

The inference bridge supports the XGBoost artifact format, although real-model integration has not yet been verified. TabNet inference remains disabled because the specified inference transformation includes scaling whereas the training implementation consumes unscaled engineered arrays. Matching the training and inference representation is a prerequisite for enabling this model. Complete dashboard integration has not yet been verified.

## 5. Experiments

### 5.1 Experimental Setup

The experiments use the prepared arrays with a fixed partition and random state 42. Python 3.11.9 was verified during setup. The recorded software pins include NumPy 1.26.0, pandas 2.1.1, scikit-learn 1.3.1, XGBoost 2.0.0, PyTorch 2.1.0, pytorch-tabnet 4.1.0, Optuna 3.4.0, imbalanced-learn 0.11.0, and SHAP 0.44.0. These environment specifications support reproduction but do not imply identical numerical behavior on every device (Network Guardian IDS Team, 2026a, 2026e).

### 5.2 Hardware and Runtime

The TabNet implementation specifies CPU execution. Complete processor, memory, operating-system, and runtime records for all model executions are not available in the evidence used here. Training duration and per-record or batch inference latency remain unreported. Subsequent measurements must identify the hardware, batch size, timing scope, and repetitions before computational comparisons are made.

### 5.3 Training Protocol

The tree models use five stratified folds, while TabNet uses three. The reduced TabNet fold count increases the number of rare-class validation examples per fold. XGBoost uses early-stopping patience 20; TabNet uses at most 30 epochs with patience 10 and an internal 10 percent validation subset during final refit. The categorical encoders are not refitted within each fold, which qualifies the cross-validation estimates.

### 5.4 Reproducibility

The repository preserves transformation artifacts, manifests, optimization studies, configuration records, and source reports. Duplicate notebook export logic initially replaced Unicode labels with object arrays, preventing safe NumPy loading. Removing the duplicate cell and re-executing the preparation notebook restored the intended representation and hash checks. Reproducibility therefore depends on verifying final artifacts after the entire notebook sequence, not only on successful execution of an intermediate cell (Network Guardian IDS Team, 2026a, 2026e).

## 6. Results

### 6.1 Preparation Findings

Preparation retained 145,584 unique feature vectors and produced a 43-column engineered representation. The observed class frequencies and raw feature ranges are documented in Section 3. These are findings about the data and transformation pipeline; they are not measurements of classifier generalization.

The available preparation figures summarize class balance and numerical correlation. They document the input data and feature selection context, rather than classifier performance. Final confusion matrices, precision recall curves, and explanation plots will be added after completion of held-out evaluation.

![Preparation figure 1](../../outputs/01_eda/family_distribution.png)

**Figure 1. Class distribution before and after deduplication**

Source: outputs/01_eda/family_distribution.png, generated by Notebook 01. Raw DoS frequency is reduced substantially by duplicate removal, while U2R remains rare.

![Preparation figure 2](../../outputs/01_eda/correlation_heatmap.png)

**Figure 2. Absolute Pearson correlation before correlation pruning**

Source: outputs/01_eda/correlation_heatmap.png, generated by Notebook 01. Strongly correlated fields motivate removal of later columns under the fixed 0.90 threshold.

### 6.2 Available Random Forest Validation

The Random Forest training record reports cross-validation Macro F1 of 0.950540, with a standard deviation of 0.021178 across five folds. Out-of-bag Macro F1 was 0.949575. Pooled validation recall was 0.999605 for normal, 0.999805 for DoS, 0.992491 for probe, 0.958611 for R2L, and 0.820513 for U2R. These recalls were reconstructed from validation targets and predictions. They describe performance within the training study and do not constitute held-out test results (Network Guardian IDS Team, 2026f).

The Random Forest cross-validation standard deviation exceeded the prespecified 0.02 threshold by approximately 0.001178. This deviation is retained as a limitation of the validation result. It does not establish model instability on its own, but requires consideration alongside fold-level performance and held-out evaluation.

Held-out test metrics and execution times are not yet available.

### 6.3 Comparative Evaluation

Only the available Random Forest validation summary is reported. The complete test comparison remains to be established.

**Table 4. Available validation summary and pending test comparison**

| Measure | Random Forest | XGBoost | TabNet |
| --- | --- | --- | --- |
| CV Macro F1 and dispersion | 0.950540 and SD 0.021178 | Not available | Not available |
| Test Macro F1 | Not available | Not available | Not available |
| Test weighted F1 | Not available | Not available | Not available |
| Normal recall | Not available | Not available | Not available |
| DoS recall | Not available | Not available | Not available |
| Probe recall | Not available | Not available | Not available |
| R2L recall | Not available | Not available | Not available |
| U2R recall | Not available | Not available | Not available |
| Training time | Not available | Not available | Not available |
| Prediction time | Not available | Not available | Not available |

Table 4 separates the available RF validation result from unmeasured test outcomes. Pooled validation recalls appear in Section 6.2. A complete comparison requires verified results for all three models (Network Guardian IDS Team, 2026f).

### 6.4 Training and Validation Comparison

**Table 5. Training and validation comparison pending verified measurements**

| Model | Train Macro F1 | Validation Macro F1 | Gap |
| --- | --- | --- | --- |
| Random Forest | Not available | 0.950540 | Not available |
| XGBoost | Not available | Not available | Not available |
| TabNet | Under verification | Under verification | Under verification |

Training performance, cross validation performance, and test performance measure different conditions. A training to validation gap can indicate optimism but cannot by itself prove severe overfitting. The analysis will consider the final refit procedure, trial selection, fold construction, and the preprocessing limitations identified in Section 3. A high training recall for a rare class does not establish that the class generalizes to unseen records.

Complete training, validation, and test comparisons are not yet available.

## 7. Explainability Analysis

### 7.1 Global and Local Tree Explanations

Global SHAP summaries will describe patterns in feature contributions for a specified evaluation subset and class output. A local explanation will describe one prediction with its feature values and reference context. Encoded columns must be labeled with the frozen manifest, and any aggregation of one-hot columns must be documented. No SHAP figure or numerical attribution is available for empirical interpretation in this draft.

### 7.2 TabNet Attention Masks

Attention visualization will identify the model decision steps and the selected inputs for the explained records. The analysis will consider whether sparse masks consistently emphasize particular connection attributes and whether those selections differ by predicted family. No claim about observed attention patterns can be made until the explanation artifacts are available.

### 7.3 Interpretive Limits

Confusion matrices, rare-class precision-recall curves, SHAP plots, and attention visualizations will be presented after the designated evaluation is completed.

SHAP attributes a prediction to input features through an additive explanation framework (Lundberg & Lee, 2017). TabNet masks indicate feature selection within its own architecture. These explanations describe model behavior and should not be presented as causal proof that a connection is malicious.

## 8. Discussion

### 8.1 Key Findings

The strongest current evidence concerns preparation reproducibility and the Random Forest validation baseline. The RF validation Macro F1 is 0.950540, but pooled U2R recall of 0.820513 remains below the recall recorded for frequent classes. This difference motivates inspection of rare-class errors. Because held-out evaluation is pending, it cannot establish that the same pattern will occur on the reserved test partition.

The measured RF validation dispersion of 0.021178 exceeds the prespecified 0.02 threshold by 0.001178. Reporting the deviation preserves the study condition rather than suppressing an unfavorable diagnostic. Independent fold scores and test evidence are needed to determine its practical significance.

### 8.2 Comparison With Published Baselines

The source literature motivates the choice of bagging, boosting, and attention models. It does not supply a verified performance ranking for this exact data treatment and split. A defensible comparison with prior studies requires matching duplicate handling, family mapping, evaluation partition, and metric averaging. This manuscript therefore reports no claim of improvement over a published numerical baseline.

### 8.3 Limitations

The evaluation uses one historical simulated benchmark and a random split. Rare-class support is limited, configured optimization budgets differ, and no controlled preprocessing ablation has been performed. Complete execution times, XGBoost outcomes, reconciled TabNet statistics, and held-out metrics remain pending. These limits affect both the precision of class estimates and the scope of any recommendation.

### 8.4 Threats to Validity

Internal validity is qualified by constant and correlation-based feature selection before splitting, and by encoders fitted to the full training pool rather than within each validation fold. Statistical conclusion validity is limited by 13 U2R test records, unequal validation-fold counts, and the distinction between cumulative Optuna intermediate means and independent fold results. External validity is limited by the benchmark age and simulated origin. Construct validity requires separating attack-family accuracy from unknown-attack detection, calibrated risk, and causal explanation.

### 8.5 Deployment Considerations

The backend enforces schema validation, deterministic feature ordering, and structured failure responses. A real RF API request and functional checks demonstrate interface behavior, while model accuracy remains a separate question. TabNet requires reconciliation of scaled inference and unscaled training inputs before activation. XGBoost needs a compatible saved artifact for real-model verification. Complete dashboard operation, latency, calibration, and robustness to new traffic have not yet been established.

## 9. Conclusion and Future Work

Network Guardian IDS establishes a documented connection-classification pipeline and an initial Random Forest validation result. The available evidence does not support choosing a final classifier or reporting a complete comparison among the three candidates. The preparation and validation records remain the basis for the planned three-model comparison.

The immediate research work is to complete held-out evaluation, reconcile TabNet fold reporting and transformation consistency, record computational conditions, and inspect errors and explanations. Subsequent experiments should fit data-dependent preprocessing within folds, test controlled transformation ablations, and assess transfer to newer network data. These steps address specific limitations identified by the current implementation.

## Acknowledgments

The authors acknowledge the maintainers of the KDD Cup 1999 benchmark and the open-source software used to implement the study. Individual funding, institutional support, and contributor details will be included only after confirmation.

## References

ACM SIGKDD. (n.d.-a). KDD Cup 1999 computer network intrusion detection. https://www.kdd.org/kdd-cup/view/kdd-cup-1999/Tasks

ACM SIGKDD. (n.d.-b). KDD Cup 1999 results. https://www.kdd.org/kdd-cup/view/kdd-cup-1999/Results

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

Scarfone, K., & Mell, P. (2007). Guide to intrusion detection and prevention systems (IDPS) (NIST Special Publication 800-94). National Institute of Standards and Technology. https://doi.org/10.6028/NIST.SP.800-94

UCI KDD Archive. (1999). KDD Cup 1999 data. https://kdd.ics.uci.edu/databases/kddcup99/kddcup99

### AI Tool Disclosure

OpenAI Codex was used to assist with environment setup, source review, manuscript drafting and formatting, preparation-artifact verification, and backend implementation and functional testing. ChatGPT was also used for troubleshooting and interpretation of execution errors. AI-generated assistance was not used to invent missing measurements or personal reflections. The authors remain responsible for validating the evidence, interpreting the results, and reviewing the final manuscript.

## Appendix A. Full Hyperparameter Tables

The tables distinguish configured search ranges from selected values. The RF configuration is supported by the available model sidecar. XGBoost selected values remain unavailable; TabNet selected values require verification. Search-space evidence comes from the architecture contract and src/models.py (Network Guardian IDS Team, 2026b, 2026f).

**Table 6. Random Forest search space and selected values**

| Parameter | Search range | Selected value |
| --- | --- | --- |
| n_estimators | 100 to 500 step 50 | 350 |
| max_depth | 5, 10, 15, 20, 25, 30 or None | 15 |
| min_samples_split | 2 to 20 | 8 |
| min_samples_leaf | 1 to 10 | 3 |
| max_features | sqrt or log2 | sqrt |
| criterion | gini or entropy | entropy |
| class_weight | balanced or balanced_subsample | balanced |

Fixed Random Forest settings: random_state = 42, n_jobs = -1, bootstrap = True, and oob_score = True. The chosen configuration is trial 17.

**Table 7. XGBoost hyperparameter search space**

| Parameter | Search range | Selected value |
| --- | --- | --- |
| learning_rate | 0.01 to 0.15 logarithmic | Not available |
| max_depth | 3 to 10 | Not available |
| min_child_weight | 1 to 20 | Not available |
| gamma | 0 to 5 | Not available |
| subsample | 0.6 to 1.0 | Not available |
| colsample_bytree | 0.5 to 1.0 | Not available |
| reg_alpha | 0 to 10 | Not available |
| reg_lambda | 1 to 20 | Not available |
| max_delta_step | 0 to 5 | Not available |
| n_estimators | 100 to 300 step 50 | Not available |

XGBoost uses a five-class objective and validation-based early stopping with patience 20. The configured budget is 30 trials; no complete execution record has been incorporated.

**Table 8. TabNet architecture and training search space**

| Parameter | Search range | Selected value |
| --- | --- | --- |
| n_d and n_a | Each 8, 16, 24 or 32 | Under verification |
| n_steps | 3 to 7 | Under verification |
| gamma | 1.0 to 1.6 | Under verification |
| lambda_sparse | 0.00001 to 0.005 logarithmic | Under verification |
| n_independent | 1 to 3 | Under verification |
| n_shared | 1 to 3 | Under verification |
| momentum | 0.02 to 0.10 | Under verification |
| mask_type | sparsemax or entmax | Under verification |
| batch_size | 512, 1024 or 2048 | Under verification |
| virtual_batch_size | 128 or 256 | Under verification |

Fixed TabNet settings: Adam learning rate 0.02, CPU execution, maximum 30 epochs, and patience 10. The configured budget is 20 trials with three validation folds. The final refit uses an internal 10 percent early-stopping partition.

## Appendix B. Additional Confusion Matrices

No test confusion matrix is included in this draft because the required evaluation artifacts are not yet available. The reserved inventory includes confusion_matrix_rf.png, confusion_matrix_xgb.png, and confusion_matrix_tabnet.png under outputs/03_evaluation/. Each final caption must identify the classifier, partition, class order, and source file. Precision-recall curves and explanation figures will use the same frozen test context.

## Appendix C. Reproducibility Instructions

Reproduction begins with docs/SETUP.md and the pinned requirements. Create the project virtual environment with Python 3.11.9, install the recorded dependencies, and execute Notebook 01 from the repository context. Verify the four frozen hashes, array shapes, Unicode target dtypes, class order, and feature manifest before consuming the prepared artifacts.

Notebook 02 contains model training and optimization. Preserve selected configurations, completed and pruned trial counts, independent validation-fold statistics, software versions, and hardware details. Keep model artifacts paired with their metadata. Apply Tomek Links only inside fold training subsets; do not resample the reserved test data or tune against it.

Notebook 03 owns held-out evaluation and explanation generation. Export the test metrics, class supports, confusion matrices, rare-class precision-recall curves, and model explanations to outputs/03_evaluation/. Complete runtime records separately from quality metrics. Resolve the TabNet transformation mismatch before inference verification. Backend startup and verification instructions are recorded in server/README.md and the backend implementation report (Network Guardian IDS Team, 2026g).
