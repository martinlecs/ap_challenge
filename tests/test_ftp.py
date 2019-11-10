import pytest
from ftplib import FTP


@pytest.fixture(scope="module")
def ftp_connection():
    with FTP("geodesy.noaa.gov") as ftp:
        ftp.login()
        yield ftp


def test_basic_connection():
    with FTP("geodesy.noaa.gov") as ftp:
        assert ftp.login() == "230 Login successful."


def test_backup_connection():
    with FTP("alt.ngs.noaa.gov") as ftp:
        assert ftp.login() == "230 Login successful."


def test_directory_change(ftp_connection):
    assert ftp_connection.cwd(
        "/cors/rinex/2019/") == "250 Directory successfully changed."


def test_bad_directory_change(ftp_connection):
    with pytest.raises(Exception, match=r"^550 .*"):
        ftp_connection.cwd("/cors/rinex/201999/")
