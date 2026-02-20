"""Detect anomalies command."""
import click
from civicspend.detect.baseline import RobustMADDetector
from civicspend.db.connection import get_connection

@click.command()
@click.option('--run-id', required=True, help='Run ID to analyze')
@click.option('--threshold', default=3.5, help='Z-score threshold')
def detect(run_id, threshold):
    """Detect spending anomalies."""
    click.echo(f"Detecting anomalies for run: {run_id}")
    
    detector = RobustMADDetector(threshold=threshold)
    anomalies = detector.detect_run(run_id)
    
    if not anomalies:
        click.echo("[OK] No anomalies detected")
        return
    
    # Display results
    click.echo(f"\n[FOUND] {len(anomalies)} anomalies detected!\n")
    
    # Group by severity
    by_severity = {}
    for a in anomalies:
        by_severity.setdefault(a['severity'], []).append(a)
    
    for severity in ['critical', 'high', 'medium', 'low']:
        if severity in by_severity:
            click.echo(f"{severity.upper()}: {len(by_severity[severity])} anomalies")
            for a in by_severity[severity][:3]:  # Show top 3
                click.echo(f"  {a['year_month']}: ${a['value']:,.2f} (z={a['z_score']:.2f})")
