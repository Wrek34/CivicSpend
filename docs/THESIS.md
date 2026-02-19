# Thesis: Making Public Spending Legible

## The Problem

Public spending data is abundant but opaque. The federal government publishes millions of award records through USAspending.gov, yet meaningful patterns—especially changes and anomalies—remain hidden in spreadsheets.

**Current state**: Analysts manually download CSVs, pivot in Excel, visually scan for outliers, then trace back to source records. This takes 40+ minutes per vendor and is error-prone.

**What's missing**: Automated detection of meaningful changes with full evidence traceability.

---

## Why This Matters

### Transparency
Citizens, journalists, and researchers need tools to understand how public money flows and changes over time.

### Accountability
Detecting spending anomalies (spikes, drops, pattern changes) enables oversight without requiring domain expertise.

### Efficiency
Automating anomaly detection saves time and scales to thousands of vendors.

---

## What This Is NOT

- ❌ **Not fraud detection**: We detect changes, not intent. No claims of wrongdoing.
- ❌ **Not political analysis**: Neutral tool, no commentary on policy or parties.
- ❌ **Not perfect**: Entity resolution is fuzzy (~85% accuracy), anomalies require human review.

---

## The Approach

### 1. Dual Detection Strategy

**Baseline (Robust MAD)**:
- Statistical method using Median Absolute Deviation
- Interpretable, explainable, no training required
- Catches obvious spikes and drops
- Provides benchmark for ML validation

**Machine Learning (Isolation Forest)**:
- Captures complex, multi-dimensional patterns
- Learns from historical vendor behavior
- Detects subtle anomalies baseline methods miss
- Provides anomaly scores for ranking

**Why both?**
- Baseline builds trust (transparent statistics)
- ML adds depth (complex pattern detection)
- Side-by-side comparison validates results
- Demonstrates technical breadth for portfolio

### 2. Evidence-First Design

Every anomaly must answer:
- **What changed?** (obligation amount, award count, etc.)
- **By how much?** (absolute and percentage change)
- **Which awards?** (specific award IDs, amounts, agencies)
- **Why should I care?** (factual narrative, no speculation)

**Traceability guarantee**: Every anomaly links to specific source records. No black boxes.

### 3. Unsupervised Learning

**Challenge**: No labeled anomalies exist.

**Solution**: Unsupervised methods (Isolation Forest) that learn normal patterns and flag deviations.

**Validation**: Injected anomalies (synthetic spikes/drops) + human review of sample results.

### 4. Tight MVP Scope

**One question**: "What changed?" (monthly vendor anomalies)  
**One geography**: Minnesota  
**One workflow**: Ingest → Normalize → Detect → Explain → Export

**Why tight scope?**
- Feasible for solo builder in 6 weeks
- Demos reliably in 3-5 minutes
- Produces portfolio-quality artifacts
- Easy to expand post-MVP

---

## Technical Choices

### DuckDB (Embedded Analytics Database)
- Fast columnar queries for aggregations
- No server setup (embedded)
- SQL interface (analyst-friendly)
- Single-file deployment

### Isolation Forest (ML Method)
- Unsupervised (no labels needed)
- Fast training and scoring
- Handles mixed features well
- Explainable via feature contribution

### Streamlit (UI)
- Rapid prototyping (Python-native)
- Built-in data components
- Sufficient for demo and portfolio
- Can migrate to React later

### CLI-First Architecture
- Composable pipeline steps
- Testable and debuggable
- Scriptable for automation
- Professional data engineering practice

---

## Success Criteria

### Technical
- Detect 80%+ of injected anomalies (precision)
- 95%+ stability (reproducible results)
- 100% evidence traceability

### Quality
- 70%+ human plausibility rate
- 5x+ time savings vs manual analysis
- Zero crashes on demo dataset

### Portfolio
- Complete documentation (8+ docs)
- Clean commit history
- Public GitHub repo with CI
- 3-5 minute demo script

---

## Impact

### For Users
- **Journalists**: Find stories in spending data
- **Researchers**: Analyze spending patterns at scale
- **Citizens**: Understand how public money is spent
- **Analysts**: Save time on manual outlier detection

### For Builder (Portfolio)
- Demonstrates end-to-end data pipeline
- Shows ML + statistics integration
- Proves ability to scope and deliver MVP
- Highlights documentation and testing practices

---

## Limitations (Acknowledged)

1. **Not fraud detection**: Identifies changes, not intent
2. **Imperfect entity resolution**: ~85% vendor matching accuracy
3. **No ground-truth validation**: Unsupervised learning, no labeled data
4. **Single geography**: MVP limited to Minnesota
5. **Batch processing**: Not real-time
6. **No predictive capability**: Detects past changes, doesn't forecast

---

## Future Directions

### Phase 2: Multi-Geography
Expand to all 50 states, add geographic comparisons

### Phase 3: Enhanced ML
Add SHAP for precise attribution, ensemble methods, time-series forecasting

### Phase 4: Advanced Features
Natural language search, automated reports, email alerts

### Phase 5: Production Deployment
Docker, cloud hosting, PostgreSQL, user authentication

---

## Conclusion

Gnit makes public spending legible by automating anomaly detection with full evidence traceability. It's not fraud detection—it's a transparency tool that saves time and scales oversight.

**Core principle**: Every anomaly must be explainable and traceable to source records. No black boxes, no speculation, just facts.

