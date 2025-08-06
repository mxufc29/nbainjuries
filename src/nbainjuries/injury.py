from os import PathLike
from datetime import datetime
from . import _constants, _parser
from ._exceptions import URLRetrievalError
from ._util import _gen_url, _gen_filepath


def get_reportdata(timestamp: datetime, local: bool = False, localdir: str | PathLike = None, return_df: bool = False,
                   **kwargs):
    """
    Extract injury data from the injury report at a specific date/time
    :param timestamp: datetime object of the report for retrieval
    :param local: if source to retreive saved locally; default to False (retrieve from url)
    :param localdir: local directory path of source, needed if local = True
    :param return_df: return output as dataframe
    :param kwargs: custom html headers in place of default ones
    """
    if not local:
        headerparam = kwargs.get('headers', _constants.requestheaders)
    if timestamp < datetime(year=2023, month=5, day=2, hour=17, minute=30):  # 21-22 and part of 22-23 season
        area_bounds = _constants.area_params2223_a
        col_bounds = _constants.cols_params2223_a
    elif datetime(year=2023, month=5, day=2, hour=17, minute=30) <= timestamp <= _constants.dictkeydts['2223'][
        'ploffend']:  # remainder of 22-23 season
        area_bounds = _constants.area_params2223_b
        col_bounds = _constants.cols_params2223_b
    elif _constants.dictkeydts['2324']['regseastart'] <= timestamp <= _constants.dictkeydts['2324'][
        'ploffend']:  # 23-24 season
        area_bounds = _constants.area_params2324
        col_bounds = _constants.cols_params2324
    elif _constants.dictkeydts['2425']['regseastart'] <= timestamp:  # 24-25 season
        area_bounds = _constants.area_params2425
        col_bounds = _constants.cols_params2425
    else:  # out of range for covered seasons - default to 24-25 params
        area_bounds = _constants.area_params2425
        col_bounds = _constants.cols_params2425

    if local:
        df_result = _parser.extract_injreplocal(_gen_filepath(timestamp, localdir), area_headpg=area_bounds,
                                                cols_headpg=col_bounds)
        return df_result if return_df else df_result.to_json(orient='records', index=False, indent=2, force_ascii=False)
    else:
        df_result = _parser.extract_injrepurl(gen_url(timestamp), area_headpg=area_bounds,
                                              cols_headpg=col_bounds,
                                              headers=headerparam)
        return df_result if return_df else df_result.to_json(orient='records', index=False, indent=2, force_ascii=False)


def check_reportvalid(timestamp: datetime, **kwargs) -> bool:
    """
    Validate data availability of report at a specific date/time
    """
    headerparam = kwargs.get('headers', _constants.requestheaders)
    try:
        _parser.validate_injrepurl(gen_url(timestamp), headers=headerparam)
        return True
    except URLRetrievalError as e:
        return False
    except Exception as e_gen:
        return False


def gen_url(timestamp: datetime) -> str:
    """
    """
    return _gen_url(timestamp)

