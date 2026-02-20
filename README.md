# CivicSpend: Public Spending Transparency Platform

> Detect meaningful changes in public spending using robust statistics + machine learning

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)]() 
[![Python](https://img.shields.io/badge/python-3.11+-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

---

## What It Does

Gnit automates the detection of spending anomalies in federal award data:

- **Fetches** award data from USAspending.gov API
- **Normalizes** vendor identities (fuzzy matching + DUNS/UEI)
- **Detects** anomalies using:
  - **Robust MAD** (baseline statistical method)
  - **Isolation Forest** (machine learning)
- **Explains** every anomaly with row-level evidence
- **Provides** dashboard + API for exploration

**Important**: This is NOT fraud detection. Gnit identifies changes, outliers, and spikes—not intent or wrongdoing.

---

## Quick Start

### Prerequisites

- Python 3.11+
- pip or Poetry

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/gnit.git
cd gnit

# Install dependencies
pip install -r requirements.txt

# Or with Poetry
poetry install
```

### Run Pipeline

```bash
# 1. Fetch awards (Minnesota, last 24 months)
gnit ingest --state MN --start-date 2022-01-01 --end-date 2024-01-31

# 2. Normalize vendors
gnit normalize --run-id <run_id>

# 3. Build features
gnit build-features --run-id <run_id>

# 4. Train model
gnit train-model --run-id <run_id>

# 5. Score anomalies
gnit score-anomalies --run-id <run_id> --model-run-id <run_id>

# 6. Generate explanations
gnit explain --run-id <run_id>

# 7. Launch dashboard
streamlit run gnit/ui/app.py
```

### Export Report

```bash
# CSV export
gnit export-report --run-id <run_id> --format csv --output report.csv

# JSON export
gnit export-report --run-id <run_id> --format json --output report.json
```

---

## Demo (3-5 Minutes)

See [docs/DEMO.md](docs/DEMO.md) for full demo script.

**Quick demo**:
1. Run pipeline on Minnesota data (2022-2024)
2. Open Streamlit dashboard
3. Filter to high-severity anomalies
4. Click anomaly → view evidence (top awards) + drivers (feature changes)
5. Compare baseline vs ML detection side-by-side

---

## Architecture

```
USAspending API → Ingest → DuckDB (raw_awards)
                     ↓
                 Normalize → vendor_entities
                     ↓
              Build Features → monthly_vendor_spend
                     ↓
              Train Model → Isolation Forest
                     ↓
            Score Anomalies → anomalies table
                     ↓
                 Explain → evidence + drivers
                     ↓
            API / Dashboard → Streamlit UI
```

**Tech Stack**:
- **Database**: DuckDB (embedded, fast analytics)
- **ML**: scikit-learn (Isolation Forest)
- **API**: FastAPI (REST endpoints)
- **UI**: Streamlit (dashboard)
- **CLI**: Click (pipeline commands)

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for details.

---

## Documentation

### Core Docs
- [**THESIS.md**](docs/THESIS.md) - Problem statement and approach
- [**SPECIFICATION.md**](docs/SPECIFICATION.md) - Complete technical spec
- [**ARCHITECTURE.md**](docs/ARCHITECTURE.md) - System design
- [**DATA_CONTRACTS.md**](docs/DATA_CONTRACTS.md) - Table schemas

### Process Docs
- [**DEMO.md**](docs/DEMO.md) - 3-5 minute demo script
- [**METRICS.md**](docs/METRICS.md) - Evaluation results
- [**RISK_REGISTER.md**](docs/RISK_REGISTER.md) - Known limitations
- [**DECISION_LOG.md**](docs/DECISION_LOG.md) - Technical choices
- [**ROADMAP.md**](docs/ROADMAP.md) - Week-by-week plan
- [**BUILD_LOG.md**](docs/BUILD_LOG.md) - Weekly progress

---

## Key Features

### Dual Detection
- **Baseline (Robust MAD)**: Statistical outlier detection using Median Absolute Deviation
- **ML (Isolation Forest)**: Unsupervised learning on 18 engineered features
- **Side-by-side comparison**: Validate ML results against statistical baseline

### Evidence Traceability
Every anomaly includes:
- **Award IDs**: Specific source records
- **Top contributing awards**: Amounts, agencies, descriptions
- **Feature drivers**: What changed (obligation sum, award count, etc.)
- **Factual narrative**: Templated explanation (no speculation)

### Reproducibility
- **Immutable runs**: Every execution gets unique `run_id`
- **Model versioning**: Artifacts saved per run
- **Config hashing**: Ensures deterministic results
- **Audit trail**: Full lineage from raw data to anomaly

---

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=gnit --cov-report=html

# Run specific test
pytest tests/test_detection.py::test_baseline_spike_detection -v
```

**Test coverage**:
- Unit tests: Normalization, feature engineering, detection
- Injected anomaly tests: Validate detection on synthetic spikes/drops
- End-to-end smoke test: Full pipeline on mock data

**Target metrics**:
- Injected anomaly precision: >= 80%
- Stability score: >= 95%
- Code coverage: >= 70%

---

## CLI Reference

### gnit ingest
Fetch awards from USAspending API
```bash
gnit ingest --state MN --start-date 2022-01-01 --end-date 2024-01-31
```

### gnit normalize
Deduplicate vendor identities
```bash
gnit normalize --run-id <run_id>
```

### gnit build-features
Aggregate monthly spend + compute rolling features
```bash
gnit build-features --run-id <run_id>
```

### gnit train-model
Train Isolation Forest
```bash
gnit train-model --run-id <run_id>
```

### gnit score-anomalies
Detect anomalies (baseline + ML)
```bash
gnit score-anomalies --run-id <run_id> --model-run-id <run_id>
```

### gnit explain
Generate evidence and narratives
```bash
gnit explain --run-id <run_id>
```

### gnit export-report
Export anomalies to CSV/JSON
```bash
gnit export-report --run-id <run_id> --format csv --output report.csv
```

---

## API Endpoints

### GET /anomalies
List anomalies with filters
```bash
curl "http://localhost:8000/anomalies?run_id=<run_id>&severity=high"
```

### GET /anomalies/{anomaly_id}
Get anomaly detail with evidence
```bash
curl "http://localhost:8000/anomalies/<anomaly_id>"
```

### GET /vendors/{vendor_id}/timeline
Get vendor spending timeline
```bash
curl "http://localhost:8000/vendors/<vendor_id>/timeline?run_id=<run_id>"
```

---

## Project Structure

```
gnit/
├── gnit/                   # Main package
│   ├── cli/                # Click commands
│   ├── ingest/             # USAspending API client
│   ├── normalize/          # Vendor deduplication
│   ├── features/           # Feature engineering
│   ├── detect/             # Anomaly detection (baseline + ML)
│   ├── explain/            # Evidence + narratives
│   ├── db/                 # DuckDB schema + queries
│   ├── api/                # FastAPI endpoints
│   └── ui/                 # Streamlit dashboard
├── tests/                  # Test suite
├── docs/                   # Documentation
├── config/                 # Configuration files
├── data/                   # DuckDB database (gitignored)
├── models/                 # Saved model artifacts
└── README.md               # This file
```

---

## Known Limitations

1. **Not fraud detection**: Identifies changes, not intent
2. **Imperfect entity resolution**: ~85% vendor matching accuracy
3. **No ground-truth validation**: Unsupervised learning
4. **Single geography (MVP)**: Minnesota only
5. **Batch processing**: Not real-time
6. **No predictive capability**: Detects past changes only

See [docs/RISK_REGISTER.md](docs/RISK_REGISTER.md) for full list.

---

## Roadmap

### MVP (Weeks 1-6) - Current
- ✅ Ingestion + schema
- ✅ Vendor normalization
- ✅ Baseline detection (Robust MAD)
- ✅ ML detection (Isolation Forest)
- ✅ Explanation layer
- ✅ Dashboard + API
- ✅ Documentation

### Post-MVP
- Multi-geography support (all 50 states)
- Enhanced ML (SHAP, ensemble methods)
- Advanced features (NL search, alerts)
- Production deployment (Docker, cloud)

See [docs/ROADMAP.md](docs/ROADMAP.md) for details.

---

## Contributing

This is a portfolio project, but feedback is welcome!

1. Open an issue for bugs or suggestions
2. Fork the repo for experiments
3. Submit PRs for documentation improvements

---

## License

MIT License - see [LICENSE](LICENSE) file

---

## Acknowledgments

- **Data source**: USAspending.gov (U.S. Department of Treasury)
- **Inspiration**: CivicSpend Lens (public spending transparency)
- **ML method**: Isolation Forest (Liu et al., 2008)

---

## Contact

Built by [Your Name]  
Portfolio: [your-portfolio.com]  
GitHub: [@yourusername](https://github.com/yourusername)

---

**Disclaimer**: This tool identifies spending changes and anomalies. It does not detect fraud, assess legality, or make claims about intent. All findings require human review and domain context.

