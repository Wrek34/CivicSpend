"""Export command for reports."""
import click
import json
import csv
from civicspend.db.connection import get_connection
from civicspend.explain.evidence import EvidenceBuilder

@click.command()
@click.option('--run-id', required=True, help='Run ID to export')
@click.option('--format', type=click.Choice(['csv', 'json']), default='csv', help='Export format')
@click.option('--output', required=True, help='Output file path')
@click.option('--top-n', default=50, help='Number of top anomalies to export')
def export(run_id, format, output, top_n):
    """Export anomaly report."""
    click.echo(f"Exporting {format.upper()} report for run: {run_id}")
    
    conn = get_connection()
    evidence_builder = EvidenceBuilder()
    
    # Get top anomalies
    query = """
        SELECT 
            ve.canonical_name as vendor_name,
            ve.vendor_id,
            mvs.year_month,
            mvs.obligation_sum,
            mvs.award_count,
            mvs.rolling_3m_mean
        FROM monthly_vendor_spend mvs
        JOIN vendor_entities ve ON mvs.vendor_id = ve.vendor_id
        WHERE mvs.run_id = ?
        ORDER BY mvs.obligation_sum DESC
        LIMIT ?
    """
    
    results = conn.execute(query, [run_id, top_n]).fetchall()
    
    if format == 'csv':
        with open(output, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Vendor', 'Month', 'Spending', 'Awards', 
                '3M Average', 'Change %', 'Severity'
            ])
            
            for row in results:
                vendor_name, vendor_id, month, spending, awards, avg_3m = row
                change_pct = ((spending - avg_3m) / avg_3m * 100) if avg_3m else 0
                severity = 'high' if abs(change_pct) > 100 else 'medium' if abs(change_pct) > 50 else 'low'
                
                writer.writerow([
                    vendor_name, month, f"${spending:,.2f}", awards,
                    f"${avg_3m:,.2f}", f"{change_pct:.1f}%", severity
                ])
    
    else:  # JSON
        export_data = []
        for row in results:
            vendor_name, vendor_id, month, spending, awards, avg_3m = row
            
            # Get evidence
            evidence = evidence_builder.build_evidence(run_id, vendor_id, month)
            context = evidence_builder.get_vendor_context(run_id, vendor_id)
            
            export_data.append({
                'vendor': vendor_name,
                'month': month,
                'spending': float(spending),
                'award_count': awards,
                'rolling_3m_avg': float(avg_3m),
                'change_pct': ((spending - avg_3m) / avg_3m * 100) if avg_3m else 0,
                'evidence': evidence,
                'context': context
            })
        
        with open(output, 'w') as f:
            json.dump(export_data, f, indent=2)
    
    click.echo(f"[OK] Exported {len(results)} records to {output}")
    conn.close()
