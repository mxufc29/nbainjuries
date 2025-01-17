# Injury.py

Created by Michael Xu as an additional feature to the swar/nba_api library

---

## //path

Package to parse and extract data on player injuries and statuses from the NBA’s official injury reports.

The NBA’s official guidelines on injury tracking and reporting for teams state that:

- Teams must report information concerning player injuries, illnesses, and rest for all NBA games.

- By 5 p.m. local time on the day before a game (other than the second day of a back-to-back), teams must designate a participation status and identify a specific injury, illness, or potential instance of a healthy player resting for any player whose participation in the game may be affected by such injury, illness or rest.

- For the second game of a back-to-back, teams must report the above information by 1 p.m. local time on the day of the game.

The data submitted are stored as pdf reports on the NBA’s server, organized in hourly intervals (at each :30 minute mark) across each day of the regular season and postseason. For example, for a particular day such as mm/dd/yyyy, the first report is timestamped mm/dd/yyyy 12:30am, and the last report is timestamped mm/dd/yyyy 11:30 pm – a total of 24 reports.

Data is only available for the 2021-2022 NBA season and after. Among these seasons, data is not available for any preseason games. Data is not available at certain times/dates, for instance during stretches of the calendar in which no games occur (e.g. all star break, playoffs), periodic gaps in data availability, etc.

---

## Methods

### `get_injurydata(timestamp: datetime, local: bool = False, localdir: str | PathLike = None, return_df: bool = False, **kwargs):`

Extracts the injury data from the injury report at a specific date/time.

#### Parameters:
- `timestamp`: date/time of the report for retrieval, in the form of a `datetime` object
  - Example: `datetime(year=2023, month=5, day=2, hour=17, minute=30)`
- `local`: if the report to extract from is saved locally; default to `False` (retrieve live from URL directly)
- `local dir`: local directory path of data source, required if `local=True`
- `return_df`: return output as dataframe, otherwise as dict (json) format
- `kwargs`: if user would like to specify custom HTML headers in place of default ones for the HTML request

---

### `check_reportvalid(timestamp: datetime, **kwargs) -> bool`

Check the validity (availability) of the injury report data at a specific date/time.

#### Parameters:
- `timestamp`: date and time of the report, in the form of a `datetime` object
- `kwargs`: custom HTML headers in place of default ones

---

### `gen_injreplink(timestamp: datetime) -> str`

Returns the URL link of the injury report at a specific date/time.

#### Parameters:
- `timestamp`: datetime of the injury report
