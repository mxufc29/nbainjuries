from datetime import datetime, timedelta
from aiohttp import ClientSession
import asyncio
import time
import pandas as pd
from nbainjuries import injury_asy


async def extconcat_all(startdt: datetime, enddt: datetime, sleep_dur: float,
                        exclude: list[datetime] = None, **kwargs) -> pd.DataFrame:
    exclude = exclude or []
    dt_range = [startdt + timedelta(hours=i) for i in range(int((enddt - startdt).total_seconds() / 3600) + 1)]
    exclude_set = set(exclude)
    dt_validrange = [dt_x for dt_x in dt_range if dt_x not in exclude_set]

    start_timer = time.perf_counter()
    async with ClientSession() as ecallsession:
        toextract = []
        for reptime_x in dt_validrange:
            toextract_x = asyncio.create_task(
                injury_asy.get_reportdata(reptime_x, session=ecallsession, return_df=True, **kwargs),
                name=f"extract-{injury_asy.gen_url(reptime_x).split('/')[-1]}")
            toextract.append(toextract_x)
            await asyncio.sleep(sleep_dur)
        extract_results = await asyncio.gather(*toextract, return_exceptions=True)

    success_tuples = [(reptime_x, df_x) for reptime_x, df_x in zip(dt_validrange, extract_results)
                      if not isinstance(df_x, Exception)]
    for reptime_x, df_x in success_tuples:
        df_x['ReportTime'] = reptime_x.strftime('%Y-%m-%dT%H:%M')
    df_all = pd.concat([df_x for _, df_x in success_tuples], ignore_index=True)
    end_timer = time.perf_counter()
    print(
        f'Extracted and aggregated from {len(success_tuples)} reports in {end_timer - start_timer} sec.')
    return df_all


if __name__ == "__main__":
    start_batchecall = datetime(2023, 2, 1, 0, 30)
    end_batchecall = datetime(2023, 2, 28, 23, 30)
    df_output = asyncio.run(extconcat_all(startdt=start_batchecall, enddt=end_batchecall, sleep_dur=0.25))
