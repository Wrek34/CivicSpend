"""End-to-end pipeline test."""
import uuid
import json
from civicspend.db.connection import get_connection, init_database
from civicspend.ingest.mock_data import generate_mock_awards
from civicspend.normalize.vendor_matcher import VendorMatcher
from civicspend.features.aggregator import MonthlyAggregator
from civicspend.detect.baseline import RobustMADDetector

def test_full_pipeline():
    """Test complete pipeline: ingest -> normalize -> features -> detect."""
    # Initialize
    init_database()
    run_id = str(uuid.uuid4())
    conn = get_connection()
    
    # 1. Ingest mock data
    conn.execute("""
        INSERT INTO run_manifest (run_id, filters_json, status)
        VALUES (?, ?, 'running')
    """, [run_id, json.dumps({"test": "e2e"})])
    
    mock_data = generate_mock_awards(200)
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
    
    print(f"[1/4] Ingested {len(mock_data['results'])} awards")
    
    # 2. Normalize vendors
    matcher = VendorMatcher()
    vendor_count = matcher.normalize_run(run_id)
    print(f"[2/4] Normalized to {vendor_count} vendors")
    
    # 3. Build features
    aggregator = MonthlyAggregator()
    feature_count = aggregator.aggregate_run(run_id)
    print(f"[3/4] Created {feature_count} vendor-month records")
    
    # 4. Detect anomalies
    detector = RobustMADDetector(threshold=2.5)  # Lower threshold for testing
    anomalies = detector.detect_run(run_id)
    print(f"[4/4] Detected {len(anomalies)} anomalies")
    
    if anomalies:
        print("\nTop Anomalies:")
        for a in sorted(anomalies, key=lambda x: abs(x['z_score']), reverse=True)[:5]:
            print(f"  {a['year_month']}: ${a['value']:,.2f} (z={a['z_score']:.2f}, {a['severity']})")
    
    conn.close()
    
    # Assertions
    assert vendor_count > 0
    assert feature_count > 0
    print("\n[OK] Full pipeline test passed!")

if __name__ == "__main__":
    test_full_pipeline()
