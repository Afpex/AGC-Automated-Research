import click
from main import TransportDataCollector
import pandas as pd

@click.group()
def cli():
    """Transport Data Collection CLI"""
    pass

@cli.command()
def collect():
    """Collect transport data from all sources"""
    collector = TransportDataCollector()
    data = collector.collect_data()
    click.echo(f"Collected {len(data)} records")

@cli.command()
@click.argument('filename')
def analyze(filename):
    """Basic analysis of collected data"""
    try:
        df = pd.read_csv(f'data/processed/{filename}')
        click.echo("\nData Summary:")
        click.echo(f"Total records: {len(df)}")
        click.echo("\nSample data:")
        click.echo(df.head())
    except Exception as e:
        click.echo(f"Error: {str(e)}")

if __name__ == '__main__':
    cli()