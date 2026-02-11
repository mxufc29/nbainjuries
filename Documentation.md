# API Documentation

## nbainjuries/injury.py

###
`get_reportdata(timestamp: datetime, local: bool = False, localdir: str | PathLike = None, return_df: bool = False, **kwargs)`

Extracts the injury data from the injury report at a specific datetime.

- `timestamp`: date/time of the report for retrieval in `datetime` form (all times ET). Reports are generally
  timestamped hourly, at 30 minute increments of the hour.
    - E.g. `datetime(year=2023, month=5, day=2, hour=17, minute=30)`for report at 5/2/2023 5:30pm ET
- `local`: if the source file from which to extract is saved on local drive; default `False` (live retrieve from URL)
- `localdir`: local directory path of data source, required if `local=True`
- `return_df`: return output data as dataframe, default `False` (return as json)
- `kwargs`: any custom HTML headers to override default headers for HTML request

### `check_reportvalid(timestamp: datetime, **kwargs) -> bool`

Check the data availability of the injury report (url) at a specific datetime.

- `timestamp`: date and time of the report, in `datetime` form
- `kwargs`: any user-specified HTML headers to override default headers for the HTML request

## InjuryScraper class

Retrieves the table of all injured players by scraping data from https://www.cbssports.com/nba/injuries/
as DataFrame table.

```
scraper = injury.InjuryScraper()
df = scraper.get_data()
```

## nbainjuries/injury_asy.py

`injury_asy` contains asynchronous methods which are compatible with concurrency/`asyncio`, for batch processing
hundreds of reports or more during one run. The API and methods `get_reportdata` and `check_reportvalid`in this module
are fully identical to those in **nbainjuries/injury.py**, except for additional `session (ClientSession)` parameter for
session management. Refer to above API documentation of injury.py for details on other parameters.

**
`get_reportdata(timestamp: datetime, session: ClientSession = None, local: bool = False, localdir: str | PathLike = None, return_df: bool = False, **kwargs)`
**

**`check_reportvalid(timestamp: datetime, session: ClientSession = None, **kwargs)-> bool`**
