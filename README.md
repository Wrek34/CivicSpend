# CivicSpend: Public Spending Transparency Platform

> Detect meaningful changes in public spending using robust statistics + machine learning

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)]() 
[![Python](https://img.shields.io/badge/python-3.11+-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

## 🎯 Live Demo

**Dashboard**: [civicspend.streamlit.app](https://civicspend.streamlit.app)  
**API Docs**: Coming soon

---

## What It Does

CivicSpend automates detection of spending anomalies in federal award data:

- **Fetches** award data from USAspending.gov API
- **Normalizes** vendor identities (fuzzy matching + DUNS/UEI)
- **Detects** anomalies using dual methods (Robust MAD + Isolation Forest)
- **Explains** every anomaly with row-level evidence
- **Provides** REST API + interactive dashboard

**Important**: This is NOT fraud detection. CivicSpend identifies changes, outliers, and spikes—not intent or wrongdoing.

---

## Quick Start

### Installation

```bash
git clone https://github.com/Wrek34/CivicSpend.git
cd CivicSpend
pip install -r requirements.txt
pip install -e .
```

### Run Dashboard

```bash
streamlit run civicspend/ui/app.py
```

Opens at http://localhost:8501

### Run API

```bash
uvicorn civicspend.api.main:app --reload
```

API at http://localhost:8000  
Docs at http://localhost:8000/docs

---

## Features

### 🔍 Anomaly Detection
- Dual detection (statistical + ML)
- Severity classification (critical/high/medium/low)
- Real-time filtering

### 📈 Vendor Analysis
- Spending timelines
- Rolling averages
- Month-over-month changes

### 📜 Award History
- Complete award records
- Search and filter
- Agency breakdown

### 📊 Spending Analysis
- Monthly trends
- Top vendors
- Agency distribution
- In-depth statistics

### 🔌 REST API
- 9 endpoints
- Full CRUD operations
- Interactive docs (Swagger/ReDoc)

---

## API Endpoints

```
GET  /                              # API info
GET  /runs                          # List runs
GET  /vendors                       # List vendors
GET  /vendors/{id}/timeline         # Vendor timeline
GET  /vendors/{id}/history          # Vendor awards
GET  /anomalies                     # List anomalies
GET  /spending/summary              # Spending stats
GET  /spending/trends               # Spending trends
GET  /health                        # Health check
```

See [docs/API.md](docs/API.md) for full documentation.

---

## Dashboard Tabs

1. **🔍 Anomaly Detection** - Detected spending changes
2. **📈 Vendor Analysis** - Individual vendor deep-dive
3. **📋 Evidence Explorer** - Award-level traceability
4. **📜 Award History** - Complete award records
5. **📊 Spending Analysis** - Trends and statistics

---

## Architecture

```
USAspending API → Ingest → DuckDB
                     ↓
                 Normalize → Vendors
                     ↓
              Build Features → Time Series
                     ↓
              Train Model → Isolation Forest
                     ↓
            Detect Anomalies → Baseline + ML
                     ↓
                 Explain → Evidence
                     ↓
            ┌────────┴────────┐
            ↓                 ↓
        REST API          Dashboard
```

**Tech Stack**: Python, DuckDB, FastAPI, Streamlit, scikit-learn

---

## Documentation

- [API.md](docs/API.md) - REST API documentation
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System design
- [DATA_CONTRACTS.md](docs/DATA_CONTRACTS.md) - Database schemas
- [METRICS.md](docs/METRICS.md) - Performance metrics
- [TESTING.md](docs/TESTING.md) - Testing guide

---

## CLI Commands

```bash
# Initialize
civicspend init

# Ingest data
civicspend ingest --state MN --start-date 2022-01-01 --end-date 2024-01-31

# Process pipeline
civicspend normalize --run-id <run_id>
civicspend build-features --run-id <run_id>
civicspend train-model --run-id <run_id>
civicspend detect --run-id <run_id>

# Export
civicspend export --run-id <run_id> --format csv --output report.csv
```

---

## Testing

```bash
pytest -v
```

7 tests, 100% passing

---

## Deployment

### Streamlit Cloud
1. Fork repo
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Deploy: `civicspend/ui/app.py`

### API (Docker)
```bash
docker build -t civicspend-api .
docker run -p 8000:8000 civicspend-api
```

---

## License

MIT License

---

## Contact

**GitHub**: [@Wrek34](https://github.com/Wrek34)  
**Repository**: [CivicSpend](https://github.com/Wrek34/CivicSpend)

---

**Disclaimer**: This tool identifies spending changes and anomalies. It does not detect fraud, assess legality, or make claims about intent. All findings require human review and domain context.
