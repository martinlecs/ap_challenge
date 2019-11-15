"""Class responsible for running the RinexDownloader and RinexMerger

The most important feature about this class is that it requires the user to pass
in the RinexDownloader and RinexMerger as arguments into the constructor. This is done to 
abstract away the initialisation detaiils of the injected dependencies.

  Typical usage example:

  foo = RinexRunner(station, start_time, end_time)
  foo.run()
"""
import tempfile
from datetime import datetime
from src.Downloader import RinexDownloader
from src.Merger import RinexMerger


class RinexRunner:
    """ Initialises and runs the RinexDownloader and Rinex Merger

        Args:
            station: 4-character site (base) identifier
            start_date: a datetime object
            end_date: a datetime object
            downloader: reference to RinexDownloader (uninitialised)
            merger: reference to RinexMerger (uninitialised)
     """

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
                self.__station, self.__start_date, self.__end_date, temp_dir)
            merger = self.__merger(
                self.__station, self.__start_date, self.__end_date, temp_dir)
            downloader.download()
            print("Merging files...")
            merger.merge()
            print('All done!')
