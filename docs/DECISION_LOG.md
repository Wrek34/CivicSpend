# Technical Decision Log

## Format
- **Date**: YYYY-MM-DD
- **Decision**: What was decided
- **Rationale**: Why this decision was made
- **Alternatives**: What other options were considered
- **Impact**: How this affects the project

---

## Decision 1: DuckDB over PostgreSQL

**Date**: 2024-01-XX  
**Decision**: Use DuckDB as primary database  
**Rationale**:
- Embedded (no server setup)
- Fast analytics queries (columnar storage)
- SQL interface familiar to analysts
- Sufficient for solo builder MVP
- Easy deployment (single file)

**Alternatives**:
- PostgreSQL: More mature, better for concurrent writes, but requires server setup
- SQLite: Simpler, but slower for analytics queries
- Pandas only: No persistent storage, harder to query

**Impact**:
- Faster development (no DB server management)
- Excellent query performance for aggregations
- Limited to single-writer scenarios (acceptable for batch pipeline)
- Easy to migrate to PostgreSQL later if needed

---

## Decision 2: Isolation Forest over Other ML Methods

**Date**: 2024-01-XX  
**Decision**: Use Isolation Forest as primary ML anomaly detector  
**Rationale**:
- Unsupervised (no labels needed)
- Fast training and scoring
- Handles mixed feature types well
- Provides anomaly scores (not just binary)
- Explainable via feature contribution approximation
- Well-supported in scikit-learn

**Alternatives**:
- One-Class SVM: Slower, harder to tune, less explainable
- Autoencoder: Requires more data, harder to debug, overkill for tabular data
- LSTM/time-series models: Complex, requires per-vendor training, harder to explain
- Robust PCA: Less effective for non-linear patterns

**Impact**:
- Faster implementation (1 week vs 2-3 weeks for deep learning)
- Good balance of accuracy and explainability
- Easier to debug and tune
- Sufficient for MVP, can add other methods later

---

## Decision 3: Streamlit over React for MVP UI

**Date**: 2024-01-XX  
**Decision**: Use Streamlit for initial UI  
**Rationale**:
- Rapid prototyping (Python-native)
- No frontend expertise required
- Built-in components for data apps
- Sufficient for demo and portfolio
- Can add React later if needed

**Alternatives**:
- React + Next.js: More polished, but requires frontend skills, slower development
- Dash (Plotly): Similar to Streamlit, but less intuitive API
- Jupyter notebooks: Not suitable for end-user UI

**Impact**:
- Faster UI development (Week 5 vs 2-3 weeks for React)
- Less polished aesthetics (acceptable for MVP)
- Easier to iterate on design
- Can migrate to React post-MVP if project scales

---

## Decision 4: Dual Detection (Baseline + ML) Always

**Date**: 2024-01-XX  
**Decision**: Always run both robust MAD and Isolation Forest  
**Rationale**:
- Baseline provides interpretable benchmark
- ML captures complex patterns baseline misses
- Side-by-side comparison builds trust
- Validates ML results against statistical method
- Demonstrates technical depth for portfolio

**Alternatives**:
- ML only: Harder to validate, less trustworthy
- Baseline only: Misses subtle patterns, less impressive technically

**Impact**:
- Slightly longer runtime (acceptable for batch processing)
- Richer anomaly dataset
- Better portfolio artifact (shows both approaches)
- Easier to explain to non-technical stakeholders

---

## Decision 5: Minnesota as Initial Geography

**Date**: 2024-01-XX  
**Decision**: Focus on Minnesota (place of performance) for MVP  
**Rationale**:
- Manageable data volume (~50K-100K awards)
- Sufficient vendor diversity
- Clear geographic boundary
- Easy to expand to other states later
- Avoids complexity of multi-state aggregation

**Alternatives**:
- All states: Too much data for solo builder, harder to demo
- Federal-only (no state filter): Less focused, harder to tell story
- Multiple states: Adds complexity without clear benefit for MVP

**Impact**:
- Faster data ingestion
- Easier to validate results (smaller scope)
- Clear demo narrative ("Minnesota public spending")
- Simple to replicate for other states post-MVP

---

## Decision 6: 24-Month Rolling Window

**Date**: 2024-01-XX  
**Decision**: Use 24 months of historical data  
**Rationale**:
- Sufficient for seasonal patterns (2 full years)
- Manageable data volume
- Recent enough to be relevant
- Balances history vs recency

**Alternatives**:
- 12 months: Too short for robust rolling features
- 36+ months: More data, but slower ingestion, less relevant
- All available history: Too much data, harder to process

**Impact**:
- Rolling features (3/6/12 months) are meaningful
- Faster ingestion and processing
- Recent anomalies are more actionable
- Can extend window post-MVP if needed

---

## Decision 7: No Perfect Entity Resolution

**Date**: 2024-01-XX  
**Decision**: Accept imperfect vendor normalization (~85% accuracy)  
**Rationale**:
- Perfect entity resolution is a research problem
- Fuzzy matching + DUNS/UEI covers most cases
- Manual overrides handle edge cases
- Diminishing returns beyond 85%
- Not critical for MVP (focus on anomaly detection)

**Alternatives**:
- Perfect entity resolution: Impossible without external data sources
- No normalization: Too many false positives (name variations)
- ML-based entity resolution: Overkill for MVP, requires training data

**Impact**:
- Some vendors may be split across multiple entities
- Documented limitation in risk register
- Manual override file provides escape hatch
- Good enough for portfolio demonstration

---

## Decision 8: Unsupervised Learning (No Labels)

**Date**: 2024-01-XX  
**Decision**: Use unsupervised anomaly detection (no ground-truth labels)  
**Rationale**:
- No labeled anomalies available
- Labeling is subjective and time-consuming
- Unsupervised methods are standard for this use case
- Evaluation via injected anomalies + human review

**Alternatives**:
- Supervised learning: Requires labeled data (not available)
- Semi-supervised: Requires some labels (not available)
- Active learning: Too complex for MVP

**Impact**:
- Cannot compute traditional precision/recall
- Evaluation relies on injected anomalies + human review
- More realistic for real-world deployment
- Documented limitation in metrics

---

## Decision 9: CLI-First Architecture

**Date**: 2024-01-XX  
**Decision**: Build CLI commands for all pipeline steps  
**Rationale**:
- Composable (can run steps independently)
- Testable (easy to mock and test)
- Scriptable (can automate with bash/cron)
- Debuggable (can inspect intermediate outputs)
- Professional (standard for data pipelines)

**Alternatives**:
- Monolithic script: Harder to test and debug
- UI-only: Not scriptable, harder to automate
- Airflow/Prefect: Overkill for MVP, adds complexity

**Impact**:
- More upfront work (CLI framework)
- Better testability and maintainability
- Easier to demonstrate technical skills
- Can add orchestration later if needed

---

## Decision 10: Immutable Runs with run_id

**Date**: 2024-01-XX  
**Decision**: Every pipeline execution gets unique run_id, data is immutable  
**Rationale**:
- Full reproducibility
- Audit trail for debugging
- Can compare runs side-by-side
- Prevents accidental data overwrites
- Professional data engineering practice

**Alternatives**:
- Mutable data: Simpler, but loses history
- Timestamp-only: Less explicit, harder to reference
- No versioning: Impossible to reproduce results

**Impact**:
- Slightly more storage (multiple runs stored)
- Better debugging and validation
- Demonstrates data engineering best practices
- Essential for portfolio quality

---

[Add new decisions as project progresses]

