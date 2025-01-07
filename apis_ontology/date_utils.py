"""
This module contains utility functions for working with dates.

- parser functions for reading a range of dates
- conversion functions between ISO and Hijri dates (ref: https://www.muslimphilosophy.com/ip/hijri.htm)
"""

import calendar
import logging
from django_interval.utils import DateTuple

logger = logging.getLogger(__name__)


def last_day_of_month(year, month):
    """Return the last day of the month for the given year and month."""
    _, last_day = calendar.monthrange(year, month)
    return last_day


def parse_hdate(date_string):
    """ """
    try:
        dates = DateTuple()
        return dates.tuple()
    except Exception as e:
        logger.error("Could not parse date: '", date_string, "' due to error: ", e)

    return None, None, None
