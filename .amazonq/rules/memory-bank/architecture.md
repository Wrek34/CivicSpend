# Architecture

## System Design
Pipeline architecture: Ingest → Normalize → Aggregate → Detect (Baseline + ML) → Explain → Export/Serve

## Key Components
- **Ingestion**: USAspending API → raw_awards table
- **Normalization**: Vendor entity resolution → vendor_entities + aliases
- **Feature Engineering**: Monthly aggregates + rolling stats → monthly_vendor_spend
- **Detection Dual Track**: Robust MAD (baseline) + Isolation Forest (ML)
- **Explanation**: Award-level evidence + feature contribution
- **Storage**: DuckDB (local, embedded, fast analytics)
- **API**: FastAPI endpoints for anomaly queries
- **UI**: Streamlit dashboard (MVP)

## Data Flow
1. CLI: ingest → fetch awards (MN, date range) → raw_awards
2. CLI: normalize → dedupe vendors → vendor_entities
3. CLI: build-features → aggregate monthly → monthly_vendor_spend
4. CLI: train → fit Isolation Forest → save model artifact
5. CLI: score → detect anomalies (both methods) → anomalies table
6. CLI: explain → link awards + compute drivers → explanation_json
7. API/UI: query anomalies with evidence

## Design Patterns
- **Immutable runs**: Each run gets run_id, stored in run_manifest
- **Lineage tracking**: Every anomaly links to award_ids
- **Dual detection**: Always run baseline + ML in parallel
- **Explainability-first**: No anomaly without evidence
