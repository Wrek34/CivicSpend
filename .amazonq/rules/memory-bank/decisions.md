# Technical Decisions

## Decision Log
Track important technical decisions made during development.

### Format
- **Date**: YYYY-MM-DD
- **Decision**: What was decided
- **Rationale**: Why this decision was made
- **Alternatives**: What other options were considered
- **Impact**: How this affects the project

---

## Decision 1: Project Scope - CivicSpend Lens Clone with ML

**Date**: 2024-01-XX  
**Decision**: Build public spending anomaly detector (Minnesota focus) with dual detection (robust statistics + Isolation Forest)  
**Rationale**:
- Feasible for solo builder in 6 weeks
- Demonstrates both statistical and ML skills
- Clear portfolio artifact with social impact
- Tight scope prevents feature creep
- Evidence traceability builds trust

**Alternatives**:
- Broader scope (all states): Too much data, harder to demo
- ML-only: Less trustworthy, harder to validate
- Different domain: Public spending has open data + clear use case

**Impact**:
- Clear 6-week roadmap
- Manageable data volume (~50K-100K awards)
- Credible demo in 3-5 minutes
- Portfolio-quality documentation

---

[See docs/DECISION_LOG.md for complete decision history]
