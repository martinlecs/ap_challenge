# AeroPoint RINEX Downloader

**AP Rinex Downloader** is a tool that aims to make downloading observation data from the [NOAA CORS](http://geodesy.noaa.gov/CORS/) network as painless as possible.

It allows you to specify the station and a time period to download logs from and automatically merges them into a single file.

Features:

- You can download and merge files going all the way back to 1994 to 2019 (within and across years).
- Automatically merges and time-windows files of different formats.
- Easy to install with a single command.

## Requirements

- Python 3.7.
- [TEQC](https://www.unavco.org/software/data-processing/teqc/teqc.html) binary placed in root directory of the project.
- [CRX2RNX](http://terras.gsi.go.jp/ja/crx2rnx.html) binary placed in root directory of the project.
- **NB: Make sure to `chmod 755` both binaries to set execution permissions!**

## Installation

If you're interested in setting up the complete dev environment, the project comes with Pipenv and a requirements.txt. Pick your favourite flavour of virtualenv/package manager and install the dependencies for the project. I prefer using [Pipenv](https://github.com/pypa/pipenv), however, the instructions below will assume that you are using standard Pip.

For Pip:

`$ pip install -r requirements.txt`

For Pipenv:

`$ pipenv install && pipenv shell`

If you're only interested in running the tool, just install the application as a Python package:

`$ pip install -e .`

**NB: Even if you've installed the full dev environment, you must also run the above command to install the tool!**

## Usage

Parameters:

- station_id: 4-character site (base) identifier. See [NOAA CORS](http://geodesy.noaa.gov/CORS/) for more information.
- start_timestamp: an ISO8601 (UTC) string of the format: `%Y-%m-%dT%H:%M:%SZ`
- end_timestamp: an ISO8601 (UTC) string of the format: `%Y-%m-%dT%H:%M:%SZ`

See [here](http://strftime.org/) for date formatting reference. See **Caveats** if you have an issue with the timestamp format.

Basic usage:

`$ grab_data [station_id] [start_timestamp] [end_timestamp]`

Example usage:

Download and merge observation files for station NYBP from 23:11:22UTC 14-09-2017 and 01:33:44UTC 15-09-2017:

`$ grab_data nybp 2017-09-14T23:11:22Z 2017-09-15T01:33:44Z`

Download and merge observation files for station P589 from 22:30:54UTC 31-12-2018 and 02:45:13UTC 01-01-2019:

`$ grab_data p589 2018-12-31T22:30:54Z 2019-01-01T02:45:13Z`

## Caveats

- In its current version, the binaries for teqc and Hatanaka decompressor must be placed the same directory as the python application. Future releases will allow the user to set the path to the binaries through the CLI.
- Complete end-to-end testing hasn't been implemented for all test cases yet, but covers the main cases.
- Only extensively tested on Mac OSX v10.14.6. However, code has loose coupling with OS structure so portability should not be an issue.
- Although it is possible to handle ISO8601 strings of different formats, I've chosen to constrain the timestamp inputs to exactly what was shown as an example in the [original specification](https://github.com/PropellerAero/aeropoint-programming-challenge) to make implementation easier for myself. However, this could easily be extended upon and made more flexible for the user.
- The output of this program does not match the exact example output in the project specification repository. The only difference between my output and the expected output are the comment headers. This could just be due to differing versions of TEQC producing slightly different outputs or there might be a flag that I'm not using that I should, however, aside from the comment headers, my output is identical to the expected example output.

## Design Decisions

**Figure 1. Basic program flow overview.**

![UML sequence diagram for program](https://imgur.com/4cSHJom)

- I stuck by the Single Responsibility Principle and created individual classes (Downloader, Merger) in an effort to separate my concerns. I then created a Runner class which takes in a Downloader and Merger as its args (Dependency Injection). In this current context, DI isn't strictly necessary but it does help clean up the code and abstract minor details away.

- **Decimation**: Observation files in the last 48 hours contain data sampled at rates of 1 second, 15 seconds, and 30 seconds whereas observation files older than 2 months or so only contain data that is sampled at a rate of every 30 seconds. When you merge an old file with a new file, the sample interval for the merged file is automatically set to 1 second. However, when you merge an old file with another old file, the default sample interval for the merged file is 30 seconds. At the moment, the program just returns whatever is set by default by TEQC, however, in order to maintain consistency with our output, it would be best to convert ALL files to a common sample interval. For example, to convert all files to 30 second sample intervals, we can pass the merged file into TEQC and run the following command `teqc -O.dec 30 input.obs > output.obs`.

- Observations files are saved to a temporary directory (generated by Python's in-built tempfile library) and removed automatically at the completion of the script. The assumption here is that the user only wants the final output file.

- The output file is saved to directory where the CLI is called by default, this is mainly done for convenience and ease of implementation. An improvement to this would be to have a flag in the CLI where the user can select the save path e.g. `--o /User/martin/desktop/`

- Although the tool can be run outside its directory (as long as its installed as a pip package), the TEQC and CRX2RNX binaries must be placed in the root directory of the project. A better implementation would be to allow users to set the path to the binaries themselves and have this information stored in a config file, and exported to the environment during run-time.

- I chose to leverage native the gunzip tool on OSX rather than using Python's inbuilt zipping library for a quicker implementation. In the future, should be replaced with in-built python library for portability.

- Implemented a rudimentary progress bar via the progress package to show give the user some system feedback; according to Sharp et. al 2019, providing the user with system feedback allows for a more pleasing experience.

- Although, I've mentioned above how important system feedback is, I've chosen to hide the TEQC output from the user. Often when you merge files together, sometimes there will be chunks of data of missing (which is normal) and TEQC will print warning messages that aren't very helpful. The sheer amount of output from TEQC is confusing and hard for a user to process. An alternative, human-readable message should be displayed in its place instead. Possibly offering a solution to the warnings.

- TEQC must receive files in a specific order, or it will fail to produce the desired output. We cannot just use wildcard expansions and pipe them all into TEQC, as this is not deterministic across systems and does not order files correctly. Files must be piped into to TEQC in order of the oldest to the latest files. For this reason, I've had to implement a filename sorting function to handle cases where, for example, `0010.19` is incorrectly ordered before `365.18`. Another example is where `315a.19` is incorrectly ordered before `3140.19`. This occurs because python's glob library lists files by alphabetical order by default (in most cases, not all the time).

## Future Improvements

- Prettier frontend with autocompletion/search for stations.
- Simpler format for timestamp inputs.
- More transparent progress indicators.
- Full portability across all platforms.
- User set paths to binaries (creation of a local config file to store user details e.g. .env or .yaml)
- Implement integration and end-to-end tests.
- Allow different output options including where to save intermediate files.

## Testing

If you have the installed the complete dev environment setup, you can run tests using the following command from the root of the project:

`$ python -m pytest tests/`

Unfortunately, due to time constraints, there isn't 100% code coverage (its on the TODO list!). However I have done my best to at least unit test the hotspots and main functions. A more complete (and varied) end-to-end test is definitely something I would like to implement in the future.

My methodology, for when I implement e-2-e testing, is to download a set of files, merge them and compare their meta information with some expected output using the `teqc +meta` command and the diff tool.

## References

Sharp, H, Preece, J, Rogers, Y 2019, Interaction Design – Beyond Human-Computer Interaction, John Wiley & Sons, Indianapolis.

---

License: [CC-BY](https://creativecommons.org/licenses/by/3.0/)
