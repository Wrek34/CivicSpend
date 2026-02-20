# Quick Reference Guide

Essential commands, thresholds, and patterns for Gnit development.

---

## CLI Commands (Cheat Sheet)

```bash
# Full pipeline
gnit ingest --state MN --start-date 2022-01-01 --end-date 2024-01-31
gnit normalize --run-id <run_id>
gnit build-features --run-id <run_id>
gnit train-model --run-id <run_id>
gnit score-anomalies --run-id <run_id> --model-run-id <run_id>
gnit explain --run-id <run_id>

# Export
gnit export-report --run-id <run_id> --format csv --output report.csv

# UI
streamlit run gnit/ui/app.py

# API
uvicorn gnit.api.main:app --reload
```

---

## Key Thresholds

### Robust MAD Severity
- `|robust_z| > 3.5`: Critical
- `|robust_z| > 3.0`: High
- `|robust_z| > 2.5`: Medium
- `|robust_z| > 2.0`: Low

### Isolation Forest Severity
- `score < -0.5`: Critical
- `score < -0.3`: High
- `score < -0.1`: Medium
- `score < 0.0`: Low

### Minimum Volume Filters
- **Vendor history**: >= 6 months
- **Total spend**: >= $50,000 (trailing 12 months)

### Vendor Normalization
- **Fuzzy match threshold**: 0.85 (85% similarity)
- **Confidence score**: 0.0-1.0

---

## Database Tables (Quick Ref)

```sql
-- Run tracking
run_manifest (run_id, run_timestamp, filters_json, row_count_raw, model_artifact_path, config_hash, status)

-- Raw data
raw_awards (run_id, award_id, recipient_name, awarding_agency_name, obligation_amount, action_date, ...)

-- Vendor normalization
vendor_entities (vendor_id, canonical_name, created_at)
vendor_aliases (alias_name, vendor_id, confidence_score)
award_vendor_map (run_id, award_id, vendor_id)

-- Features
monthly_vendor_spend (run_id, vendor_id, year_month, obligation_sum, award_count, rolling_3m_mean, ...)

-- Anomalies
anomalies (anomaly_id, run_id, vendor_id, year_month, detection_method, anomaly_score, severity, explanation_json, award_ids)
```

---

## Feature List (18 Features)

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
18. `vendor_tenure_months`

---

## Model Hyperparameters

```python
IsolationForest(
    n_estimators=200,
    max_samples=256,
    contamination=0.05,  # 5% expected anomalies
    random_state=42,
    n_jobs=-1
)
```

---

## Language Constraints

### ✅ Use These Words
- change
- anomaly
- outlier
- spike
- drop
- deviation
- increase
- decrease
- pattern

### ❌ Never Use These Words
- fraud
- corruption
- suspicious
- illegal
- improper
- wrongdoing
- misconduct

---

## File Paths

```
data/gnit.duckdb                          # Main database
models/<run_id>/isolation_forest.joblib   # Trained model
models/<run_id>/scaler.joblib             # Feature scaler
models/<run_id>/features.json             # Feature list
config/vendor_overrides.csv               # Manual vendor mappings
config/detection_thresholds.yaml          # Configurable params
```

---

## Testing Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=gnit --cov-report=html

# Run specific test file
pytest tests/test_detection.py -v

# Run specific test
pytest tests/test_detection.py::test_baseline_spike_detection -v

# Run injected anomaly tests only
pytest tests/test_detection.py -k "injected" -v
```

---

## Common Queries

### Top 20 Vendors by Obligation
```sql
SELECT 
    ve.canonical_name,
    SUM(ra.obligation_amount) as total_obligation
FROM raw_awards ra
JOIN award_vendor_map avm ON ra.run_id = avm.run_id AND ra.award_id = avm.award_id
JOIN vendor_entities ve ON avm.vendor_id = ve.vendor_id
WHERE ra.run_id = '<run_id>'
GROUP BY ve.canonical_name
ORDER BY total_obligation DESC
LIMIT 20;
```

### Anomalies by Severity
```sql
SELECT 
    severity,
    detection_method,
    COUNT(*) as count
FROM anomalies
WHERE run_id = '<run_id>'
GROUP BY severity, detection_method
ORDER BY severity, detection_method;
```

### Vendor Timeline
```sql
SELECT 
    year_month,
    obligation_sum,
    award_count,
    rolling_12m_median
FROM monthly_vendor_spend
WHERE run_id = '<run_id>' AND vendor_id = '<vendor_id>'
ORDER BY year_month;
```

---

## API Endpoints

```bash
# List anomalies
GET /anomalies?run_id=<run_id>&severity=high&method=isolation_forest

# Get anomaly detail
GET /anomalies/<anomaly_id>

# Vendor timeline
GET /vendors/<vendor_id>/timeline?run_id=<run_id>
```

---

## Git Workflow

```bash
# Feature branch
git checkout -b feature/week-1-ingestion

# Commit with conventional commits
git commit -m "feat(ingest): add USAspending API client"
git commit -m "test(ingest): add rate limit tests"
git commit -m "docs(readme): update quickstart"

# Push and merge
git push origin feature/week-1-ingestion
# Create PR, review, merge to main

# Tag release
git tag -a v0.1.0-mvp -m "MVP release"
git push origin v0.1.0-mvp
```

---

## Debugging Tips

### Check Run Status
```sql
SELECT * FROM run_manifest ORDER BY run_timestamp DESC LIMIT 5;
```

### Validate Row Counts
```sql
SELECT 
    (SELECT COUNT(*) FROM raw_awards WHERE run_id = '<run_id>') as raw_count,
    (SELECT COUNT(*) FROM award_vendor_map WHERE run_id = '<run_id>') as mapped_count,
    (SELECT COUNT(*) FROM monthly_vendor_spend WHERE run_id = '<run_id>') as feature_count;
```

### Check Anomaly Distribution
```sql
SELECT 
    detection_method,
    severity,
    COUNT(*) as count,
    AVG(anomaly_score) as avg_score
FROM anomalies
WHERE run_id = '<run_id>'
GROUP BY detection_method, severity;
```

### Find Vendors with Most Anomalies
```sql
SELECT 
    ve.canonical_name,
    COUNT(*) as anomaly_count
FROM anomalies a
JOIN vendor_entities ve ON a.vendor_id = ve.vendor_id
WHERE a.run_id = '<run_id>'
GROUP BY ve.canonical_name
ORDER BY anomaly_count DESC
LIMIT 10;
```

---

## Performance Optimization

### Add Indexes
```sql
CREATE INDEX idx_raw_awards_run_id ON raw_awards(run_id);
CREATE INDEX idx_raw_awards_award_id ON raw_awards(award_id);
CREATE INDEX idx_anomalies_run_id ON anomalies(run_id);
CREATE INDEX idx_anomalies_vendor_id ON anomalies(vendor_id);
CREATE INDEX idx_monthly_vendor_spend_composite ON monthly_vendor_spend(run_id, vendor_id, year_month);
```

### Batch Processing
```python
# Process in chunks
BATCH_SIZE = 1000
for i in range(0, len(awards), BATCH_SIZE):
    batch = awards[i:i+BATCH_SIZE]
    process_batch(batch)
```

---

## Environment Variables

```bash
# .env file
USASPENDING_API_URL=https://api.usaspending.gov/api/v2/search/spending_by_award/
USASPENDING_RATE_LIMIT=5  # requests per second
DUCKDB_PATH=data/gnit.duckdb
MODEL_DIR=models/
LOG_LEVEL=INFO
```

---

## Code Style

```bash
# Format code
black gnit/ tests/
isort gnit/ tests/

# Lint
flake8 gnit/ tests/

# Type check
mypy gnit/
```

---

## Weekly Checklist Template

```markdown
## Week X: [Title]

### Monday
- [ ] Task 1
- [ ] Task 2

### Tuesday-Thursday
- [ ] Implementation
- [ ] Tests

### Friday
- [ ] Documentation
- [ ] Weekly update in BUILD_LOG.md
- [ ] Commit and push

### Exit Criteria
- [ ] Criterion 1
- [ ] Criterion 2
```

---

## Demo Prep Checklist

- [ ] Run full pipeline on demo dataset
- [ ] Verify anomalies detected (both methods)
- [ ] Check evidence links work
- [ ] Test all UI filters
- [ ] Rehearse script 3+ times
- [ ] Prepare backup (video recording)
- [ ] Test on fresh environment

---

## Success Metrics (Week 6 Target)

- [ ] Injected anomaly precision >= 80%
- [ ] Stability score >= 95%
- [ ] Code coverage >= 70%
- [ ] Evidence traceability = 100%
- [ ] Human plausibility >= 70%
- [ ] Time savings >= 5x
- [ ] Zero crashes on demo
- [ ] All docs complete (10+)
- [ ] Tests passing (CI green)
- [ ] Demo rehearsed (3-5 min)

