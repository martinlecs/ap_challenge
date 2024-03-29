import click
from datetime import datetime
from typing import List
import string
from src.Runner import RinexRunner
from src.Downloader import RinexDownloader
from src.Merger import RinexMerger


@click.command()
@click.argument('station', type=str)
@click.argument('start_date', type=click.DateTime(formats=['%Y-%m-%dT%H:%M:%SZ']))
@click.argument('end_date', type=click.DateTime(formats=['%Y-%m-%dT%H:%M:%SZ']))
def cli(station: str, start_date: datetime, end_date: datetime):
    """ Downloads RINEX files from FTP server and merges them into one file 

        Args:
            station: 4-character site (base) identifier
            start_date: datetime object
            end_date: datetime object
    """
    try:
        if start_date > end_date:
            raise ValueError('Start date is past end date')
        if start_date > datetime.now() or end_date > datetime.now():
            raise ValueError(
                'FTP does not have log files that extend all the way to your end date yet.')
        if start_date.year < 1994 or end_date.year < 1994:
            raise ValueError('Date is too early')

        runner = RinexRunner(station, start_date, end_date,
                             RinexDownloader, RinexMerger)
        runner.run()

    except Exception as e:
        print("Error:", e)
