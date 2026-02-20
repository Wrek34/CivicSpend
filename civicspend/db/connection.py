"""Database connection and initialization."""
import duckdb
from pathlib import Path

DB_PATH = Path("data/civicspend.duckdb")

def get_connection():
    """Get DuckDB connection."""
    DB_PATH.parent.mkdir(exist_ok=True)
    return duckdb.connect(str(DB_PATH))

def init_database():
    """Initialize database with schema."""
    conn = get_connection()
    schema_path = Path(__file__).parent / "schema.sql"
    with open(schema_path) as f:
        conn.execute(f.read())
    conn.close()
    return True
