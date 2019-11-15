from datetime import datetime
import filecmp
from glob import glob
import os
import pytest
import subprocess
import tempfile
from src.Downloader import RinexDownloader
from src.Merger import RinexMerger


@pytest.mark.parametrize('test_input,expected', [
    (['nybp', '2017-12-31T23:11:22Z', '2018-01-01T01:33:44Z'],
     ['nybp3650.17o', 'nybp0010.18o']),
    (['nybp', '2017-09-14T23:11:22Z', '2017-09-15T01:33:44Z'],
     ['nybp2580.17o', 'nybp2570.17o']),
])
def test_decompress_files(test_input, expected):
    with tempfile.TemporaryDirectory() as temp_dir:
        station, start, end = test_input
        start_date = datetime.strptime(start, '%Y-%m-%dT%H:%M:%SZ')
        end_date = datetime.strptime(end, '%Y-%m-%dT%H:%M:%SZ')
        r = RinexDownloader(station, start_date, end_date, temp_dir)
        m = RinexMerger(station, start_date, end_date, temp_dir)
        r.download()
        m.decompress_files()
        assert set(glob('{}/{}'.format(temp_dir, '*.??o')
                        )) == set(['{}/{}'.format(temp_dir, i) for i in expected])


# The following code was supposed to do a diff between meta files.
# However since meta files change depending on what time you use the teqc tool
# You will always end up failing the diff. This can be fixed if you compare certain lines
# or remove differing lines. Output file will save to root directory of project by default as well
# which is not intended behaviour for testing. This behaviour will need to be modified in the future.

# @pytest.mark.parametrize('test_input,expected', [
#     (['nybp', '2017-12-31T23:11:22Z', '2018-01-01T01:33:44Z'],
#      'across_years.txt'),
#     (['nybp', '2017-09-14T23:11:22Z', '2017-09-15T01:33:44Z'],
#      'old_to_old.txt'),
# ])
# def test_merge_files(test_input, expected, tmpdir):
#     with tempfile.TemporaryDirectory() as temp_dir:
#         delete_files_in_directory(temp_dir)
#         station, start, end = test_input
#         start_date = datetime.strptime(start, '%Y-%m-%dT%H:%M:%SZ')
#         end_date = datetime.strptime(end, '%Y-%m-%dT%H:%M:%SZ')
#         r = RinexDownloader(station, start_date, end_date, temp_dir)
#         m = RinexMerger(station, start_date, end_date, temp_dir)
#         r.download()
#         m.decompress_files()
#         m.merge()
#         subprocess.run(['./teqc +meta {0}/{1}.obs > {0}/test_compare.txt'.format(temp_dir,
#                                                                                  station)], capture_output=True, shell=True)
#         assert filecmp.cmp(os.path.join(os.path.dirname(os.path.realpath(
#             __file__)), 'diff_files', expected), '{}/test_compare.txt'.format(temp_dir))
