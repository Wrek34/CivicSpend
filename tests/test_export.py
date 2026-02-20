"""Test export functionality."""
import uuid
import json
import csv
from pathlib import Path
from civicspend.db.connection import get_connection, init_database
from civicspend.ingest.mock_data import generate_mock_awards
from civicspend.normalize.vendor_matcher import VendorMatcher
from civicspend.features.aggregator import MonthlyAggregator
from civicspend.cli.export import export
from click.testing import CliRunner

def test_export_csv():
    """Test CSV export."""
    init_database()
    run_id = str(uuid.uuid4())
    conn = get_connection()
    
    # Setup data
    conn.execute("""
        INSERT INTO run_manifest (run_id, filters_json, status)
        VALUES (?, ?, 'completed')
    """, [run_id, json.dumps({"test": "export"})])
    
    mock_data = generate_mock_awards(100)
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
    
    matcher = VendorMatcher()
    matcher.normalize_run(run_id)
    
    aggregator = MonthlyAggregator()
    aggregator.aggregate_run(run_id)
    
    # Test CSV export
    output_file = f"test_export_{run_id[:8]}.csv"
    runner = CliRunner()
    result = runner.invoke(export, [
        '--run-id', run_id,
        '--format', 'csv',
        '--output', output_file,
        '--top-n', '10'
    ])
    
    assert result.exit_code == 0
    assert Path(output_file).exists()
    
    # Verify CSV content
    with open(output_file, 'r') as f:
        reader = csv.reader(f)
        rows = list(reader)
        assert len(rows) > 1  # Header + data
        assert rows[0][0] == 'Vendor'
    
    # Cleanup
    Path(output_file).unlink()
    conn.close()
    
    print(f"[OK] CSV export test passed!")
    print(f"Exported {len(rows)-1} records")

if __name__ == "__main__":
    test_export_csv()
