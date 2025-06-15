import random
from os import path, PathLike
from datetime import datetime, timedelta
from aiohttp import ClientSession
import asyncio
import time
from nbainjuries import _constants, injury_asy


# URL tests
async def generate_repdts_url(ts_start: datetime, ts_end: datetime, sleep_dur: float = 0.4, **kwargs) -> list:
    """
    :param sleep_dur: default to 1.0
    :return: list[datetime] - list of datetimes whose corresponding injrep urls are valid
    """
    hourscount = 0
    dt_stamps = []
    tasks_tovalidate = []
    start_timer = time.perf_counter()
    async with ClientSession() as currentsession:
        while (ts_start + timedelta(hours=hourscount)) <= ts_end:
            t = ts_start + timedelta(hours=hourscount)
            dt_stamps.append(t)
            tovalidate_x = asyncio.create_task(
                injury_asy.check_reportvalid(timestamp=t, session=currentsession, **kwargs),
                name=f'validate-report-{t}')
            tasks_tovalidate.append(tovalidate_x)
            hourscount += 1
            await asyncio.sleep(sleep_dur)
        validation_results = await asyncio.gather(*tasks_tovalidate, return_exceptions=True)  # list of bools

    # filter for datetimes for "true" validated report urls

    valid_dtrange = [dt_x for dt_x, is_valid in zip(dt_stamps, validation_results) if is_valid]
    end_timer = time.perf_counter()
    print(f'Total validation time of {len(dt_stamps)} urls, {sleep_dur} sleep = {end_timer - start_timer} sec.')
    print(
        f'Passed validation - {len(valid_dtrange)} urls; failed validation - {len(dt_stamps) - len(valid_dtrange)} urls.')
    return valid_dtrange


async def maintest_sampleurl(start_dt: datetime, end_dt: datetime, samplesize: int, sleep_dur: float = 0.5, **kwargs):
    dt_testrange = await generate_repdts_url(start_dt, end_dt, **kwargs)
    dt_testsample = random.sample(dt_testrange, k=samplesize)
    async with ClientSession() as mainsession:
        to_extract = []
        for reptime_x in dt_testsample:
            to_extract.append(injury_asy.get_reportdata(timestamp=reptime_x, session=mainsession, return_df=True))
            await asyncio.sleep(sleep_dur)
        extract_results = await asyncio.gather(*to_extract)

    dict_dfinjtest = {}
    for reptime_x, df_x in zip(dt_testsample, extract_results):
        filename = injury_asy.gen_url(reptime_x).split('/')[-1]
        df_x['ReportTime'] = reptime_x.strftime('%Y-%m-%dT%H:%M')
        dict_dfinjtest[filename] = df_x
    return dict_dfinjtest


async def maintest_sampleurljson(start_dt: datetime, end_dt: datetime, samplesize: int, sleep_dur: float = 0.5,
                                 **kwargs):
    dt_testrange = await generate_repdts_url(start_dt, end_dt, **kwargs)
    dt_testsample = random.sample(dt_testrange, k=samplesize)
    async with ClientSession() as mainsession:
        to_extract = []
        for reptime_x in dt_testsample:
            to_extract.append(injury_asy.get_reportdata(timestamp=reptime_x, session=mainsession))
            await asyncio.sleep(sleep_dur)
        extract_results = await asyncio.gather(*to_extract)

    dict_dfinjtest = {}
    for reptime_x, outputx in zip(dt_testsample, extract_results):
        filename = injury_asy.gen_url(reptime_x).split('/')[-1]
        dict_dfinjtest[filename] = outputx
    return dict_dfinjtest


# LOCAL tests
async def validate_local(timestamp: datetime, datadir: str | PathLike) -> bool:
    return await asyncio.to_thread(path.isfile, injury_asy.gen_filepath(timestamp, datadir))


async def validate_localdts(dt_list, datadir: str | PathLike):
    for dt_x in dt_list:
        if await validate_local(timestamp=dt_x, datadir=datadir):
            yield dt_x
            print(f"Validated {injury_asy.gen_url(dt_x).split('/')[-1]}")
        else:
            print(f"Failed validation - {injury_asy.gen_url(dt_x).split('/')[-1]}")


async def maintest_samplelocal(start_dt: datetime, end_dt: datetime, datadir: str | PathLike, samplesize: int,
                               sleep_dur: float = 0.5, **kwargs):
    """
    """
    dt_range = [start_dt + timedelta(hours=n) for n in range(int((end_dt - start_dt).total_seconds() / 3600) + 1)]
    dt_testrange = [dtx async for dtx in validate_localdts(dt_range, datadir)]
    dt_testsample = random.sample(dt_testrange, k=samplesize)
    to_extract = []
    for reptime_x in dt_testsample:
        to_extract.append(injury_asy.get_reportdata(timestamp=reptime_x, local=True, localdir=datadir, return_df=True))
        await asyncio.sleep(sleep_dur)
    extract_results = await asyncio.gather(*to_extract, return_exceptions=True)

    dict_dfinjtestlocal = {}
    for reptime_x, df_x in zip(dt_testsample, extract_results):
        filename = injury_asy.gen_url(reptime_x).split('/')[-1]
        df_x['ReportTime'] = reptime_x.strftime('%Y-%m-%dT%H:%M')
        dict_dfinjtestlocal[filename] = df_x
    return dict_dfinjtestlocal


async def maintest_samplelocaljson(start_dt: datetime, end_dt: datetime, datadir: str | PathLike, samplesize: int,
                                   sleep_dur: float = 0.5, **kwargs):
    dt_range = [start_dt + timedelta(hours=n) for n in range(int((end_dt - start_dt).total_seconds() / 3600) + 1)]
    dt_testrange = [dtx async for dtx in validate_localdts(dt_range, datadir)]
    dt_testsample = random.sample(dt_testrange, k=samplesize)
    to_extract = []
    for reptime_x in dt_testsample:
        to_extract.append(injury_asy.get_reportdata(timestamp=reptime_x, local=True, localdir=datadir))
        await asyncio.sleep(sleep_dur)
    extract_results = await asyncio.gather(*to_extract, return_exceptions=True)

    dict_dfinjtestlocal = {}
    for reptime_x, outputx in zip(dt_testsample, extract_results):
        filename = injury_asy.gen_url(reptime_x).split('/')[-1]
        dict_dfinjtestlocal[filename] = outputx
    return dict_dfinjtestlocal


if __name__ == "__main__":
    DOWNLOAD_DATADIR = 'C:/Users/Michael Xu/Desktop/Sports Analytics/Projects/Data/Downloads/NBAOfficialInjReports'
    EXPORT_DATADIR = 'C:/Users/Michael Xu/Desktop/Sports Analytics/Projects/Data/Exports'
    DATADIR = 'C:/Users/Michael Xu/Desktop/Sports Analytics/Projects/Data'

    # DATE RANGES
    start_urltest = datetime(year=2022, month=2, day=12, hour=0, minute=30)
    end_urltest = _constants.dictkeydts['2122']['asbend']
    start_localtest = datetime(year=2023, month=2, day=1, hour=0, minute=30)
    end_localtest = _constants.dictkeydts['2223']['regseaend']
    # start_extcon = _constants.dictkeydts['2425']['regseastart']
    # end_extcon = datetime(year=2024, month=10, day=31, hour=23, minute=30)

    # samplingtest_url = asyncio.run(maintest_sampleurl(start_dt=start_urltest, end_dt=end_urltest, samplesize=20))
    # samplingtest_urljson = asyncio.run(maintest_sampleurljson(start_dt=start_urltest, end_dt=end_urltest, samplesize=20))

    if start_localtest.month >= 10:
        seasondesc = f"{start_localtest.year}-{start_localtest.year + 1}"
    elif start_localtest.month <= 6:
        seasondesc = f"{start_localtest.year - 1}-{start_localtest.year}"
    else:
        raise ValueError(f"Month {start_localtest.month} in NBA offseason — season is undefined.")

    samplingtest_local = asyncio.run(maintest_samplelocal(start_dt=start_localtest, end_dt=end_localtest,
                                                          datadir=path.join(DOWNLOAD_DATADIR, seasondesc),
                                                          samplesize=20))
    samplingtest_localjson = asyncio.run(maintest_samplelocaljson(start_dt=start_localtest, end_dt=end_localtest,
                                                                  datadir=path.join(DOWNLOAD_DATADIR, seasondesc),
                                                                  samplesize=20))
