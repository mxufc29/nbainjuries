from os import PathLike
import os
import tempfile
import pandas as pd
import PyPDF2
from io import BytesIO
from ._exceptions import URLRetrievalError, LocalRetrievalError
from ._util import __concat_injreppgs, _validate_headers, _pagect_localpdf, __clean_injrep
from ._constants import requestheaders
import asyncio
import aiohttp
from aiohttp import ClientSession
import threading
import jpype
# import jpype.imports
# from tabula.backend import jar_path
# jpype.addClassPath(jar_path())
# jvmpath = jpype.getDefaultJVMPath()
# java_opts = ["-Dfile.encoding=UTF-8", "-Xrs"]
# jpype.startJVM(jvmpath, *java_opts, convertStrings=False)
import tabula

_jvm_lock = threading.Lock()


def _download_pdf_bytes_sync(url: str, headers: dict | None = None) -> bytes:
    """Download PDF bytes using curl_cffi (sync), for use in asyncio.to_thread."""
    from curl_cffi import requests as cffi_requests
    hdrs = headers if headers is not None else requestheaders
    resp = cffi_requests.get(url, impersonate='chrome', headers=hdrs, timeout=30)
    resp.raise_for_status()
    return resp.content


async def validate_irurl_async(filepath: str | PathLike, session: ClientSession, **kwargs):
    """
    :param filepath: url of report
    :param session:
    :param kwargs: custom headers
    :return: PDF content bytes (if validation succeeds)
    """
    try:
        # Try curl_cffi first (in a thread since it's sync) to bypass Akamai bot detection
        headers = kwargs.get('headers', requestheaders)
        pdf_content = await asyncio.to_thread(_download_pdf_bytes_sync, filepath, headers)
        print(f"Validated {filepath.split('/')[-1].rsplit('.', 1)[0]}.")
        return pdf_content
    except ImportError:
        # Fall back to aiohttp if curl_cffi is not installed
        try:
            async with session.get(filepath, **kwargs) as resp:
                resp.raise_for_status()
                print(f"Validated {filepath.split('/')[-1].rsplit('.', 1)[0]}.")
                return await resp.read()
        except aiohttp.ClientError as e_gen:
            print(f"Failed validation - {filepath.split('/')[-1].rsplit('.', 1)[0]}.")
            raise URLRetrievalError(filepath, e_gen)
    except Exception as e_gen:
        print(f"Failed validation - {filepath.split('/')[-1].rsplit('.', 1)[0]}.")
        raise URLRetrievalError(filepath, e_gen)
        ## TODO logging?


def _read_pdfjvmwrap(*args, **kwargs):
    """
    Wrapper to coordinate jpype/JVM
    """
    with _jvm_lock:
        if not jpype.isJVMStarted():
            jvmpath = jpype.getDefaultJVMPath()
            java_opts = ["-Dfile.encoding=UTF-8", "-Xrs"]
            jpype.startJVM(jvmpath, *java_opts, convertStrings=False)
        result = tabula.read_pdf(*args, **kwargs)
    return result


async def extract_irurl_async(filepath: str | PathLike, session: ClientSession, area_headpg: list, cols_headpg: list,
                      area_otherpgs: list | None = None, cols_otherpgs: list | None = None,
                      **kwargs) -> pd.DataFrame:
    """
    :param filepath: url of report
    :param session:
    :param area_headpg: area boundaries of first pg of pdf
    :param cols_headpg: column boundaries of first pg of pdf
    :param area_otherpgs: area boundaries of other pgs of pdf if needed
    :param cols_otherpgs: column boundaries of other pgs of pdf if needed
    :param kwargs: custom headers
    :return:
    """
    pdf_content = await validate_irurl_async(filepath, session, **kwargs)
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
        dfs_headpg = await asyncio.to_thread(_read_pdfjvmwrap, tmp_path, stream=True,
                                             area=area_headpg, columns=cols_headpg, pages=1)
        _validate_headers(dfs_headpg[0])
        # Following pgs
        dfs_otherpgs = []  # default to empty if single pg
        if pdf_numpgs >= 2:
            dfs_otherpgs = await asyncio.to_thread(_read_pdfjvmwrap, tmp_path, stream=True,
                                                   area=area_otherpgs, columns=cols_otherpgs,
                                                   pages='2-' + str(pdf_numpgs),
                                                   pandas_options={'header': None})
            # default to pandas_options={'header': 'infer'}
            # Override with pandas_options={'header': None}; manually drop included headers if necessary
        # Processing
        df_rawdata = __concat_injreppgs(dflist_headpg=dfs_headpg, dflist_otherpgs=dfs_otherpgs)
        df_cleandata = __clean_injrep(df_rawdata)
        return df_cleandata
    finally:
        os.unlink(tmp_path)


async def extract_irlocal_async(filepath: str | PathLike, area_headpg: list, cols_headpg: list,
                        area_otherpgs: list | None = None, cols_otherpgs: list | None = None) -> pd.DataFrame:
    try:
        pdf_numpgs = await asyncio.to_thread(_pagect_localpdf, filepath)
    except (FileNotFoundError, PermissionError) as e_gen:
        raise LocalRetrievalError(filepath, e_gen)
        ## potential logging
        # archive FileNotFoundError(f'Could not open {str(filepath)} due to {e_gen}.')

    if area_otherpgs is None:
        area_otherpgs = area_headpg
    if cols_otherpgs is None:
        cols_otherpgs = cols_headpg

    # First page
    dfs_headpg = await asyncio.to_thread(_read_pdfjvmwrap, filepath, stream=True, area=area_headpg,
                                 columns=cols_headpg, pages=1)
    _validate_headers(dfs_headpg[0])
    # Following pgs
    dfs_otherpgs = []  # default to empty if single pg
    if pdf_numpgs >= 2:
        dfs_otherpgs = await asyncio.to_thread(_read_pdfjvmwrap, filepath, stream=True, area=area_otherpgs,
                                       columns=cols_otherpgs, pages='2-' + str(pdf_numpgs), pandas_options={'header': None})
        # default setting - pandas_options={'header': 'infer'} has been overridden with pandas_options={'header': None}
        # Check first row contents; no headers present --> good, headers present --> drop and set headers manually
    # Processing
    df_rawdata = __concat_injreppgs(dflist_headpg=dfs_headpg, dflist_otherpgs=dfs_otherpgs)
    df_cleandata = __clean_injrep(df_rawdata)
    return df_cleandata
