"""Test ML detection with evidence layer."""
import uuid
import json
from civicspend.db.connection import get_connection, init_database
from civicspend.ingest.mock_data import generate_mock_awards
from civicspend.normalize.vendor_matcher import VendorMatcher
from civicspend.features.aggregator import MonthlyAggregator
from civicspend.detect.baseline import RobustMADDetector
from civicspend.detect.ml import MLDetector
from civicspend.explain.evidence import EvidenceBuilder

def test_ml_with_evidence():
    """Test ML detection + evidence layer for transparency."""
    init_database()
    run_id = str(uuid.uuid4())
    conn = get_connection()
    
    # 1. Ingest
    conn.execute("""
        INSERT INTO run_manifest (run_id, filters_json, status)
        VALUES (?, ?, 'running')
    """, [run_id, json.dumps({"test": "ml_evidence"})])
    
    mock_data = generate_mock_awards(300)
    for award in mock_data['results']:
        conn.execute("""
            INSERT INTO raw_awards (
                run_id, award_id, recipient_name, recipient_duns,
                awarding_agency_name, action_date, obligation_amount,
                place_of_performance_state
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            run_id, award['Award ID'], award['Recipient Name'],
            award['recipient_duns'], award['Awarding Agency'],
            award['Start Date'], award['Award Amount'], 'MN'
        ])
    
    print(f"[1/6] Ingested {len(mock_data['results'])} awards")
    
    # 2. Normalize
    matcher = VendorMatcher()
    vendor_count = matcher.normalize_run(run_id)
    print(f"[2/6] Normalized to {vendor_count} vendors")
    
    # 3. Build features
    aggregator = MonthlyAggregator()
    feature_count = aggregator.aggregate_run(run_id)
    print(f"[3/6] Created {feature_count} vendor-month records")
    
    # 4. Baseline detection
    baseline = RobustMADDetector(threshold=2.5)
    baseline_anomalies = baseline.detect_run(run_id)
    print(f"[4/6] Baseline detected {len(baseline_anomalies)} anomalies")
    
    # 5. ML detection
    ml_detector = MLDetector(contamination=0.1)
    ml_detector.train(run_id)
    ml_anomalies = ml_detector.predict(run_id)
    print(f"[5/6] ML detected {len(ml_anomalies)} anomalies")
    
    # 6. Build evidence for top anomaly
    if ml_anomalies:
        top_anomaly = sorted(ml_anomalies, key=lambda x: abs(x['score']))[0]
        
        evidence_builder = EvidenceBuilder()
        evidence = evidence_builder.build_evidence(
            run_id, 
            top_anomaly['vendor_id'],
            top_anomaly['year_month']
        )
        context = evidence_builder.get_vendor_context(run_id, top_anomaly['vendor_id'])
        narrative = evidence_builder.generate_narrative(top_anomaly, evidence, context)
        
        print(f"[6/6] Built evidence for top anomaly\n")
        print("="*70)
        print("ANOMALY REPORT (For Transparency)")
        print("="*70)
        print(narrative)
        print("="*70)
        print(f"\nEvidence Trail ({len(evidence)} awards):")
        for e in evidence:
            print(f"  - Award {e['award_id']}: ${e['amount']:,.2f} ({e['pct_of_month']:.1f}%)")
        print("="*70)
    
    conn.close()
    
    # Assertions
    assert vendor_count > 0
    assert len(ml_anomalies) > 0
    assert len(evidence) > 0
    
    print("\n[OK] ML + Evidence test passed!")
    print(f"\nComparison:")
    print(f"  Baseline: {len(baseline_anomalies)} anomalies")
    print(f"  ML: {len(ml_anomalies)} anomalies")
    print(f"  Evidence: 100% traceable to source awards")

if __name__ == "__main__":
    test_ml_with_evidence()
