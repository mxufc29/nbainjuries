import unittest
from datetime import datetime, timedelta
import random
import pandas as pd
from injuries import Injury, _constants


class getinjurydata_test(unittest.TestCase):
    def setUp(self):
        self.DATA_DIR = 'C:/Users/Michael Xu/Desktop/Sports Analytics/Projects/Data/Downloads/NBAOfficialInjReports/2023-2024/regseas23-24'
        self.expected_cols = ['Game Date', 'Game Time', 'Matchup', 'Team', 'Player Name', 'Current Status', 'Reason',
                              'ReportTime']

    def test_randomurl(self):
        ts_start = _constants.dictkeydts['2122']['regseastart']
        ts_end = datetime(2021, 12, 31, 23, 30)
        hrs = int((ts_end - ts_start).total_seconds() / 3600)
        random.seed(42)
        ts_test = ts_start + timedelta(hours=random.randint(0, hrs))
        result = Injury.get_injurydata(ts_test)
        print(f"Timestamp - {ts_test}")
        print(result.head(25))
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        for colx in result.columns:
            with self.subTest(colx=colx):
                self.assertIn(colx, self.expected_cols)

    def test_urlinvalid(self):
        ts_test = _constants.dictkeydts['2223']['asbstart'] + timedelta(hours=10)
        with self.assertRaises(FileNotFoundError):
            result = Injury.get_injurydata(ts_test)
            print(f"Timestamp - {ts_test}")
            print(result.head(25))
            self.assertIsInstance(result, pd.DataFrame)
            self.assertFalse(result.empty)

    def test_randomlocalvalid(self):
        while True:
            ts_start = _constants.dictkeydts['2324']['regseastart']
            ts_end = _constants.dictkeydts['2324']['regseaend']
            hrs = int((ts_end - ts_start).total_seconds() / 3600)
            random.seed(29)
            ts_test = ts_start + timedelta(hours=random.randint(0, hrs))
            try:
                result = Injury.get_injurydata(ts_test, True, self.DATA_DIR)
                print(f"Timestamp - {ts_test}")
                print(result.head(25))
                self.assertIsInstance(result, pd.DataFrame)
                self.assertFalse(result.empty)
                for colx in result.columns:
                    with self.subTest(colx=colx):
                        self.assertIn(colx, self.expected_cols)
                break
            except FileNotFoundError as FNFerror:
                print(f"Regenerate datetime due to {FNFerror}.")

    def test_localinvalid(self):
        ts_test = datetime.now().replace(second=0, microsecond=0)
        with self.assertRaises(FileNotFoundError):
            result = Injury.get_injurydata(ts_test, True, self.DATA_DIR)
            print(f"Timestamp - {ts_test}")
            print(result.head(25))
        # alternative - remove assertRaises statement and add below to fail
        # self.assertIsInstance(result, pd.DataFrame)
        # self.assertFalse(result.empty)

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
        result = Injury.get_injurydata(ts_test, headers=custom_headers)
        print(f"Timestamp - {ts_test}")
        print(result.head(25))
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        for colx in result.columns:
            with self.subTest(colx=colx):
                self.assertIn(colx, self.expected_cols)

    def test_headersinvalid(self):
        ts_test = datetime.now().replace(minute=30, second=0, microsecond=0) - timedelta(days=15)
        fail_customheaders = {'xyz'}
        with self.assertRaises(FileNotFoundError):
            result = Injury.get_injurydata(ts_test, headers=fail_customheaders)
            print(f"Timestamp - {ts_test}")
            print(result.head(25))
        # alternative - remove assertRaises statement and add below to fail
        # self.assertIsInstance(result, pd.DataFrame)
        # self.assertFalse(result.empty)


class checkreportvalid_test(unittest.TestCase):
    def test_random(self):
        ts_start = datetime(2022, 10, 17, 0, 30)
        ts_end = datetime(2023, 6, 12, 23, 30)
        hrs = int((ts_end - ts_start).total_seconds()/3600)
        random.seed(42)
        ts_test = ts_start + timedelta(hours=random.randint(0, hrs))
        result = Injury.check_reportvalid(ts_test)
        print(f"Report at {ts_test}, url {Injury.gen_injreplink(ts_test)}, validation status {result}")
        self.assertIsInstance(result, bool)

    def test_invalidfuture(self):
        ts_test = (datetime.now() + timedelta(days=30)).replace(minute=30, second=0, microsecond=0)
        result = Injury.check_reportvalid(ts_test)
        print(f"Timestamp - {ts_test}")
        self.assertEqual(result, False)

    def test_invalidpast(self):
        ts_test = datetime(2022, 2, 22, 20, 30)
        result = Injury.check_reportvalid(ts_test)
        print(f"Timestamp - {ts_test}")
        self.assertEqual(result, False)

    def test_valid(self):
        random.seed(29)
        ts_test = _constants.dictkeydts['2324']['regseastart'] + timedelta(hours=random.randint(0, 730))
        result = Injury.check_reportvalid(ts_test)
        print(f"Timestamp - {ts_test}")
        self.assertEqual(result, True)

    def test_headers(self):
        random.seed(100)
        ts_test = _constants.dictkeydts['2324']['regseastart'] + timedelta(hours=random.randint(0, 730))
        result = Injury.check_reportvalid(ts_test, headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
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
        result = Injury.check_reportvalid(ts_test, headers=fail_customheaders)
        print(f"Timestamp - {ts_test}")
        self.assertEqual(result, False)

if __name__ == "__main__":
    unittest.TextTestRunner().run(unittest.TestLoader().loadTestsFromTestCase(getinjurydata_test))
    unittest.TextTestRunner().run(unittest.TestLoader().loadTestsFromTestCase(checkreportvalid_test))

