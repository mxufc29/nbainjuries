import pandas as pd
from os import path, PathLike
from datetime import datetime, timedelta
from injuries import _constants, _parser


def get_injurydata(timestamp: datetime, local: bool = False, localdir: str | PathLike = None, **kwargs) -> pd.DataFrame:
    """
    Extract injury data from the injury report at a specific date/time (datetime object).
    :param timestamp: datetime object of the report for retrieval
    :param local: if source to retreive saved locally; default to False (retrieve from url)
    :param localdir: local directory path of source, needed if local = True
    :param kwargs: custom html headers in place of default ones
    :return:
    """
    if not local:
        if 'headers' in kwargs:
            headerparam = kwargs['headers']
        else:
            headerparam = _constants.requestheaders
    if timestamp < datetime(year=2023, month=5, day=2, hour=17, minute=30):  # 21-22 and part of 22-23 season
        area_bounds = _constants.area_params2223_a
        col_bounds = _constants.cols_params2223_a
    elif datetime(year=2023, month=5, day=2, hour=17, minute=30) <= timestamp <= _constants.dictkeydts['2223'][
        'ploffend']:  # remainder of 22-23 season
        area_bounds = _constants.area_params2223_b
        col_bounds = _constants.cols_params2223_b
    elif _constants.dictkeydts['2324']['regseastart'] <= timestamp <= _constants.dictkeydts['2324']['ploffend']:  # 23-24 season
        area_bounds = _constants.area_params2324
        col_bounds = _constants.cols_params2324
    elif _constants.dictkeydts['2425']['regseastart'] <= timestamp:  # 24-25 season
        area_bounds = _constants.area_params2425
        col_bounds = _constants.cols_params2425
    else:  # out of range for covered seasons - default to 24-25 params
        area_bounds = _constants.area_params2425
        col_bounds = _constants.cols_params2425

    if local:  # TODO patch this
        return _parser.extract_injreplocal(_gen_injrep_dlpath(timestamp, localdir), area_headpg=area_bounds, cols_headpg=col_bounds)
    else:
        return _parser.extract_injrepurl(gen_injreplink(timestamp), area_headpg=area_bounds, cols_headpg=col_bounds,
                                        headers=headerparam)


def check_reportvalid(timestamp: datetime, **kwargs) -> bool:
    """
    Confirm the access/validity of the injury report URL at a specific date/time (datetime object).
    :param timestamp:
    :param kwargs: custom html headers in place of default ones
    :return:
    """
    if 'headers' in kwargs:
        headerparam = kwargs['headers']
    else:
        headerparam = _constants.requestheaders
    return _parser.validate_injrepurl(gen_injreplink(timestamp), headers=headerparam)


def gen_injreplink(timestamp: datetime) -> str:
    """
    Generate the URL link of the injury report on the NBA.com server.
    :param timestamp: datetime of the injury report
    :return: URL of injury report based on the specified timestamp
    """
    URLstem_date = timestamp.date().strftime('%Y-%m-%d')
    URLstem_time = (timestamp - timedelta(minutes=30)).time().strftime('%I%p')
    return _constants.urlstem_injreppdf.replace('*', URLstem_date + '_' + URLstem_time)


def _gen_injrep_dlpath(timestamp: datetime, directorypath: str | PathLike) -> str:
    """
    Internal
    """
    URLstem_date = timestamp.date().strftime('%Y-%m-%d')
    URLstem_time = (timestamp - timedelta(minutes=30)).time().strftime('%I%p')
    filename = 'Injury-Report_' + URLstem_date + '_' + URLstem_time + '.pdf'
    injrep_dlpath = path.join(directorypath, filename)
    return injrep_dlpath
