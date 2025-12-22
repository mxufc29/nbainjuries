from os import path, PathLike
from datetime import datetime, timedelta
import re
import pandas as pd
import PyPDF2
from . import _constants
from ._exceptions import DataValidationError



def _gen_urls(timestamp: datetime) -> list[str]:
    urls = []
    date_str = timestamp.strftime('%Y-%m-%d')

    # -------- NEW FORMAT (15-min cadence) --------
    minute = (timestamp.minute // 15) * 15
    rounded_ts = timestamp.replace(minute=minute, second=0, microsecond=0)
    time_new = rounded_ts.strftime('%I_%M%p')

    urls.append(
        _constants.urlstem_injreppdf.replace(
            '*', f"{date_str}_{time_new}"
        )
    )

    # -------- LEGACY FORMAT (hourly, no minutes) --------
    legacy_ts = timestamp - timedelta(minutes=30)
    time_legacy = legacy_ts.strftime('%I%p')

    urls.append(
        _constants.urlstem_injreppdf.replace(
            '*', f"{date_str}_{time_legacy}"
        )
    )

    return urls


def _gen_filepath(timestamp: datetime, directorypath: str | PathLike) -> str:
    URLstem_date = timestamp.date().strftime('%Y-%m-%d')
    URLstem_time = (timestamp - timedelta(minutes=30)).time().strftime('%I%p')
    filename = 'Injury-Report_' + URLstem_date + '_' + URLstem_time + '.pdf'
    injrep_dlpath = path.join(directorypath, filename)
    return injrep_dlpath


def _pagect_localpdf(filepath: str | PathLike):
    with open(filepath, mode='rb') as injrepfile:
        pdf_reader = PyPDF2.PdfReader(injrepfile)
        pdf_numpgs = len(pdf_reader.pages)
        return pdf_numpgs


def __concat_injreppgs(dflist_headpg: list, dflist_otherpgs: list) -> pd.DataFrame:
    list_dfparts = [dflist_headpg[0]]
    for appenddf_x in dflist_otherpgs:
        if appenddf_x.loc[appenddf_x.index[0]].tolist() == list(dflist_headpg[0].columns):
            appenddf_x.drop(index=appenddf_x.index[0], inplace=True)
        appenddf_x.columns = dflist_headpg[0].columns
        list_dfparts.append(appenddf_x)
    for df_x in list_dfparts:
        df_x['LastonPgBoundary'] = False
    for df_x in list_dfparts[:-1]:
        df_x.at[(df_x.shape[0] - 1), 'LastonPgBoundary'] = True
    df_injrepconcat = pd.concat(list_dfparts, ignore_index=True)
    return df_injrepconcat


def __clean_injrep(dfinjrep_x: pd.DataFrame) -> pd.DataFrame:
    dfcleaning_x = dfinjrep_x.copy()

    ffill_cols = ['Game Date', 'Game Time', 'Matchup', 'Team']  # CONSTANT - modify as needed
    for colname, seriesx in dfcleaning_x.items():
        if (colname in ffill_cols):
            seriesx.ffill(inplace=True)

    dfcleaning_x['unsubmitted'] = dfcleaning_x['Reason'].apply(
        lambda x: str(x).casefold()) == 'NOT YET SUBMITTED'.casefold()
    df_unsubmitted = dfcleaning_x.loc[dfcleaning_x['unsubmitted'], :]
    dfcleaning_x = dfcleaning_x.loc[~(dfcleaning_x['unsubmitted']), :]

    dfcleaning_x['NextReas'] = dfcleaning_x['Reason'].shift(periods=-1, fill_value='N/A')
    dfcleaning_x['NextPlname'] = dfcleaning_x['Player Name'].shift(periods=-1, fill_value='N/A')
    dfcleaning_x['NextCstatus'] = dfcleaning_x['Current Status'].shift(periods=-1, fill_value='N/A')
    dfcleaning_x['Nextx2Reas'] = dfcleaning_x['Reason'].shift(periods=-2, fill_value='N/A')

    dfcleaning_x['PrevReas'] = dfcleaning_x['Reason'].shift(periods=1, fill_value='N/A')
    dfcleaning_x['PrevPlname'] = dfcleaning_x['Player Name'].shift(periods=1, fill_value='N/A')
    dfcleaning_x['PrevCstatus'] = dfcleaning_x['Current Status'].shift(periods=1, fill_value='N/A')
    dfcleaning_x['Prevx2Reas'] = dfcleaning_x['Reason'].shift(periods=2, fill_value='N/A')
    dfcleaning_x['PrevLastonPgBdry'] = dfcleaning_x['LastonPgBoundary'].shift(periods=1, fill_value='N/A')

    # Create Flags
    ## (a)
    dfcleaning_x['GLeague'] = dfcleaning_x['Reason'].str.contains('G League', case=False).astype(pd.BooleanDtype())
    ## (b)
    dfcleaning_x['likely_reas1linecomplete'] = (
            (dfcleaning_x['Reason'].str.contains('-', case=False)) &
            (dfcleaning_x['Reason'].str.contains(';', case=False)) &
            (dfcleaning_x['Player Name'].notna()) &
            (dfcleaning_x['Current Status'].notna()) &
            ~(dfcleaning_x['LastonPgBoundary'])
    )
    ## (c)
    dfcleaning_x['likely_reas1linecomplete_alt'] = (
            (dfcleaning_x['Reason'].notna()) &
            (dfcleaning_x['Player Name'].notna()) &
            (dfcleaning_x['Current Status'].notna()) &
            (dfcleaning_x['Nextx2Reas'].isna()) &
            (dfcleaning_x['Prevx2Reas'].isna()) &
            ~(dfcleaning_x['LastonPgBoundary'])
    )
    ## (d)
    list_uniquecases = ['League Suspension', 'Not with Team', 'Personal Reasons', 'Rest', 'Concussion Protocol']
    uniquecase_regex = r'\b(?:' + '|'.join([case.replace(' ', '') for case in list_uniquecases]) + r')\b'
    dfcleaning_x['likely_reas1linecomplete_alt2'] = (
            (dfcleaning_x['Reason'].notna()) &
            (dfcleaning_x['Player Name'].notna()) &
            (dfcleaning_x['Current Status'].notna()) &
            (dfcleaning_x['Reason'].str.replace(r'\s+', '', regex=True).str.contains(uniquecase_regex, case=False,
                                                                                     na=False, regex=True)) &
            ~(dfcleaning_x['LastonPgBoundary'])
    )
    ## (e)
    dfcleaning_x['reas_multilinesplit'] = (
            (dfcleaning_x['NextPlname'].isna()) &
            (dfcleaning_x['NextCstatus'].isna()) &
            (dfcleaning_x['PrevPlname'].isna()) &
            (dfcleaning_x['PrevCstatus'].isna()) &
            (~(dfcleaning_x['LastonPgBoundary'])) &
            (~(dfcleaning_x['likely_reas1linecomplete'])) &
            (~(dfcleaning_x['likely_reas1linecomplete_alt'])) &
            (~(dfcleaning_x['likely_reas1linecomplete_alt2']))
    )
    # Overrides
    ##
    dfcleaning_x.loc[dfcleaning_x['GLeague'], 'reas_multilinesplit'] = False

    # Handle multiline text in 'Reason' split onto preceding and succeeding line
    ## (a)
    dfcleaning_x.loc[((dfcleaning_x['reas_multilinesplit']) & (dfcleaning_x['Reason'].notna())), 'Reason'] = (
            dfcleaning_x['PrevReas'] + ' ' + dfcleaning_x['Reason'] + ' ' + dfcleaning_x['NextReas'])
    ## (b)
    dfcleaning_x.fillna(value={'Reason': dfcleaning_x['Reason'].ffill() + ' ' + dfcleaning_x['Reason'].bfill()},
                        inplace=True)
    ## (c)
    dfcleaning_x['next_multiline'] = dfcleaning_x['reas_multilinesplit'].shift(periods=-1, fill_value=False).astype(
        bool)
    dfcleaning_x['prev_multiline'] = dfcleaning_x['reas_multilinesplit'].shift(periods=1, fill_value=False).astype(bool)
    dfcleaning_x['del_multiline'] = (
            (dfcleaning_x['next_multiline']) |
            (dfcleaning_x['prev_multiline'])
    )
    dfcleaning_x = dfcleaning_x.loc[~(dfcleaning_x['del_multiline']), :]

    # Page Break Split
    ## (a)
    dfcleaning_x['NextReas'] = dfcleaning_x['Reason'].shift(periods=-1, fill_value='N/A')
    dfcleaning_x['NextPlname'] = dfcleaning_x['Player Name'].shift(periods=-1, fill_value='N/A')
    dfcleaning_x['NextCstatus'] = dfcleaning_x['Current Status'].shift(periods=-1, fill_value='N/A')
    dfcleaning_x['PrevReas'] = dfcleaning_x['Reason'].shift(periods=1, fill_value='N/A')
    dfcleaning_x['PrevPlname'] = dfcleaning_x['Player Name'].shift(periods=1, fill_value='N/A')
    dfcleaning_x['PrevCstatus'] = dfcleaning_x['Current Status'].shift(periods=1, fill_value='N/A')

    ## (b)
    dfcleaning_x['reas_pgbksplit'] = (
            (dfcleaning_x['LastonPgBoundary']) &
            (dfcleaning_x['Reason'].notna()) &
            (dfcleaning_x['Player Name'].notna()) &
            (dfcleaning_x['Current Status'].notna()) &
            (dfcleaning_x['NextPlname'].isna()) &
            (dfcleaning_x['NextCstatus'].isna()) &
            (dfcleaning_x['NextReas'].notna())
    )
    dfcleaning_x.loc[dfcleaning_x['reas_pgbksplit'], 'Reason'] = (
            dfcleaning_x['Reason'] + ' ' + dfcleaning_x['NextReas'])

    ## (c)
    dfcleaning_x['prev_pgbksplit'] = dfcleaning_x['reas_pgbksplit'].shift(periods=1, fill_value=False).astype(bool)
    dfcleaning_x = dfcleaning_x.loc[~(dfcleaning_x['prev_pgbksplit']), :]

    # Drop variables used for cleaning (keep first seven cols), add back unsubmitted cols, reindex
    dfcleaning_xfinal = pd.concat([dfcleaning_x[dfcleaning_x.columns[:7]], df_unsubmitted[df_unsubmitted.columns[:7]]])
    dfcleaning_xfinal.sort_index(inplace=True)
    dfcleaning_xfinal.reset_index(inplace=True, drop=True)
    return dfcleaning_xfinal


def _validate_headers(df_headpg: pd.DataFrame):
    pg1cols_norm = [re.sub(r'[\W_]+', '', str(colx).strip().lower()) for colx in df_headpg.columns]
    expcols_norm = [re.sub(r'[\W_]+', '', str(colx).strip().lower()) for colx in _constants.expected_cols]
    if pg1cols_norm == expcols_norm:
        return True
    else:
        unexp_inds = [ind for ind, (x, y) in enumerate(zip(pg1cols_norm, expcols_norm)) if x != y]
        unexp_cols = df_headpg.columns[unexp_inds].tolist()
        raise DataValidationError(f"Incompatible column headers present: {unexp_cols}")

