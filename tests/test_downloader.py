import pytest
from src.Downloader import RinexFTPDownloader


@pytest.mark.parametrize("test_input,expected", [([2019, 314, 'nybp', 'a', 'a'], 1),
                                                 ([2019, 314, 'nybp', 'a', 'b'], 2),
                                                 ([2019, 314, 'nybp', 'a', 'x'], 24),
                                                 pytest.param([2019, 314, 'nybp', 'd', 'a'], 2, marks=pytest.mark.xfail)])
def test_create_file_list(test_input, expected):
    year, day, station, start, end = test_input
    r = RinexFTPDownloader(year, day, station, start, end)
    r.create_file_list()
    assert len(r.file_list) == expected
