"""A one line summary of the module or program, terminated by a period.

Leave one blank line.  The rest of this docstring should contain an
overall description of the module or program.  Optionally, it may also
contain a brief description of exported classes and functions and/or usage
examples.

  Typical usage example:

  foo = RinexFTPDownloader(station, start_time, end_time)
  foo.run()
"""
from ftplib import FTP, error_perm
from socket import gaierror
import string
import os
from progress.bar import IncrementalBar
import subprocess
from glob import glob
from datetime import datetime
from typing import List

MAIN_SERVER = 'geodesy.noaa.gov'
ALT_SERVER = 'alt.ngs.noaa.gov'
DIRECTORY_PATH = '/cors/rinex/{}/{:03d}/{}'


class RinexDownloader:
    """ Downloads RINEX files from the FTP server.

        Args:
            station: 4-character site (base) identifier
            start_time: datetime object
            end_time: datetime object
    """

    def __init__(self, station: str, start_time: datetime, end_time: datetime, directory: str = ''):
        self.__station = station.lower()
        self.__start = start_time
        self.__end = end_time
        self.__directory = directory
        self.__ftp = None

    def __set_ftp(self):
        """ Create new FTP object. """
        try:
            self.__ftp = FTP(MAIN_SERVER)
        except gaierror:
            try:
                self.__ftp = FTP(ALT_SERVER)  # try alternate server
            except gaierror:
                raise RuntimeError(
                    'Unable to connect to FTP. Please check your connection.')

    def __ftp_connect(self):
        """ Open up a connection with the FTP server. """
        self.__set_ftp()
        try:
            # Check if connection is currently alive
            self.__ftp.voidcmd('NOOP')
        except error_perm:
            try:
                self.__ftp.login()
            except:
                raise RuntimeError(
                    'Unable to connect to FTP. NOAA servers are down.')

    def deconstruct_datetime(self, date: datetime) -> List[int]:
        """ Extracts information from a datetime object

        Args:
                date: a datetime object

        Returns: A list containing the year (int), day-of-year (int) and hour (int) extracted from the datetime object
         """
        year, month, day, hour, _, _, _, yday, _ = date.timetuple()
        return [year, yday, hour]

    def is_valid_station_code(self):
        """ Checks if station code is valid (and accessible) on the FTP server. """
        if not self.__station:
            return False
        self.__ftp_connect()
        self.__ftp.cwd('/cors/station_log')
        station_results = []
        self.__ftp.retrlines('NLST *{}*'.format(self.__station),
                             station_results.append)
        return bool(station_results)

    def get_days_left_in_year(self, date: datetime) -> int:
        """ Get number of days left in the year given a specific date

            Args:
                date: datetime object

            Returns: number of days left in the year

         """
        last_day_of_year = datetime.strptime(
            '02/01/{}'.format(date.year+1), '%d/%m/%Y')
        delta = last_day_of_year - date
        return delta.days

    def get_days_in_year(self, year: int) -> int:
        """ Gets the total number of days in a given year. 

            Args:
                year: 4-digit year

            Returns: The total number of days in a year

        """
        date_format = '%d/%m/%Y'
        start = datetime.strptime('01/01/{}'.format(year), date_format)
        end = datetime.strptime('31/12/{}'.format(year), date_format)
        return (end - start).days + 1

    def generate_file_names(self, year: int, yday: int, start: str, end: str) -> List[str]:
        """ Generate a list of files using initialised variables that will be downloaded from FTP.

        Args:
            year: 4-digit year
            yday: day-of-year
            [start|end]: a letter 'a' through 'x' that corresponds to the start hour as shown below
                    00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23
                    a  b  c  d  e  f  g  h  i  j  k  l  m  n  o  p  q  r  s  t  u  v  w  x

        Returns: List of file names
        """
        if type(year) is not int or len(str(year)) != 4:
            raise ValueError('Year must be a 4-digit integer.')
        if year < 1994 or year > datetime.now().year:
            raise ValueError(
                'Year must be between 1994 and {}.'.format(datetime.now().year))
        if type(yday) is not int:
            raise ValueError('Day-of-year must be a 3-digit integer.')
        if yday < 0 or yday > 366:
            raise ValueError('Day-of-year must be between 0 and 366')
        if type(start) is not str or type(end) is not str:
            raise ValueError('Start or end hour block must be a string.')
        if not start or not end:
            raise ValueError('Start or end hour block is invalid.')
        elif len(start) > 1 or len(end) > 1:
            raise ValueError('Start or end hour must be only one character.')
        elif ord(start) > ord(end):
            raise ValueError(
                'Start hour block cannot be later than end hour block.')
        elif ord(start) > ord('x') or ord(end) > ord('x'):
            raise ValueError("Start or end hour block cannot exceed 'x'.")

        # * We make use of in-built structures to efficiently generate all alphabetical letters between hour_block_start and hour_block_end
        hour_range = string.ascii_lowercase[ord(start)-97: ord(end)-96]
        return ["{}{:03d}{}.{}o.gz".format(self.__station, yday, h, year % 100) for h in hour_range]

    def create_file_list(self, directory_listing: str, current_day: int, start_year: int, start_day: int, start_hour: str, end_day: int, end_hour: str) -> List[str]:
        """ Create list of files to download from FTP.

            Args:
                directory_listing: ftp directory where files will be downloaded from
                current_day: day-of-year
                start_year: 4-digit year
                start_day: day-of-year
                start_hour: hour in 24-hour format
                end_day: day-of-year
                end_hour: hour in 24-hour format

            Returns: A list of file names.

         """
        file_list = []
        start_hour = chr(start_hour+97)
        end_hour = chr(end_hour+97)

        standard_day_log = "{}{:03d}0.{}o.gz".format(
            self.__station, current_day, start_year % 100)
        # older full day logs look different and are compressed differently
        hatanaka_day_log = "{}{:03d}0.{}d.Z".format(
            self.__station, current_day, start_year % 100)

        if standard_day_log in directory_listing:
            # download full day log in available
            file_list.append(standard_day_log)
        elif hatanaka_day_log in directory_listing:
            file_list.append(hatanaka_day_log)
        else:
            # generate all files to download using their hour block code
            if current_day == start_day:
                # on start day, get all files from start_hour to x
                file_list = self.generate_file_names(
                    start_year, start_day, start_hour, 'x')
            elif current_day == end_day:
                # on end day, get all files up to end_hour
                file_list = self.generate_file_names(
                    start_year, end_day, 'a', end_hour)
            else:
                # on in-between day, get all files
                file_list = self.generate_file_names(
                    start_year, current_day, 'a', 'x')
        return file_list

    def download(self):
        """ Download files within a specific time window from the FTP server. """
        self.__ftp_connect()
        with self.__ftp as ftp:
            try:
                if not self.is_valid_station_code():
                    raise ValueError('Station code is not valid!')

                start_year, start_day, start_hour = self.deconstruct_datetime(
                    self.__start)
                end_year, end_day, end_hour = self.deconstruct_datetime(
                    self.__end)

                day_count = 0
                current_day = start_day
                days_between_dates = (
                    self.__end.date() - self.__start.date()).days + 1
                days_left_in_year = self.get_days_left_in_year(self.__start)

                # go through directories and download all relevant files
                while start_year <= end_year:
                    while day_count < days_between_dates and day_count < days_left_in_year:

                        ftp.cwd(DIRECTORY_PATH.format(
                            start_year, current_day, self.__station))
                        directory_listing = ftp.nlst()

                        # generate files to download in current directory
                        file_list = self.create_file_list(
                            directory_listing, current_day, start_year, start_day, start_hour, end_day, end_hour)

                        # Download files from FTP and store them into specified directory(by default, will save in current folder)
                        with IncrementalBar('Downloading files', max=len(file_list)) as bar:
                            for file in file_list:
                                if file in directory_listing:
                                    ftp.retrbinary('RETR {}'.format(file),
                                                   open(os.path.join(self.__directory, file), 'wb').write)
                                    bar.next()
                                else:
                                    bar.finish()
                                    print(
                                        "Warning: your end timestamp exceeds the logs that are currently available on the FTP server.")
                                    break

                        current_day += 1
                        day_count += 1

                    start_year += 1
                    current_day = 1
                    days_left_in_year = self.get_days_in_year(start_year)

            except Exception as e:
                raise e
