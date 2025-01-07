from django.test import TestCase
from django.conf import settings

from apis_ontology.date_utils import parse_hdate


class ParseHDateTestCase(TestCase):
    databases = "__all__"

    def setUp(self):
        settings.DATABASES = {}

    def test_hdate_only_year(self):
        date_sort, date_start, date_end = parse_hdate("311AH")
        self.assertEqual(date_end, None)
