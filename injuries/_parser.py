from os import path, PathLike
import pandas as pd
import tabula
import PyPDF2
from io import BytesIO
import requests
from datetime import datetime


def validate_injrepurl(filepath: str | PathLike, **kwargs) -> bool:
    """
    :param filepath: url of report (nba.com domain)
    :param kwargs: any headers
    :return: access status of report
    """
    try:
        resp = requests.get(filepath, **kwargs)
        resp.raise_for_status()
        print(f'Validated {filepath}.')
        return True
    except Exception as e_gen:
        print(f'File at {filepath} cannot be accessed due to {e_gen}')
        return False

def extract_injrepurl(filepath: str | PathLike, area_headpg: list, cols_headpg: list,
                             area_otherpgs: list | None = None, cols_otherpgs: list | None = None,
                             **kwargs) -> pd.DataFrame:
    """
    :param filepath: url of report (nba.com domain)
    :param area_headpg: area boundaries of first pg of pdf
    :param cols_headpg: column boundaries of first pg of pdf
    :param area_otherpgs: area boundaries of other pgs of pdf if needed
    :param cols_otherpgs: column boundaries of other pgs of pdf if needed
    :param kwargs: any headers
    :return:
    """
    if validate_injrepurl(filepath, **kwargs):
        resp = requests.get(filepath, **kwargs)
        pdf_content = resp.content
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_content))
        pdf_numpgs = len(pdf_reader.pages)
    else:
        raise FileNotFoundError(f'File at url {filepath} cannot be accessed.')

    if area_otherpgs is None:
        area_otherpgs = area_headpg
    if cols_otherpgs is None:
        cols_otherpgs = cols_headpg

    # First pg
    dfs_headpg = tabula.read_pdf(filepath, stream=True, area=area_headpg,
                                         columns=cols_headpg, pages=1)
    # Following pgs
    dfs_otherpgs = []  # default to empty list if only single pg
    if pdf_numpgs >= 2:
        dfs_otherpgs = tabula.read_pdf(filepath, stream=True, area=area_otherpgs,
                                               columns=cols_otherpgs, pages='2-' + str(pdf_numpgs), pandas_options={'header': None})
        # default to pandas_options={'header': 'infer'}
        # Override with pandas_options={'header': None}; manually drop included headers if necessary
    # Processing
    df_rawdata = __concat_injreppgs(dflist_headpg=dfs_headpg, dflist_otherpgs=dfs_otherpgs)
    df_cleandata = __clean_injrep(df_rawdata)
    return df_cleandata


def extract_injreplocal(filepath: str | PathLike, area_headpg: list, cols_headpg: list,
                             area_otherpgs: list | None = None, cols_otherpgs: list | None = None) -> pd.DataFrame:
    try:
        pdf_numpgs = _pagect_localpdf(filepath)
    except Exception as e_gen:
        raise FileNotFoundError(f'Could not open {str(filepath)} due to {e_gen}.')

    if area_otherpgs is None:
        area_otherpgs = area_headpg
    if cols_otherpgs is None:
        cols_otherpgs = cols_headpg

    # First page
    dfs_headpg = tabula.read_pdf(filepath, stream=True, area=area_headpg,
                                 columns=cols_headpg, pages=1)
    # Following pgs
    dfs_otherpgs = []  # default to empty list if only single pg
    if pdf_numpgs >= 2:
        dfs_otherpgs = tabula.read_pdf(filepath, stream=True, area=area_otherpgs,
                                               columns=cols_otherpgs, pages='2-' + str(pdf_numpgs), pandas_options={'header': None})
        # default to pandas_options={'header': 'infer'}
        # Override with pandas_options={'header': None}; manually drop included headers if necessary
    # Process and clean data
    df_rawdata = __concat_injreppgs(dflist_headpg=dfs_headpg, dflist_otherpgs=dfs_otherpgs)
    df_cleandata = __clean_injrep(df_rawdata)
    return df_cleandata


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

    dfcleaning_x['unsubmitted'] = dfcleaning_x['Reason'].apply(lambda x: str(x).casefold()) == 'NOT YET SUBMITTED'.casefold()
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
    dfcleaning_x['next_multiline'] = dfcleaning_x['reas_multilinesplit'].shift(periods=-1, fill_value=False).astype(bool)
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
