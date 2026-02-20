"""Test database initialization."""
from civicspend.db.connection import get_connection, init_database

def test_database_creation():
    """Test database can be created and initialized."""
    init_database()
    conn = get_connection()
    
    tables = conn.execute("SHOW TABLES").fetchall()
    table_names = [t[0] for t in tables]
    
    assert "run_manifest" in table_names
    assert "raw_awards" in table_names
    
    conn.close()
