from ftplib import FTP
import string
import os
from progress.bar import IncrementalBar
import tempfile
import subprocess
import shlex
import sys


class RinexFTPDownloader:
    """ Downloads RINEX files from FTP server and merges them into one file.

        Args:
            year: 4-digit year
            day: 3-digit day-of-year
            station: 4-character site (base) identifier
            hour_block_[start|end]: for 1 hour long (60 minute duration) files this is a letter
                                    a through x that corresponds to the start hour as shown below
                                    00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23
                                    a  b  c  d  e  f  g  h  i  j  k  l  m  n  o  p  q  r  s  t  u  v  w  x

    """

    def __init__(self, year: int, day: int, station: str, hour_block_start: str, hour_block_end: str):
        self.__year = year
        self.__day = day
        self.__station = station
        self.__start = hour_block_start
        self.__end = hour_block_end
        self.__file_list = None  # stores generated list of files to download from FTP server

    @property
    def file_list(self):
        return self.__file_list

    def create_file_list(self):
        """ Generate a list of files using initialised variables that will be downloaded from FTP

        """
        if ord(self.__start) > ord(self.__end):
            raise ValueError('Time range is invalid')

        # also check for or ord(self.__start) > ord('x') or ord(self.__end) > ord('x') much earlier on

        # We make use of in-built structures to efficiently generate all
        # alphabetical letters between hour_block_start and hour_block_end
        hour_range = string.ascii_lowercase[ord(
            self.__start)-97: ord(self.__end)-96]
        self.__file_list = ["{}{}{}.{}o.gz".format(
            self.__station, self.__day, h, self.__year % 100) for h in hour_range]

    def merge_files(self, directory: str):
        # ! Look into doing better error handling here
        """ Decompresses Rinex files in a directory and merges them into one output file

        Args:
            directory: Path of directory that contains the rinex files

        """
        subprocess.run(["gunzip", "-dr", directory])
        merge_command = os.path.join(
            directory, "{0}{1}*.{2}o > {0}{1}.{2}.obs".format(self.__station, self.__day, self.__year % 100))
        # Output file will be saved in the location where you called this script
        subprocess.run("./teqc {}".format(merge_command), shell=True)

    def grab_data(self):
        """ Driver function that downloads RINEX files from FTP server and merges them into one file.

        """
        with FTP("geodesy.noaa.gov") as ftp:
            try:
                ftp.login()
                ftp.cwd("/cors/rinex/{}/{}/{}".format(self.__year,
                                                      self.__day, self.__station))
                directory_files = ftp.nlst()

                with tempfile.TemporaryDirectory() as temp_dir:

                    full_day_log = "{}{}0.{}o.gz".format(
                        self.__station,  self.__day, self.__year % 100)

                    # Check if daily log in folder
                    if full_day_log in directory_files:
                        with IncrementalBar('Downloading file', max=1) as bar:
                            ftp.retrbinary('RETR {}'.format(full_day_log),
                                           open(os.path.join(temp_dir, full_day_log), 'wb').write)
                            bar.next()
                            bar.finish()
                    else:  # Otherwise download hourly logs
                        self.create_file_list()
                        with IncrementalBar('Downloading files', max=len(self.__file_list)) as bar:
                            for file in self.__file_list:
                                if file in directory_files:
                                    ftp.retrbinary('RETR {}'.format(file),
                                                   open(os.path.join(temp_dir, file), 'wb').write)
                                    bar.next()
                                else:
                                    print(
                                        "Could only find logs up to hour block {}".format(file))
                                    bar.finish()
                                    break
                    print("Merging files")
                    self.merge_files(temp_dir)
                    print("Process completed!")
            except Exception as e:
                print("Error during download from FTP:", e)


if __name__ == "__main__":
    r = RinexFTPDownloader(2019, 314, 'nybp', 'a', 'b')
    r.grab_data()
