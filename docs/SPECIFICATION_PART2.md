# Gnit Specification (Part 2)

## Evaluation + Metrics

### Challenge: No Ground-Truth Labels

Since we have no labeled anomalies, evaluation uses:

### 1. Injected Anomaly Testing

**Method**: Synthetically inject known anomalies into aggregates, test detection

**Test cases** (in `tests/test_detection.py`):

```python
def test_spike_detection():
    # Inject 5x spike in one month for vendor
    # Expected: Both methods flag as anomaly
    
def test_drop_detection():
    # Inject 90% drop in one month
    # Expected: Both methods flag as anomaly
    
def test_stable_vendor():
    # Vendor with consistent spend
    # Expected: No anomalies flagged
```

**Metrics**:
- Precision on injected anomalies: % of injected anomalies detected
- False positive rate: % of stable months flagged
- Target: Precision >= 80%, FPR <= 10%

### 2. Stability Checks

**Method**: Run detection twice on same data, measure consistency

**Metric**: Stability score = % of vendor-months with same classification

**Target**: >= 95% stability (Isolation Forest with fixed random_state should be 100%)

### 3. Human Review Workflow

**Process**:
1. Sample 20 anomalies (10 baseline, 10 ML)
2. Manual review: "plausible" vs "noise"
3. Document criteria for plausibility:
   - Large absolute change (>$100K or >100%)
   - Explainable by evidence (e.g., single large contract)
   - Not due to data quality issues

**Metrics**:
- Plausibility rate: % marked "plausible"
- Target: >= 70% plausible

### 4. Time-to-Answer Workflow

**Comparison**: Manual analysis vs tool

**Manual baseline**:
- Download CSV from USAspending: ~5 min
- Pivot/aggregate in Excel: ~10 min
- Identify outliers visually: ~10 min
- Trace back to source awards: ~15 min
- **Total: ~40 minutes per vendor**

**Tool workflow**:
- Run pipeline: ~2 min
- Query anomalies: <10 sec
- Review evidence: ~2 min per anomaly
- **Total: ~5 minutes for all vendors**

**Target**: 8x time savings

### 5. Metrics Documentation

**File**: `docs/metrics.md`

**Contents**:
- Injected anomaly test results
- Stability scores
- Human review log
- Time-to-answer comparison
- Weekly metric snapshots

**Success criteria by Week 6**:
- ✅ Injected anomaly precision >= 80%
- ✅ Stability >= 95%
- ✅ Human plausibility >= 70%
- ✅ Time savings >= 5x
- ✅ Zero crashes on demo dataset
- ✅ Full evidence traceability (100% of anomalies)

---

## Architecture Options + Recommendation

### Recommended Stack (Option 1)

**Components**:
- **Language**: Python 3.11+
- **Database**: DuckDB (embedded, no server)
- **CLI**: Click (command-line interface)
- **API**: FastAPI (REST endpoints)
- **UI**: Streamlit (rapid prototyping)
- **ML**: scikit-learn (Isolation Forest)
- **Data**: pandas (wrangling), numpy/scipy (stats)
- **Testing**: pytest
- **Packaging**: Poetry or pip-tools

**Pros**:
- Fast development (solo builder friendly)
- No infrastructure overhead (embedded DB)
- Easy deployment (single Python environment)
- Rich ecosystem for data + ML
- Streamlit = instant UI with minimal code

**Cons**:
- DuckDB not ideal for concurrent writes (fine for batch pipeline)
- Streamlit less polished than React (acceptable for MVP)

**Component Diagram**:
```
┌─────────────────┐
│ USAspending API │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Ingestion CLI  │ (gnit ingest)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  DuckDB         │ (raw_awards)
│  data/gnit.db   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Normalization   │ (gnit normalize)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Feature Build   │ (gnit build-features)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Train Model     │ (gnit train-model)
│ → models/       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Score Anomalies │ (gnit score-anomalies)
│ → anomalies tbl │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Explain         │ (gnit explain)
│ → explanation   │
└────────┬────────┘
         │
         ▼
┌──────────────────────────────┐
│  FastAPI        Streamlit UI │
│  (REST API)     (Dashboard)  │
└──────────────────────────────┘
```

### Alternative 1: Streamlit-Only MVP

**Changes**:
- Remove FastAPI
- All interaction via Streamlit UI
- CLI for pipeline, UI for exploration

**Pros**:
- Simpler (one less component)
- Faster to build

**Cons**:
- No programmatic API access
- Harder to integrate with other tools

**Recommendation**: Use for Week 1-3, add FastAPI in Week 4 if time permits

### Alternative 2: dbt-Style Transforms

**Changes**:
- Use dbt for SQL transformations
- DuckDB as backend
- Python only for ML + API

**Pros**:
- SQL-native transformations (more readable for analysts)
- Built-in lineage tracking
- Testable data transformations

**Cons**:
- Additional tool to learn
- Overkill for solo builder
- Adds complexity

**Recommendation**: Consider for post-MVP if project scales

---

## Roadmap (Week 1-6)

### Week 1: Ingestion + Schema + Top Vendor Query

**Deliverables**:
- ✅ DuckDB schema created (`gnit/db/schema.sql`)
- ✅ USAspending API client (`gnit/ingest/api_client.py`)
- ✅ CLI command: `gnit ingest --state MN --start-date 2022-01-01 --end-date 2024-01-31`
- ✅ `raw_awards` table populated (expect ~50K-100K rows for MN)
- ✅ `run_manifest` tracking
- ✅ Query: Top 20 vendors by total obligation

**Tests**:
- API client handles rate limits
- Schema constraints enforced
- Duplicate award_ids rejected

**Exit criteria**: Can fetch and store MN awards for 24 months

---

### Week 2: Normalization + Aggregates + Baseline Detection

**Deliverables**:
- ✅ Vendor normalization (`gnit/normalize/vendor_matcher.py`)
  - Fuzzy matching on recipient_name
  - DUNS/UEI as strong identifiers
  - Manual override file: `config/vendor_overrides.csv`
- ✅ `vendor_entities`, `vendor_aliases`, `award_vendor_map` populated
- ✅ CLI: `gnit normalize --run-id <run_id>`
- ✅ Monthly aggregation (`gnit/features/aggregator.py`)
- ✅ `monthly_vendor_spend` table with rolling features
- ✅ CLI: `gnit build-features --run-id <run_id>`
- ✅ Baseline detector (`gnit/detect/baseline.py`)
- ✅ CLI: `gnit detect-baseline --run-id <run_id>`
- ✅ Anomalies table populated (baseline method)

**Tests**:
- Normalization: known aliases map correctly
- Aggregation: monthly sums match raw totals
- Baseline: injected spike detected

**Exit criteria**: Can detect anomalies using robust MAD

---

### Week 3: ML Anomaly Pipeline + Model Artifacts

**Deliverables**:
- ✅ Feature engineering complete (18 features)
- ✅ Isolation Forest trainer (`gnit/detect/ml.py`)
- ✅ CLI: `gnit train-model --run-id <run_id>`
- ✅ Model artifacts saved: `models/<run_id>/isolation_forest.joblib`
- ✅ CLI: `gnit score-anomalies --run-id <run_id> --model-run-id <model_run_id>`
- ✅ Anomalies table populated (ML method)
- ✅ Side-by-side comparison: baseline vs ML anomalies

**Tests**:
- Model training deterministic (same random_state)
- Scoring reproducible
- Injected anomaly detected by ML

**Exit criteria**: Can train and score with Isolation Forest

---

### Week 4: Explanation Endpoints + Traceability

**Deliverables**:
- ✅ Evidence builder (`gnit/explain/evidence.py`)
- ✅ Feature driver calculator (`gnit/explain/drivers.py`)
- ✅ Narrative generator (`gnit/explain/narrative.py`)
- ✅ CLI: `gnit explain --run-id <run_id>`
- ✅ `explanation_json` populated for all anomalies
- ✅ FastAPI endpoints:
  - `GET /anomalies?run_id=<>&severity=<>&method=<>`
  - `GET /anomalies/{anomaly_id}`
  - `GET /vendors/{vendor_id}/timeline`
- ✅ API documentation (auto-generated by FastAPI)

**Tests**:
- Every anomaly has award_ids
- Evidence rows sum to monthly total
- Narrative template renders correctly

**Exit criteria**: Can explain any anomaly with evidence

---

### Week 5: UI + Report Export

**Deliverables**:
- ✅ Streamlit dashboard (`gnit/ui/app.py`)
  - Page 1: Anomaly list (filterable by severity, method, vendor)
  - Page 2: Vendor detail (timeline + anomalies)
  - Page 3: Anomaly detail (evidence + drivers + narrative)
- ✅ CLI: `gnit export-report --run-id <run_id> --format csv`
- ✅ CSV export with columns:
  - vendor_name, year_month, severity, method, anomaly_score, obligation_sum, explanation_summary
- ✅ JSON export: full anomaly records with evidence

**Tests**:
- UI loads without errors
- Filters work correctly
- Export matches database records

**Exit criteria**: Can demo full workflow in UI

---

### Week 6: Hardening + Docs + Demo Script + Release

**Deliverables**:
- ✅ Error handling: API failures, missing data, edge cases
- ✅ Logging: structured logs for debugging
- ✅ Performance: optimize queries (add indexes)
- ✅ Documentation:
  - README.md (setup + quickstart)
  - docs/THESIS.md (problem statement)
  - docs/ARCHITECTURE.md (system design)
  - docs/DATA_CONTRACTS.md (table schemas)
  - docs/METRICS.md (evaluation results)
  - docs/DEMO.md (demo script)
  - docs/RISK_REGISTER.md (known limitations)
  - docs/DECISION_LOG.md (technical choices)
  - docs/ROADMAP.md (future work)
  - docs/BUILD_LOG.md (weekly progress)
- ✅ Demo script (3-5 min)
- ✅ Release tag: `v0.1.0-mvp`
- ✅ GitHub repo: clean commit history, CI badge

**Tests**:
- Full end-to-end test (ingest → explain)
- Smoke test on fresh environment
- Demo script rehearsed

**Exit criteria**: Production-ready MVP, portfolio-quality artifacts

---

## Repo Scaffold

```
gnit/
├── .github/
│   └── workflows/
│       └── ci.yml                 # pytest + linting
├── .amazonq/
│   └── rules/
│       └── memory-bank/           # Project context
├── gnit/                          # Main package
│   ├── __init__.py
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── main.py                # Click CLI entry
│   │   ├── ingest.py
│   │   ├── normalize.py
│   │   ├── features.py
│   │   ├── train.py
│   │   ├── score.py
│   │   ├── explain.py
│   │   └── export.py
│   ├── ingest/
│   │   ├── __init__.py
│   │   ├── api_client.py          # USAspending API
│   │   └── fetcher.py
│   ├── normalize/
│   │   ├── __init__.py
│   │   ├── vendor_matcher.py      # Fuzzy matching
│   │   └── entity_resolver.py
│   ├── features/
│   │   ├── __init__.py
│   │   ├── aggregator.py          # Monthly rollups
│   │   └── engineer.py            # Feature generation
│   ├── detect/
│   │   ├── __init__.py
│   │   ├── baseline.py            # Robust MAD
│   │   ├── ml.py                  # Isolation Forest
│   │   └── backup.py              # Quantile method
│   ├── explain/
│   │   ├── __init__.py
│   │   ├── evidence.py            # Award linkage
│   │   ├── drivers.py             # Feature contribution
│   │   └── narrative.py           # Text generation
│   ├── db/
│   │   ├── __init__.py
│   │   ├── schema.sql             # Table definitions
│   │   ├── connection.py          # DuckDB client
│   │   └── queries.py             # Common queries
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py                # FastAPI app
│   │   ├── routes.py              # Endpoints
│   │   └── models.py              # Pydantic schemas
│   └── ui/
│       ├── __init__.py
│       └── app.py                 # Streamlit dashboard
├── tests/
│   ├── __init__.py
│   ├── test_ingest.py
│   ├── test_normalize.py
│   ├── test_features.py
│   ├── test_detection.py          # Injected anomaly tests
│   ├── test_explain.py
│   └── test_e2e.py                # End-to-end smoke test
├── config/
│   ├── vendor_overrides.csv       # Manual vendor mappings
│   └── detection_thresholds.yaml  # Configurable params
├── data/
│   ├── gnit.duckdb                # Main database (gitignored)
│   └── .gitkeep
├── models/
│   ├── <run_id>/
│   │   ├── isolation_forest.joblib
│   │   ├── scaler.joblib
│   │   └── features.json
│   └── .gitkeep
├── docs/
│   ├── SPECIFICATION.md           # This file
│   ├── THESIS.md
│   ├── ARCHITECTURE.md
│   ├── DATA_CONTRACTS.md
│   ├── METRICS.md
│   ├── DEMO.md
│   ├── RISK_REGISTER.md
│   ├── DECISION_LOG.md
│   ├── ROADMAP.md
│   └── BUILD_LOG.md
├── .gitignore
├── README.md
├── pyproject.toml                 # Poetry config
├── requirements.txt               # Pip fallback
└── LICENSE
```

