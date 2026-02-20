# Data Contracts

## Overview

This document defines the schema for all tables in CivicSpend's DuckDB database.

## Tables

### 1. run_manifest

Tracks all pipeline executions for reproducibility.

```sql
CREATE TABLE run_manifest (
    run_id VARCHAR PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    state VARCHAR,
    start_date DATE,
    end_date DATE,
    config_hash VARCHAR,
    status VARCHAR,
    record_count INTEGER
);
```

**Fields**:
- `run_id`: Unique identifier (UUID)
- `created_at`: Execution timestamp
- `state`: State code (e.g., "MN")
- `start_date`: Award date range start
- `end_date`: Award date range end
- `config_hash`: Configuration fingerprint
- `status`: "pending", "complete", "failed"
- `record_count`: Number of awards fetched

**Purpose**: Audit trail, reproducibility, run comparison

---

### 2. raw_awards

Immutable source data from USAspending API.

```sql
CREATE TABLE raw_awards (
    award_id VARCHAR PRIMARY KEY,
    run_id VARCHAR,
    recipient_name VARCHAR,
    recipient_duns VARCHAR,
    recipient_uei VARCHAR,
    awarding_agency_name VARCHAR,
    awarding_sub_agency_name VARCHAR,
    award_description VARCHAR,
    award_type VARCHAR,
    total_obligation DECIMAL(18,2),
    action_date DATE,
    period_of_performance_start_date DATE,
    period_of_performance_end_date DATE,
    place_of_performance_state VARCHAR,
    place_of_performance_city VARCHAR,
    naics_code VARCHAR,
    naics_description VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Fields**:
- `award_id`: Unique award identifier (from API)
- `run_id`: Link to run_manifest
- `recipient_name`: Vendor name (raw, not normalized)
- `recipient_duns`: DUNS number (legacy identifier)
- `recipient_uei`: UEI number (new identifier)
- `awarding_agency_name`: Federal agency
- `awarding_sub_agency_name`: Sub-agency
- `award_description`: Award purpose/description
- `award_type`: Contract type (e.g., "A", "B", "C")
- `total_obligation`: Award amount (USD)
- `action_date`: Award action date
- `period_of_performance_start_date`: Contract start
- `period_of_performance_end_date`: Contract end
- `place_of_performance_state`: State code
- `place_of_performance_city`: City name
- `naics_code`: Industry code
- `naics_description`: Industry description
- `created_at`: Ingestion timestamp

**Purpose**: Source of truth, lineage tracking

**Indexes**: `run_id`, `recipient_name`, `action_date`

---

### 3. vendor_entities

Deduplicated vendor identities.

```sql
CREATE TABLE vendor_entities (
    vendor_id VARCHAR PRIMARY KEY,
    canonical_name VARCHAR,
    duns VARCHAR,
    uei VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Fields**:
- `vendor_id`: Unique vendor identifier (UUID)
- `canonical_name`: Normalized vendor name
- `duns`: Primary DUNS (if available)
- `uei`: Primary UEI (if available)
- `created_at`: Creation timestamp

**Purpose**: Entity resolution, vendor tracking

---

### 4. award_vendor_map

Links awards to normalized vendors.

```sql
CREATE TABLE award_vendor_map (
    award_id VARCHAR,
    vendor_id VARCHAR,
    match_score FLOAT,
    match_method VARCHAR,
    PRIMARY KEY (award_id, vendor_id)
);
```

**Fields**:
- `award_id`: Link to raw_awards
- `vendor_id`: Link to vendor_entities
- `match_score`: Fuzzy match confidence (0-100)
- `match_method`: "exact_duns", "exact_uei", "fuzzy_name"

**Purpose**: Traceability, match quality tracking

---

### 5. monthly_vendor_spend

Aggregated time series with features.

```sql
CREATE TABLE monthly_vendor_spend (
    vendor_id VARCHAR,
    month DATE,
    obligation_sum DECIMAL(18,2),
    award_count INTEGER,
    avg_award_size DECIMAL(18,2),
    max_award_size DECIMAL(18,2),
    agency_count INTEGER,
    naics_count INTEGER,
    rolling_3m_avg DECIMAL(18,2),
    rolling_3m_std DECIMAL(18,2),
    rolling_3m_max DECIMAL(18,2),
    month_over_month_change DECIMAL(18,2),
    month_over_month_pct_change FLOAT,
    PRIMARY KEY (vendor_id, month)
);
```

**Fields**:
- `vendor_id`: Link to vendor_entities
- `month`: Month (first day of month)
- `obligation_sum`: Total monthly spend
- `award_count`: Number of awards
- `avg_award_size`: Mean award amount
- `max_award_size`: Largest award
- `agency_count`: Distinct agencies
- `naics_count`: Distinct industries
- `rolling_3m_avg`: 3-month rolling average
- `rolling_3m_std`: 3-month rolling std dev
- `rolling_3m_max`: 3-month rolling max
- `month_over_month_change`: Absolute change
- `month_over_month_pct_change`: Percent change

**Purpose**: Time series analysis, feature engineering

**Indexes**: `vendor_id`, `month`

---

### 6. anomalies (Logical View)

Detected anomalies (not a physical table, generated on-the-fly).

**Fields**:
- `anomaly_id`: Unique identifier (UUID)
- `run_id`: Link to run_manifest
- `vendor_id`: Link to vendor_entities
- `month`: Anomaly month
- `detection_method`: "baseline" or "ml"
- `anomaly_score`: Numeric score (higher = more anomalous)
- `severity`: "low", "medium", "high", "critical"
- `obligation_sum`: Monthly spend
- `baseline_median`: Historical median
- `deviation`: Absolute deviation
- `deviation_pct`: Percent deviation
- `top_awards`: JSON array of contributing awards
- `feature_drivers`: JSON object of feature changes
- `narrative`: Factual explanation text

**Purpose**: Anomaly storage, evidence linking

---

## Data Types

### Monetary Values
- Type: `DECIMAL(18,2)`
- Precision: 18 digits, 2 decimal places
- Range: -999,999,999,999,999.99 to 999,999,999,999,999.99
- Sufficient for federal spending (trillions)

### Dates
- Type: `DATE`
- Format: YYYY-MM-DD
- Range: 1000-01-01 to 9999-12-31

### Timestamps
- Type: `TIMESTAMP`
- Format: YYYY-MM-DD HH:MM:SS
- Timezone: UTC (implicit)

### Identifiers
- Type: `VARCHAR`
- Format: UUID v4 (36 characters)
- Example: "550e8400-e29b-41d4-a716-446655440000"

### Scores
- Type: `FLOAT`
- Range: 0.0 to 100.0 (match scores)
- Range: -∞ to +∞ (anomaly scores)

---

## Relationships

```
run_manifest (1) ──< (N) raw_awards
                         │
                         │ (N)
                         ▼
                    award_vendor_map
                         │
                         │ (N)
                         ▼
vendor_entities (1) ──< (N) monthly_vendor_spend
```

---

## Constraints

### Primary Keys
- All tables have primary keys
- Composite keys for junction tables

### Foreign Keys
- Not enforced (DuckDB limitation)
- Maintained by application logic

### NOT NULL
- Primary keys: NOT NULL (implicit)
- Optional fields: NULL allowed

### Defaults
- `created_at`: CURRENT_TIMESTAMP
- `status`: "pending"

---

## Indexes

### Performance Indexes
```sql
CREATE INDEX idx_raw_awards_run_id ON raw_awards(run_id);
CREATE INDEX idx_raw_awards_recipient ON raw_awards(recipient_name);
CREATE INDEX idx_raw_awards_date ON raw_awards(action_date);
CREATE INDEX idx_monthly_vendor ON monthly_vendor_spend(vendor_id);
CREATE INDEX idx_monthly_month ON monthly_vendor_spend(month);
```

### Rationale
- `run_id`: Filter by run
- `recipient_name`: Fuzzy matching
- `action_date`: Time range queries
- `vendor_id`: Vendor lookups
- `month`: Time series queries

---

## Data Volumes (Estimated)

### Minnesota (24 months)
- `raw_awards`: ~50K-100K rows
- `vendor_entities`: ~5K-10K rows
- `award_vendor_map`: ~50K-100K rows
- `monthly_vendor_spend`: ~10K-20K rows
- `anomalies`: ~20-50 rows

### All 50 States (24 months)
- `raw_awards`: ~2M-5M rows
- `vendor_entities`: ~200K-500K rows
- `award_vendor_map`: ~2M-5M rows
- `monthly_vendor_spend`: ~500K-1M rows
- `anomalies`: ~1K-2K rows

---

## Storage Estimates

### Minnesota (24 months)
- Database size: ~50-100 MB
- Model artifacts: ~1-5 MB
- Logs: ~10 MB
- **Total**: ~60-115 MB

### All 50 States (24 months)
- Database size: ~2-5 GB
- Model artifacts: ~10-50 MB
- Logs: ~50 MB
- **Total**: ~2-5 GB

---

## Data Quality

### Completeness
- `recipient_name`: 100% (required by API)
- `recipient_duns`: ~70% (legacy, being phased out)
- `recipient_uei`: ~90% (new standard)
- `award_description`: ~95%
- `naics_code`: ~85%

### Accuracy
- Vendor matching: ~85% (fuzzy + exact)
- Date fields: 100% (validated by API)
- Monetary values: 100% (validated by API)

### Consistency
- State codes: Validated against ISO 3166-2
- NAICS codes: Validated against 2022 NAICS
- Award types: Validated against USAspending schema

---

## Versioning

### Schema Version: 1.0
- Initial release
- Compatible with USAspending API v2

### Migration Strategy
- Future schema changes: ALTER TABLE
- Backward compatibility: Maintain old columns
- Data migration: SQL scripts in `migrations/`

---

## Backup & Recovery

### Backup Strategy
- DuckDB file: Copy `data/civicspend.duckdb`
- Frequency: After each run
- Retention: Keep last 5 runs

### Recovery
```bash
# Restore from backup
cp data/civicspend.duckdb.backup data/civicspend.duckdb

# Verify integrity
duckdb data/civicspend.duckdb "SELECT COUNT(*) FROM raw_awards;"
```

---

## API Mapping

### USAspending API → raw_awards

| API Field | Table Column |
|-----------|--------------|
| `award_id` | `award_id` |
| `recipient.recipient_name` | `recipient_name` |
| `recipient.recipient_duns` | `recipient_duns` |
| `recipient.recipient_uei` | `recipient_uei` |
| `awarding_agency.toptier_agency.name` | `awarding_agency_name` |
| `awarding_agency.subtier_agency.name` | `awarding_sub_agency_name` |
| `description` | `award_description` |
| `type` | `award_type` |
| `total_obligation` | `total_obligation` |
| `action_date` | `action_date` |
| `period_of_performance.start_date` | `period_of_performance_start_date` |
| `period_of_performance.end_date` | `period_of_performance_end_date` |
| `place_of_performance.state_code` | `place_of_performance_state` |
| `place_of_performance.city_name` | `place_of_performance_city` |
| `naics_code` | `naics_code` |
| `naics_description` | `naics_description` |

---

## Example Queries

### Get vendor spending timeline
```sql
SELECT 
    month,
    obligation_sum,
    award_count,
    rolling_3m_avg
FROM monthly_vendor_spend
WHERE vendor_id = '<vendor_id>'
ORDER BY month;
```

### Find high-severity anomalies
```sql
SELECT 
    vendor_id,
    month,
    anomaly_score,
    severity,
    obligation_sum
FROM anomalies
WHERE severity IN ('high', 'critical')
ORDER BY anomaly_score DESC;
```

### Trace anomaly to source awards
```sql
SELECT 
    a.award_id,
    a.recipient_name,
    a.total_obligation,
    a.awarding_agency_name,
    a.award_description
FROM raw_awards a
JOIN award_vendor_map m ON a.award_id = m.award_id
WHERE m.vendor_id = '<vendor_id>'
  AND DATE_TRUNC('month', a.action_date) = '<anomaly_month>'
ORDER BY a.total_obligation DESC
LIMIT 5;
```
