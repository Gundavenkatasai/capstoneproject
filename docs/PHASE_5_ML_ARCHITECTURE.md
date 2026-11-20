# CivicMind AI — Phase 5 Machine Learning Architecture Specification
## Multi-Task Intelligence, Inference Pipelines, Model Registry & Explainability

**Document Status**: COMPLETED  
**Version**: 1.0.0  
**Date**: November 20, 2026  
**Author**: Principal Machine Learning Engineer & MLOps Architect  

---

## 1. Architecture Overview

CivicMind AI Phase 5 integrates six predictive and semantic intelligence engines into a modular, production-grade ML subsystem:

```
                               ┌──────────────────────────────────────────────┐
                               │       Citizen / Officer / Admin APIs         │
                               └──────────────────────┬───────────────────────┘
                                                      │
                       ┌──────────────────────────────┼──────────────────────────────┐
                       ▼                              ▼                              ▼
            ┌──────────────────────┐       ┌──────────────────────┐       ┌──────────────────────┐
            │   POST /ai/triage    │       │ POST /ai/duplicates  │       │ POST /ai/predict-sla │
            └──────────┬───────────┘       └──────────┬───────────┘       └──────────┬───────────┘
                       │                              │                              │
                       ▼                              ▼                              ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              CivicMind ML Model Registry & Manager                             │
│                  - Lazy-loading, LRU model caching, version pinning & audit metadata           │
│                  - Clean fallback to calibrated municipal rule engines when data is sparse     │
└──────┬───────────────────────┬──────────────────────┬───────────────────────┬──────────────────┘
       │                       │                      │                       │
       ▼                       ▼                      ▼                       ▼
┌──────────────┐       ┌──────────────┐       ┌──────────────┐       ┌───────────────────┐
│ NLP Category │       │ Sentence-BERT│       │   LightGBM   │       │      XGBoost      │
│  Classifier  │       │  Embeddings  │       │  Resolution  │       │     SLA Breach    │
│ (DeBERTa /   │       │  (768-dim    │       │   Duration   │       │   Classification  │
│  TF-IDF)     │       │   pgvector)  │       │  Regression  │       │    + Calibration  │
└──────┬───────┘       └──────┬───────┘       └──────┬───────┘       └─────────┬─────────┘
       │                      │                      │                         │
       └──────────────────────┴──────────┬───────────┴─────────────────────────┘
                                         ▼
                       ┌───────────────────────────────────┐
                       │      SHAP & XAI Attribution       │
                       │ - TreeSHAP feature contributions  │
                       │ - Lexical keyword impact weights  │
                       │ - Transparent confidence bounds   │
                       └───────────────────────────────────┘
```

---

## 2. Model Family Specifications

### 2.1. Grievance Categorization Engine (`backend/ml/classification/`)
- **Primary Model**: Fine-tuned DeBERTa-v3 (`microsoft/deberta-v3-small` / `deberta-v3-base`) for token sequence classification.
- **Baseline Model**: TF-IDF Vectorizer (ngram_range=(1,2), sublinear_tf=True) + Regularized Multinomial Naive Bayes / Logistic Regression.
- **Taxonomy**: 8 municipal grievance categories (`Roads & Footpaths`, `Water Supply & Sewerage`, `Sanitation & Waste Management`, `Electricity & Street Lighting`, `Public Health & Vector Control`, `Parks & Horticulture`, `Traffic & Transport`, `Revenue & General Administration`).
- **Inference Output**: Top-1 predicted category, confidence score (0.0 to 1.0), and Top-3 ranked alternative categories.

### 2.2. Department Recommendation Engine (`backend/ml/classification/`)
- **Model**: Multi-class department routing classifier mapping textual features and predicted category to authorized municipal department IDs (`PWD-RDS`, `WSSB`, `SWD`, `ELEC`, `HLS`).
- **Principle**: Distinguishes `predicted_department` from `assigned_department`. Never overrides human officer assignment automatically.

### 2.3. Semantic Vector Embeddings (`backend/ml/embeddings/`)
- **Model**: Sentence-BERT (`sentence-transformers/all-mpnet-base-v2` or `paraphrase-multilingual-mpnet-base-v2`).
- **Dimension Invariant**: **Strictly 768 dimensions** matching `EMBEDDING_DIMENSION=768` in `app.core.config` and the PostgreSQL `grievance_embeddings.embedding` pgvector column.
- **Asynchronous Pipeline**: Embedded in the background via Celery (`app.tasks.ml.generate_grievance_embedding_task`) to guarantee non-blocking grievance creation.

### 2.4. Semantic Duplicate Detection (`backend/ml/duplicates/`)
- **Mechanism**: Cosine distance similarity search over pgvector HNSW index (`cosine_distance(embedding, query)`).
- **Thresholds**: Calibrated cosine similarity threshold (default: 0.82 for potential duplicate, 0.90 for high-confidence candidate).
- **Human Review**: Candidates are flagged as `similar_grievances`. Automatic destructive merges are strictly prohibited.

### 2.5. Resolution-Time Prediction (`backend/ml/resolution/`)
- **Model**: LightGBM Regressor (`objective='regression'`, `metric='mae'`).
- **Leak-Free Features**: Category, department, priority, submission hour, day of week, ward/zone encoding, historical department workload at submission time.
- **Excluded Features**: Actual resolution date, resolution report text, final status, future officer actions.
- **Output**: Estimated resolution duration in days with uncertainty bounds (± days).

### 2.6. SLA Breach Risk Prediction (`backend/ml/sla/`)
- **Model**: XGBoost Classifier (`objective='binary:logistic'`, `eval_metric='aucpr'`).
- **Prediction Point**: Submission time (or periodic SLA checkpoint).
- **Output**: Probability of SLA breach (0.0 to 1.0), risk tier (`low`, `medium`, `high`, `critical`), and top risk drivers.

### 2.7. Explainable AI Engine (`backend/ml/explainability/`)
- **Tabular Models (LightGBM / XGBoost)**: TreeSHAP computes exact Shapley values for each input feature (e.g., department workload +0.18 breach probability, priority tier -0.12).
- **Text Models**: Normalized lexical feature attribution highlighting decisive municipal tokens.

---

## 3. Directory Layout

```
backend/
├── ml/
│   ├── __init__.py
│   ├── data/                    # Data extraction, normalization, and reproducible splitting
│   │   ├── __init__.py
│   │   ├── extractor.py         # Database record extraction with test fixture exclusion
│   │   ├── normalization.py     # Text cleaning and municipal label standardization
│   │   ├── splitting.py         # Grouped & temporal train/val/test splits (zero leakage)
│   │   ├── benchmark_dataset.py # Curated 500-sample research benchmark suite
│   │   └── quality_report.py    # Class balance and missingness diagnostics
│   ├── classification/          # Category & department NLP models
│   │   ├── __init__.py
│   │   ├── baseline.py          # TF-IDF + LogisticRegression baseline
│   │   ├── deberta_model.py     # DeBERTa architecture wrapper (CPU/GPU)
│   │   └── predictor.py         # Category & department routing inference
│   ├── embeddings/              # Sentence-BERT 768-dim embeddings
│   │   ├── __init__.py
│   │   └── embedder.py          # SBERT wrapper with batch caching & 768-dim assertion
│   ├── duplicates/              # Cosine similarity search in pgvector
│   │   ├── __init__.py
│   │   └── detector.py          # HNSW vector query & duplicate candidate ranking
│   ├── resolution/              # LightGBM duration regression
│   │   ├── __init__.py
│   │   └── regressor.py         # LightGBM trainer, evaluator & predictor
│   ├── sla/                     # XGBoost SLA breach classification
│   │   ├── __init__.py
│   │   └── classifier.py        # XGBoost trainer, calibrator & risk predictor
│   ├── explainability/          # TreeSHAP & token attribution
│   │   ├── __init__.py
│   │   └── explainer.py         # Feature contribution calculator
│   ├── evaluation/              # Standardized metrics & reports
│   │   ├── __init__.py
│   │   └── metrics.py           # Precision, Recall, F1, PR-AUC, MAE, RMSE, Confusion Matrix
│   └── registry/                # Model registry, caching & lifecycle management
│       ├── __init__.py
│       └── registry.py          # Version tracking, artifact storage & fallback controller
```

---

## 4. Model Registry & Fallback Protocol

When live database records do not satisfy empirical training requirements:
1. Model status is marked as `insufficient_data`.
2. The endpoint seamlessly activates the verified municipal operational fallback.
3. Responses return explicit metadata:
   - `model_name`: `"CivicRuleFallback-v1"` or `"CivicDeBERTa-v1"`
   - `model_version`: `"1.0.0-fallback"` or `"1.0.0"`
   - `is_fallback`: `true`
   - `reason`: `"insufficient_historical_training_data"`
4. Zero HTTP 500 errors occur when models are uncalibrated or weights are missing.
