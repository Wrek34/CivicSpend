# Build Log

Weekly progress updates for CivicSpend project.

---

## Week 1: Foundation ✅

### Goals
- ✅ DuckDB schema created
- ✅ USAspending API client
- ✅ CLI: `civicspend ingest`
- ✅ `raw_awards` table populated
- ✅ Mock data generator

### Completed
- Database schema with 5 tables
- API client with rate limiting (5 req/sec)
- Exponential backoff retry logic
- CLI framework using Click
- Mock data generator (12 vendors, 24 months)
- 7 tests passing

### Challenges
- API rate limits required careful throttling
- Mock data needed realistic patterns

### Decisions Made
- Use DuckDB for embedded analytics
- Mock data for testing (avoid API dependency)

---

## Week 2: Normalization + Baseline ✅

### Goals
- ✅ Vendor normalization
- ✅ Monthly aggregation
- ✅ Robust MAD detector
- ✅ Baseline anomalies detected

### Completed
- VendorMatcher with fuzzy matching (85% threshold)
- DUNS/UEI exact matching
- MonthlyAggregator with rolling features
- RobustMADDetector (Modified Z-score)
- 8 baseline anomalies detected

### Challenges
- Fuzzy matching performance (O(n²))
- Vendor name variations

### Decisions Made
- Use RapidFuzz for speed
- 85% threshold balances precision/recall

---

## Week 3: ML Detection ✅

### Goals
- ✅ Feature engineering (16 features)
- ✅ Isolation Forest trainer
- ✅ Model artifacts saved
- ✅ ML anomalies detected

### Completed
- FeatureEngineer with 16 features
- MLDetector using Isolation Forest
- Model save/load with joblib
- 13 ML anomalies detected
- Evidence layer with 100% traceability

### Challenges
- Feature scaling and normalization
- Contamination parameter tuning

### Decisions Made
- 200 trees, 5% contamination
- Log transforms for skewed features
- Fixed random_state=42 for reproducibility

---

## Week 4: Explanation + Export ✅

### Goals
- ✅ Evidence builder
- ✅ Feature drivers
- ✅ Narrative generator
- ✅ CSV/JSON export

### Completed
- EvidenceBuilder with award traceability
- Top 5 contributing awards
- Feature drivers (what changed)
- Factual narratives (no speculation)
- Export command with CSV/JSON formats

### Challenges
- Narrative generation without speculation
- Evidence formatting

### Decisions Made
- Template-based narratives
- Always include award IDs
- Skip FastAPI (focus on Streamlit)

---

## Week 5: UI + Demo ✅

### Goals
- ✅ Streamlit dashboard (3 tabs)
- ✅ Interactive visualizations
- ✅ Full workflow demo

### Completed
- Streamlit app with 3 tabs (Anomalies, Vendors, Evidence)
- Plotly charts (timeline, severity distribution)
- Interactive filters
- Demo script (3-5 minutes)
- Evidence drill-down

### Challenges
- Streamlit state management
- Chart performance with large datasets

### Decisions Made
- Use Plotly for interactivity
- Cache data loading
- Simple tab-based navigation

---

## Week 6: Hardening + Docs 🚧

### Goals
- ✅ Configuration management
- ✅ Logging infrastructure
- ✅ Custom exceptions
- ✅ Installation script
- ✅ Complete documentation
- [ ] Final testing
- [ ] Demo rehearsal
- [ ] Release tag: v0.1.0-mvp

### Completed
- config/default.yaml with all settings
- Config loader (singleton pattern)
- Logging setup (file + console)
- Custom exception hierarchy
- install.py script
- ARCHITECTURE.md (comprehensive)
- DATA_CONTRACTS.md (all schemas)
- METRICS.md (evaluation results)
- TESTING.md (testing guide)
- Updated CONTRIBUTING.md
- Updated all docs to CivicSpend branding

### In Progress
- Final testing pass
- Demo rehearsal
- Release preparation

### Decisions Made
- YAML for configuration (human-readable)
- Rotating file logs (10MB, 3 backups)
- Singleton config pattern
- Comprehensive documentation over code comments

---

## Metrics Snapshot (End of Week 6)

### Technical Metrics
- Injected anomaly precision: 80%
- Stability score: 100%
- Code coverage: 70%
- Test pass rate: 100% (24/24)

### Quality Metrics
- Evidence traceability: 100%
- Vendor matching accuracy: 85%
- Time savings vs manual: 5x

### Portfolio Metrics
- Documentation pages: 15+
- Commit count: 20+
- Test count: 24
- Lines of code: ~2000
- Demo duration: 3-5 minutes

---

## Lessons Learned

### What Went Well
- Mock data enabled fast iteration without API dependency
- Dual detection (baseline + ML) provided validation
- Evidence traceability built trust in results
- DuckDB was perfect for embedded analytics
- Streamlit enabled rapid UI prototyping
- Comprehensive documentation from day 1

### What Could Be Improved
- Fuzzy matching performance (O(n²) bottleneck)
- Seasonal patterns not yet modeled
- FastAPI not implemented (deprioritized)
- Test coverage could be higher (70% vs 80% target)

### What to Do Differently Next Time
- Start with configuration management earlier
- Add logging from Week 1
- Write tests alongside features (not after)
- Consider seasonal decomposition upfront
- Use pre-commit hooks for code quality

