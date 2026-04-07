# Team Project Submission -- Task #2

## Team Members
- Thabo Ibrahim Traore
- Jordan Barnes
- Zizwe Mtonga
- Tapiwa Musinga

## Topic Area
**Cybersecurity** -- IoT Botnet Detection

---

## a) Objective

**Problem:** IoT devices (smart cameras, routers, smart-home gear) are easy targets for hackers. Once compromised, they get conscripted into botnets used for DDoS attacks, data theft, and malware propagation. Detecting these infections by hand is impossible at the scale of modern networks.

**Goal:** Build an automated machine-learning system that classifies IoT network connections as **benign** or **malicious**, identify which network features most strongly indicate an attack, and run the entire pipeline on the ASAX supercomputer using a Linux shell script.

**Specific questions we wanted to answer:**
1. Can we accurately distinguish malicious IoT traffic from normal traffic?
2. Which network features (bytes, packets, protocol, ports) are the strongest predictors of an attack?
3. How well does a Random Forest classifier handle a heavily imbalanced cybersecurity dataset (94% malicious, 6% benign)?

---

## b) Data Processing / Visualization Program

**File:** `iot_intrusion_detection.py`

Pipeline:
1. **Load** -- reads the IoT-23 CSV (auto-detects pipe vs comma delimited)
2. **Preprocess** -- drops dead columns, fills missing values, encodes labels
3. **Explore** -- generates 4 charts (attack distribution, protocol breakdown, benign-vs-malicious pie, top targeted ports)
4. **Train** -- 100-tree Random Forest classifier with 70/30 train/test split
5. **Evaluate** -- accuracy, precision, recall, F1-score, confusion matrix, feature importances

---

## c) Linux Shell Script

**File:** `run_analysis.sh`

- SLURM directives for ASAX job scheduling (4 cores, 8 GB RAM, 1 hour limit)
- Loads Python modules via `module load`
- Installs Python dependencies (`pandas`, `numpy`, `scikit-learn`, `matplotlib`, `seaborn`, `kaggle`)
- Auto-downloads and combines the IoT-23 dataset from Kaggle
- Launches the Python program and reports results

---

## d) PPT Presentation

**File:** `Task2_Presentation.pptx` (10 slides)

1. Title
2. Objective & Problem Statement
3. Dataset Overview
4. Attack Categories
5. Methodology / Pipeline
6. Exploratory Data Analysis
7. Model Performance
8. Feature Importances
9. ASAX Workflow
10. Conclusion & Demo

---

## Key Results

| Metric | Value |
|--------|-------|
| **Accuracy** | **97.87%** |
| Total samples processed | 1,885,004 |
| Test samples | 565,502 |
| Training time | 23.4 seconds |
| Prediction time | 0.7 seconds |
| Benign F1-score | 0.83 |
| Malicious F1-score | 0.99 |

---

## Deliverables Submitted

| # | Item | File |
|---|------|------|
| 1 | Dataset (link) | https://www.stratosphereips.org/datasets-iot23 |
| 2 | Data processing program | `iot_intrusion_detection.py` |
| 3 | Linux shell script | `run_analysis.sh` |
| 4 | PPT presentation | `Task2_Presentation.pptx` |

Repository: https://github.com/ibrahimt39/AAMU-Linux-Project
