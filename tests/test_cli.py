from datetime import datetime
import pytest
from src.cli import cli

from click.testing import CliRunner


@pytest.mark.parametrize('test_input', [
    (['nybp', '2017-12-31T23:11:22Z', '2018-01-01T01:33:44Z']),
    (['nybp', '2017-09-14T23:11:22Z', '2017-09-15T01:33:44Z']),

])
def test_date_inputs(test_input):
    runner = CliRunner()
    result = runner.invoke(cli, test_input)
    assert result.exit_code == 0


@pytest.mark.parametrize('test_input', [
    pytest.param(['nybp', '2020-09-14T23:11:22Z',
                  '2017-09-15T01:33:44Z'], marks=pytest.mark.xfail),
    pytest.param(['nybp', '2017-09-14T23:11:22Z',
                  '2020-09-15T01:33:44Z'], marks=pytest.mark.xfail),
    pytest.param(['asdsadsada', '2017-09-14T23:11:22Z',
                  '2017-09-15T01:33:44Z'], marks=pytest.mark.xfail),
    pytest.param(['p589', '',
                  '2017-09-15T01:33:44Z'], marks=pytest.mark.xfail),
    pytest.param(['p589', '2017-09-15T01:33:44Z',
                  ''], marks=pytest.mark.xfail),
])
def test_date_inputs_fail(test_input):
    runner = CliRunner()
    with pytest.raises(ValueError):
        result = runner.invoke(cli, test_input)
