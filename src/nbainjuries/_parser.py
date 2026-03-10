from os import PathLike
import os
import tempfile
import pandas as pd
import tabula
import PyPDF2
from io import BytesIO
import requests
from ._exceptions import URLRetrievalError, LocalRetrievalError
from ._util import __concat_injreppgs, _validate_headers, _pagect_localpdf, __clean_injrep
from ._constants import requestheaders


def _download_pdf_bytes(url: str, **kwargs) -> bytes:
    """Download PDF from URL, using curl_cffi if available to bypass CDN bot detection."""
    try:
        from curl_cffi import requests as cffi_requests
        headers = kwargs.get('headers', requestheaders)
        resp = cffi_requests.get(url, impersonate='chrome', headers=headers, timeout=30)
        resp.raise_for_status()
        print(f"Validated {url.split('/')[-1].rsplit('.', 1)[0]}.")
        return resp.content
    except ImportError:
        # Fall back to requests if curl_cffi is not installed
        resp = requests.get(url, **kwargs)
        resp.raise_for_status()
        print(f"Validated {url.split('/')[-1].rsplit('.', 1)[0]}.")
        return resp.content


def validate_injrepurl(filepath: str | PathLike, **kwargs) -> requests.Response:
    """
    :param filepath: url of report
    :param kwargs: custom headers
    :return: response object (if validation succeeds)
    """
    try:
        from curl_cffi import requests as cffi_requests
        headers = kwargs.get('headers', requestheaders)
        resp = cffi_requests.get(filepath, impersonate='chrome', headers=headers, timeout=30)
        resp.raise_for_status()
        print(f"Validated {filepath.split('/')[-1].rsplit('.', 1)[0]}.")
        return resp
    except ImportError:
        # Fall back to requests if curl_cffi is not installed
        try:
            resp = requests.get(filepath, **kwargs)
            resp.raise_for_status()
            print(f"Validated {filepath.split('/')[-1].rsplit('.', 1)[0]}.")
            return resp
        except requests.exceptions.RequestException as e_gen:
            print(f"Failed validation - {filepath.split('/')[-1].rsplit('.', 1)[0]}.")
            raise URLRetrievalError(filepath, e_gen)
    except Exception as e_gen:
        print(f"Failed validation - {filepath.split('/')[-1].rsplit('.', 1)[0]}.")
        raise URLRetrievalError(filepath, e_gen)


def extract_injrepurl(filepath: str | PathLike, area_headpg: list, cols_headpg: list,
                      area_otherpgs: list | None = None, cols_otherpgs: list | None = None,
                      **kwargs) -> pd.DataFrame:
    """
    :param filepath: url of report
    :param area_headpg: area boundaries of first pg of pdf
    :param cols_headpg: column boundaries of first pg of pdf
    :param area_otherpgs: area boundaries of other pgs of pdf if needed
    :param cols_otherpgs: column boundaries of other pgs of pdf if needed
    :param kwargs: custom headers
    """
    try:
        pdf_content = _download_pdf_bytes(filepath, **kwargs)
    except Exception as e_gen:
        print(f"Failed validation - {filepath.split('/')[-1].rsplit('.', 1)[0]}.")
        raise URLRetrievalError(filepath, e_gen)

    pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_content))
    pdf_numpgs = len(pdf_reader.pages)

    if area_otherpgs is None:
        area_otherpgs = area_headpg
    if cols_otherpgs is None:
        cols_otherpgs = cols_headpg

    # Save to temp file for tabula (tabula can't read from BytesIO)
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        tmp.write(pdf_content)
        tmp_path = tmp.name

    try:
        # First pg — read from local temp file instead of URL
        dfs_headpg = tabula.read_pdf(tmp_path, stream=True, area=area_headpg,
                                     columns=cols_headpg, pages=1)
        _validate_headers(dfs_headpg[0])
        # Following pgs
        dfs_otherpgs = []  # default to empty if single pg
        if pdf_numpgs >= 2:
            dfs_otherpgs = tabula.read_pdf(tmp_path, stream=True, area=area_otherpgs,
                                           columns=cols_otherpgs, pages='2-' + str(pdf_numpgs),
                                           pandas_options={'header': None})
            # default to pandas_options={'header': 'infer'}
            # Override with pandas_options={'header': None}; manually drop included headers if necessary
        # Processing
        df_rawdata = __concat_injreppgs(dflist_headpg=dfs_headpg, dflist_otherpgs=dfs_otherpgs)
        df_cleandata = __clean_injrep(df_rawdata)
        return df_cleandata
    finally:
        os.unlink(tmp_path)


def extract_injreplocal(filepath: str | PathLike, area_headpg: list, cols_headpg: list,
                        area_otherpgs: list | None = None, cols_otherpgs: list | None = None) -> pd.DataFrame:
    try:
        pdf_numpgs = _pagect_localpdf(filepath)
    except (FileNotFoundError, PermissionError) as e_gen:
        raise LocalRetrievalError(filepath, e_gen)
        # archive FileNotFoundError(f'Could not open {str(filepath)} due to {e_gen}.')

    if area_otherpgs is None:
        area_otherpgs = area_headpg
    if cols_otherpgs is None:
        cols_otherpgs = cols_headpg

    # First page
    dfs_headpg = tabula.read_pdf(filepath, stream=True, area=area_headpg,
                                 columns=cols_headpg, pages=1)
    _validate_headers(dfs_headpg[0])
    # Following pgs
    dfs_otherpgs = []  # default to empty if single pg
    if pdf_numpgs >= 2:
        dfs_otherpgs = tabula.read_pdf(filepath, stream=True, area=area_otherpgs,
                                       columns=cols_otherpgs, pages='2-' + str(pdf_numpgs),
                                       pandas_options={'header': None})
        # default setting - pandas_options={'header': 'infer'} has been overridden with pandas_options={'header': None}
        # Check first row contents; no headers present --> good, headers present --> drop and set headers manually
    # Processing
    df_rawdata = __concat_injreppgs(dflist_headpg=dfs_headpg, dflist_otherpgs=dfs_otherpgs)
    df_cleandata = __clean_injrep(df_rawdata)
    return df_cleandata
