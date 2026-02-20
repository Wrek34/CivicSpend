"""CivicSpend Flask Web Application."""
from flask import Flask, render_template, jsonify
import duckdb
from pathlib import Path
import json

app = Flask(__name__)

# Initialize database
db_path = Path("data/civicspend.duckdb")
db_path.parent.mkdir(exist_ok=True)

def get_db():
    conn = duckdb.connect(str(db_path))
    
    # Check if tables exist, create demo data if not
    tables = conn.execute("SHOW TABLES").fetchall()
    if not tables:
        conn.execute("""
            CREATE TABLE vendor_entities (
                vendor_id VARCHAR PRIMARY KEY,
                canonical_name VARCHAR
            )
        """)
        
        conn.execute("""
            CREATE TABLE monthly_vendor_spend (
                vendor_id VARCHAR,
                month DATE,
                obligation_sum DECIMAL(18,2),
                award_count INTEGER,
                rolling_3m_avg DECIMAL(18,2)
            )
        """)
        
        conn.execute("""
            INSERT INTO vendor_entities VALUES 
            ('v1', '3M Company'),
            ('v2', 'Ecolab Inc'),
            ('v3', 'Target Corporation'),
            ('v4', 'General Mills'),
            ('v5', 'Medtronic')
        """)
        
        conn.execute("""
            INSERT INTO monthly_vendor_spend VALUES 
            ('v1', '2024-01-01', 5000000, 10, 4500000),
            ('v1', '2024-02-01', 6000000, 12, 5000000),
            ('v1', '2024-03-01', 5500000, 11, 5500000),
            ('v2', '2024-01-01', 3000000, 8, 2800000),
            ('v2', '2024-02-01', 9000000, 15, 4000000),
            ('v2', '2024-03-01', 4000000, 10, 5333000),
            ('v3', '2024-01-01', 2000000, 5, 1800000),
            ('v3', '2024-02-01', 2500000, 6, 2000000),
            ('v4', '2024-01-01', 4000000, 9, 3800000),
            ('v5', '2024-01-01', 7000000, 14, 6500000)
        """)
    
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    conn = get_db()
    stats = conn.execute("""
        SELECT COUNT(DISTINCT vendor_id) as vendors,
               SUM(obligation_sum) as total_spend,
               SUM(award_count) as total_awards
        FROM monthly_vendor_spend
    """).fetchone()
    
    return jsonify({
        'vendors': stats[0],
        'total_spend': float(stats[1]),
        'total_awards': stats[2]
    })

@app.route('/api/spending')
def get_spending():
    conn = get_db()
    result = conn.execute("""
        SELECT ve.canonical_name, mvs.month, mvs.obligation_sum, mvs.award_count
        FROM monthly_vendor_spend mvs
        JOIN vendor_entities ve ON mvs.vendor_id = ve.vendor_id
        ORDER BY mvs.month, mvs.obligation_sum DESC
    """).fetchall()
    
    data = [{
        'vendor': row[0],
        'month': str(row[1]),
        'spending': float(row[2]),
        'awards': row[3]
    } for row in result]
    
    return jsonify(data)

@app.route('/api/vendors')
def get_vendors():
    conn = get_db()
    result = conn.execute("""
        SELECT vendor_id, canonical_name
        FROM vendor_entities
        ORDER BY canonical_name
    """).fetchall()
    
    return jsonify([{'id': row[0], 'name': row[1]} for row in result])

@app.route('/api/vendor/<vendor_id>')
def get_vendor_timeline(vendor_id):
    conn = get_db()
    result = conn.execute("""
        SELECT month, obligation_sum, award_count, rolling_3m_avg
        FROM monthly_vendor_spend
        WHERE vendor_id = ?
        ORDER BY month
    """, [vendor_id]).fetchall()
    
    data = [{
        'month': str(row[0]),
        'spending': float(row[1]),
        'awards': row[2],
        'avg_3m': float(row[3]) if row[3] else None
    } for row in result]
    
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
