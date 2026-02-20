"""CivicSpend CLI."""
import click
from civicspend.db.connection import init_database

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
    click.echo("✓ Database initialized!")

if __name__ == "__main__":
    cli()
