# Roadmap

## MVP (Weeks 1-6) - CURRENT PHASE

### Week 1: Foundation ✅
- [x] DuckDB schema created
- [x] USAspending API client with rate limiting
- [x] CLI: `civicspend ingest`
- [x] `raw_awards` table populated
- [x] `run_manifest` tracking
- [x] Query: Top 20 vendors by obligation
- [x] Tests: API client, schema constraints

**Exit Criteria**: ✅ Can fetch and store MN awards for 24 months

---

### Week 2: Normalization + Baseline Detection ✅
- [x] Vendor fuzzy matching (rapidfuzz)
- [x] DUNS/UEI strong identifiers
- [ ] Manual override file support
- [x] CLI: `civicspend normalize`
- [x] `vendor_entities`, `vendor_aliases`, `award_vendor_map` populated
- [x] Monthly aggregation with rolling features
- [x] CLI: `civicspend build-features`
- [x] `monthly_vendor_spend` table populated
- [x] Robust MAD detector
- [x] CLI: `civicspend detect`
- [x] Anomalies detected (baseline method)
- [x] Tests: Normalization, aggregation, injected spike detection

**Exit Criteria**: ✅ Can detect anomalies using robust MAD

---

### Week 3: ML Anomaly Detection ✅
- [x] Feature engineering (16 features)
- [x] Log transforms, cyclical encoding
- [x] StandardScaler pipeline
- [x] Isolation Forest trainer
- [x] CLI: `civicspend train-model`
- [x] Model artifacts saved (`models/<run_id>/`)
- [x] ML anomalies detected
- [x] Side-by-side comparison: baseline vs ML
- [x] Tests: Model training deterministic, injected anomaly detection

**Exit Criteria**: ✅ Can train and score with Isolation Forest

---

### Week 4: Explanation + Export ✅
- [x] Evidence builder (top N awards per anomaly)
- [x] Feature driver calculator (deviation from historical median)
- [x] Narrative generator (templated explanations)
- [x] Evidence layer with 100% traceability
- [x] CLI: `civicspend export`
- [x] CSV export (summary columns)
- [x] JSON export (full records with evidence)
- [ ] FastAPI app setup
- [ ] Endpoints: `/anomalies`, `/anomalies/{id}`, `/vendors/{id}/timeline`
- [ ] Pydantic schemas for validation
- [ ] API documentation (auto-generated)
- [x] Tests: Evidence traceability, narrative rendering

**Exit Criteria**: ✅ Can explain any anomaly with evidence

---

### Week 5: UI + Dashboard ✅
- [x] Streamlit dashboard
- [x] Page 1: Anomaly list (filterable)
- [x] Page 2: Vendor detail (timeline + anomalies)
- [x] Page 3: Evidence explorer (drill-down to awards)
- [x] Interactive Plotly charts
- [x] Export functionality integrated
- [x] Tests: Export CSV/JSON

**Exit Criteria**: ✅ Can demo full workflow in UI

---

### Week 6: Hardening + Documentation 🚧
- [ ] Error handling (API failures, missing data)
- [ ] Structured logging
- [ ] Query optimization (indexes)
- [x] README.md (setup + quickstart)
- [x] docs/THESIS.md
- [ ] docs/ARCHITECTURE.md (detailed)
- [ ] docs/DATA_CONTRACTS.md
- [ ] docs/METRICS.md (evaluation results)
- [x] docs/DEMO.md (3-5 min script)
- [x] docs/RISK_REGISTER.md
- [x] docs/DECISION_LOG.md
- [x] docs/ROADMAP.md (this file)
- [ ] docs/BUILD_LOG.md (weekly updates)
- [ ] Demo script rehearsed
- [ ] Release tag: v0.1.0-mvp
- [ ] GitHub repo public
- [ ] CI badge (tests passing)
- [x] Tests: End-to-end smoke test, demo dataset

**Exit Criteria**: Production-ready MVP, portfolio-quality artifacts

---

## Post-MVP (Future Work)

### Phase 2: Multi-Geography Support (Weeks 7-8)
- [ ] Extend to all 50 states
- [ ] State-level comparison dashboard
- [ ] Geographic heatmap of anomalies
- [ ] Performance optimization for larger datasets

### Phase 3: Enhanced ML (Weeks 9-10)
- [ ] SHAP for precise feature attribution
- [ ] Ensemble methods (combine multiple detectors)
- [ ] Time-series forecasting (predict future spend)
- [ ] Anomaly clustering (group similar anomalies)

### Phase 4: Advanced Features (Weeks 11-12)
- [ ] Natural language search ("show me highway contracts")
- [ ] Automated report generation (weekly summaries)
- [ ] Email alerts for new anomalies
- [ ] Historical trend analysis

### Phase 5: Production Deployment (Weeks 13-14)
- [ ] Docker containerization
- [ ] Cloud deployment (AWS/GCP)
- [ ] PostgreSQL migration (for concurrent access)
- [ ] User authentication
- [ ] Multi-tenant support

### Phase 6: Data Expansion (Weeks 15-16)
- [ ] Additional data sources (grants, loans)
- [ ] Contract modifications tracking
- [ ] Vendor relationship networks
- [ ] Agency-level analysis

---

## Backlog (Prioritized)

### High Priority
- [ ] Improve vendor normalization accuracy (target 95%)
- [ ] Add more robust statistical methods (Grubbs' test, GESD)
- [ ] Implement quantile-based backup detector
- [ ] Add data quality dashboard

### Medium Priority
- [ ] React UI (replace Streamlit)
- [ ] Real-time data ingestion (streaming)
- [ ] Anomaly feedback loop (user corrections)
- [ ] Comparative analysis (vendor vs vendor)

### Low Priority
- [ ] Mobile app
- [ ] Internationalization (i18n)
- [ ] Dark mode UI
- [ ] PDF report generation

---

## Out of Scope (Explicitly)

These will NOT be implemented:

- ❌ Fraud detection or intent attribution
- ❌ Political analysis or commentary
- ❌ Perfect entity resolution (accept ~85% accuracy)
- ❌ Real-time alerting (batch processing only)
- ❌ Predictive modeling beyond anomaly detection
- ❌ Natural language generation (beyond templates)
- ❌ Multi-user collaboration features
- ❌ Data entry or manual corrections (read-only)
- ❌ Integration with procurement systems
- ❌ Compliance or regulatory reporting

---

## Success Metrics (Week 6 Target)

### Technical
- ✅ Injected anomaly precision >= 80%
- ✅ Stability score >= 95%
- ✅ Code coverage >= 70%
- ✅ All tests passing
- ✅ Zero crashes on demo dataset

### Quality
- ✅ 100% evidence traceability
- ✅ Human plausibility rate >= 70%
- ✅ Time savings >= 5x vs manual analysis

### Portfolio
- ✅ Complete documentation (8+ docs)
- ✅ Clean commit history
- ✅ Public GitHub repo
- ✅ CI badge (tests passing)
- ✅ 3-5 min demo script rehearsed
- ✅ Release tag: v0.1.0-mvp

