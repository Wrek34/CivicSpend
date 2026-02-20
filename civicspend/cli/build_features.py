"""Build features command."""
import click
from civicspend.features.aggregator import MonthlyAggregator

@click.command()
@click.option('--run-id', required=True, help='Run ID to process')
def build_features(run_id):
    """Build monthly features."""
    click.echo(f"Building features for run: {run_id}")
    
    aggregator = MonthlyAggregator()
    count = aggregator.aggregate_run(run_id)
    
    click.echo(f"[OK] Created {count} vendor-month records")
