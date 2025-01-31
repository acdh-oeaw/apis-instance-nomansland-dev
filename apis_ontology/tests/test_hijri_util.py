from django.test import SimpleTestCase

from apis_ontology.hijri_util import hijri_to_gregorian

from datetime import datetime as dt


class ParseHDateTestCase(SimpleTestCase):

    def setUp(self):
        pass

    def test_hijri_to_gregorain(self):
        gregorian_date = hijri_to_gregorian(60, 1, 1)
        self.assertEqual(gregorian_date.year, 679)
        self.assertEqual(gregorian_date.month, 10)
        self.assertEqual(gregorian_date.day, 13)

        gregorian_date = hijri_to_gregorian(630, 1, 1)
        self.assertEqual(gregorian_date.year, 1232)
        self.assertEqual(gregorian_date.month, 10)
        self.assertEqual(gregorian_date.day, 18)

        gregorian_date = hijri_to_gregorian(630, 12, 30)
        self.assertEqual(gregorian_date.year, 1233)
        self.assertEqual(gregorian_date.month, 10)
        self.assertEqual(gregorian_date.day, 7)

        gregorian_date = hijri_to_gregorian(688, 2, 1)
        self.assertEqual(gregorian_date.year, 1289)
        self.assertEqual(gregorian_date.month, 2)
        self.assertEqual(gregorian_date.day, 24)
