"""A one line summary of the module or program, terminated by a period.

Leave one blank line.  The rest of this docstring should contain an
overall description of the module or program.  Optionally, it may also
contain a brief description of exported classes and functions and/or usage
examples.

  Typical usage example:

  foo = RinexRunner(station, start_time, end_time)
  foo.run()
"""
import tempfile
from datetime import datetime
from src.Downloader import RinexDownloader
from src.Merger import RinexMerger


class RinexRunner:

    def __init__(self, station: str, start_date: datetime, end_date: datetime, downloader: RinexDownloader, merger: RinexMerger):
        self.__station = station
        self.__start_date = start_date
        self.__end_date = end_date
        self.__downloader = downloader
        self.__merger = merger

    def run(self):
        """ Downloads multiple RINEX files from FTP and merges them into a single file. """
        with tempfile.TemporaryDirectory() as temp_dir:
            downloader = self.__downloader(
                self.__station, self.__start_date, self.__end_date, 'output')
            merger = self.__merger(
                self.__station, self.__start_date, self.__end_date, 'output')
            downloader.download()
            print("Merging files...")
            merger.merge()
            print('All done!')
