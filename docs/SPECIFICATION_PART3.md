# Gnit Specification (Part 3)

## README Skeleton

```markdown
# Gnit: Government Insight Tracker

Detect meaningful changes in public spending using robust statistics + ML anomaly detection.

## What It Does

- Fetches federal award data from USAspending.gov
- Normalizes vendor identities
- Detects spending anomalies using:
  - Robust MAD (baseline statistical method)
  - Isolation Forest (machine learning)
- Explains every anomaly with row-level evidence
- Provides dashboard + API for exploration

**Not fraud detection.** Focuses on changes, outliers, and spikes.

## Quick Start

### Install
```bash
pip install -r requirements.txt
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
gnit export-report --run-id <run_id> --format csv --output report.csv
```

## Documentation

- [Specification](docs/SPECIFICATION.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Demo Script](docs/DEMO.md)
- [Metrics](docs/METRICS.md)

## Tech Stack

Python 3.11+ • DuckDB • scikit-learn • FastAPI • Streamlit

## License

MIT
```

---

## CLI Commands (Detailed)

### 1. gnit ingest

**Purpose**: Fetch awards from USAspending API

**Usage**:
```bash
gnit ingest --state MN --start-date 2022-01-01 --end-date 2024-01-31 [--run-id <id>]
```

**Options**:
- `--state`: Two-letter state code (place of performance)
- `--start-date`: YYYY-MM-DD
- `--end-date`: YYYY-MM-DD
- `--run-id`: Optional (auto-generated if not provided)
- `--batch-size`: Records per API request (default: 100)
- `--rate-limit`: Requests per second (default: 5)

**Output**:
- Creates `run_id` in `run_manifest`
- Populates `raw_awards` table
- Prints: "Fetched {count} awards for run {run_id}"

**Implementation**: `gnit/cli/ingest.py`

---

### 2. gnit normalize

**Purpose**: Deduplicate and normalize vendor identities

**Usage**:
```bash
gnit normalize --run-id <run_id>
```

**Options**:
- `--run-id`: Required
- `--similarity-threshold`: Fuzzy match threshold (default: 0.85)
- `--overrides-file`: Path to manual mappings CSV (default: config/vendor_overrides.csv)

**Output**:
- Populates `vendor_entities`, `vendor_aliases`, `award_vendor_map`
- Prints: "Normalized {count} vendors from {raw_count} raw names"

**Implementation**: `gnit/cli/normalize.py`

---

### 3. gnit build-features

**Purpose**: Aggregate monthly spend and compute rolling features

**Usage**:
```bash
gnit build-features --run-id <run_id>
```

**Options**:
- `--run-id`: Required
- `--min-months`: Minimum vendor history (default: 6)

**Output**:
- Populates `monthly_vendor_spend` table
- Prints: "Built features for {vendor_count} vendors, {month_count} vendor-months"

**Implementation**: `gnit/cli/features.py`

---

### 4. gnit train-model

**Purpose**: Train Isolation Forest on historical data

**Usage**:
```bash
gnit train-model --run-id <run_id>
```

**Options**:
- `--run-id`: Required
- `--n-estimators`: Trees in forest (default: 200)
- `--contamination`: Expected anomaly rate (default: 0.05)
- `--random-state`: Seed (default: 42)

**Output**:
- Saves model to `models/<run_id>/isolation_forest.joblib`
- Saves scaler to `models/<run_id>/scaler.joblib`
- Saves feature list to `models/<run_id>/features.json`
- Updates `run_manifest` with model path
- Prints: "Trained model on {sample_count} vendor-months"

**Implementation**: `gnit/cli/train.py`

---

### 5. gnit score-anomalies

**Purpose**: Detect anomalies using baseline + ML methods

**Usage**:
```bash
gnit score-anomalies --run-id <run_id> --model-run-id <model_run_id>
```

**Options**:
- `--run-id`: Data to score
- `--model-run-id`: Model to use
- `--methods`: Comma-separated (default: "robust_mad,isolation_forest")
- `--min-severity`: Filter (default: "low")

**Output**:
- Populates `anomalies` table
- Prints: "Detected {count} anomalies ({baseline_count} baseline, {ml_count} ML)"

**Implementation**: `gnit/cli/score.py`

---

### 6. gnit explain

**Purpose**: Generate evidence and narratives for anomalies

**Usage**:
```bash
gnit explain --run-id <run_id>
```

**Options**:
- `--run-id`: Required
- `--top-n-awards`: Evidence rows per anomaly (default: 5)
- `--top-n-drivers`: Feature drivers (default: 3)

**Output**:
- Updates `anomalies.explanation_json`
- Prints: "Generated explanations for {count} anomalies"

**Implementation**: `gnit/cli/explain.py`

---

### 7. gnit export-report

**Purpose**: Export anomalies to CSV/JSON

**Usage**:
```bash
gnit export-report --run-id <run_id> --format csv --output report.csv
```

**Options**:
- `--run-id`: Required
- `--format`: csv or json (default: csv)
- `--output`: File path (default: stdout)
- `--severity`: Filter (default: all)

**Output**:
- CSV columns: vendor_name, year_month, severity, method, anomaly_score, obligation_sum, explanation_summary
- JSON: full anomaly records with evidence

**Implementation**: `gnit/cli/export.py`

---

## Model Artifact Storage

### Directory Structure

```
models/
├── <run_id_1>/
│   ├── isolation_forest.joblib    # Trained model
│   ├── scaler.joblib              # StandardScaler
│   ├── features.json              # Feature names + order
│   ├── config.json                # Hyperparameters
│   └── metadata.json              # Training stats
└── <run_id_2>/
    └── ...
```

### Loading Model

```python
import joblib
import json

def load_model(run_id: str):
    base_path = f"models/{run_id}"
    model = joblib.load(f"{base_path}/isolation_forest.joblib")
    scaler = joblib.load(f"{base_path}/scaler.joblib")
    with open(f"{base_path}/features.json") as f:
        features = json.load(f)
    return model, scaler, features
```

### Saving Model

```python
import joblib
import json
import hashlib

def save_model(run_id: str, model, scaler, features, config):
    base_path = f"models/{run_id}"
    os.makedirs(base_path, exist_ok=True)
    
    joblib.dump(model, f"{base_path}/isolation_forest.joblib")
    joblib.dump(scaler, f"{base_path}/scaler.joblib")
    
    with open(f"{base_path}/features.json", "w") as f:
        json.dump(features, f)
    
    with open(f"{base_path}/config.json", "w") as f:
        json.dump(config, f)
    
    # Config hash for reproducibility
    config_str = json.dumps(config, sort_keys=True)
    config_hash = hashlib.sha256(config_str.encode()).hexdigest()
    
    return config_hash
```

---

## Test Strategy

### Unit Tests

**File**: `tests/test_normalize.py`
```python
def test_vendor_fuzzy_match():
    # "3M Company" and "3M COMPANY" should match
    
def test_vendor_duns_match():
    # Same DUNS = same vendor
    
def test_vendor_override():
    # Manual override takes precedence
```

**File**: `tests/test_features.py`
```python
def test_monthly_aggregation():
    # Sum of monthly obligations = sum of raw awards
    
def test_rolling_features():
    # Rolling mean calculated correctly
    
def test_feature_engineering():
    # Log transform, cyclical encoding
```

### Injected Anomaly Tests

**File**: `tests/test_detection.py`

```python
def test_baseline_spike_detection():
    # Create vendor with stable $100K/month for 12 months
    # Inject $500K spike in month 13
    # Assert: robust_z > 3.5, severity = 'critical'
    
def test_ml_spike_detection():
    # Same setup as above
    # Assert: anomaly_score < -0.5, severity = 'critical'
    
def test_baseline_drop_detection():
    # Create vendor with stable $200K/month
    # Inject $20K drop in month 13
    # Assert: flagged as anomaly
    
def test_stable_vendor_no_anomaly():
    # Create vendor with consistent spend
    # Assert: no anomalies flagged
    
def test_minimum_volume_filter():
    # Create vendor with <$50K total spend
    # Assert: not scored (filtered out)
```

### End-to-End Smoke Test

**File**: `tests/test_e2e.py`

```python
def test_full_pipeline():
    # 1. Mock API response with 100 awards
    # 2. Run ingest
    # 3. Run normalize
    # 4. Run build-features
    # 5. Run train-model
    # 6. Run score-anomalies
    # 7. Run explain
    # 8. Assert: anomalies table populated
    # 9. Assert: all anomalies have explanation_json
    # 10. Assert: all anomalies have award_ids
```

### Test Execution

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=gnit --cov-report=html

# Run specific test
pytest tests/test_detection.py::test_baseline_spike_detection -v
```

---

## Definition of Done Checklist

### Feature Complete
- [ ] All CLI commands implemented
- [ ] Baseline detection working
- [ ] ML detection working
- [ ] Explanation layer complete
- [ ] API endpoints functional
- [ ] UI dashboard functional
- [ ] Export working (CSV + JSON)

### Quality Bar
- [ ] All unit tests passing
- [ ] Injected anomaly tests passing (precision >= 80%)
- [ ] End-to-end smoke test passing
- [ ] Code coverage >= 70%
- [ ] No linting errors (black, isort, flake8)
- [ ] Type hints on public functions

### Evidence Traceability
- [ ] 100% of anomalies have award_ids
- [ ] 100% of anomalies have explanation_json
- [ ] Evidence rows sum to monthly totals
- [ ] All award_ids exist in raw_awards

### Documentation
- [ ] README with quickstart
- [ ] SPECIFICATION.md complete
- [ ] ARCHITECTURE.md with diagrams
- [ ] DATA_CONTRACTS.md with schemas
- [ ] METRICS.md with evaluation results
- [ ] DEMO.md with script
- [ ] RISK_REGISTER.md with limitations
- [ ] DECISION_LOG.md with rationale
- [ ] BUILD_LOG.md with weekly updates

### Demo Ready
- [ ] Demo script rehearsed (3-5 min)
- [ ] Demo dataset prepared
- [ ] UI loads without errors
- [ ] No crashes during demo
- [ ] Explanations are clear and factual

### Portfolio Quality
- [ ] Clean commit history
- [ ] GitHub repo public
- [ ] CI badge (tests passing)
- [ ] Release tag: v0.1.0-mvp
- [ ] License file (MIT)
- [ ] No credentials in repo

---

## 3-5 Minute Demo Script

**File**: `docs/DEMO.md`

### Setup (Pre-Demo)

```bash
# Run pipeline on demo dataset (Minnesota, 2022-2024)
gnit ingest --state MN --start-date 2022-01-01 --end-date 2024-01-31
gnit normalize --run-id <run_id>
gnit build-features --run-id <run_id>
gnit train-model --run-id <run_id>
gnit score-anomalies --run-id <run_id> --model-run-id <run_id>
gnit explain --run-id <run_id>

# Launch UI
streamlit run gnit/ui/app.py
```

### Demo Script (5 minutes)

**[0:00-0:30] Introduction**

"Gnit detects meaningful changes in public spending. It's not fraud detection—it surfaces outliers and spikes using both robust statistics and machine learning, with full evidence traceability."

**[0:30-1:30] Show the Problem**

"Traditional approach: Download CSVs, pivot in Excel, manually spot outliers. Takes 40+ minutes per vendor."

"Gnit automates this: Fetch data, normalize vendors, detect anomalies, explain with evidence. Takes 5 minutes for all vendors."

**[1:30-2:30] Dashboard Walkthrough**

*Navigate to Anomaly List page*

"Here are detected anomalies for Minnesota vendors over 24 months. We can filter by severity, detection method, or vendor."

*Filter to 'high' severity*

"Let's look at high-severity anomalies. Notice we have two detection methods: robust MAD (baseline statistics) and Isolation Forest (machine learning)."

*Click on an anomaly*

**[2:30-4:00] Anomaly Detail**

"This vendor showed a spike in January 2024. Monthly spending jumped to $2.7M from a typical $450K."

*Scroll to Evidence section*

"Here's the evidence: the top 5 awards that contributed to this month. The largest was a $1.25M highway construction contract."

*Scroll to Drivers section*

"The ML model identified key drivers: obligation_sum increased 511%, while award_count dropped 75%. Fewer, larger contracts."

*Show narrative*

"The system generates a factual narrative: 'Vendor X showed a high anomaly in 2024-01. Monthly spending increased to $2.7M from a typical $450K. Key changes: obligation sum increased significantly, award count decreased.'"

**[4:00-4:30] Comparison: Baseline vs ML**

*Navigate to Vendor Timeline page*

"Here's the vendor's spending timeline. Red dots are anomalies. Notice both methods flagged January 2024, but ML also flagged March 2023—a subtler pattern the baseline method missed."

**[4:30-5:00] Export + Wrap-Up**

*Show export command*

```bash
gnit export-report --run-id <run_id> --format csv --output report.csv
```

"You can export results to CSV or JSON for further analysis. Every anomaly is traceable to specific award IDs."

"Gnit makes public spending legible: detect changes, explain with evidence, save time."

---

## Implementation Notes (Practical)

### API Rate Limiting

USAspending API has rate limits. Implement exponential backoff:

```python
import time
import requests

def fetch_with_backoff(url, params, max_retries=5):
    for attempt in range(max_retries):
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:  # Rate limit
            wait = 2 ** attempt
            time.sleep(wait)
        else:
            response.raise_for_status()
    raise Exception("Max retries exceeded")
```

### Vendor Normalization Approach

Use fuzzy matching with thresholds:

```python
from rapidfuzz import fuzz

def normalize_vendor_name(name: str) -> str:
    # Uppercase, remove punctuation, strip whitespace
    return re.sub(r'[^\w\s]', '', name.upper()).strip()

def find_match(name: str, existing_vendors: list, threshold=85):
    normalized = normalize_vendor_name(name)
    for vendor in existing_vendors:
        score = fuzz.ratio(normalized, vendor['normalized_name'])
        if score >= threshold:
            return vendor['vendor_id']
    return None  # No match, create new entity
```

### Feature Engineering Pipeline

```python
import pandas as pd
import numpy as np

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    # df has columns: vendor_id, year_month, obligation_sum, ...
    
    # Log transform monetary amounts
    df['log_obligation'] = np.log1p(df['obligation_sum'])
    
    # Rolling features (3, 6, 12 months)
    for window in [3, 6, 12]:
        df[f'rolling_{window}m_mean'] = df.groupby('vendor_id')['obligation_sum'].transform(
            lambda x: x.rolling(window, min_periods=1).mean()
        )
        df[f'rolling_{window}m_mad'] = df.groupby('vendor_id')['obligation_sum'].transform(
            lambda x: (x - x.rolling(window, min_periods=1).median()).abs().rolling(window, min_periods=1).median()
        )
    
    # Month-over-month change
    df['mom_pct_change'] = df.groupby('vendor_id')['obligation_sum'].pct_change()
    
    # Cyclical encoding for month
    df['month'] = pd.to_datetime(df['year_month']).dt.month
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
    
    return df
```

### Robust MAD Implementation

```python
import numpy as np

def compute_robust_z(series: np.ndarray) -> np.ndarray:
    median = np.median(series)
    mad = np.median(np.abs(series - median))
    if mad == 0:
        return np.zeros_like(series)
    robust_z = 0.6745 * (series - median) / mad
    return robust_z

def detect_baseline_anomalies(df: pd.DataFrame, threshold=3.5):
    anomalies = []
    for vendor_id, group in df.groupby('vendor_id'):
        if len(group) < 6:  # Minimum history
            continue
        if group['obligation_sum'].sum() < 50000:  # Minimum volume
            continue
        
        robust_z = compute_robust_z(group['obligation_sum'].values)
        group['robust_z'] = robust_z
        
        # Flag anomalies
        mask = np.abs(robust_z) > threshold
        anomalies.append(group[mask])
    
    return pd.concat(anomalies) if anomalies else pd.DataFrame()
```

---

## Assumptions (Explicit)

1. **Data availability**: USAspending API is accessible and stable
2. **Data quality**: Award IDs are unique, amounts are accurate
3. **Vendor names**: Fuzzy matching achieves ~85% accuracy (manual overrides for edge cases)
4. **Compute resources**: Solo builder has laptop with 16GB RAM, can process ~100K awards
5. **Time range**: 24 months is sufficient for meaningful anomaly detection
6. **Geography**: Minnesota has enough award volume (~50K-100K awards)
7. **Anomaly rate**: ~5% of vendor-months are anomalous (contamination parameter)
8. **No labels**: Unsupervised learning is acceptable (no ground-truth anomalies)
9. **Explainability**: Feature contribution approximation is sufficient (no SHAP required)
10. **Deployment**: Local execution is acceptable for MVP (no cloud hosting)

