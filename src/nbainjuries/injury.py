from datetime import datetime
from os import PathLike

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from . import _constants, _parser
from ._exceptions import URLRetrievalError
from ._util import _gen_url, _gen_filepath


def get_reportdata(
        timestamp: datetime, local: bool = False, localdir: str | PathLike = None, return_df: bool = False, **kwargs
):
    """
    Extract injury data from the injury report at a specific date/time
    :param timestamp: datetime of the report for retrieval
    :param local: if source data saved locally; default to False (retrieve live)
    :param localdir: local directory path of source, needed if local = True
    :param return_df: return output as dataframe
    :param kwargs: custom headers to replace default
    """
    if not local:
        headerparam = kwargs.get("headers", _constants.requestheaders)
    if timestamp < datetime(year=2023, month=5, day=2, hour=17, minute=30):  # 21-22 and part of 22-23 season
        area_bounds = _constants.area_params2223_a
        col_bounds = _constants.cols_params2223_a
    elif (
            datetime(year=2023, month=5, day=2, hour=17, minute=30)
            <= timestamp
            <= _constants.dictkeydts["2223"]["ploffend"]
    ):  # remainder of 22-23 season
        area_bounds = _constants.area_params2223_b
        col_bounds = _constants.cols_params2223_b
    elif (
            _constants.dictkeydts["2324"]["regseastart"] <= timestamp <= _constants.dictkeydts["2324"]["ploffend"]
    ):  # 23-24 season
        area_bounds = _constants.area_params2324
        col_bounds = _constants.cols_params2324
    elif (
            _constants.dictkeydts["2425"]["regseastart"] <= timestamp <= _constants.dictkeydts["2425"]["ploffend"]
    ):  # 24-25 season
        area_bounds = _constants.area_params2425
        col_bounds = _constants.cols_params2425
    elif _constants.dictkeydts["2526"]["regseastart"] <= timestamp:
        area_bounds = _constants.area_params2526
        col_bounds = _constants.cols_params2526
    else:  # out of range - default to 25-26 params
        area_bounds = _constants.area_params2526
        col_bounds = _constants.cols_params2526

    if local:
        df_result = _parser.extract_injreplocal(
            _gen_filepath(timestamp, localdir), area_headpg=area_bounds, cols_headpg=col_bounds
        )
        return df_result if return_df else df_result.to_json(orient="records", index=False, indent=2, force_ascii=False)
    else:
        df_result = _parser.extract_injrepurl(
            gen_url(timestamp), area_headpg=area_bounds, cols_headpg=col_bounds, headers=headerparam
        )
        return df_result if return_df else df_result.to_json(orient="records", index=False, indent=2, force_ascii=False)


def check_reportvalid(timestamp: datetime, **kwargs) -> bool:
    """
    Validate data availability of report at a specific date/time
    """
    headerparam = kwargs.get("headers", _constants.requestheaders)
    try:
        _parser.validate_injrepurl(gen_url(timestamp), headers=headerparam)
        return True
    except URLRetrievalError as e:
        return False
    except Exception as e_gen:
        return False


def gen_url(timestamp: datetime) -> str:
    """ """
    return _gen_url(timestamp)


class InjuryScraper:
    def __init__(self):
        opts = Options()
        opts.add_argument("--headless")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(options=opts, service=service)
        self.driver = driver

    def __del__(self):
        self.driver.close()

    def parse(self, html):
        soup = BeautifulSoup(html, "html.parser")
        team_injuries = soup.find_all("div", class_="TableBaseWrapper")
        injuries = []
        for team in team_injuries:
            team_name = team.find("div", class_="TeamLogoNameLockup-name").get_text(strip=True)
            players = team.find_all("tr", class_="TableBase-bodyTr")
            for player in players:
                player_td = player.find_all("td", class_="TableBase-bodyTd")
                player_data = {
                    "Team": team_name,
                    "Name": player.find("span", class_="CellPlayerName--long").get_text(strip=True),
                    "Updated": player.find("span", class_="CellGameDate").get_text(strip=True),
                    "Injury": player_td[3].get_text(strip=True),
                    "Status": player_td[4].get_text(strip=True),
                }
                injuries.append(player_data)
        return pd.DataFrame(injuries).sort_values("Team")

    def get_data(self):
        self.driver.get(_constants.all_injuries_url)
        return self.parse(self.driver.page_source)
