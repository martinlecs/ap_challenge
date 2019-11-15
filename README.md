# AeroPoint RINEX Downloader

**AP Rinex Downloader** is a tool that aims to make downloading observation data from the [NOAA CORS](http://geodesy.noaa.gov/CORS/) network as painless as possible.

It allows you to specify the station and time period in which logs you want to download and automatically merges them into a single file.

Features:

- You can download and merge files going all the way back to 1994 to 2019 (within and across years).
- Automatically merges and time-windows files of different formats.
- Easy to install with a single command.

## Requirements

- Python 3.7.
- [TEQC](https://www.unavco.org/software/data-processing/teqc/teqc.html) binary placed in root directory of the project.
- [CRX2RNX](http://terras.gsi.go.jp/ja/crx2rnx.html) binary placed in root directory of the project.

## Installation

If you're interested in setting up the complete dev environment, the project comes with Pipenv and a requirements.txt. Pick your favourite flavour of virtualenv/package manager and install the dependencies for the project. I prefer using [Pipenv](https://github.com/pypa/pipenv), however, the instructions below will assume that you are using standard Pip.

For Pip:

`$ pip install -r requirements.txt`

For Pipenv:

`$ pipenv install && pipenv shell`

If you're only interested in running the tool, just install the application as a Python package:

`$ pip install -e .`

## Usage

Parameters:

- station_id: 4-character site (base) identifier. See [NOAA CORS](http://geodesy.noaa.gov/CORS/) for more information.
- start_timestamp: an ISO8601 (UTC) string of the format: %Y-%m-%dT%H:%M:%SZ
- end_timestamp: an ISO8601 (UTC) string of the format: %Y-%m-%dT%H:%M:%SZ

See [here](http://strftime.org/) for date formatting reference.

Basic usage:

`$ grab_data [station_id] [start_timestamp] [end_timestamp]`

Example usage:

Download and merge observation files for station NYBP from 23:11:22UTC 14-09-2017 and 01:33:44UTC 15-09-2017:

`$ grab_data nybp 2017-09-14T23:11:22Z 2017-09-15T01:33:44Z`

Download and merge observation files for station P589 from 22:30:54UTC 31-12-2018 and 02:45:13UTC 01-01-2019:

`$ grab_data p589 2018-12-31T22:30:54Z 2019-01-01T02:45:13Z`

## Caveats

- In its current version, the binaries for teqc and Hatanaka decompressor must be placed the same directory as the python application. Future releases will allow the user to set the path to the binaries through the CLI.
- Complete end-to-end testing hasn't been implemented for all test cases yet, but covers the majority.
- Only extensively tested on Mac OSX v10.14.6. However, code has loose coupling with OS structure so portability should not be an issue.
- Although it is possible (and easy) to handle ISO8601 strings of different formats, I've chosen to constrain the timestamp inputs to exactly what was shown as an example in the [original specification](https://github.com/PropellerAero/aeropoint-programming-challenge) to make implementation easier for myself. However, this could easily be extended upon and made more flexible for the user.

## Future Improvements

- Prettier frontend with autocompletion/search for stations.
- Simpler format for timestamp inputs.
- More transparent progress indicators.
- Full portability across all platforms.
- User set paths to binaries.
- Full integration and end-to-end tests.

## Testing

If you have the installed the complete dev environment setup, you can run tests using the following command from the root of the project:

`$ python -m pytest tests/`
