"""Normalize command."""
import click
from civicspend.normalize.vendor_matcher import VendorMatcher

@click.command()
@click.option('--run-id', required=True, help='Run ID to normalize')
@click.option('--threshold', default=85.0, help='Fuzzy match threshold')
def normalize(run_id, threshold):
    """Normalize vendor identities."""
    click.echo(f"Normalizing vendors for run: {run_id}")
    
    matcher = VendorMatcher(threshold=threshold)
    vendor_count = matcher.normalize_run(run_id)
    
    click.echo(f"[OK] Normalized to {vendor_count} unique vendors")
