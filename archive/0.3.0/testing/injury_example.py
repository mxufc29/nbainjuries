from nbainjuries.src.nbainjuries import Injury
import pandas as pd
from datetime import datetime, timedelta

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

if __name__ == "__main__":
    print(round_prev30min(datetime.now()))
    output_test = Injury.get_injurydata(round_prev30min(datetime.now()))
    print(output_test)
    df_test = Injury.get_injurydata(round_prev30min(datetime.now()), return_df=True)




