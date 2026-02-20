# Coding Conventions

## Naming Conventions
- Tables: snake_case (raw_awards, monthly_vendor_spend)
- Functions: snake_case (fetch_awards, compute_mad_score)
- Classes: PascalCase (AnomalyDetector, VendorNormalizer)
- Constants: UPPER_SNAKE (MIN_VOLUME_THRESHOLD)
- CLI commands: kebab-case (build-features, train-model)

## Code Style
- Python: Black formatter, isort, type hints
- Max line length: 100
- Docstrings: Google style
- No magic numbers: use named constants

## File Organization
```
gnit/
  cli/          # Click commands
  ingest/       # API fetching
  normalize/    # Vendor deduplication
  features/     # Aggregation + feature engineering
  detect/       # Baseline + ML anomaly detection
  explain/      # Evidence + feature contribution
  db/           # DuckDB schema + queries
  api/          # FastAPI endpoints
  ui/           # Streamlit app
  models/       # Saved model artifacts
```

## Best Practices
- Every anomaly must be traceable to source awards
- Never use words: "fraud," "corruption," "suspicious"
- Use: "change," "anomaly," "outlier," "spike," "deviation"
- All runs are immutable: run_id + timestamp
- Model artifacts versioned per run
- Tests must include injected anomaly validation
