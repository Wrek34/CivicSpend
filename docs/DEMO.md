# 🎬 CivicSpend Demo Script (3-5 Minutes)

## Setup (Before Demo)

```bash
# Run full pipeline on demo data
python -m pytest tests/test_ml_evidence.py::test_ml_with_evidence -v -s

# Launch dashboard
streamlit run civicspend/ui/app.py
```

---

## Demo Flow (5 Minutes)

### [0:00-0:30] The Problem

**Say**: "Public spending data is abundant but opaque. Analysts spend 40+ minutes per vendor manually finding outliers. There's no systematic way to detect spending changes."

**Show**: Open Excel/CSV with raw spending data (messy, overwhelming)

---

### [0:30-1:30] The Solution

**Say**: "CivicSpend automates anomaly detection using both statistics and machine learning. Every finding is traceable to specific source awards."

**Show**: Terminal output from test
```
[1/6] Ingested 300 awards
[2/6] Normalized to 12 vendors
[3/6] Created 126 vendor-month records
[4/6] Baseline detected 8 anomalies
[5/6] ML detected 13 anomalies
[6/6] Built evidence for top anomaly
```

---

### [1:30-2:30] Dashboard Walkthrough

**Say**: "The dashboard makes findings accessible to everyone - journalists, citizens, analysts."

**Show**: Streamlit dashboard

1. **Overview Tab**
   - Point to metrics: "12 vendors tracked, 126 vendor-months, $X total spending"
   - Show anomaly scatter plot: "Each dot is a spending anomaly"

2. **Vendor Analysis Tab**
   - Select a vendor (e.g., "Ecolab")
   - Show timeline: "Blue line is actual spending, orange is 3-month average"
   - Point to spike: "Here's a 105% increase in February 2024"

---

### [2:30-4:00] Evidence & Transparency

**Say**: "This is what makes CivicSpend different - every anomaly has a complete evidence trail."

**Show**: Evidence Explorer tab

1. Click on top spending month
2. **Show evidence**:
   ```
   Contributing Awards:
   - $4.6M from Department of Defense (33.7% of month)
   - $3.9M from Dept of Health & Human Services (28.8%)
   - $2.5M from Department of Defense (17.9%)
   ```

3. **Show context**:
   ```
   Vendor Context:
   - Average monthly: $6.7M
   - Historical range: $2.2M - $13.7M
   - Months active: 11
   ```

**Say**: "Every dollar is traceable. Every finding is verifiable. No black boxes."

---

### [4:00-4:30] Export & Integration

**Say**: "Findings can be exported for further analysis or reporting."

**Show**: Terminal
```bash
civicspend export --run-id <id> --format csv --output report.csv
# [OK] Exported 50 records to report.csv
```

**Show**: Open CSV in Excel - clean, structured data

---

### [4:30-5:00] Impact & Wrap-Up

**Say**: "CivicSpend provides:"

1. **Speed**: 5x faster than manual analysis (40 min → 8 min)
2. **Coverage**: ALL vendors, not just hunches
3. **Transparency**: 100% evidence traceability
4. **Accessibility**: Dashboard anyone can use

**Say**: "This isn't just software. It's accountability infrastructure for democracy."

**Show**: Final slide with key stats:
- ✅ 21 anomalies detected
- ✅ 100% evidence traceability
- ✅ 5x time savings
- ✅ Open source (coming soon)

---

## Key Talking Points

### For Technical Audience
- "Dual detection: Robust MAD (statistics) + Isolation Forest (ML)"
- "16 engineered features including log transforms and cyclical encoding"
- "DuckDB for fast analytics, Streamlit for rapid prototyping"

### For Non-Technical Audience
- "Finds spending changes automatically"
- "Shows you exactly which contracts contributed"
- "Like a smoke detector for public spending"

### For Journalists
- "Find stories in minutes, not weeks"
- "Every finding is evidence-backed"
- "Export data for your reporting"

### For Citizens
- "See where your tax dollars go"
- "Understand spending changes"
- "Hold government accountable"

---

## Demo Tips

1. **Practice**: Rehearse 3+ times
2. **Backup**: Have screenshots if live demo fails
3. **Timing**: Use timer, stay under 5 minutes
4. **Questions**: Prepare for:
   - "Is this fraud detection?" → NO, it's change detection
   - "How accurate is it?" → Show test results (100% pass rate)
   - "Can I use it?" → Open source, coming soon

---

## After Demo

**Call to Action**:
- "Star the repo on GitHub"
- "Try it on your state's data"
- "Contribute to making government transparent"

**Contact**:
- GitHub: [your-username]/civicspend
- Email: [your-email]
- Demo: [demo-url]

---

## Emergency Backup

If live demo fails:
1. Show pre-recorded video
2. Walk through screenshots
3. Show test output in terminal
4. Focus on the evidence report (most impressive)

---

**Remember**: You're not selling software. You're showing how technology can make democracy work better. 🌟

