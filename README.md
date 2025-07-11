# nbainjuries

A package for retrieving historical and real-time NBA player injury data in a structured, API-like format. 

## Table of Contents

- [Description](#description)

- [Installation / Getting Started](#installation--getting-started)

- [API Reference](#api-reference)

- [Examples / Usage](#examples--usage)

- [Contributing](#contributing)

## Description

In the NBA, injuries sustained by players significantly influence the success of their teams over the course of the regular season and postseason, as well as long-term franchise trajectory. Due to these massive implications, tracking the overall incidence and severity of these injuries, as well as player health and recovery progress, is often a central area of interest for most stakeholders directly or indirectly involved with the league.

The NBA’s official guidelines on injury tracking and reporting for teams state that:

    (a) Teams must report information concerning player injuries, illnesses, and rest for all NBA games.

    (b) By 5 p.m. local time on the day before a game (other than the second day of a back-to-back), teams must designate a participation status and identify a specific injury, illness, or potential instance of a healthy player resting for any player whose participation in the game may be affected by such injury, illness or rest.

    (c) For the second game of a back-to-back, teams must report the above information by 1 p.m. local time on the day of the game.

Official player injury data are submitted by team medical staff pursuant to the above guidelines, and are stored as static report files on the NBA’s server, organized in hourly snapshots across each day of the regular season and postseason. Historical data in this
format have been available since the 2021-2022 NBA season. Data are not available for preseason games, and are not available at certain times/dates, for instance during stretches of the calendar in which no games occur (e.g. all star break, postseason), and other periodic gaps in data availability.

This package was conceived and formulated as a tool for systematically retrieving, extracting, and cleaning the data in these static reports. It is intended to be versatile in its usage, and can serve as both a potential ETL pipeline for storage/analysis and an API-style interface for querying up-to date injury information in quasi real-time settings.

## Installation / Getting Started

#### Prerequisites

- **Python 3.10+**

- **Java** - `nbainjuries` utilizes the tabula-py module for data processing, which requiresa Java Runtime (JRE) or Development Kit (JDK) version 8 or higher. Ensure you have [Java installed](https://www.java.com/en/download/manual.jsp) and that that running `java` from your system's terminal works (i.e., the `java` command is available in your system’s PATH).
  
  - Step-by-step [instructions](https://www.baeldung.com/java-home-on-windows-mac-os-x-linux) on adding Java to system PATH variable
  
  - To verify Java is successfully configured, ensure that execution of “java -version” in your system’s terminal returns information about the java version (no errors or command not found messages).
  
  - For additional information/troubleshooting in Java, please reference the [tabula-py getting started page](https://tabula-py.readthedocs.io/en/latest/getting_started.html#requirements)

`nbainjuries` is available on PyPI. To install via pip, run `pip install nbainjuries`.

## API Reference

Refer to [Documentation.md](https://github.com/mxufc29/nbainjuries/blob/main/Documentation.md).

## Examples / Usage

#### Single Report Query

Let's say one wishes to retrieve the injury report data for 04/25/2025 at 5:30pm ET in both json and DataFrame formats.

```python
from nbainjuries import injury
from datetime import datetime

json_output = injury.get_reportdata(datetime(year=2025, month=4, day=25, hour=17, minute=30)) 
df_output = injury.get_reportdata(datetime(year=2025, month=4, day=25, hour=17, minute=30), return_df=True)
```

**json_output (first four records)**

```json
[
  {
    "Game Date":"04\/25\/2025",
    "Game Time":"07:00 (ET)",
    "Matchup":"BOS@ORL",
    "Team":"Boston Celtics",
    "Player Name":"Brown, Jaylen",
    "Current Status":"Questionable",
    "Reason":"Injury\/Illness - Right Knee; Posterior Impingement"
  },
  {
    "Game Date":"04\/25\/2025",
    "Game Time":"07:00 (ET)",
    "Matchup":"BOS@ORL",
    "Team":"Boston Celtics",
    "Player Name":"Holiday, Jrue",
    "Current Status":"Questionable",
    "Reason":"Injury\/Illness - Right Hamstring; Strain"
  },
  {
    "Game Date":"04\/25\/2025",
    "Game Time":"07:00 (ET)",
    "Matchup":"BOS@ORL",
    "Team":"Boston Celtics",
    "Player Name":"Tatum, Jayson",
    "Current Status":"Questionable",
    "Reason":"Injury\/Illness - Right Distal Radius; Bone Bruise"
  },
  {
    "Game Date":"04\/25\/2025",
    "Game Time":"07:00 (ET)",
    "Matchup":"BOS@ORL",
    "Team":"Orlando Magic",
    "Player Name":"Suggs, Jalen",
    "Current Status":"Out",
    "Reason":"Injury\/Illness - Left Knee; Trochlea cartilage tear"
  },
  ...
]
```

**df_output.head(10)**

| Game Date  | Game Time  | Matchup | Team                   | Player Name     | Current Status | Reason                                              |
| ---------- | ---------- | ------- | ---------------------- | --------------- | -------------- | --------------------------------------------------- |
| 04/25/2025 | 07:00 (ET) | BOS@ORL | Boston Celtics         | Brown, Jaylen   | Questionable   | Injury/Illness - Right Knee; Posterior Impingement  |
| 04/25/2025 | 07:00 (ET) | BOS@ORL | Boston Celtics         | Holiday, Jrue   | Questionable   | Injury/Illness - Right Hamstring; Strain            |
| 04/25/2025 | 07:00 (ET) | BOS@ORL | Boston Celtics         | Tatum, Jayson   | Questionable   | Injury/Illness - Right Distal Radius; Bone Bruise   |
| 04/25/2025 | 07:00 (ET) | BOS@ORL | Orlando Magic          | Suggs, Jalen    | Out            | Injury/Illness - Left Knee; Trochlea cartilage tear |
| 04/25/2025 | 07:00 (ET) | BOS@ORL | Orlando Magic          | Wagner, Moritz  | Out            | Injury/Illness - Left Knee; Torn ACL                |
| 04/25/2025 | 08:00 (ET) | IND@MIL | Indiana Pacers         | Jackson, Isaiah | Out            | Injury/Illness - Right Achilles Tendon; Tear        |
| 04/25/2025 | 08:00 (ET) | IND@MIL | Milwaukee Bucks        | Smith, Tyler    | Questionable   | Injury/Illness - Left Ankle; Sprain                 |
| 04/25/2025 | 09:30 (ET) | LAL@MIN | Los Angeles Lakers     | Hachimura, Rui  | Available      | Injury/Illness - Custom; Facemask                   |
| 04/25/2025 | 09:30 (ET) | LAL@MIN | Los Angeles Lakers     | Kleber, Maxi    | Out            | Injury/Illness - Right Foot; Surgery Recovery       |
| 04/25/2025 | 09:30 (ET) | LAL@MIN | Minnesota Timberwolves | Dillingham, Rob | Out            | Injury/Illness - Right Ankle; Sprain                |

#### Batch Report Query

Let's say one wants to retrieve and consolidate all injury report data for the entire 2023-2024 NBA regular season, or obtain the data from a random sample of 100 injury reports from the 2023-2024 NBA regular season. For improved processing speed, instead of the `injury` module, use the `injury_asy` module in addition to `asyncio` to enable concurrent (batch) processing of reports. For an example of this usage, reference tests/injuryasy_example.py

## Contributing

I welcome any suggestions or feedback; please feel free to submit [comments](https://github.com/mxufc29/nbainjuries/issues) and/or [pull requests](https://github.com/mxufc29/nbainjuries/pulls) on GitHub.

I am also actively looking for collaborators on some potential ancillary projects in the pipeline:

(a) expanding data coverage to include seasons before 2021-2022,

(b) developing a centralized database solution to store these data

(c) classifying/analyzing/dashboarding season-level injury trends.

If any/all of these avenues are of interest, please feel free to reach out to me via email at mxufc29 (at) outlook (dot) com.
