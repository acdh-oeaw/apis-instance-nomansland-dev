"""
This module contains utility functions for working with dates.

- parser functions for reading a range of dates
"""

from enum import Enum
from typing import Tuple
import calendar
import logging
from datetime import datetime, timedelta
from django_interval.utils import DateTuple
import re

from apis_ontology.hijri_util import incomplete_hijridate_to_interval


logger = logging.getLogger(__name__)


class DateType(Enum):
    START_DATE = "start_date"
    END_DATE = "end_date"


def last_day_of_month(year, month):
    """Return the last day of the month for the given year and month."""
    _, last_day = calendar.monthrange(year, month)
    return last_day


def incomplete_date_to_interval(date_str) -> Tuple[datetime, datetime, datetime]:
    """
    returns start and end dates in ISO format
    when an incomplete date is provided.
    - If the date string only contains the century,
      then the first and last dates of a century are used
    - If the date string only contains a year,
      then the first and last dates of a year are used
    - If the date string contains a year and month,
      then the first and last dates of the month are used
    """

    dates = DateTuple()
    if date_str.endswith("AH"):
        return incomplete_hijridate_to_interval(date_str)

    date_str = date_str.strip()
    if date_str.endswith("c"):
        century = int(date_str[:-1]) - 1
        from_date = datetime(century * 100, 1, 1)
        to_date = datetime(century * 100 + 99, 12, 31)
        dates.set_range(from_date, to_date)
        return dates.tuple()

    bce = date_str.endswith("BC")
    if bce:
        date_str = date_str.replace("BC", "")
        # TODO: Figure out how to handle BC dates
        return None, None, None

    date_parts = date_str.split("-")
    year = int(date_parts[0]) if not bce else int(date_parts[0])
    month, day = None, None
    from_date, to_date = None, None
    if len(date_parts) > 1:
        month = int(date_parts[1])
    if len(date_parts) > 2:
        # complete date
        day = int(date_parts[2])

    if not month:
        from_date = datetime(year, 1, 1)
        to_date = datetime(year, 12, 31)
    elif not day:
        from_date = datetime(year, month, 1)
        to_date = datetime(year, month, last_day_of_month(year, month))
    else:
        from_date = datetime(year, month, day)
        to_date = from_date

    dates.set_range(from_date, to_date)
    return dates.tuple()


def nomansland_dateparser(
    date_string: str,
) -> Tuple[datetime, datetime, datetime]:
    """
    This can be
    - a single date (exact) or
    - a date range with start (after, not before) and end (before, not after) dates or
    - two dates with a - separating the start and end dates
    - a date range with only start or
    - a date range with only end
    A single date (exact, start or end ) can be specified as a
    - date string, (YYYY | YYY | YY)(-MM optional)(-DD optional) format
    - only the century (YYYY or YY or YYY followed by c)
    - Hijri date (date or century followed by a H)
    """
    # https://nomansland.acdh-dev.oeaw.ac.at/apis/entities/entity/manuscript/21153/detail
    # 	- before 496/1102-3v
    date_string = date_string.strip()
    dates = DateTuple()
    try:
        if " - " in date_string:
            range_parts = date_string.split(" - ")
            _, from_date, _ = incomplete_date_to_interval(range_parts[0])
            _, _, to_date = incomplete_date_to_interval(range_parts[1])
            dates.set_range(from_date, to_date)
        elif date_string.startswith("-"):
            _, _, dates.to_date = incomplete_date_to_interval(date_string[1:])
        elif date_string.endswith("-"):
            _, dates.from_date, _ = incomplete_date_to_interval(date_string[:-1])
        else:
            pattern_desc_range = r"\b(before|not after|not before|after)\s+(\S+)"
            matches_desc_range = re.finditer(pattern_desc_range, date_string)
            groups_desc_range = {
                match.group(1): match.group(2) for match in matches_desc_range
            }

            if groups_desc_range:
                # before/after type of input
                for desc, date in groups_desc_range.items():
                    interval_middle, interval_start, interval_end = (
                        incomplete_date_to_interval(date)
                    )
                    if desc == "not after":
                        # to_date will be set to the beginning of the interval
                        dates.to_date = interval_end
                    elif desc == "after":
                        # from_date will be set one day after the end of the interval
                        dates.from_date = interval_end + timedelta(days=1)
                    elif desc == "before":
                        # to_date will be set to one day before this interval's beginning
                        dates.to_date = interval_start - timedelta(days=1)

                    elif desc == "not before":
                        # from_date will be set to this date
                        _, dates.from_date, _ = incomplete_date_to_interval(date)

                if dates.from_date and dates.to_date:
                    dates.set_range(dates.from_date, dates.to_date)
            else:
                # convert a single date to interval
                dates.sort_date, dates.from_date, dates.to_date = (
                    incomplete_date_to_interval(date_string)
                )

    except Exception as e:
        logger.debug("Could not parse date: '%s' due to error: %s", date_string, e)

    if not dates.sort_date:
        dates.sort_date = dates.from_date or dates.to_date

    return dates.tuple()
