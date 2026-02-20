"""Demo data loader for CivicSpend dashboard."""
import os
from pathlib import Path
from civicspend.ingest.mock_data import generate_mock_data
from civicspend.db.connection import get_connection, init_database


def ensure_demo_data():
    """Ensure demo data exists for dashboard."""
    db_path = Path("data/civicspend.duckdb")
    
    # Create data directory if needed
    db_path.parent.mkdir(exist_ok=True)
    
    # Initialize database if needed
    if not db_path.exists():
        init_database(str(db_path))
        
        # Generate and insert mock data
        conn = get_connection(str(db_path))
        run_id = generate_mock_data(conn)
        conn.close()
        
        return run_id
    
    # Check if data exists
    conn = get_connection(str(db_path))
    result = conn.execute("SELECT run_id FROM run_manifest LIMIT 1").fetchone()
    conn.close()
    
    if result:
        return result[0]
    
    # Generate data if empty
    conn = get_connection(str(db_path))
    run_id = generate_mock_data(conn)
    conn.close()
    
    return run_id
