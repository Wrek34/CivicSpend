# Project Overview

## Project Name
Gnit (Government Insight Tracker)

## Purpose
Detect meaningful changes in public spending using robust statistics + ML anomaly detection, with full row-level evidence traceability. NOT fraud detection—focuses on "changes," "anomalies," "outliers," "spikes."

## Tech Stack
- Python 3.11+
- DuckDB (embedded analytics DB)
- FastAPI (API layer)
- scikit-learn (ML: Isolation Forest primary)
- Streamlit (MVP UI)
- pytest (testing)

## Key Dependencies
- requests (USAspending API)
- pandas/polars (data wrangling)
- numpy/scipy (robust statistics)
- joblib (model serialization)
- pydantic (data validation)
