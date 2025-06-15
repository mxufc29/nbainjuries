from nbainjuries import injury
from datetime import datetime, timedelta
import random


def round_prev30min(timestamp: datetime) -> datetime:
    if timestamp.minute >= 45:
        redr = timestamp.minute % 30
        tsdelta = timestamp - timedelta(minutes=redr)
        return tsdelta.replace(second=0, microsecond=0)
    elif timestamp.minute <= 30:
        tsdelta = timestamp - timedelta(hours=1) + timedelta(minutes=(30 - timestamp.minute))
        return tsdelta.replace(second=0, microsecond=0)
    else:
        tsdelta = timestamp - timedelta(hours=1) - timedelta(minutes=(timestamp.minute - 30))
        return tsdelta.replace(second=0, microsecond=0)


def gen_randomdt(startdt, enddt, exclude_list: list[tuple[datetime, datetime]] = None):
    dtpool = []
    dtx = startdt
    exclude_list = exclude_list or []
    while dtx <= enddt:
        if not any(excl_start <= dtx <= excl_end for (excl_start, excl_end) in exclude_list):
            dtpool.append(dtx)
        dtx += timedelta(hours=1)
    return random.choice(dtpool)


if __name__ == "__main__":
    # # output_test = injury.get_reportdata(round_prev30min(datetime.now()))
    # print(output_test)
    # URL
    df_test = injury.get_reportdata(gen_randomdt(startdt=datetime(2024, 10, 21, 0, 30),
                                                 enddt=datetime(2025, 4, 13, 23, 30),
                                                 exclude_list=[(datetime(2025, 2, 14, 0, 30),
                                                                datetime(2025, 2, 18, 23, 30))]),
                                    return_df=True)
    dict_test = injury.get_reportdata(gen_randomdt(startdt=datetime(2024, 10, 21, 0, 30),
                                                   enddt=datetime(2025, 4, 13, 23, 30),
                                                   exclude_list=[(datetime(2025, 2, 14, 0, 30),
                                                                  datetime(2025, 2, 18, 23, 30))]))
    # LOCAL
    DATA_DIR = ('C:/Users/Michael Xu/Desktop/Sports Analytics/Projects/Data/Downloads/NBAOfficialInjReports/2023-2024'
                '/regseas23-24')
    dt_testl1 = gen_randomdt(startdt=datetime(2023, 10, 24, 17, 30),
                                                      enddt=datetime(2024, 4, 14, 23, 30),
                                                      exclude_list=[(datetime(2024, 2, 16, 0, 30),
                                                                     datetime(2024, 2, 20, 23, 30))])
    df_testlocal = injury.get_reportdata(dt_testl1, local=True, localdir=DATA_DIR, return_df=True)
    print(dt_testl1)
    dt_testl2 = gen_randomdt(startdt=datetime(2023, 10, 24, 17, 30),
                             enddt=datetime(2024, 4, 14, 23, 30),
                             exclude_list=[(datetime(2024, 2, 16, 0, 30),
                                            datetime(2024, 2, 20, 23, 30))])
    dict_testlocal = injury.get_reportdata(dt_testl2, local=True, localdir=DATA_DIR)
    print(dt_testl2)


