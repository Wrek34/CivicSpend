# Risk Register

## Data Quality Risks

### Risk: Incomplete or Missing Award Data
- **Likelihood**: Medium
- **Impact**: Medium
- **Mitigation**: 
  - Validate row counts against API metadata
  - Log missing fields
  - Filter out awards with null amounts
- **Contingency**: Manual data quality report, exclude problematic date ranges

### Risk: Vendor Name Inconsistency
- **Likelihood**: High
- **Impact**: Medium
- **Mitigation**:
  - Use DUNS/UEI as strong identifiers
  - Fuzzy matching with 85% threshold
  - Manual override file for known aliases
- **Contingency**: Accept imperfect entity resolution, document limitations

### Risk: API Rate Limiting or Downtime
- **Likelihood**: Medium
- **Impact**: High
- **Mitigation**:
  - Exponential backoff retry logic
  - Cache raw responses
  - Batch requests with delays
- **Contingency**: Use cached data, schedule ingestion during off-peak hours

---

## Model Risks

### Risk: High False Positive Rate
- **Likelihood**: Medium
- **Impact**: High
- **Mitigation**:
  - Minimum volume thresholds ($50K, 6 months history)
  - Dual detection (baseline + ML) for validation
  - Human review of sample anomalies
- **Contingency**: Adjust contamination parameter, increase severity thresholds

### Risk: Model Overfitting to Seasonal Patterns
- **Likelihood**: Low
- **Impact**: Medium
- **Mitigation**:
  - Cyclical month encoding
  - Rolling features capture seasonality
  - Isolation Forest is robust to periodic patterns
- **Contingency**: Add STL decomposition to remove seasonality

### Risk: Non-Reproducible Results
- **Likelihood**: Low
- **Impact**: High
- **Mitigation**:
  - Fixed random_state=42
  - Version model artifacts per run_id
  - Config hash in run_manifest
- **Contingency**: Re-train model, compare results

---

## Technical Risks

### Risk: DuckDB Performance Degradation
- **Likelihood**: Low
- **Impact**: Medium
- **Mitigation**:
  - Add indexes on frequently queried columns
  - Partition by run_id
  - Monitor query times
- **Contingency**: Migrate to PostgreSQL if needed

### Risk: Memory Overflow on Large Datasets
- **Likelihood**: Low
- **Impact**: High
- **Mitigation**:
  - Process in batches
  - Use DuckDB for out-of-core operations
  - Monitor memory usage
- **Contingency**: Reduce date range, filter to top N vendors

### Risk: Dependency Conflicts
- **Likelihood**: Low
- **Impact**: Low
- **Mitigation**:
  - Pin dependency versions in requirements.txt
  - Use virtual environment
  - Test on fresh install
- **Contingency**: Use Docker for reproducible environment

---

## Scope Risks

### Risk: Feature Creep
- **Likelihood**: High
- **Impact**: High
- **Mitigation**:
  - Strict MVP scope definition
  - Weekly milestone reviews
  - "Out of scope" list in spec
- **Contingency**: Cut features, prioritize core workflow

### Risk: Timeline Overrun
- **Likelihood**: Medium
- **Impact**: High
- **Mitigation**:
  - Week-by-week deliverables
  - Early integration testing
  - Buffer in Week 6 for hardening
- **Contingency**: Ship minimal UI (Streamlit only), defer FastAPI

---

## Interpretation Risks

### Risk: Anomalies Misinterpreted as Fraud
- **Likelihood**: Medium
- **Impact**: Critical
- **Mitigation**:
  - Explicit language constraints (no "fraud," "corruption")
  - Factual narratives only
  - Prominent disclaimer in UI
- **Contingency**: Add legal disclaimer, user education

### Risk: Lack of Domain Context
- **Likelihood**: High
- **Impact**: Medium
- **Mitigation**:
  - Provide evidence rows for manual review
  - Link to USAspending.gov for full context
  - Encourage human-in-the-loop validation
- **Contingency**: Add "Report Issue" button for user feedback

---

## Portfolio Risks

### Risk: Insufficient Documentation
- **Likelihood**: Low
- **Impact**: High
- **Mitigation**:
  - Documentation templates created upfront
  - Weekly build log updates
  - Demo script rehearsed
- **Contingency**: Dedicate Week 6 to documentation

### Risk: Demo Failure
- **Likelihood**: Low
- **Impact**: Critical
- **Mitigation**:
  - Smoke test before demo
  - Prepared dataset
  - Rehearse script 3+ times
- **Contingency**: Video recording as backup

---

## Known Limitations

1. **Not fraud detection**: Tool identifies changes, not intent
2. **Imperfect entity resolution**: Vendor normalization ~85% accurate
3. **No ground-truth validation**: Unsupervised learning, no labeled anomalies
4. **Single geography**: MVP limited to Minnesota
5. **24-month window**: Limited historical context
6. **Batch processing**: Not real-time
7. **No user authentication**: Open access (MVP)
8. **Local deployment**: Not cloud-hosted
9. **English only**: No internationalization
10. **No predictive capability**: Detects past changes, doesn't forecast

