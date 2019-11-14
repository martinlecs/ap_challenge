import pytest
from datetime import datetime
from src.Downloader import RinexDownloader


@pytest.mark.parametrize('test_input,expected', [
    (['nybp', datetime.now(), datetime.now()], True),
    (['p589', datetime.now(), datetime.now()], True),
    (['NYBP', datetime.now(), datetime.now()], True),    # uppercase
    (['nyas!', datetime.now(), datetime.now()], False),  # Invalid case
    (['!@#$', datetime.now(), datetime.now()], False),   # Invalid case
    (['', datetime.now(), datetime.now()], False)        # Invalid case
])
def test_valid_station_code(test_input, expected):
    """ Tests if user inputted station code is valid. """
    station, start_date, end_date = test_input
    r = RinexDownloader(station, start_date, end_date)
    assert r.is_valid_station_code() == expected


@pytest.mark.parametrize('test_input,expected', [
    ([2019, 314, 'a', 'a'], 1),
    ([2019, 314, 'a', 'g'], 7),
    ([2019, 314, 'a', 'x'], 24),
])
def test_file_name_generation(test_input, expected):
    r = RinexDownloader('nybp', datetime.now(), datetime.now())
    year, yday, start, end = test_input
    assert len(r.generate_file_names(year, yday, start, end)) == expected


@pytest.mark.parametrize('test_input', [
    # Invalid year exceptions
    ([201, 314, 'a', 'x', r'.*4-digit integer.*']),
    ([2020, 314, 'a', 'x', r'.*must be between 1994 and.*']),
    # Invalid day-of-year exceptions
    ([2019, 367, 'a', 'x', r'.*between 0 and 366.*']),
    ([2019, -1, 'a', 'x', r'.*between 0 and 366.*']),
    ([2019, '314', 'a', 'x', r'.*must be a 3-digit.*']),
    # Invalid start and end hour block exceptions
    ([2019, 314, 12, 15, r'.*must be a string.*']),
    ([2019, 314, 'a', 15, r'.*must be a string.*']),
    ([2019, 314, 12, 'x', r'.*must be a string.*']),
    ([2019, 314, '', '', r'.*is invalid.*']),
    ([2019, 314, 'a', '', r'.*is invalid.*']),
    ([2019, 314, '', 'x', r'.*is invalid.*']),
    ([2019, 314, 'abc', 'cde', r'.*must be only one character.*']),
    ([2019, 314, 'a', 'cde', r'.*must be only one character.*']),
    ([2019, 314, 'abc', 'e', r'.*must be only one character.*']),
    ([2019, 314, 'a', 'z', r'.*cannot exceed \'x\'.*']),
    ([2019, 314, 'x', 'a', r'.*cannot be later.*']),
])
def test_file_name_exceptions(test_input):
    r = RinexDownloader('nybp', datetime.now(), datetime.now())
    year, yday, start, end, error_message = test_input
    with pytest.raises(ValueError, match=error_message):
        r.generate_file_names(year, yday, start, end)


@pytest.mark.parametrize('test_input,expected', [
    ('2017-09-14T23:11:22Z', [2017, 257, 23]),
    ('2017-09-15T01:33:44Z', [2017, 258, 1]),
    ('2019-11-11T00:15:22Z', [2019, 315, 0]),
])
def test_deconstruct_time(test_input, expected):
    d = datetime.strptime(test_input, '%Y-%m-%dT%H:%M:%SZ')
    r = RinexDownloader('nybp', datetime.now(), datetime.now(), 'output')
    assert r.deconstruct_datetime(d) == expected


@pytest.mark.parametrize('test_input,expected', [
    ('2019-12-31T00:15:22Z', 1),
    ('2019-12-30T00:15:22Z', 2),
    ('2019-01-01T00:15:22Z', 365),
    ('2020-01-01T00:15:22Z', 366)
])
def test_days_left_in_year(test_input, expected):
    d = datetime.strptime(test_input, '%Y-%m-%dT%H:%M:%SZ')
    r = RinexDownloader('nybp', datetime.now(), datetime.now(), 'output')
    assert r.get_days_left_in_year(d) == expected


def test_run():
    pass
