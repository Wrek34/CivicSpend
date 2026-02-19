# Gnit: Project Summary

## Executive Overview

**Project**: Gnit (Government Insight Tracker)  
**Goal**: Detect meaningful changes in public spending using robust statistics + machine learning  
**Timeline**: 6 weeks (MVP)  
**Builder**: Solo developer  
**Status**: Specification complete, ready for Week 1 implementation

---

## What Makes This Project Unique

### 1. Dual Detection Strategy
- **Baseline (Robust MAD)**: Transparent statistical method
- **ML (Isolation Forest)**: Complex pattern detection
- **Side-by-side**: Validates ML with statistics, demonstrates technical breadth

### 2. Evidence-First Design
- Every anomaly traceable to source award IDs
- No black boxes: full lineage from raw data to finding
- Factual narratives only (no speculation or fraud claims)

### 3. Portfolio-Quality Artifacts
- 10+ documentation files
- Complete test suite (unit + integration + injected anomalies)
- Clean architecture (CLI → DB → API → UI)
- Reproducible runs (immutable run_id, versioned models)

### 4. Realistic Scope
- Feasible for solo builder in 6 weeks
- Demos reliably in 3-5 minutes
- Manageable data volume (~50K-100K awards)
- Clear expansion path post-MVP

---

## Technical Highlights

### Architecture
```
USAspending API → DuckDB → Feature Engineering → Dual Detection → Explanation → Dashboard
```

### Stack
- **Python 3.11+**: Core language
- **DuckDB**: Embedded analytics database (no server)
- **scikit-learn**: Isolation Forest (ML)
- **FastAPI**: REST API
- **Streamlit**: Dashboard UI
- **pytest**: Testing framework

### Key Algorithms
1. **Robust MAD**: Modified Z-score using Median Absolute Deviation
2. **Isolation Forest**: Unsupervised anomaly detection on 18 features
3. **Fuzzy Matching**: Vendor normalization (rapidfuzz)

### Data Pipeline
1. **Ingest**: Fetch awards from USAspending API
2. **Normalize**: Deduplicate vendors (fuzzy + DUNS/UEI)
3. **Aggregate**: Monthly spend + rolling features
4. **Train**: Fit Isolation Forest on historical data
5. **Score**: Detect anomalies (baseline + ML)
6. **Explain**: Link to evidence awards + compute drivers
7. **Serve**: API + dashboard for exploration

---

## Deliverables (Week 6)

### Code
- ✅ 7 CLI commands (ingest, normalize, build-features, train-model, score-anomalies, explain, export-report)
- ✅ DuckDB schema (7 tables)
- ✅ Dual detection (baseline + ML)
- ✅ Explanation layer (evidence + drivers + narratives)
- ✅ FastAPI endpoints (3 routes)
- ✅ Streamlit dashboard (3 pages)

### Tests
- ✅ Unit tests (normalization, features, detection)
- ✅ Injected anomaly tests (precision >= 80%)
- ✅ End-to-end smoke test
- ✅ Code coverage >= 70%

### Documentation
- ✅ README.md (setup + quickstart)
- ✅ THESIS.md (problem statement)
- ✅ SPECIFICATION.md (complete technical spec)
- ✅ ARCHITECTURE.md (system design)
- ✅ DATA_CONTRACTS.md (table schemas)
- ✅ METRICS.md (evaluation results)
- ✅ DEMO.md (3-5 min script)
- ✅ RISK_REGISTER.md (limitations)
- ✅ DECISION_LOG.md (technical choices)
- ✅ ROADMAP.md (week-by-week plan)
- ✅ BUILD_LOG.md (weekly progress)

### Artifacts
- ✅ GitHub repo (public, clean history)
- ✅ CI badge (tests passing)
- ✅ Release tag: v0.1.0-mvp
- ✅ Demo dataset (Minnesota, 2022-2024)
- ✅ Model artifacts (versioned per run)

---

## Success Metrics

### Technical
- **Injected anomaly precision**: >= 80%
- **Stability score**: >= 95% (reproducible results)
- **Code coverage**: >= 70%
- **Evidence traceability**: 100% (all anomalies link to awards)

### Quality
- **Human plausibility rate**: >= 70% (sample review)
- **Time savings**: >= 5x vs manual analysis
- **Zero crashes**: On demo dataset

### Portfolio
- **Documentation**: 10+ files
- **Tests**: 20+ test cases
- **Demo**: 3-5 minutes, rehearsed
- **Commit history**: Clean, professional

---

## Week-by-Week Plan

### Week 1: Foundation
- DuckDB schema + USAspending API client
- CLI: `gnit ingest`
- `raw_awards` table populated
- Top 20 vendors query

### Week 2: Normalization + Baseline
- Vendor deduplication (fuzzy + DUNS/UEI)
- Monthly aggregation + rolling features
- Robust MAD detector
- Baseline anomalies detected

### Week 3: ML Detection
- Feature engineering (18 features)
- Isolation Forest trainer
- Model artifacts saved
- ML anomalies detected

### Week 4: Explanation + API
- Evidence builder (top N awards)
- Feature driver calculator
- Narrative generator
- FastAPI endpoints

### Week 5: UI + Export
- Streamlit dashboard (3 pages)
- CSV/JSON export
- Full workflow demo

### Week 6: Hardening + Docs
- Error handling + logging
- Complete documentation
- Demo script rehearsed
- Release tag: v0.1.0-mvp

---

## Key Decisions

### 1. DuckDB over PostgreSQL
- Embedded (no server)
- Fast analytics (columnar)
- Easy deployment

### 2. Isolation Forest over Other ML
- Unsupervised (no labels)
- Fast training/scoring
- Explainable

### 3. Streamlit over React
- Rapid prototyping
- Python-native
- Sufficient for MVP

### 4. Dual Detection Always
- Baseline validates ML
- Demonstrates breadth
- Builds trust

### 5. Minnesota Focus
- Manageable data volume
- Clear demo narrative
- Easy to expand

See [docs/DECISION_LOG.md](docs/DECISION_LOG.md) for full rationale.

---

## Risk Mitigation

### Data Quality
- Validate row counts
- Filter null amounts
- Log missing fields

### Vendor Normalization
- Use DUNS/UEI as strong IDs
- Manual override file
- Accept ~85% accuracy

### False Positives
- Minimum volume thresholds
- Dual detection validation
- Human review sample

### Timeline
- Week-by-week milestones
- Buffer in Week 6
- Cut features if needed

See [docs/RISK_REGISTER.md](docs/RISK_REGISTER.md) for complete list.

---

## Post-MVP Roadmap

### Phase 2: Multi-Geography (Weeks 7-8)
- Expand to all 50 states
- State comparison dashboard
- Geographic heatmap

### Phase 3: Enhanced ML (Weeks 9-10)
- SHAP for precise attribution
- Ensemble methods
- Time-series forecasting

### Phase 4: Advanced Features (Weeks 11-12)
- Natural language search
- Automated reports
- Email alerts

### Phase 5: Production (Weeks 13-14)
- Docker containerization
- Cloud deployment
- PostgreSQL migration
- User authentication

---

## Portfolio Value

### Demonstrates
- **End-to-end pipeline**: Ingest → Transform → Model → Serve
- **ML + Statistics**: Dual detection approach
- **Data engineering**: Immutable runs, lineage tracking
- **API design**: RESTful endpoints, Pydantic validation
- **Testing**: Unit + integration + injected anomalies
- **Documentation**: 10+ comprehensive docs
- **Scoping**: Tight MVP, clear expansion path

### Differentiators
- **Social impact**: Public spending transparency
- **Evidence traceability**: No black boxes
- **Realistic scope**: Deliverable in 6 weeks
- **Professional quality**: CI, tests, docs, clean code

---

## Next Steps

1. **Week 1**: Implement ingestion pipeline
2. **Week 2**: Build normalization + baseline detection
3. **Week 3**: Add ML detection
4. **Week 4**: Implement explanation layer
5. **Week 5**: Build UI + export
6. **Week 6**: Harden + document + demo

**Start date**: [To be determined]  
**Target completion**: [Start + 6 weeks]

---

## Questions to Resolve

1. Exact date range for Minnesota data (confirm 24 months available)
2. USAspending API rate limits (confirm 5 req/sec acceptable)
3. Demo environment (local vs cloud for presentation)
4. GitHub username for repo URL
5. Portfolio site URL for README

---

## Contact

**Builder**: [Your Name]  
**Email**: [your.email@example.com]  
**GitHub**: [@yourusername](https://github.com/yourusername)  
**Portfolio**: [your-portfolio.com]

---

**Status**: ✅ Specification complete, ready to build

