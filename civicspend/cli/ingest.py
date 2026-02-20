"""Ingest command."""
import click
import uuid
import json
from datetime import datetime
from civicspend.ingest.api_client import USAspendingClient
from civicspend.db.connection import get_connection

@click.command()
@click.option('--state', required=True, help='State code (e.g., MN)')
@click.option('--start-date', required=True, help='Start date (YYYY-MM-DD)')
@click.option('--end-date', required=True, help='End date (YYYY-MM-DD)')
@click.option('--limit', default=100, help='Records per page')
@click.option('--max-pages', default=5, help='Maximum pages to fetch')
def ingest(state, start_date, end_date, limit, max_pages):
    """Ingest awards from USAspending API."""
    run_id = str(uuid.uuid4())
    click.echo(f"Starting ingestion run: {run_id}")
    click.echo(f"Fetching {state} awards from {start_date} to {end_date}")
    
    client = USAspendingClient()
    conn = get_connection()
    
    # Create run manifest
    filters = {
        "state": state,
        "start_date": start_date,
        "end_date": end_date
    }
    
    conn.execute("""
        INSERT INTO run_manifest (run_id, filters_json, status)
        VALUES (?, ?, 'running')
    """, [run_id, json.dumps(filters)])
    
    total_records = 0
    
    try:
        for page in range(1, max_pages + 1):
            click.echo(f"Fetching page {page}...")
            
            result = client.fetch_awards(state, start_date, end_date, limit, page)
            
            if not result.get('results'):
                break
            
            # Insert awards
            for award in result['results']:
                award_id = award.get('Award ID', f"unknown_{uuid.uuid4()}")
                
                conn.execute("""
                    INSERT OR IGNORE INTO raw_awards (
                        run_id, award_id, recipient_name, recipient_duns,
                        awarding_agency_name, action_date, obligation_amount,
                        place_of_performance_state
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, [
                    run_id,
                    award_id,
                    award.get('Recipient Name'),
                    award.get('recipient_duns'),
                    award.get('Awarding Agency'),
                    award.get('Start Date'),
                    award.get('Award Amount', 0),
                    state
                ])
                total_records += 1
            
            click.echo(f"  Inserted {len(result['results'])} records")
        
        # Update manifest
        conn.execute("""
            UPDATE run_manifest 
            SET status = 'completed', row_count_raw = ?
            WHERE run_id = ?
        """, [total_records, run_id])
        
        click.echo(f"\n[OK] Ingestion complete!")
        click.echo(f"Run ID: {run_id}")
        click.echo(f"Total records: {total_records}")
        
    except Exception as e:
        conn.execute("""
            UPDATE run_manifest SET status = 'failed' WHERE run_id = ?
        """, [run_id])
        click.echo(f"[ERROR] Ingestion failed: {e}")
        raise
    
    finally:
        conn.close()
