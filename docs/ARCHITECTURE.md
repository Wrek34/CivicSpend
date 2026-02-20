# Architecture

## Overview

CivicSpend uses a pipeline architecture with embedded analytics database (DuckDB) for fast local processing.

## System Design

```
┌─────────────────┐
│ USAspending API │
└────────┬────────┘
         │ fetch
         ▼
┌─────────────────┐
│   raw_awards    │ ← Immutable source data
└────────┬────────┘
         │ normalize
         ▼
┌─────────────────┐
│ vendor_entities │ ← Deduplicated vendors
└────────┬────────┘
         │ aggregate
         ▼
┌──────────────────────┐
│ monthly_vendor_spend │ ← Time series + features
└──────────┬───────────┘
           │ train/score
           ▼
┌─────────────────┐
│   anomalies     │ ← Detected outliers
└────────┬────────┘
         │ explain
         ▼
┌─────────────────┐
│    evidence     │ ← Award-level traceability
└────────┬────────┘
         │
         ▼
┌──────────────────────┐
│  API / Dashboard     │ ← User interface
└──────────────────────┘
```

## Components

### 1. Ingestion Layer
- **Module**: `civicspend/ingest/`
- **Purpose**: Fetch awards from USAspending API
- **Key Classes**: `USAspendingClient`
- **Features**:
  - Rate limiting (5 req/sec)
  - Exponential backoff retry
  - Pagination handling
  - Mock data generator for testing

### 2. Normalization Layer
- **Module**: `civicspend/normalize/`
- **Purpose**: Deduplicate vendor identities
- **Key Classes**: `VendorMatcher`
- **Features**:
  - Fuzzy name matching (RapidFuzz)
  - DUNS/UEI-based exact matching
  - Alias tracking
  - ~85% accuracy

### 3. Feature Engineering
- **Module**: `civicspend/features/`
- **Purpose**: Aggregate and engineer features
- **Key Classes**: `MonthlyAggregator`, `FeatureEngineer`
- **Features**:
  - Monthly vendor-level aggregation
  - Rolling 3-month statistics
  - 16 ML features (log transforms, trends, volatility)
  - Cyclical time encoding

### 4. Detection Layer
- **Module**: `civicspend/detect/`
- **Purpose**: Identify anomalies
- **Key Classes**: `RobustMADDetector`, `MLDetector`
- **Methods**:
  - **Baseline**: Robust MAD (Modified Z-score with MAD)
  - **ML**: Isolation Forest (200 trees, 5% contamination)
- **Output**: Anomaly scores + severity levels

### 5. Explanation Layer
- **Module**: `civicspend/explain/`
- **Purpose**: Provide evidence for anomalies
- **Key Classes**: `EvidenceBuilder`
- **Features**:
  - Top 5 contributing awards
  - Feature drivers (what changed)
  - Vendor context (history, trends)
  - Factual narratives (no speculation)

### 6. Storage Layer
- **Module**: `civicspend/db/`
- **Technology**: DuckDB (embedded)
- **Tables**: 5 core tables (see DATA_CONTRACTS.md)
- **Features**:
  - ACID transactions
  - Fast analytics (columnar storage)
  - No server required
  - SQL interface

### 7. API Layer
- **Module**: `civicspend/api/`
- **Technology**: FastAPI
- **Endpoints**:
  - `GET /anomalies` - List with filters
  - `GET /anomalies/{id}` - Detail with evidence
  - `GET /vendors/{id}/timeline` - Spending history
- **Status**: Planned (not yet implemented)

### 8. UI Layer
- **Module**: `civicspend/ui/`
- **Technology**: Streamlit
- **Features**:
  - 3 tabs: Anomalies, Vendors, Evidence
  - Interactive filters
  - Plotly charts
  - Evidence drill-down

### 9. CLI Layer
- **Module**: `civicspend/cli/`
- **Technology**: Click
- **Commands**:
  - `init` - Initialize database
  - `ingest` - Fetch awards
  - `normalize` - Deduplicate vendors
  - `build-features` - Aggregate data
  - `train-model` - Train ML model
  - `detect` - Run anomaly detection
  - `export` - Export results

## Data Flow

### Full Pipeline
```
1. civicspend init
   → Create database schema

2. civicspend ingest --state MN --start-date 2022-01-01 --end-date 2024-01-31
   → Fetch awards → raw_awards table
   → Generate run_id

3. civicspend normalize --run-id <run_id>
   → Fuzzy match vendors → vendor_entities table
   → Create award_vendor_map

4. civicspend build-features --run-id <run_id>
   → Aggregate monthly → monthly_vendor_spend table
   → Compute rolling features

5. civicspend train-model --run-id <run_id>
   → Train Isolation Forest
   → Save model artifact → models/<run_id>/

6. civicspend detect --run-id <run_id>
   → Run baseline detection
   → Run ML detection
   → Store results → anomalies table

7. civicspend export --run-id <run_id> --format csv
   → Generate evidence
   → Export to CSV/JSON

8. streamlit run civicspend/ui/app.py
   → Launch dashboard
   → Explore anomalies
```

## Design Patterns

### Immutable Runs
- Every execution gets unique `run_id` (UUID)
- Stored in `run_manifest` table
- Enables reproducibility and comparison

### Lineage Tracking
- Every anomaly links to specific `award_id`s
- Full traceability from anomaly → awards → raw data
- Audit trail for transparency

### Dual Detection
- Always run baseline + ML in parallel
- Baseline validates ML results
- ML catches complex patterns baseline misses

### Explainability-First
- No anomaly without evidence
- Top contributing awards always included
- Feature drivers computed
- Factual narratives (no speculation)

### Configuration-Driven
- Centralized config (config/default.yaml)
- All thresholds configurable
- Environment-specific overrides

## Technology Choices

### Why DuckDB?
- **Fast**: Columnar storage, vectorized execution
- **Embedded**: No server, no setup
- **Analytics-optimized**: Built for aggregations
- **SQL interface**: Familiar query language
- **Portable**: Single file database

### Why Isolation Forest?
- **Unsupervised**: No labels required
- **Fast**: O(n log n) training
- **Effective**: Handles high-dimensional data
- **Interpretable**: Anomaly scores are intuitive
- **Proven**: Industry standard for anomaly detection

### Why Streamlit?
- **Fast prototyping**: Dashboard in <100 lines
- **Interactive**: Built-in widgets
- **Python-native**: No JS required
- **Good enough**: MVP quality UI

### Why Click?
- **Composable**: Commands as functions
- **Type-safe**: Automatic validation
- **Help generation**: Auto-generated docs
- **Testing-friendly**: Easy to test CLI

## Performance

### Expected Throughput
- **Ingestion**: ~1000 awards/minute (API limited)
- **Normalization**: ~10K vendors/second
- **Feature engineering**: ~100K rows/second
- **ML training**: ~1 second for 1K samples
- **Detection**: ~10K rows/second

### Scalability Limits
- **DuckDB**: Handles 100M+ rows on laptop
- **Memory**: ~1GB for 100K awards
- **Disk**: ~100MB for 100K awards + models

### Bottlenecks
- **API rate limit**: 5 req/sec (USAspending)
- **Fuzzy matching**: O(n²) worst case
- **ML training**: O(n log n) but memory-bound

## Security

### Data Privacy
- All data is public (USAspending.gov)
- No PII collected
- Local processing only

### API Security
- No authentication required (public API)
- Rate limiting prevents abuse
- Retry logic handles transient failures

### Code Security
- No eval() or exec()
- SQL parameterization (DuckDB)
- Input validation (Pydantic)

## Deployment

### Local Development
```bash
python install.py
civicspend init
```

### Production (Future)
- Docker container
- Cloud deployment (AWS/GCP)
- Scheduled runs (cron/Airflow)
- API authentication

## Monitoring

### Logging
- Rotating file logs (10MB, 3 backups)
- Console output
- Configurable levels (DEBUG/INFO/WARNING/ERROR)

### Metrics (Future)
- Run duration
- Anomaly counts
- Detection precision
- API latency

## Testing Strategy

### Unit Tests
- Each module tested independently
- Mock external dependencies
- Fast (<1 second)

### Integration Tests
- End-to-end pipeline
- Real DuckDB database
- Mock API data

### Validation Tests
- Injected anomalies (synthetic spikes)
- Precision >= 80%
- Stability >= 95%

## Future Enhancements

### Short-term
- FastAPI implementation
- SHAP explanations
- Multi-geography support

### Long-term
- Real-time detection
- Ensemble models
- Natural language search
- Alert system
