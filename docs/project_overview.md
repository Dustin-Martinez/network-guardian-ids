# Project Overview: Network Guardian IDS

## Executive Summary
Network Guardian is an enterprise-grade prototype for an Intrusion Detection System (IDS) designed to classify high-volume network connection traffic into normal activity or four distinct attack families: **Denial of Service (DoS)**, **Probe**, **Remote to Local (R2L)**, and **User to Root (U2R)**[cite: 1, 4].

The system leverages machine learning to automatically inspect network packet telemetry, reducing human analyst burnout and minimizing critical detection failures.

## Problem Statement
Modern Security Operations Centers (SOCs) analyze millions of connection logs daily. Traditional rule-based firewalls miss novel zero-day exploits and trigger overwhelming numbers of false alarms. Network Guardian solves this by applying non-linear classification models capable of identifying complex attack signatures across 41 network telemetry features[cite: 1, 3].

## Attack Family Classifications
The model targets five specific output categories[cite: 1, 4]:
1. **Normal:** Standard, non-malicious user and server traffic.
2. **DoS (Denial of Service):** Flooding resources to render systems unresponsive (e.g., `neptune`, `smurf`, `back`, `teardrop`)[cite: 4].
3. **Probe:** Surveillance and port scanning to map network topology (e.g., `satan`, `ipsweep`, `nmap`, `portsweep`)[cite: 4].
4. **R2L (Remote to Local):** Unauthorized access from a remote machine (e.g., `guess_passwd`, `warezmaster`, `ftp_write`, `imap`)[cite: 4].
5. **U2R (User to Root):** Local non-privileged user attempting administrative root access (e.g., `buffer_overflow`, `rootkit`, `loadmodule`, `perl`)[cite: 4].

## Core Objectives
* **Agnostic Feature Engineering:** Convert raw network protocol data into scaled numerical features without data leakage.
* **Multi-Model Comparison:** Train and evaluate three distinct algorithmic families: Random Forest (Bagging), XGBoost (Gradient Boosting), and PyTorch TabNet (Deep Learning).
* **Macro F1 Optimization:** Prioritize detection of rare, high-severity attacks (U2R, R2L) over simple bulk accuracy[cite: 1, 4].
* **Forensic Explainability:** Integrate SHAP (SHapley Additive exPlanations) and TabNet Attention Masks to explain predictions to human analysts.