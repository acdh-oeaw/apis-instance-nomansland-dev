from django.test import SimpleTestCase

from apis_ontology.date_utils import nomansland_dateparser
from datetime import datetime as dt


class ParseHDateTestCase(SimpleTestCase):

    def setUp(self):
        pass

    def test_century_suffix(self):
        _, from_date, to_date = nomansland_dateparser("7c")
        self.assertEqual(from_date, dt.fromisoformat("0600-01-01"))
        self.assertEqual(to_date, dt.fromisoformat("0699-12-31"))

    def test_only_start(self):
        sort_date, from_date, to_date = nomansland_dateparser("1815 -")
        self.assertEqual(from_date, dt.fromisoformat("1815-01-01"))
        self.assertEqual(sort_date, from_date)
        self.assertEqual(to_date, None)

        sort_date, from_date, to_date = nomansland_dateparser("1815-11 -")
        self.assertEqual(from_date, dt.fromisoformat("1815-11-01"))
        self.assertEqual(sort_date, from_date)
        self.assertEqual(to_date, None)

        sort_date, from_date, to_date = nomansland_dateparser("1815-01-05 -")
        self.assertEqual(from_date, dt.fromisoformat("1815-01-05"))
        self.assertEqual(sort_date, from_date)
        self.assertEqual(to_date, None)

    def test_only_end(self):
        sort_date, from_date, to_date = nomansland_dateparser("- 1989-01")
        self.assertEqual(to_date, dt.fromisoformat("1989-01-31"))
        self.assertEqual(sort_date, to_date)
        self.assertEqual(from_date, None)

        sort_date, from_date, to_date = nomansland_dateparser("- 1989-11")
        self.assertEqual(to_date, dt.fromisoformat("1989-11-30"))
        self.assertEqual(sort_date, to_date)

        sort_date, from_date, to_date = nomansland_dateparser("- 1989-11-05")
        self.assertEqual(to_date, dt.fromisoformat("1989-11-05"))
        self.assertEqual(sort_date, to_date)

    def test_range(self):
        sort_date, from_date, to_date = nomansland_dateparser("130 - 1989-01")
        self.assertEqual(to_date, dt.fromisoformat("1989-01-31"))
        self.assertEqual(from_date, dt.fromisoformat("0130-01-01"))

        sort_date, from_date, to_date = nomansland_dateparser("9c - 1989-01")
        self.assertEqual(to_date, dt.fromisoformat("1989-01-31"))
        self.assertEqual(from_date, dt.fromisoformat("0800-01-01"))

    def test_before(self):
        sort_date, from_date, to_date = nomansland_dateparser("before 7c")
        self.assertEqual(to_date, dt.fromisoformat("0599-12-31"))
        self.assertEqual(sort_date, dt.fromisoformat("0599-12-31"))
        self.assertEqual(from_date, None)

    def test_not_before(self):
        sort_date, from_date, to_date = nomansland_dateparser("not before 7c")
        self.assertEqual(from_date, dt.fromisoformat("0600-01-01"))
        self.assertEqual(sort_date, dt.fromisoformat("0600-01-01"))
        self.assertEqual(to_date, None)

    def test_after(self):
        sort_date, from_date, to_date = nomansland_dateparser("after 7c")
        self.assertEqual(from_date, dt.fromisoformat("0700-01-01"))
        self.assertEqual(sort_date, dt.fromisoformat("0700-01-01"))
        self.assertEqual(to_date, None)

    def test_not_after(self):
        sort_date, from_date, to_date = nomansland_dateparser("not after 7c")
        self.assertEqual(to_date, dt.fromisoformat("0699-12-31"))
        self.assertEqual(sort_date, dt.fromisoformat("0699-12-31"))
        self.assertEqual(from_date, None)

        sort_date, from_date, to_date = nomansland_dateparser("not after 1985-04-03")
        self.assertEqual(to_date, dt.fromisoformat("1985-04-03"))
        self.assertEqual(sort_date, dt.fromisoformat("1985-04-03"))
        self.assertEqual(from_date, None)

    def test_BC(self):
        # TODO: handle BC dates better and rewrite failing tests
        sort_date, from_date, to_date = nomansland_dateparser("315 BC")
        self.assertIsNone(from_date)
        self.assertIsNone(sort_date)
        self.assertIsNone(to_date)

        sort_date, from_date, to_date = nomansland_dateparser("315-11 BC")
        self.assertIsNone(from_date)
        self.assertIsNone(sort_date)
        self.assertIsNone(to_date)

        sort_date, from_date, to_date = nomansland_dateparser("315-01-05 BC")
        self.assertIsNone(from_date)
        self.assertIsNone(sort_date)
        self.assertIsNone(to_date)

    def test_flourish_date(self):
        sort_date, from_date, to_date = nomansland_dateparser("fl. 7c ")
        self.assertEqual(from_date, dt.fromisoformat("0600-01-01"))
        self.assertEqual(to_date, dt.fromisoformat("0699-12-31"))
        self.assertEqual(sort_date, dt.fromisoformat("0649-12-31"))

        sort_date, from_date, to_date = nomansland_dateparser("flourish 7c ")
        self.assertEqual(from_date, dt.fromisoformat("0600-01-01"))
        self.assertEqual(to_date, dt.fromisoformat("0699-12-31"))
        self.assertEqual(sort_date, dt.fromisoformat("0649-12-31"))
