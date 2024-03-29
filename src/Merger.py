"""Class responsible for decompressing and merging RINEX files.

Decompresses Gzipped or Hatanaka compressed files.
Merges files using TEQC with specified time-window and outputs file
to root directory of project.

  Typical usage example:

  foo = RinexMerger(station, start_time, end_time, directory)
  foo.merge()
"""
import os
import subprocess
from glob import glob
from datetime import datetime
from typing import List

START_TIMESTAMP = '{}{:02d}{:02d}{:02d}0000'
END_TIMESTAMP = '{}{:02d}{:02d}{:02d}5959'
ROOT_DIR = os.path.join(os.path.dirname(
    os.path.dirname(os.path.realpath(__file__))))


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

            Returns: 
                A list containing the year, month, day and hour extracted from the datetime object
         """
        year, month, day, hour, _, _, _, _, _ = date.timetuple()
        return [year, month, day, hour]

    def __file_sorter(self, filename: str) -> int:
        """ Sorts file name by their looking at their day-of-year and hour block code 

            File names are of the form: /file/path/ssssdddh.YYo
            We focus on using dddh and YY as our sorting keys.

            We extract the year from YYo to use as our first key.

            In order to sort all ddd0 before ddd[a-x], we split the 4-letter string into
            two components and add them together to get our second key.

            E.g. 
            for 3140, we split into 314 + 0 = 314
            for 314a, we split int 314 + ord(a) = 314 + 97

            Args:
                filename: the filename in format /file/path/ssssdddh.YYo

            Returns: 
                Return a tuple (YY, ddd + h) that we want the sorting function to sort on 
        """
        filename = filename.split('/')[-1]
        year = int(filename[-3:-1])  # extracts YY from ssssdddh.YYo
        day_info = filename[4:8]  # extracts dddh from ssssdddh.YYo
        day_of_year = int(day_info[:3])  # ddd
        hour_block = day_info[-1]    # h
        if hour_block.isdigit():
            return (year, day_of_year)
        return (year, day_of_year + ord(hour_block))

    def decompress_files(self):
        """ Decompresses all downloaded Rinex files inside a specified directory. """
        crx2rnx_path = os.path.join(ROOT_DIR, 'CRX2RNX')
        if not os.path.isfile(crx2rnx_path):
            raise OSError('Cannot find CRX2RNX binary in project directory!')

        if glob('{}/*'.format(self.__directory)):
            subprocess.run(["gunzip", "-dr", self.__directory])
            # convert Hatanaka compressed RINEX to standard RINEX
            for f in glob('{}/*.??d'.format(self.__directory)):
                subprocess.run([crx2rnx_path, f])
        else:
            raise RuntimeError(
                'Could not decompress. No files were downloaded from FTP server.')

    def merge(self):
        """ Merges RINEX files and extracts required time window from merged file. """
        self.decompress_files()
        teqc_path = os.path.join(ROOT_DIR, 'teqc')
        if not os.path.isfile(teqc_path):
            raise OSError('Cannot find TEQC binary in project directory!')

        # currently cannot tell if there are daily logs or not
        daily_logs = glob('{}/*0.??o'.format(self.__directory)) + \
            glob('{}/*.??d'.format(self.__directory))
        try:
            # Merge and extract the time window from the Rinex files if using daily logs
            if daily_logs:
                start_timestamp = START_TIMESTAMP.format(*self.__start)
                end_timestamp = END_TIMESTAMP.format(*self.__end)
                # files must be entered into TEQC in (a specific) chronological order or it will fail
                # hence we must sort them
                day_logs_uncompressed = glob(
                    '{}/*0.??o'.format(self.__directory))
                hourly_logs_uncompressed = glob(
                    '{}/*[a-z].??o'.format(self.__directory))
                files = sorted(day_logs_uncompressed, key=self.__file_sorter) + \
                    sorted(hourly_logs_uncompressed, key=self.__file_sorter)
                subprocess.run(
                    ['{0} -O.s M -st {1} -e {2} {3} > {4}.obs'.format(teqc_path, start_timestamp, end_timestamp, ' '.join(files), self.__station)], capture_output=True, shell=True)
            else:
                # Merge files as is if there are no daily logs present
                subprocess.run(
                    "{0} -O.s M {1}/*.??o > {2}.obs".format(teqc_path, self.__directory, self.__station), capture_output=True, shell=True)
        except Exception as e:
            print(e)
            # raise RuntimeError('Error occurred while trying to merge files.')
