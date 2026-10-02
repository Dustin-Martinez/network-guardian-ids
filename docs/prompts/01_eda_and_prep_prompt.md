# AI Prompt: EDA and Data Preparation Phase

*Use this vendor-agnostic prompt in any general AI assistant (e.g., Claude, ChatGPT, Llama) when writing code for your initial data cleaning script (`src/data_prep.py` or Notebook 01).*

---

### Prompt Text:
> "Act as a senior machine learning engineer specializing in cybersecurity and digital forensics. I am building an Intrusion Detection System using network connection telemetry (KDD-style data with 41 features). 
> 
> Please write production-ready, modular Python functions using `pandas` and `numpy` for the following data preparation steps, ensuring **strict prevention of data leakage**:
> 1. **Target Mapping:** Write a function that maps raw attack strings (e.g., `smurf`, `buffer_overflow`, `guess_passwd`) into five primary classes: `normal`, `dos`, `probe`, `r2l`, and `u2r`.
> 2. **Deduplication & Correlation Pruning:** Write a function to drop duplicate rows and remove features that exhibit greater than 90% Pearson correlation.
> 3. **Logarithmic Scaling:** Write a transformation function that applies $log(1+x)$ scaling to heavily skewed continuous columns (`duration`, `src_bytes`, `dst_bytes`).
> 4. **Hybrid Categorical Encoding:** Implement Frequency Encoding for the high-cardinality `service` column, and One-Hot Encoding for `protocol_type` and `flag`.
> 
> Ensure the code is written cleanly for modular import and includes clear docstrings."