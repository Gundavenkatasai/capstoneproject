# CivicMind AI — Phase 5 Dataset Readiness Report
## Empirical Data Audit, Label Integrity & Readiness Gate Assessment

**Document Status**: COMPLETED  
**Date**: November 20, 2026  
**Auditor**: Principal Machine Learning Engineer & MLOps Architect  
**Target Environment**: PostgreSQL 16 + pgvector (`civicmind_db`)

---

## 1. Executive Summary

Prior to model training, a rigorous empirical audit of the `civicmind_db` PostgreSQL database was conducted in accordance with the Phase 5 engineering specification. 

The audit evaluated 9 primary entities for sample volume, label balance, outcome resolution timestamps, SLA breach records, semantic clusters, and data leakage risks.

### Verdict of the Dataset Readiness Gate:
| Machine Learning Capability | Target Label / Output | Production Data Status | Readiness Gate Verdict | Operational Fallback |
| :--- | :--- | :--- | :--- | :--- |
| **Grievance Categorization** | 8 Municipal Categories | Insufficient Operational Records | **GATE: INSUFFICIENT DATA** | Deterministic Keyword Classifier + TF-IDF Baseline |
| **Department Recommendation** | 5 Municipal Dept Codes | Insufficient Operational Records | **GATE: INSUFFICIENT DATA** | Municipal Mandate Mapping |
| **Semantic Embeddings** | 768-dim Dense Vectors | Architecture Compatible | **GATE: READY** | Sentence-BERT (`paraphrase-multilingual-mpnet-base-v2` / `all-mpnet-base-v2`) |
| **Duplicate Detection** | Cosine Distance in pgvector | Verified HNSW Vector Index | **GATE: READY** | Cosine Similarity Search + Top-k Thresholds |
| **Resolution-Time Prediction** | Continuous Duration (Days) | 0 Historical Resolutions in DB | **GATE: INSUFFICIENT DATA** | Priority-based SLA Duration Matrix (48h/72h/96h/120h) |
| **SLA Breach Risk** | Binary Probability (0.0 to 1.0) | 0 Historical Breach Outliers in DB | **GATE: INSUFFICIENT DATA** | Workload & Hours-Remaining Heuristic |

---

## 2. Quantitative Database Audit

An direct SQL inspection of all primary application tables yielded the following census:

```
Database Census (Executed on 2026-11-20):
- users: 109
- departments: 18
- officers: 4
- grievances: 12
- grievance_evidence: 2
- resolution_reports: 0
- grievance_timeline: 10
- duplicate_clusters: 0
- outbox_events: 46
```

### Detailed Grievance Record Breakdown:
| Grievance ID | Title | Category | Dept ID | Priority | Status | Resolution Date | SLA Breached |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `GRV-2026-10048` | Pothole on Main Road... | Roads & Footpaths | TEST-DEPT-2323 | high | submitted | `NULL` | `False` |
| `GRV-2026-10049` | Pothole on Main Road... | Roads & Footpaths | TEST-DEPT-bfdf | high | submitted | `NULL` | `False` |
| `GRV-2026-10050` | Pothole on Main Road... | Roads & Footpaths | TEST-DEPT-a92b | high | submitted | `NULL` | `False` |
| `GRV-2026-10051` | Pothole on Main Road... | Roads & Footpaths | TEST-DEPT-0e8a | high | submitted | `NULL` | `False` |
| `GRV-2026-10052` | Pothole on Main Road... | Roads & Footpaths | TEST-DEPT-b6fd | high | submitted | `NULL` | `False` |
| `GRV-2026-10053` | Pothole on Main Road... | Roads & Footpaths | TEST-DEPT-18da | high | submitted | `NULL` | `False` |
| `GRV-2026-e0a18` | Evidence Test Grievance | Sanitation | DEPT-EV-a392 | medium | submitted | `NULL` | `False` |
| `GRV-2026-10054` | Pothole on Main Road... | Roads & Footpaths | TEST-DEPT-b82a | high | submitted | `NULL` | `False` |
| `GRV-2026-8b741` | Evidence Test Grievance | Sanitation | DEPT-EV-37d6 | medium | submitted | `NULL` | `False` |
| `GRV-2026-10062` | Test Contaminated Water | Water | DEPT-HEALTH | medium | assigned | `NULL` | `False` |
| `GRV-2026-10063` | Pothole on Main Road... | Roads & Footpaths | TEST-DEPT-0505 | high | submitted | `NULL` | `False` |
| `GRV-2026-d5b49` | Evidence Test Grievance | Sanitation | DEPT-EV-aff5 | medium | submitted | `NULL` | `False` |

---

## 3. Data Integrity & Quality Findings

1. **Test Fixture Artifacts**: All 12 grievances currently residing in PostgreSQL were generated dynamically by automated test executions in Phases 1–4. There are **zero organic citizen complaints**.
2. **Missing Ground Truth for Resolution Duration**:
   - `actual_resolution_date` is `NULL` for 100% of rows.
   - `resolution_reports` has 0 rows.
   - Training a regression model (e.g. LightGBM) on the database directly would produce zero samples or catastrophic overfitting.
3. **Missing Ground Truth for SLA Breach Classification**:
   - `sla_breached` is `False` for 100% of rows.
   - There is zero outcome variance for binary classification training.
4. **Target Leakage Risk**:
   - When training resolution-time models on operational data, features such as `resolution_reports.report_text`, `resolution_reports.labor_hours`, or final status updates (`closed`, `resolution_submitted`) must be strictly excluded, as they are unavailable at the time of initial citizen submission.

---

## 4. Benchmark & Synthetic Research Dataset Strategy

To ensure reproducible testing, pipeline calibration, and evaluation benchmarking without violating the cardinal rule against fabricating production data:

1. **Separation of Concerns**:
   - Production models connecting to live endpoints report `status: "insufficient_data"` and activate rule-based municipal fallbacks when trained checkpoints do not meet empirical validation thresholds.
2. **Curated Research Benchmark Dataset (`BENCHMARK_RESEARCH_DATASET_v1`)**:
   - A standardized benchmark suite of 500 validated municipal complaints is provided in `backend/ml/data/benchmark_dataset.py`.
   - Used strictly for:
     - Pipeline smoke testing (tokenization, feature engineering, loss convergence).
     - Baseline vs. model comparisons.
     - SHAP explainability verification.
     - Test suite execution.
   - It is explicitly segregated from PostgreSQL operational tables.

---

## 5. Requirements for Production Model Training

To graduate models from `insufficient_data` to `production_active`, the city administration must ingest:
- Minimum **500 labelled complaints per category** (minimum 4,000 complaints across the 8 municipal categories).
- Minimum **200 verified resolution reports per department** with non-null `actual_resolution_date`.
- Verified temporal history spanning at least 90 calendar days to capture seasonal, day-of-week, and weather-related variations.
