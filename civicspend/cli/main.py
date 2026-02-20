"""CivicSpend CLI."""
import click
from civicspend.db.connection import init_database
from civicspend.cli.ingest import ingest
from civicspend.cli.normalize import normalize
from civicspend.cli.build_features import build_features
from civicspend.cli.detect import detect
from civicspend.cli.train_model import train_model
from civicspend.cli.export import export

@click.group()
@click.version_option(version="0.1.0-dev")
def cli():
    """CivicSpend: Public Spending Transparency Platform."""
    pass

@cli.command()
def init():
    """Initialize database."""
    click.echo("Initializing CivicSpend database...")
    init_database()
    click.echo("[OK] Database initialized!")

cli.add_command(ingest)
cli.add_command(normalize)
cli.add_command(build_features)
cli.add_command(detect)
cli.add_command(train_model)
cli.add_command(export)

if __name__ == "__main__":
    cli()
