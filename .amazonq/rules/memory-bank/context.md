# Project Context

## Current Status
Specification phase → Week 1 implementation starting

## Active Features
- MVP scope: Monthly vendor anomalies in Minnesota
- Dual detection: Robust MAD + Isolation Forest
- Evidence traceability: Every anomaly → award IDs

## Known Issues
- Vendor normalization is fuzzy (not perfect entity resolution)
- No ground-truth labels (unsupervised learning)
- API rate limits on USAspending (need backoff/caching)

## Next Steps
1. Implement ingestion pipeline (Week 1)
2. Build vendor normalization (Week 2)
3. Implement baseline + ML detection (Week 2-3)
4. Add explanation layer (Week 4)
5. Build UI + demo (Week 5)
6. Harden + document (Week 6)
