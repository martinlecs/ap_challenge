"""A one line summary of the module or program, terminated by a period.

Leave one blank line.  The rest of this docstring should contain an
overall description of the module or program.  Optionally, it may also
contain a brief description of exported classes and functions and/or usage
examples.

  Typical usage example:

  foo = RinexFTPDownloader(station, start_time, end_time)
  foo.run()
"""
import subprocess
from glob import glob
from datetime import datetime
from typing import List

START_TIMESTAMP = '{}{:02d}{:02d}{:02d}0000'
END_TIMESTAMP = '{}{:02d}{:02d}{:02d}5959'


class RinexMerger:
    """ Merges multiple RINEX files together into one file. 

        Args:
            station: 4-character site (base) identifier
            start_time: datetime object
            end_time: datetime object
            directory: path to directory containing RINEX files (default: current directory)
    """

    def __init__(self, station: str, start_time: datetime, end_time: datetime, directory: str = ''):
        self.__station = station.lower()
        self.__start = self.deconstruct_datetime(start_time)
        self.__end = self.deconstruct_datetime(end_time)
        self.__directory = directory

    def deconstruct_datetime(self, date: datetime) -> List[int]:
        """ Extracts information from a datetime object

            Args:
                date: a datetime object

            Returns: A list containing the year, month, day and hour extracted from the datetime object
         """
        year, month, day, hour, _, _, _, _, _ = date.timetuple()
        return [year, month, day, hour]

    def __decompress_files(self):
        """ Decompresses all downloaded Rinex files inside a specified directory. """
        if glob('{}/*'.format(self.__directory)):
            subprocess.run(["gunzip", "-dr", self.__directory])
            # convert Hatanaka compressed RINEX to standard RINEX
            for f in glob('{}/*.??d'.format(self.__directory)):
                subprocess.run(['./CRX2RNX', f])
        else:
            raise RuntimeError(
                'Could not decompress. No files were downloaded from FTP server.')

    def merge(self):
        """ Merges RINEX files and extracts required time window from merged file. """
        self.__decompress_files()
        # ! Error handling, what if none of these are installed?
        daily_logs = glob('{}/*0.??o'.format(self.__directory)) + \
            glob('{}/*.??d'.format(self.__directory))
        try:
            # Merge and extract the time window from the Rinex files if using daily logs
            if daily_logs:
                start_timestamp = START_TIMESTAMP.format(*self.__start)
                end_timestamp = END_TIMESTAMP.format(*self.__end)
                # * files must be entered in their chronological order. Glob does this for us by default unlike shell wildcard expansions
                files = ' '.join(glob('{}/*.??o'.format(self.__directory)))
                print(files)
                subprocess.run(
                    ['./teqc -O.s M -st {0} -e {1} {2} > {3}.obs'.format(start_timestamp, end_timestamp, files, self.__station)], capture_output=True, shell=True)
            else:
                # * Merge files as is if there are no daily logs present
                subprocess.run(
                    "./teqc -O.s M {0}/{1}*.??o > {1}.obs".format(self.__directory, self.__station), capture_output=True, shell=True)
        except:
            raise RuntimeError('Error occured while trying to merge files.')
