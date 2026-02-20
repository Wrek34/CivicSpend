# Implementation Checklist

Step-by-step checklist for building Gnit MVP (Weeks 1-6).

---

## Pre-Development Setup

### Environment
- [ ] Python 3.11+ installed
- [ ] Virtual environment created (`python -m venv venv`)
- [ ] Virtual environment activated
- [ ] Git initialized (`git init`)
- [ ] GitHub repo created (public)
- [ ] Initial commit with docs

### Project Structure
- [ ] Create `gnit/` package directory
- [ ] Create `tests/` directory
- [ ] Create `config/` directory
- [ ] Create `data/` directory (add to .gitignore)
- [ ] Create `models/` directory (add to .gitignore)
- [ ] Create `.gitignore` file
- [ ] Create `requirements.txt` or `pyproject.toml`

### Dependencies
```bash
pip install duckdb pandas numpy scipy scikit-learn requests rapidfuzz click fastapi uvicorn streamlit pydantic pytest pytest-cov black isort flake8 mypy
```

- [ ] Install core dependencies
- [ ] Freeze requirements (`pip freeze > requirements.txt`)
- [ ] Test imports work

---

## Week 1: Foundation

### Day 1-2: Database Schema
- [ ] Create `gnit/db/schema.sql`
- [ ] Define `run_manifest` table
- [ ] Define `raw_awards` table
- [ ] Create `gnit/db/connection.py` (DuckDB client)
- [ ] Test: Create database, verify tables exist
- [ ] Commit: `feat(db): add schema and connection`

### Day 3-4: API Client
- [ ] Create `gnit/ingest/api_client.py`
- [ ] Implement `fetch_awards()` with filters
- [ ] Add rate limiting (5 req/sec)
- [ ] Add exponential backoff retry
- [ ] Test: Mock API response, verify parsing
- [ ] Commit: `feat(ingest): add USAspending API client`

### Day 5: CLI Ingest Command
- [ ] Create `gnit/cli/main.py` (Click app)
- [ ] Create `gnit/cli/ingest.py`
- [ ] Implement `gnit ingest` command
- [ ] Add `--state`, `--start-date`, `--end-date` options
- [ ] Generate `run_id` (UUID)
- [ ] Insert into `run_manifest`
- [ ] Batch insert into `raw_awards`
- [ ] Test: Run on small date range, verify data
- [ ] Commit: `feat(cli): add ingest command`

### Day 6: Validation & Testing
- [ ] Write `tests/test_ingest.py`
- [ ] Test: API client handles rate limits
- [ ] Test: Schema constraints enforced
- [ ] Test: Duplicate award_ids rejected
- [ ] Run full ingest (MN, 2022-2024)
- [ ] Query: Top 20 vendors by obligation
- [ ] Commit: `test(ingest): add unit tests`

### Day 7: Documentation
- [ ] Update BUILD_LOG.md (Week 1 progress)
- [ ] Update context.md (current status)
- [ ] Create DATA_CONTRACTS.md (table schemas)
- [ ] Commit: `docs(week1): add progress update`

**Exit Criteria**: ✅ Can fetch and store MN awards for 24 months

---

## Week 2: Normalization + Baseline

### Day 1-2: Vendor Normalization
- [ ] Create `gnit/normalize/vendor_matcher.py`
- [ ] Implement fuzzy matching (rapidfuzz)
- [ ] Use DUNS/UEI as strong identifiers
- [ ] Create `config/vendor_overrides.csv`
- [ ] Implement override loading
- [ ] Populate `vendor_entities` table
- [ ] Populate `vendor_aliases` table
- [ ] Populate `award_vendor_map` table
- [ ] Test: Known aliases map correctly
- [ ] Commit: `feat(normalize): add vendor deduplication`

### Day 3: CLI Normalize Command
- [ ] Create `gnit/cli/normalize.py`
- [ ] Implement `gnit normalize` command
- [ ] Add `--run-id` option
- [ ] Add `--similarity-threshold` option
- [ ] Test: Run on Week 1 data
- [ ] Commit: `feat(cli): add normalize command`

### Day 4-5: Feature Engineering
- [ ] Create `gnit/features/aggregator.py`
- [ ] Aggregate monthly spend per vendor
- [ ] Compute rolling features (3/6/12 months)
- [ ] Compute month-over-month change
- [ ] Add cyclical month encoding
- [ ] Populate `monthly_vendor_spend` table
- [ ] Test: Monthly sums match raw totals
- [ ] Commit: `feat(features): add monthly aggregation`

### Day 6: Baseline Detection
- [ ] Create `gnit/detect/baseline.py`
- [ ] Implement `compute_robust_z()`
- [ ] Implement `RobustMADDetector` class
- [ ] Apply minimum volume filters
- [ ] Map scores to severity levels
- [ ] Populate `anomalies` table (baseline method)
- [ ] Test: Injected spike detected
- [ ] Commit: `feat(detect): add robust MAD detector`

### Day 7: CLI Commands + Testing
- [ ] Create `gnit/cli/features.py` (`gnit build-features`)
- [ ] Create `gnit/cli/detect.py` (`gnit detect-baseline`)
- [ ] Write `tests/test_normalize.py`
- [ ] Write `tests/test_features.py`
- [ ] Write `tests/test_detection.py` (injected anomalies)
- [ ] Update BUILD_LOG.md (Week 2)
- [ ] Commit: `feat(cli): add features and detect commands`

**Exit Criteria**: ✅ Can detect anomalies using robust MAD

---

## Week 3: ML Detection

### Day 1-2: Feature Engineering for ML
- [ ] Create `gnit/features/engineer.py`
- [ ] Implement log transforms
- [ ] Implement StandardScaler pipeline
- [ ] Create feature matrix (18 features)
- [ ] Handle missing values
- [ ] Test: Feature matrix shape correct
- [ ] Commit: `feat(features): add ML feature engineering`

### Day 3-4: Isolation Forest
- [ ] Create `gnit/detect/ml.py`
- [ ] Implement `IsolationForestDetector` class
- [ ] Set hyperparameters (n_estimators=200, contamination=0.05)
- [ ] Implement training method
- [ ] Implement scoring method
- [ ] Map anomaly scores to severity
- [ ] Test: Model training deterministic
- [ ] Commit: `feat(detect): add Isolation Forest detector`

### Day 5: Model Artifacts
- [ ] Create `models/` directory structure
- [ ] Save model: `models/<run_id>/isolation_forest.joblib`
- [ ] Save scaler: `models/<run_id>/scaler.joblib`
- [ ] Save features: `models/<run_id>/features.json`
- [ ] Save config: `models/<run_id>/config.json`
- [ ] Compute config hash
- [ ] Update `run_manifest` with model path
- [ ] Test: Model loading works
- [ ] Commit: `feat(ml): add model artifact storage`

### Day 6: CLI Commands
- [ ] Create `gnit/cli/train.py` (`gnit train-model`)
- [ ] Create `gnit/cli/score.py` (`gnit score-anomalies`)
- [ ] Add `--model-run-id` option to score
- [ ] Populate `anomalies` table (ML method)
- [ ] Test: Injected anomaly detected by ML
- [ ] Commit: `feat(cli): add train and score commands`

### Day 7: Comparison + Testing
- [ ] Query: Side-by-side baseline vs ML anomalies
- [ ] Write `tests/test_ml.py`
- [ ] Test: Stability check (run twice, compare)
- [ ] Update BUILD_LOG.md (Week 3)
- [ ] Commit: `test(ml): add stability tests`

**Exit Criteria**: ✅ Can train and score with Isolation Forest

---

## Week 4: Explanation + API

### Day 1-2: Evidence Builder
- [ ] Create `gnit/explain/evidence.py`
- [ ] Implement `build_evidence()` function
- [ ] Query top N awards per anomaly
- [ ] Compute % of month total
- [ ] Format evidence JSON
- [ ] Test: Evidence rows sum to monthly total
- [ ] Commit: `feat(explain): add evidence builder`

### Day 3: Feature Drivers
- [ ] Create `gnit/explain/drivers.py`
- [ ] Implement `compute_feature_drivers()` function
- [ ] Compare current vs historical median
- [ ] Compute deviation percentage
- [ ] Rank by absolute deviation
- [ ] Test: Top 3 drivers identified
- [ ] Commit: `feat(explain): add feature driver calculator`

### Day 4: Narrative Generator
- [ ] Create `gnit/explain/narrative.py`
- [ ] Implement `generate_narrative()` function
- [ ] Create narrative template
- [ ] Enforce language constraints (no "fraud")
- [ ] Test: Narrative renders correctly
- [ ] Commit: `feat(explain): add narrative generator`

### Day 5: CLI Explain Command
- [ ] Create `gnit/cli/explain.py` (`gnit explain`)
- [ ] Update `anomalies.explanation_json` for all records
- [ ] Update `anomalies.award_ids` array
- [ ] Test: 100% of anomalies have explanation
- [ ] Commit: `feat(cli): add explain command`

### Day 6-7: FastAPI
- [ ] Create `gnit/api/main.py` (FastAPI app)
- [ ] Create `gnit/api/models.py` (Pydantic schemas)
- [ ] Create `gnit/api/routes.py`
- [ ] Implement `GET /anomalies`
- [ ] Implement `GET /anomalies/{anomaly_id}`
- [ ] Implement `GET /vendors/{vendor_id}/timeline`
- [ ] Test: All endpoints return 200
- [ ] Update BUILD_LOG.md (Week 4)
- [ ] Commit: `feat(api): add FastAPI endpoints`

**Exit Criteria**: ✅ Can explain any anomaly with evidence

---

## Week 5: UI + Export

### Day 1-3: Streamlit Dashboard
- [ ] Create `gnit/ui/app.py`
- [ ] Page 1: Anomaly list
  - [ ] Filterable by severity
  - [ ] Filterable by method
  - [ ] Filterable by vendor
  - [ ] Sortable by score
- [ ] Page 2: Vendor detail
  - [ ] Spending timeline chart
  - [ ] Anomaly markers
  - [ ] Summary stats
- [ ] Page 3: Anomaly detail
  - [ ] Evidence table (top awards)
  - [ ] Feature drivers chart
  - [ ] Narrative text
- [ ] Test: UI loads without errors
- [ ] Commit: `feat(ui): add Streamlit dashboard`

### Day 4: Export Functionality
- [ ] Create `gnit/cli/export.py` (`gnit export-report`)
- [ ] Implement CSV export
  - [ ] Columns: vendor_name, year_month, severity, method, anomaly_score, obligation_sum, explanation_summary
- [ ] Implement JSON export
  - [ ] Full anomaly records with evidence
- [ ] Add `--format` option (csv/json)
- [ ] Add `--output` option (file path)
- [ ] Add `--severity` filter
- [ ] Test: Export matches database records
- [ ] Commit: `feat(cli): add export command`

### Day 5-6: Integration Testing
- [ ] Write `tests/test_ui.py` (basic smoke tests)
- [ ] Write `tests/test_export.py`
- [ ] Write `tests/test_e2e.py` (full pipeline)
- [ ] Run full pipeline end-to-end
- [ ] Verify all data flows correctly
- [ ] Update BUILD_LOG.md (Week 5)
- [ ] Commit: `test(e2e): add integration tests`

### Day 7: Demo Prep
- [ ] Prepare demo dataset (MN, 2022-2024)
- [ ] Run full pipeline on demo data
- [ ] Verify anomalies detected
- [ ] Test all UI features
- [ ] Draft DEMO.md script
- [ ] Commit: `docs(demo): add demo script`

**Exit Criteria**: ✅ Can demo full workflow in UI

---

## Week 6: Hardening + Docs

### Day 1-2: Error Handling & Logging
- [ ] Add try/except blocks to all CLI commands
- [ ] Add structured logging (Python logging module)
- [ ] Handle API failures gracefully
- [ ] Handle missing data gracefully
- [ ] Add progress bars (tqdm)
- [ ] Test: Graceful degradation on errors
- [ ] Commit: `feat(core): add error handling and logging`

### Day 3: Performance Optimization
- [ ] Add database indexes
  - [ ] `idx_raw_awards_run_id`
  - [ ] `idx_anomalies_run_id`
  - [ ] `idx_monthly_vendor_spend_composite`
- [ ] Profile slow queries
- [ ] Optimize aggregations
- [ ] Test: Query times acceptable (<5 sec)
- [ ] Commit: `perf(db): add indexes and optimize queries`

### Day 4-5: Documentation
- [ ] Complete DATA_CONTRACTS.md (all table schemas)
- [ ] Complete DEMO.md (full script)
- [ ] Complete METRICS.md (evaluation results)
- [ ] Update ARCHITECTURE.md (add diagrams)
- [ ] Update README.md (correct URLs)
- [ ] Verify all links work
- [ ] Commit: `docs(final): complete all documentation`

### Day 6: Testing & QA
- [ ] Run full test suite (`pytest`)
- [ ] Verify code coverage >= 70%
- [ ] Run linting (`black`, `isort`, `flake8`)
- [ ] Fix all linting errors
- [ ] Run type checking (`mypy`)
- [ ] Smoke test on fresh environment
- [ ] Commit: `test(qa): final QA pass`

### Day 7: Release
- [ ] Update BUILD_LOG.md (Week 6 + retrospective)
- [ ] Update METRICS.md (final results)
- [ ] Rehearse demo script 3+ times
- [ ] Record demo video (backup)
- [ ] Clean commit history (squash if needed)
- [ ] Create release tag: `v0.1.0-mvp`
- [ ] Push to GitHub
- [ ] Verify CI passes
- [ ] Update README badges
- [ ] Commit: `release: v0.1.0-mvp`

**Exit Criteria**: ✅ Production-ready MVP, portfolio-quality artifacts

---

## Final Verification

### Code Quality
- [ ] All tests passing
- [ ] Code coverage >= 70%
- [ ] No linting errors
- [ ] Type hints on public functions
- [ ] Clean commit history

### Functionality
- [ ] Can ingest MN awards (24 months)
- [ ] Can normalize vendors (~85% accuracy)
- [ ] Can detect anomalies (baseline + ML)
- [ ] Can explain anomalies (100% traceability)
- [ ] Can export reports (CSV + JSON)
- [ ] UI loads and works

### Documentation
- [ ] README.md complete
- [ ] 10+ docs in `docs/`
- [ ] Memory Bank updated
- [ ] All links work
- [ ] Demo script rehearsed

### Metrics
- [ ] Injected anomaly precision >= 80%
- [ ] Stability score >= 95%
- [ ] Evidence traceability = 100%
- [ ] Human plausibility >= 70%
- [ ] Time savings >= 5x
- [ ] Zero crashes on demo

### Portfolio
- [ ] GitHub repo public
- [ ] CI badge (tests passing)
- [ ] Release tag: v0.1.0-mvp
- [ ] Clean README
- [ ] Professional presentation

---

## Post-MVP

### Immediate Next Steps
- [ ] Share demo with peers (get feedback)
- [ ] Add to portfolio site
- [ ] Write blog post about project
- [ ] Consider Phase 2 features

### Phase 2 Planning
- [ ] Review ROADMAP.md post-MVP phases
- [ ] Prioritize features based on feedback
- [ ] Estimate effort for next phase
- [ ] Update project board

---

**Status**: Ready to start Week 1  
**Target Start Date**: [To be determined]  
**Target Completion**: [Start + 6 weeks]

