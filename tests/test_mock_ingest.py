"""Quick test ingestion with mock data."""
import uuid
import json
from civicspend.db.connection import get_connection
from civicspend.ingest.mock_data import generate_mock_awards

def test_ingest_mock_data():
    """Test ingestion with mock data."""
    run_id = str(uuid.uuid4())
    conn = get_connection()
    
    # Create run
    conn.execute("""
        INSERT INTO run_manifest (run_id, filters_json, status)
        VALUES (?, ?, 'running')
    """, [run_id, json.dumps({"test": "mock"})])
    
    # Generate and insert mock data
    mock_data = generate_mock_awards(100)
    
    for award in mock_data['results']:
        conn.execute("""
            INSERT INTO raw_awards (
                run_id, award_id, recipient_name, recipient_duns,
                awarding_agency_name, action_date, obligation_amount,
                place_of_performance_state
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            run_id,
            award['Award ID'],
            award['Recipient Name'],
            award['recipient_duns'],
            award['Awarding Agency'],
            award['Start Date'],
            award['Award Amount'],
            'MN'
        ])
    
    # Update manifest
    conn.execute("""
        UPDATE run_manifest 
        SET status = 'completed', row_count_raw = ?
        WHERE run_id = ?
    """, [len(mock_data['results']), run_id])
    
    # Verify
    result = conn.execute("""
        SELECT COUNT(*) FROM raw_awards WHERE run_id = ?
    """, [run_id]).fetchone()
    
    assert result[0] == 100
    
    # Get top vendors
    top_vendors = conn.execute("""
        SELECT recipient_name, SUM(obligation_amount) as total
        FROM raw_awards
        WHERE run_id = ?
        GROUP BY recipient_name
        ORDER BY total DESC
        LIMIT 5
    """, [run_id]).fetchall()
    
    print(f"\n[OK] Mock ingestion complete!")
    print(f"Run ID: {run_id}")
    print(f"Total records: {result[0]}")
    print(f"\nTop 5 Vendors:")
    for vendor, total in top_vendors:
        print(f"  {vendor}: ${total:,.2f}")
    
    conn.close()
    return run_id

if __name__ == "__main__":
    test_ingest_mock_data()
