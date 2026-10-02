# Developer Onboarding & Environment Setup

## Prerequisites
* Python 3.10+ installed
* PowerShell 7+ or Windows PowerShell
* Visual Studio Code with Python and Jupyter extensions

## Quickstart Installation


1. **Clone and Open Workspace**
   ```powershell
   cd network-guardian-ids
   code .
---
## Quickstart: Running the Web Application

1. **Start the Express API Server (Port 5000):**
   ```powershell
   cd server
   node server.js
---

# 1. Initialize Environment & Set Execution Policy

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install Dependencies

pip install --upgrade pip
pip install -r requirements.txt

# 3. Verify Jupyter Kernel

Open notebooks/01_EDA_and_Data_Prep.ipynb, click Select Kernel in the upper-right corner of VS Code, and select the .venv environment.

# Code Guidelines

**Reproducibility First:** Always call src.utils.seed_everything(42) at the start of any module or notebook execution cell[cite: 1].

**No Inline Logic:** Do not write complex data parsing or model training loops directly in notebook cells. Add functions to src/ modules and import them into notebooks.

**Text Cell Explanations:** Every code cell in notebooks must be accompanied by explanatory Markdown text cells justifying the decision[cite: 1].