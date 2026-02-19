# Documentation Index

Complete guide to Gnit project documentation.

---

## Start Here

### New to the Project?
1. **[README.md](../README.md)** - Project overview, quickstart, installation
2. **[THESIS.md](THESIS.md)** - Problem statement and approach
3. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Executive summary

### Ready to Build?
1. **[SPECIFICATION.md](SPECIFICATION.md)** - Complete technical specification
2. **[ROADMAP.md](ROADMAP.md)** - Week-by-week plan
3. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Commands and thresholds

---

## Core Documentation

### Technical Specs
- **[SPECIFICATION.md](SPECIFICATION.md)** - Complete technical specification (MVP scope, data model, detection methods, evaluation)
- **[SPECIFICATION_PART2.md](SPECIFICATION_PART2.md)** - Evaluation, architecture options, roadmap, repo scaffold
- **[SPECIFICATION_PART3.md](SPECIFICATION_PART3.md)** - Implementation details, CLI commands, test strategy, demo script

### Architecture
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design, components, data flow (see Memory Bank)
- **[DATA_CONTRACTS.md](DATA_CONTRACTS.md)** - Table schemas (to be created)

### Problem & Approach
- **[THESIS.md](THESIS.md)** - Problem statement, approach, success criteria, limitations

---

## Process Documentation

### Planning
- **[ROADMAP.md](ROADMAP.md)** - Week-by-week milestones, post-MVP phases, backlog
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Executive overview, deliverables, key decisions

### Execution
- **[BUILD_LOG.md](BUILD_LOG.md)** - Weekly progress updates (to be filled during development)
- **[DECISION_LOG.md](DECISION_LOG.md)** - Technical decisions with rationale

### Risk Management
- **[RISK_REGISTER.md](RISK_REGISTER.md)** - Known risks, mitigation strategies, limitations

---

## Operational Documentation

### Demo & Evaluation
- **[DEMO.md](DEMO.md)** - 3-5 minute demo script (to be created)
- **[METRICS.md](METRICS.md)** - Evaluation results, success criteria (to be created)

### Reference
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - CLI commands, thresholds, queries, debugging tips

---

## Memory Bank (Amazon Q Context)

Located in `.amazonq/rules/memory-bank/`:

- **[project-overview.md](../.amazonq/rules/memory-bank/project-overview.md)** - Project name, purpose, tech stack
- **[architecture.md](../.amazonq/rules/memory-bank/architecture.md)** - System design, components, data flow
- **[context.md](../.amazonq/rules/memory-bank/context.md)** - Current status, active features, next steps
- **[conventions.md](../.amazonq/rules/memory-bank/conventions.md)** - Naming, code style, best practices
- **[decisions.md](../.amazonq/rules/memory-bank/decisions.md)** - Key technical decisions

---

## Documentation by Role

### For Developers
1. [SPECIFICATION.md](SPECIFICATION.md) - Full technical spec
2. [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Commands and patterns
3. [ARCHITECTURE.md](ARCHITECTURE.md) - System design
4. [BUILD_LOG.md](BUILD_LOG.md) - Weekly progress

### For Reviewers (Portfolio)
1. [README.md](../README.md) - Project overview
2. [THESIS.md](THESIS.md) - Problem and approach
3. [DEMO.md](DEMO.md) - Demo script
4. [METRICS.md](METRICS.md) - Evaluation results

### For Stakeholders
1. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Executive summary
2. [ROADMAP.md](ROADMAP.md) - Timeline and milestones
3. [RISK_REGISTER.md](RISK_REGISTER.md) - Limitations and risks

---

## Documentation Status

### ✅ Complete
- [x] README.md
- [x] SPECIFICATION.md (Parts 1-3)
- [x] THESIS.md
- [x] PROJECT_SUMMARY.md
- [x] ROADMAP.md
- [x] RISK_REGISTER.md
- [x] DECISION_LOG.md
- [x] BUILD_LOG.md (template)
- [x] QUICK_REFERENCE.md
- [x] Memory Bank (5 files)

### 🚧 To Be Created During Development
- [ ] DATA_CONTRACTS.md (Week 1)
- [ ] DEMO.md (Week 5)
- [ ] METRICS.md (Week 6)
- [ ] ARCHITECTURE.md (detailed diagrams, Week 6)

### 📝 To Be Updated Weekly
- [ ] BUILD_LOG.md (weekly progress)
- [ ] context.md (current status)
- [ ] ROADMAP.md (check off milestones)

---

## Documentation Standards

### File Naming
- Use UPPERCASE for major docs (README.md, SPECIFICATION.md)
- Use lowercase for Memory Bank files (context.md, decisions.md)
- Use descriptive names (QUICK_REFERENCE.md, not QR.md)

### Structure
- Start with H1 title
- Include table of contents for long docs (>500 lines)
- Use consistent heading hierarchy (H2 for sections, H3 for subsections)
- Include code blocks with language tags

### Content
- Be concrete: name files, tables, commands, thresholds
- No hype or vague "future work"
- List assumptions explicitly
- Include examples and code snippets

### Maintenance
- Update BUILD_LOG.md weekly
- Update context.md when status changes
- Add to DECISION_LOG.md when making technical choices
- Keep ROADMAP.md checkboxes current

---

## Quick Links

### Most Referenced
- [CLI Commands](QUICK_REFERENCE.md#cli-commands-cheat-sheet)
- [Database Tables](QUICK_REFERENCE.md#database-tables-quick-ref)
- [Detection Thresholds](QUICK_REFERENCE.md#key-thresholds)
- [Week-by-Week Plan](ROADMAP.md#mvp-weeks-1-6---current-phase)

### Most Important
- [MVP Scope](SPECIFICATION.md#mvp-scope-tight-wedge)
- [Data Model](SPECIFICATION.md#data-model--lineage)
- [Anomaly Detection](SPECIFICATION.md#anomaly-detection-approaches)
- [Success Metrics](PROJECT_SUMMARY.md#success-metrics)

---

## Contributing to Docs

### When to Update
- **BUILD_LOG.md**: Every Friday (weekly update)
- **context.md**: When status/features/issues change
- **DECISION_LOG.md**: When making technical decisions
- **ROADMAP.md**: When completing milestones
- **METRICS.md**: When running evaluations

### How to Update
1. Open relevant file
2. Find appropriate section
3. Add content following existing format
4. Commit with descriptive message: `docs(build-log): add week 1 update`

### Documentation Checklist (Week 6)
- [ ] All templates filled
- [ ] BUILD_LOG.md has 6 weekly updates
- [ ] METRICS.md has evaluation results
- [ ] DEMO.md has rehearsed script
- [ ] DATA_CONTRACTS.md has all table schemas
- [ ] ARCHITECTURE.md has diagrams
- [ ] README.md has correct URLs
- [ ] All links work (no 404s)

---

## Document Dependencies

```
README.md
  ├─> THESIS.md
  ├─> SPECIFICATION.md
  ├─> ARCHITECTURE.md
  ├─> DEMO.md
  └─> METRICS.md

SPECIFICATION.md
  ├─> DATA_CONTRACTS.md
  ├─> DECISION_LOG.md
  └─> RISK_REGISTER.md

PROJECT_SUMMARY.md
  ├─> ROADMAP.md
  ├─> DECISION_LOG.md
  └─> RISK_REGISTER.md

ROADMAP.md
  ├─> BUILD_LOG.md
  └─> METRICS.md
```

---

## Total Documentation Count

- **Core docs**: 11 files
- **Memory Bank**: 5 files
- **Total**: 16 files
- **Target**: 10+ (✅ Exceeded)

---

**Last Updated**: [Date]  
**Status**: Specification phase complete, ready for Week 1 implementation

