import os
import unittest
from datetime import datetime, timedelta
import random
import pandas as pd
from nbainjuries import injury, _parser, _constants
from nbainjuries._util import _gen_url, _gen_filepath, _DT_LEGACYFMT1, _DT_LEGACYFMT2
from nbainjuries._exceptions import DataValidationError, URLRetrievalError, LocalRetrievalError


class getinjurydata_test(unittest.TestCase):
    def setUp(self):
        self.DATA_DIR = ('C:/Users/Michael Xu/Desktop/Sports Analytics/Projects/Data/Downloads/NBAOfficialInjReports/'
                         '2023-2024/regseas23-24')

    def test_randomurl(self):
        ts_start = _constants.dictkeydts['2122']['regseastart']
        ts_end = datetime(2021, 12, 31, 23, 30)
        hrs = int((ts_end - ts_start).total_seconds() / 3600)
        random.seed(42)
        ts_test = ts_start + timedelta(hours=random.randint(0, hrs))
        result = injury.get_reportdata(ts_test, return_df=True)
        print(f"Timestamp - {ts_test}")
        print(result.head(25))
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        for colx in result.columns:
            with self.subTest(colx=colx):
                self.assertIn(colx, _constants.expected_cols)

    def test_urlinvalid(self):
        ts_test = _constants.dictkeydts['2223']['asbstart'] + timedelta(hours=10)
        print(f"Timestamp - {ts_test}")
        with self.assertRaises(URLRetrievalError):
            result = injury.get_reportdata(ts_test)

    @unittest.skipIf(os.environ.get("CI", "").lower() == "true", "CI skip")
    def test_randomlocalvalid(self):
        while True:
            ts_start = _constants.dictkeydts['2324']['regseastart']
            ts_end = _constants.dictkeydts['2324']['regseaend']
            hrs = int((ts_end - ts_start).total_seconds() / 3600)
            random.seed(29)
            ts_test = ts_start + timedelta(hours=random.randint(0, hrs))
            try:
                result = injury.get_reportdata(ts_test, True, self.DATA_DIR, return_df=True)
                print(f"Timestamp - {ts_test}")
                print(result.head(25))
                self.assertIsInstance(result, pd.DataFrame)
                self.assertFalse(result.empty)
                for colx in result.columns:
                    with self.subTest(colx=colx):
                        self.assertIn(colx, _constants.expected_cols)
                break
            except LocalRetrievalError as LRerror:
                print(f"Regenerate datetime due to {LRerror}.")

    @unittest.skipIf(os.environ.get("CI", "").lower() == "true", "CI skip")
    def test_localinvalid(self):
        ts_test = datetime.now().replace(second=0, microsecond=0)
        print(f"Timestamp - {ts_test}")
        with self.assertRaises(LocalRetrievalError):
            result = injury.get_reportdata(ts_test, True, self.DATA_DIR, return_df=True)
            print(result.head(25))
        # alternative - remove assertRaises statement and add below to fail
        # self.assertIsInstance(result, pd.DataFrame)
        # self.assertFalse(result.empty)

    @unittest.skip('Header edge case getting blocked; needs refactor or omit')
    def test_headersedgecase(self):
        ts_test = datetime.now().replace(minute=30, second=0, microsecond=0) - timedelta(days=30)
        custom_headers = {
            "User-Agent": "TestAgent/1.0 (Compatible; EdgeCaseBot)",
            "Accept": "application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US;q=0.7,en;q=0.3",
            "Accept-Encoding": "gzip, deflate",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Connection": "keep-alive",
        }
        result = injury.get_reportdata(ts_test, headers=custom_headers, return_df=True)
        print(f"Timestamp - {ts_test}")
        print(result.head(25))
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        for colx in result.columns:
            with self.subTest(colx=colx):
                self.assertIn(colx, _constants.expected_cols)

    def test_headersinvalid(self):
        ts_test = datetime.now().replace(minute=30, second=0, microsecond=0) - timedelta(days=15)
        fail_customheaders = {"xyz"}
        with self.assertRaises(AttributeError):
            result = injury.get_reportdata(ts_test, headers=fail_customheaders)
            print(f"Timestamp - {ts_test}")
            print(result.head(25))
        # alternative - remove assertRaises statement and add below to fail
        # self.assertIsInstance(result, pd.DataFrame)
        # self.assertFalse(result.empty)


# TODO revise the checkreportvalid tests to acct for new URLRetrievalError raised from _parser.validate_injrepurl
class checkreportvalid_test(unittest.TestCase):
    def test_random(self):
        ts_start = datetime(2022, 10, 17, 0, 30)
        ts_end = datetime(2023, 6, 12, 23, 30)
        hrs = int((ts_end - ts_start).total_seconds()/3600)
        random.seed(42)
        ts_test = ts_start + timedelta(hours=random.randint(0, hrs))
        result = injury.check_reportvalid(ts_test)
        print(f"Report at {ts_test}, url {injury.gen_url(ts_test)}, validation status {result}")
        self.assertIsInstance(result, bool)

    def test_invalidfuture(self):
        ts_test = (datetime.now() + timedelta(days=30)).replace(minute=30, second=0, microsecond=0)
        result = injury.check_reportvalid(ts_test)
        print(f"Timestamp - {ts_test}")
        self.assertEqual(result, False)

    def test_invalidpast(self):
        ts_test = datetime(2022, 2, 22, 20, 30)
        result = injury.check_reportvalid(ts_test)
        print(f"Timestamp - {ts_test}")
        self.assertEqual(result, False)

    def test_valid(self):
        random.seed(29)
        ts_test = _constants.dictkeydts['2324']['regseastart'] + timedelta(hours=random.randint(0, 730))
        result = injury.check_reportvalid(ts_test)
        print(f"Timestamp - {ts_test}")
        self.assertEqual(result, True)

    def test_headers(self):
        random.seed(100)
        ts_test = _constants.dictkeydts['2324']['regseastart'] + timedelta(hours=random.randint(0, 730))
        result = injury.check_reportvalid(ts_test, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
                                                            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                                                            "Accept-Language": "en-US,en;q=0.9",
                                                            "Accept-Encoding": "gzip, deflate, br",
                                                            "Connection": "keep-alive",
                                                            "Upgrade-Insecure-Requests": "1"})
        print(f"Timestamp - {ts_test}")
        self.assertEqual(result, True)

    def test_headersinvalid(self):
        ts_test = datetime.now().replace(minute=30, second=0, microsecond=0) - timedelta(days=15)
        fail_customheaders = {'xyz'}
        result = injury.check_reportvalid(ts_test, headers=fail_customheaders)
        print(f"Timestamp - {ts_test}")
        self.assertEqual(result, False)


@unittest.skipIf(os.environ.get("CI", "").lower() == "true", "CI skip")
class validateheaders_test(unittest.TestCase):
    def test_headersvalid(self):
        ts_start = _constants.dictkeydts['2122']['regseastart']
        ts_end = datetime(2021, 12, 31, 23, 30)
        hrs = int((ts_end - ts_start).total_seconds() / 3600)
        ts_test = ts_start + timedelta(hours=random.randint(0, hrs))
        result = injury.get_reportdata(ts_test, return_df=True)
        print(f"Timestamp - {ts_test}")
        self.assertEqual(_parser._validate_headers(result), True)

    def test_headersinvalid(self):
        ts_start = _constants.dictkeydts['2122']['regseastart']
        ts_end = datetime(2021, 12, 31, 23, 30)
        hrs = int((ts_end - ts_start).total_seconds() / 3600)
        ts_test = ts_start + timedelta(hours=random.randint(0, hrs))
        result = injury.get_reportdata(ts_test, return_df=True)
        resultx = result[random.sample(list(result.columns), len(result.columns))]
        print(f"Timestamp - {ts_test}")
        print(resultx.head(25))
        with self.assertRaises(DataValidationError):
            _parser._validate_headers(resultx)


class genurl_test(unittest.TestCase):
    """Tests for URL generation covering old and new formats.
    """

    def test_old_format_structure(self):
        """Test legacy format before _DT_LEGACYFMT1"""
        ts = datetime(2024, 1, 15, 17, 30)
        url = _gen_url(ts)
        self.assertIn('Injury-Report_2024-01-15_05PM.pdf', url)
        self.assertNotIn('05_00PM', url)

    def test_new_format_structure(self):
        """Test new format (on/after _DT_NEWFMT15M)"""
        ts = datetime(2026, 1, 6, 17, 0)
        url = _gen_url(ts)
        self.assertIn('Injury-Report_2026-01-06_05_00PM.pdf', url)

    def test_transition_date_legacyfmt1(self):
        """Test the format boundary at _DT_LEGACYFMT1."""
        ts = _DT_LEGACYFMT1
        url = _gen_url(ts)
        self.assertIn('_03PM.pdf', url)
        self.assertNotIn('_03_00PM.pdf', url)

    def test_transition_date_legacyfmt2(self):
        """Test the format boundary at _DT_LEGACYFMT2."""
        ts = _DT_LEGACYFMT2
        url = _gen_url(ts)
        self.assertIn('_04PM.pdf', url)
        self.assertNotIn('_04_00PM.pdf', url)

    def test_legacy_gap_err(self):
        gap_time = _DT_LEGACYFMT1 + timedelta(minutes=10)
        with self.assertRaises(ValueError):
            _gen_url(gap_time)
        gap_time2 = _DT_LEGACYFMT2 - timedelta(minutes=10)
        with self.assertRaises(ValueError):
            _gen_url(gap_time2)

    def test_old_format_random_hm1(self):
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        ts = datetime(2024, 3, 15, hour, minute)  # before legacy format 1
        expected_hour = ts.replace(minute=0).strftime('%I%p')
        url = _gen_url(ts)
        self.assertIn(f'_{expected_hour}.pdf', url)

    def test_old_format_random_hm2(self):
        hour = random.randint(0, 8)
        minute = random.randint(0, 59)
        ts = datetime(2025, 12, 22, hour, minute)  # legacy format 2
        expected_hour = ts.replace(minute=0).strftime('%I%p')
        url = _gen_url(ts)
        self.assertIn(f'_{expected_hour}.pdf', url)

    def test_old_format_am_time(self):
        ts = datetime(2024, 3, 10, 9, 30)
        url = _gen_url(ts)
        self.assertIn('_09AM.pdf', url)

    def test_old_format_pm_time(self):
        ts = datetime(2024, 3, 10, 14, 30)
        url = _gen_url(ts)
        self.assertIn('_02PM.pdf', url)

    def test_old_format_noon(self):
        ts = datetime(2024, 3, 10, 12, 30)
        url = _gen_url(ts)
        self.assertIn('_12PM.pdf', url)

    def test_old_format_midnight(self):
        ts = datetime(2024, 3, 10, 0, 30)
        url = _gen_url(ts)
        self.assertIn('_12AM.pdf', url)

    def test_new_format_with_minutes(self):
        ts = datetime(2026, 1, 6, 17, 30)
        url = _gen_url(ts)
        self.assertIn('_05_30PM.pdf', url)

    def test_new_format_15_min_intervals(self):
        """Test new format at typical 15-minute intervals."""
        base = datetime(2026, 1, 6, 14, 0)
        expected_times = ['02_00PM', '02_15PM', '02_30PM', '02_45PM']
        for i, expected in enumerate(expected_times):
            ts = base + timedelta(minutes=i*15)
            url = _gen_url(ts)
            self.assertIn(f'_{expected}.pdf', url, f"Failed for {ts}")

    def test_new_format_am_time(self):
        ts = datetime(2026, 1, 6, 9, 15)
        url = _gen_url(ts)
        self.assertIn('_09_15AM.pdf', url)

    def test_new_format_noon(self):
        ts = datetime(2026, 1, 6, 12, 0)
        url = _gen_url(ts)
        self.assertIn('_12_00PM.pdf', url)

    def test_new_format_midnight(self):
        ts = datetime(2026, 1, 6, 0, 0)
        url = _gen_url(ts)
        self.assertIn('_12_00AM.pdf', url)

    def test_url_base_path(self):
        ts = datetime(2024, 1, 15, 17, 0)
        url = _gen_url(ts)
        self.assertTrue(url.startswith('https://ak-static.cms.nba.com/referee/injury/Injury-Report_'))

    def test_gen_url_matches_injury_gen_url(self):
        test_dates = [
            datetime(2024, 1, 15, 17, 0),
            datetime(2025, 12, 21, 12, 0),
            datetime(2025, 12, 22, 12, 0),
            datetime(2026, 1, 6, 17, 30),
        ]
        for ts in test_dates:
            with self.subTest(ts=ts):
                self.assertEqual(_gen_url(ts), injury.gen_url(ts))


class genfilepath_test(unittest.TestCase):
    def test_old_format_filepath(self):
        ts = datetime(2024, 1, 15, 17, 30)
        filepath = _gen_filepath(ts, '/data/reports')
        self.assertIn('Injury-Report_2024-01-15_05PM.pdf', filepath)

    def test_new_format_filepath(self):
        """Test filepath generation for new format dates."""
        ts = datetime(2026, 1, 6, 17, 45)
        filepath = _gen_filepath(ts, '/data/reports')
        self.assertIn('Injury-Report_2026-01-06_05_45PM.pdf', filepath)

    def test_filepath_includes_directory(self):
        ts = datetime(2024, 1, 15, 17, 0)
        filepath = _gen_filepath(ts, '/my/custom/path')
        self.assertTrue(filepath.startswith('/my/custom/path'))


if __name__ == "__main__":
    unittest.TextTestRunner().run(unittest.TestLoader().loadTestsFromTestCase(genurl_test))
    unittest.TextTestRunner().run(unittest.TestLoader().loadTestsFromTestCase(genfilepath_test))
    unittest.TextTestRunner().run(unittest.TestLoader().loadTestsFromTestCase(getinjurydata_test))
    unittest.TextTestRunner().run(unittest.TestLoader().loadTestsFromTestCase(checkreportvalid_test))
    unittest.TextTestRunner().run(unittest.TestLoader().loadTestsFromTestCase(validateheaders_test))

