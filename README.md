# IBM HR Analytics — Employee Attrition Report

> A complete end-to-end HR data pipeline: data cleaning, quality audit, metric computation, and an interactive HTML executive report.

---

## 📦 Dataset

| Field | Detail |
|---|---|
| **Name** | IBM HR Analytics Employee Attrition & Performance |
| **Source** | Kaggle |
| **Link** | [Download Dataset](https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset?resource=download) |
| **Rows** | 1,470 employees |
| **Columns** | 35 features |
| **File (raw)** | `HR IBM.BOB.csv` |
| **File (clean)** | `HR IBM.BOB.CLEANED.csv` |

---

## 📁 Project Structure

```
IBM.BOB/
│
├── HR IBM.BOB.csv                  ← Raw dataset (original download)
├── HR IBM.BOB.CLEANED.csv          ← Cleaned dataset (output of clean_hr.py)
│
├── audit_hr.py                     ← Basic data quality audit (missing values, ranges, etc.)
├── deep_audit.py                   ← Deep audit (IQR outliers, special chars, logic checks)
├── clean_hr.py                     ← Full cleaning script — produces CLEANED.csv
├── compute_metrics.py              ← Computes all HR metrics and group statistics
│
├── HR_Attrition_Report.html        ← 📊 Interactive executive report (open in browser)
│
├── requirements.txt                ← Python dependencies (standard library only)
└── README.md                       ← This file
```

---

## 🚀 Quick Start

### 1. Download the dataset
Go to:
> [https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset?resource=download](https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset?resource=download)

Download `WA_Fn-UseC_-HR-Employee-Attrition.csv` and rename it to `HR IBM.BOB.csv` and place it in this folder.

### 2. Run the cleaning pipeline

```bash
# Step 1 — Basic audit (missing values, nulls, ranges)
python audit_hr.py

# Step 2 — Deep audit (IQR outliers, special chars, logical consistency)
python deep_audit.py

# Step 3 — Clean the dataset → outputs HR IBM.BOB.CLEANED.csv
python clean_hr.py

# Step 4 — Compute all HR metrics and group statistics
python compute_metrics.py
```

> **Requirements:** Python 3.8+ only. No pip installs needed — all scripts use the standard library.

### 3. Open the report

Double-click `HR_Attrition_Report.html` or open it in any browser:

```bash
# Windows
start HR_Attrition_Report.html

# macOS
open HR_Attrition_Report.html

# Linux
xdg-open HR_Attrition_Report.html
```

---

## 📊 What the Report Contains

The `HR_Attrition_Report.html` is a fully self-contained interactive report with:

| Section | Contents |
|---|---|
| **Key HR Metrics** | Attrition rate (16.1%), avg income, avg age, avg tenure, and more |
| **10 Interactive Charts** | Department, OverTime (donut), JobRole (combo), Job Satisfaction, Work-Life Balance, Age Groups, Tenure, Distance from Home, Business Travel, Job Level |
| **Group Summary Tables** | All 9 job roles ranked by attrition risk with colour-coded pills |
| **High-Risk Profile** | 8-trait employee profile with 75% attrition probability |
| **5 Business Insights** | Root cause analysis + concrete HR action steps |
| **Executive Summary** | Manager-ready narrative including ~$6.8M annual cost estimate |

---

## 🔍 Key Findings

| Finding | Detail |
|---|---|
| 🔴 **Overall Attrition Rate** | **16.1%** — above the 10–12% industry benchmark |
| 🔴 **Overtime is the #1 driver** | OT employees leave at **30.5%** vs 10.4% without OT |
| 🔴 **Sales Representative** | Highest role attrition at **39.8%** |
| 🟡 **Young employees (18–25)** | **35.8%** attrition — 3.9× the 36–45 cohort |
| 🟡 **First 2 years at company** | **29.8%** attrition — highest tenure window |
| 🟡 **Low Job Satisfaction (L1)** | **22.8%** vs 11.3% for high satisfaction (L4) |
| 🟢 **Senior/long-tenured staff** | Very stable — Research Director at only 2.5% |

---

## 🛠️ Data Cleaning Summary

The raw `HR IBM.BOB.csv` had **1 issue fixed**:

| Issue | Detail | Fix |
|---|---|---|
| UTF-8 BOM | Bytes `EF BB BF` present in header — corrupts CSV parsers | Stripped on rewrite |

All 13 other audit checks **passed** (no missing values, no duplicates, no out-of-range numbers, no invalid categoricals, no logical inconsistencies).

---

## 📋 Requirements

- **Python:** 3.8 or higher
- **Dependencies:** Standard library only (`csv`, `collections`, `re`, `json`, `os`)
- **Browser:** Any modern browser for `HR_Attrition_Report.html` (Chrome, Edge, Firefox, Safari)
- **Internet:** Only needed to load Chart.js CDN when opening the HTML report

See [`requirements.txt`](requirements.txt) for full details and optional packages.

---

## 📄 License

This project uses the IBM HR Analytics dataset published on Kaggle under the [CC0: Public Domain](https://creativecommons.org/publicdomain/zero/1.0/) licence.

---

*Generated with IBM Bob — AI-powered analytics assistant*
