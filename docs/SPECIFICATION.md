# Gnit: Public Spending Change Detection Specification

## Executive Summary

**One-sentence goal**: Create a tool that makes public spending legible by detecting meaningful changes using both deterministic/robust statistics and machine learning anomaly detection, explaining each anomaly with row-level evidence.

**Domain**: Public spending (federal award-level data)  
**Geography**: Minnesota (place of performance)  
**Data source**: USAspending.gov API (award search endpoint)  
**Timeline**: 6 weeks to production-ready MVP  
**Demo time**: 3-5 minutes

---

## MVP Scope (Tight Wedge)

### In Scope
- **One question**: "What changed?" (monthly anomalies by vendor)
- **One geography**: Minnesota (place of performance)
- **One workflow**: Ingest → Normalize vendors → Aggregate monthly → Detect anomalies → Explain with evidence → Export report + minimal UI
- **Dual detection**: Robust MAD (baseline) + Isolation Forest (ML)
- **Evidence traceability**: Every anomaly links to specific award IDs, amounts, agencies, descriptions
- **Time range**: Last 24 months (rolling window)
- **Output formats**: JSON export, CSV report, Streamlit dashboard

### Explicitly Out of Scope
- ❌ Fraud detection or intent attribution
- ❌ Political analysis or commentary
- ❌ Perfect entity resolution (use fuzzy matching with known limitations)
- ❌ Multi-tenant cloud hosting
- ❌ Real-time streaming
- ❌ Multiple geographies in MVP
- ❌ Predictive modeling ("what will happen")
- ❌ Natural language generation beyond templated explanations
- ❌ User authentication/authorization
- ❌ Historical data beyond 24 months

---

## Data Model + Lineage

### Database: DuckDB (embedded, fast analytics)

**File location**: `data/gnit.duckdb`

### Table Schemas

#### 1. run_manifest
Tracks every pipeline execution for reproducibility.

```sql
CREATE TABLE run_manifest (
    run_id TEXT PRIMARY KEY,
    run_timestamp TIMESTAMP,
    filters_json TEXT,  -- {place_of_performance: "MN", date_range: [...]}
    row_count_raw INTEGER,
    row_count_normalized INTEGER,
    model_artifact_path TEXT,
    config_hash TEXT,
    status TEXT  -- 'running', 'completed', 'failed'
);
```

#### 2. raw_awards
Immutable storage of fetched awards.

```sql
CREATE TABLE raw_awards (
    run_id TEXT,
    award_id TEXT,
    recipient_name TEXT,
    recipient_duns TEXT,
    recipient_uei TEXT,
    awarding_agency_name TEXT,
    awarding_sub_agency_name TEXT,
    award_type TEXT,
    action_date DATE,
    obligation_amount DECIMAL(18,2),
    outlay_amount DECIMAL(18,2),
    naics_code TEXT,
    naics_description TEXT,
    psc_code TEXT,
    psc_description TEXT,
    award_description TEXT,
    place_of_performance_state TEXT,
    place_of_performance_city TEXT,
    PRIMARY KEY (run_id, award_id)
);
```

#### 3. vendor_entities
Normalized vendor identities.

```sql
CREATE TABLE vendor_entities (
    vendor_id TEXT PRIMARY KEY,  -- UUID
    canonical_name TEXT,
    created_at TIMESTAMP
);
```

#### 4. vendor_aliases
Maps raw recipient names to canonical vendors.

```sql
CREATE TABLE vendor_aliases (
    alias_name TEXT PRIMARY KEY,
    vendor_id TEXT REFERENCES vendor_entities(vendor_id),
    confidence_score DECIMAL(3,2)  -- 0.0-1.0
);
```

#### 5. award_vendor_map
Links awards to normalized vendors.

```sql
CREATE TABLE award_vendor_map (
    run_id TEXT,
    award_id TEXT,
    vendor_id TEXT,
    PRIMARY KEY (run_id, award_id),
    FOREIGN KEY (run_id, award_id) REFERENCES raw_awards(run_id, award_id)
);
```

#### 6. monthly_vendor_spend
Feature base for anomaly detection.

```sql
CREATE TABLE monthly_vendor_spend (
    run_id TEXT,
    vendor_id TEXT,
    year_month TEXT,  -- 'YYYY-MM'
    obligation_sum DECIMAL(18,2),
    outlay_sum DECIMAL(18,2),
    award_count INTEGER,
    avg_award_size DECIMAL(18,2),
    median_award_size DECIMAL(18,2),
    top3_award_concentration DECIMAL(5,4),  -- % of spend in top 3 awards
    -- Rolling features (trailing 3 months)
    rolling_3m_mean DECIMAL(18,2),
    rolling_3m_median DECIMAL(18,2),
    rolling_3m_mad DECIMAL(18,2),
    -- Rolling features (trailing 6 months)
    rolling_6m_mean DECIMAL(18,2),
    rolling_6m_median DECIMAL(18,2),
    rolling_6m_mad DECIMAL(18,2),
    -- Rolling features (trailing 12 months)
    rolling_12m_mean DECIMAL(18,2),
    rolling_12m_median DECIMAL(18,2),
    rolling_12m_mad DECIMAL(18,2),
    -- Change metrics
    mom_pct_change DECIMAL(8,4),  -- month-over-month % change
    -- Category diversity
    naics_count INTEGER,
    psc_count INTEGER,
    agency_count INTEGER,
    PRIMARY KEY (run_id, vendor_id, year_month)
);
```

#### 7. anomalies
Stores detected anomalies from both methods.

```sql
CREATE TABLE anomalies (
    anomaly_id TEXT PRIMARY KEY,  -- UUID
    run_id TEXT,
    vendor_id TEXT,
    year_month TEXT,
    detection_method TEXT,  -- 'robust_mad', 'isolation_forest'
    anomaly_score DECIMAL(8,6),
    severity TEXT,  -- 'low', 'medium', 'high', 'critical'
    explanation_json TEXT,  -- JSON with drivers + evidence
    award_ids TEXT[],  -- Array of contributing award IDs
    created_at TIMESTAMP,
    FOREIGN KEY (run_id, vendor_id, year_month) 
        REFERENCES monthly_vendor_spend(run_id, vendor_id, year_month)
);
```

### Lineage Guarantee
Every row in `anomalies` table MUST have:
- `award_ids`: Array of specific award IDs from `raw_awards`
- `explanation_json`: Contains top contributing awards with amounts, agencies, descriptions

---

## Anomaly Detection Approaches

### A) Baseline (Non-ML): Robust MAD

**Method**: Modified Z-score using Median Absolute Deviation

**Formula**:
```
MAD = median(|x_i - median(x)|)
robust_z = 0.6745 * (x - median(x)) / MAD
```

**Thresholds**:
- `|robust_z| > 3.5`: Critical
- `|robust_z| > 3.0`: High
- `|robust_z| > 2.5`: Medium
- `|robust_z| > 2.0`: Low

**Minimum volume filter**: Only flag vendors with:
- At least 6 months of history
- At least $50,000 total spend in trailing 12 months

**Implementation**: `gnit/detect/baseline.py::RobustMADDetector`

### B) ML Anomaly Detection: Isolation Forest (Primary)

**Algorithm**: Isolation Forest (scikit-learn)

**Rationale**:
- Unsupervised (no labels needed)
- Fast training and scoring
- Works well with mixed feature types
- Provides anomaly scores (not just binary)
- Explainable via feature contribution approximation

**Features per vendor-month** (18 features):
1. `obligation_sum` (log-transformed)
2. `outlay_sum` (log-transformed)
3. `award_count`
4. `avg_award_size` (log-transformed)
5. `top3_award_concentration`
6. `rolling_3m_mean` (log-transformed)
7. `rolling_3m_mad` (log-transformed)
8. `rolling_6m_mean` (log-transformed)
9. `rolling_6m_mad` (log-transformed)
10. `rolling_12m_mean` (log-transformed)
11. `rolling_12m_mad` (log-transformed)
12. `mom_pct_change`
13. `naics_count`
14. `psc_count`
15. `agency_count`
16. `month_sin` (cyclical encoding)
17. `month_cos` (cyclical encoding)
18. `vendor_tenure_months` (months since first award)

**Hyperparameters**:
```python
IsolationForest(
    n_estimators=200,
    max_samples=256,
    contamination=0.05,  # Expect 5% anomalies
    random_state=42,
    n_jobs=-1
)
```

**Training window**: All vendor-months with >= 6 months history  
**Scoring window**: Most recent 3 months

**Severity mapping** (based on anomaly score):
- Score < -0.5: Critical
- Score < -0.3: High
- Score < -0.1: Medium
- Score < 0.0: Low

**Implementation**: `gnit/detect/ml.py::IsolationForestDetector`

### C) Backup Method: Quantile-Based Outlier Detection

**Method**: Flag values beyond 95th/5th percentile with seasonal adjustment

**Use case**: Fallback if Isolation Forest fails or for comparison

**Implementation**: `gnit/detect/backup.py::QuantileDetector`

---

## Training Plan

### Approach: Unsupervised Learning

**No ground-truth labels available** → Use unsupervised methods

### Training Process

1. **Data preparation**:
   - Filter: vendors with >= 6 months history
   - Filter: total spend >= $50K in trailing 12 months
   - Handle missing values: forward-fill rolling features, drop if >30% missing
   - Log-transform: all monetary amounts (add 1 to handle zeros)
   - Standardize: StandardScaler on all features

2. **Model training**:
   ```bash
   gnit train-model --run-id <run_id>
   ```
   - Fit Isolation Forest on prepared features
   - Save model artifact: `models/<run_id>/isolation_forest.joblib`
   - Save scaler: `models/<run_id>/scaler.joblib`
   - Save feature names: `models/<run_id>/features.json`
   - Save config hash in `run_manifest`

3. **Reproducibility**:
   - Fixed `random_state=42`
   - Config hash includes: hyperparameters + feature list + filters
   - Model artifacts versioned per `run_id`
   - Training data snapshot stored in `monthly_vendor_spend` with `run_id`

### Scoring Process

```bash
gnit score-anomalies --run-id <run_id> --model-run-id <model_run_id>
```

- Load model from `models/<model_run_id>/`
- Apply same preprocessing pipeline
- Score most recent 3 months
- Store results in `anomalies` table

---

## Explainability Requirements (Trust Layer)

### For ALL Anomalies (Baseline + ML)

Every anomaly record must include:

#### 1. Evidence Rows (Top Contributing Awards)

```json
{
  "evidence": [
    {
      "award_id": "CONT_AWD_12345",
      "amount": 1250000.00,
      "agency": "Department of Transportation",
      "description": "Highway construction project",
      "action_date": "2024-01-15",
      "pct_of_month_total": 0.45
    }
  ]
}
```

**Selection criteria**: Top 5 awards by obligation amount for that vendor-month

#### 2. Feature Drivers (ML only)

For Isolation Forest anomalies, approximate feature contribution:

**Method**: Compare feature values to vendor's historical median

```json
{
  "drivers": [
    {
      "feature": "obligation_sum",
      "current_value": 2750000.00,
      "historical_median": 450000.00,
      "deviation_pct": 511.1,
      "direction": "increase"
    },
    {
      "feature": "award_count",
      "current_value": 2,
      "historical_median": 8,
      "deviation_pct": -75.0,
      "direction": "decrease"
    }
  ]
}
```

**Selection**: Top 3 features by absolute deviation percentage

#### 3. Narrative Template

```
{vendor_name} showed a {severity} anomaly in {year_month}.
Monthly spending {increased/decreased} to ${current_amount:,.0f} 
from a typical ${historical_median:,.0f} (median of prior 12 months).

Key changes:
- {driver_1_description}
- {driver_2_description}

Top contributing awards:
- {award_1_summary}
- {award_2_summary}
```

**Language constraints**:
- ✅ Use: "change," "anomaly," "outlier," "spike," "deviation," "increase," "decrease"
- ❌ Never: "fraud," "corruption," "suspicious," "illegal," "improper"

### Implementation

- `gnit/explain/evidence.py::build_evidence()`
- `gnit/explain/drivers.py::compute_feature_drivers()`
- `gnit/explain/narrative.py::generate_narrative()`

