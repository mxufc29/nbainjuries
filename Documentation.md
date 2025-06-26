# API Documentation

## nbainjuries/injury.py

### `get_reportdata(timestamp: datetime, local: bool = False, localdir: str | PathLike = None, return_df: bool = False, **kwargs)`

Extracts the injury data from the injury report at a specific datetime.

- `timestamp`: date/time of the report for retrieval in the form of a `datetime` object (all times ET). Reports are generally saved hourly, at the 30 minute mark of the hour.
  - E.g. `datetime(year=2023, month=5, day=2, hour=17, minute=30)`for report at 5/2/2023 5:30pm ET
- `local`: if the injury report source file from which to extract is saved on local drive; default `False` (live retrieve from URL directly)
- `localdir`: local directory path of data source, required if `local=True`
- `return_df`: return output data as dataframe, default `False` (return as json format)
- `kwargs`: any user-specified HTML headers to override default headers for the HTML request

### `check_reportvalid(timestamp: datetime, **kwargs) -> bool`

Check the data availability of the injury report (the URL source) at a specific datetime.

- `timestamp`: date and time of the report, in the form of a `datetime` object
- `kwargs`: any user-specified HTML headers to override default headers for the HTML request

### `gen_url(timestamp: datetime) -> str`

Returns the URL link of the injury report at a specific date/time.

- `timestamp`: date and time of the report, in the form of a `datetime` object

## nbainjuries/injury_asy.py

This module contains asynchronous methods which are compatible with concurrency/`asyncio`, for batch processing hundreds of reports or more during one run. The API and methods `get_reportdata` and `check_reportvalid`in this module are fully identical to those in nbainjuries/injury.py, except for an additional `session (ClientSession)` parameter for session management. Refer to above API documentation of injury.py for details on other parameters.

**`get_reportdata(timestamp: datetime, <mark>session:</mark> ClientSession = None, local: bool = False, localdir: str | PathLike = None, return_df: bool = False, **kwargs)`**

**`check_reportvalid(timestamp: datetime, <mark>session:</mark> ClientSession = None, **kwargs)-> bool`**
