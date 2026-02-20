"""Train ML model command."""
import click
from civicspend.detect.ml import MLDetector

@click.command()
@click.option('--run-id', required=True, help='Run ID for training data')
@click.option('--contamination', default=0.05, help='Expected anomaly rate')
def train_model(run_id, contamination):
    """Train ML anomaly detection model."""
    click.echo(f"Training Isolation Forest on run: {run_id}")
    
    detector = MLDetector(contamination=contamination)
    sample_count = detector.train(run_id)
    model_path = detector.save_model(run_id)
    
    click.echo(f"[OK] Trained on {sample_count} samples")
    click.echo(f"Model saved to: {model_path}")
