from ftplib import FTP
from typing import List
import string
import os

# can construct most of this ourselves: ftp://www.ngs.noaa.gov/cors/rinex/2018/314/nybp/

TEMP = os.environ['TMPDIR']  # osx only


def filelist_constructor(format_string: str, start: str, end: str) -> List[str]:
    letter_range = string.ascii_lowercase[ord(start)-97: ord(end)-96]
    return letter_range


def grab_data(year: int, day: int, station: str, hour_block_start: str, hour_block_end) -> bool:
    """ Downloads RINEX files from FTP server and merges them into one file.

    Args:
        year: 4-digit year
        day: 3-digit day-of-year
        station: 4-character site (base) identifier
        hour_block_[start|end]: for 1 hour long (60 minute duration) files this is a letter
                                a through x that corresponds to the start hour as shown below
                                00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23
                                a  b  c  d  e  f  g  h  i  j  k  l  m  n  o  p  q  r  s  t  u  v  w  x

    Returns:
        True if download and merge succeeds. False otherwise.

    """
    with FTP("geodesy.noaa.gov") as ftp:
        try:
            ftp.login()
            ftp.cwd("/cors/rinex/{}/{}/{}".format(year, day, station))
            directory_files = ftp.nlst()
            # generate letter range
            # ord('a') - 97 = 0
            hour_range = string.ascii_lowercase[ord(
                hour_block_start)-97: ord(hour_block_end)-96]
            # attempt to download files from a-x. write to a temp folder
            for h in hour_range:
                filename = '{}{}{}.{}o.gz'.format(station, day, h, year % 100)
                if filename in directory_files:
                    print("find a file!")
                    ftp.retrbinary('RETR {}.format(filename), open(filename, 'wb').write)
                else:
                    # if no hourly logs, just download full day logs
                    print("downloading full day log")
            ftp.dir()

        except Exception as e:
            print("Error during download from FTP:", e)
            return False
    return True

    # do 1 pass for file existence check
    # do another pass for file download
    # if fail file existence, attempt to download full day logs


if __name__ == "__main__":
    grab_data(2019, 314, 'nybp', 'a', 'x')
