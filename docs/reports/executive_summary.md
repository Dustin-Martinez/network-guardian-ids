# Executive Summary: Network Guardian IDS

*This summary provides a concise overview written for a reader who has not reviewed the complete notebook[cite: 1, 2].*

### 1. What problem did we set out to solve, and why does it matter?
Modern security teams are overwhelmed by millions of network connection logs daily. Rule-based systems miss stealthy zero-day attacks and generate excessive false alarms[cite: 1]. Network Guardian automates intrusion detection by classifying network telemetry into normal activity or four attack families (**DoS, Probe, R2L, U2R**), protecting critical infrastructure from analyst burnout and critical breaches[cite: 1, 4].

### 2. What did we discover about the data that shaped our decisions?
Initial exploration revealed massive class imbalance, heavy feature skewness, and thousands of duplicate rows[cite: 2, 3]. We discovered that raw models would easily overfit to duplicate entries and ignore rare attacks[cite: 3, 4]. This drove our decision to implement rigorous deduplication, logarithmic transforms, hybrid categorical encoding, and in-fold Tomek Link cleaning[cite: 2, 3].

### 3. Which approaches did we compare, and how did we judge them?
We compared three fundamentally different algorithmic paradigms: **Random Forest** (Tree Bagging), **XGBoost** (Gradient Boosting with Optuna tuning), and **PyTorch TabNet** (Deep Learning with Attention)[cite: 1]. We judged them primarily using **Macro F1-Score** rather than simple accuracy to ensure rare, high-severity attacks were treated with equal mathematical weight[cite: 1, 4].

### 4. What do we recommend, and what evidence supports it?
We recommend deploying **XGBoost** paired with **TabNet** as a dual-engine IDS. XGBoost delivered the fastest execution and highest overall Macro F1-Score, while TabNet provided instance-wise attention masks that gave our security team clear forensic evidence explaining *why* a packet was flagged[cite: 1].

### 5. What are the limitations of our work, and what would we do next?
While effective, our models were trained on historical benchmark telemetry[cite: 3]. In a live production environment, streaming network packets introduce latency and novel, evolving attack vectors. Next steps include integrating real-time packet capture streaming and containerizing the backend via FastAPI[cite: 1].

### 6. What was our biggest mistake or surprise, and what did we learn from it?
Our biggest surprise was how heavily models relied on redundant features until we performed correlation pruning (>90% threshold)[cite: 3]. We learned that feature quality and clean data preparation matter significantly more than raw model complexity[cite: 1, 2].