"""
This module contains utility functions for working with Hiri dates
(ref: https://www.muslimphilosophy.com/ip/hijri.htm)
"""

from datetime import datetime
from typing import Tuple

from django_interval.utils import DateTuple


def _last_day_of_hijri_year(hijri_year):
    is_leap_year = (11 * hijri_year + 14) % 30 == 0
    if is_leap_year:
        return 30
    return 29


def incomplete_hijridate_to_interval(
    hijri_date,
) -> Tuple[datetime, datetime, datetime]:
    """
    hijri date might contain
    (YYYY or YYY or YY or Y)(-MM or M optional)(-DD or D optional)
    """
    hijri_date = hijri_date.strip()
    before_hijri = hijri_date.endswith("bh")
    hijri_date = hijri_date.replace("ah", "").replace("bh", "").strip()
    dates = DateTuple()
    hijri_month = None
    hijri_day = None

    if hijri_date.endswith("c"):
        century = int(hijri_date[:-1].strip()) - 1
        from_date = hijri_to_gregorian(century * 100, 1, 1)
        to_date = hijri_to_gregorian(
            century * 100 + 99, 12, _last_day_of_hijri_year(century * 100 + 99)
        )
    else:
        date_parts = [p.strip() for p in hijri_date.split("-")]
        hijri_year = int(date_parts[0]) if not before_hijri else -int(date_parts[0])
        if len(date_parts) > 1:
            hijri_month = int(date_parts[1])
        if len(date_parts) > 2:
            # complete date
            hijri_day = int(date_parts[2])

        if not hijri_month:
            from_date = hijri_to_gregorian(hijri_year, 1, 1)
            to_date = hijri_to_gregorian(
                hijri_year, 12, _last_day_of_hijri_year(hijri_year)
            )

        elif not hijri_day:
            from_date = hijri_to_gregorian(hijri_year, hijri_month, 1)
            to_date = hijri_to_gregorian(
                hijri_year,
                hijri_month,
                _last_day_of_hijri_year(hijri_year) if hijri_month == 12 else 29,
            )

        else:
            from_date = hijri_to_gregorian(hijri_year, hijri_month, hijri_day)
            to_date = from_date

    dates.set_range(from_date, to_date)
    return dates.tuple()


def hijri_to_gregorian(hijri_year, hijri_month, hijri_day):
    """
    source: islToChr in https://www.muslimphilosophy.com/ip/hijri.htm
    """
    jd = (
        int((11 * hijri_year + 3) / 30)
        + 354 * hijri_year
        + 30 * hijri_month
        - int((hijri_month - 1) / 2)
        + hijri_day
        + 1948440
        - 385
    )
    if jd > 2299160:
        l = jd + 68569
        n = int((4 * l) / 146097)
        l = l - int((146097 * n + 3) / 4)
        i = int((4000 * (l + 1)) / 1461001)
        l = l - int((1461 * i) / 4) + 31
        j = int((80 * l) / 2447)
        d = l - int((2447 * j) / 80)
        l = int(j / 11)
        m = j + 2 - 12 * l
        y = 100 * (n - 49) + i + l
    else:
        j = jd + 1402
        k = int((j - 1) / 1461)
        l = j - 1461 * k
        n = int((l - 1) / 365) - int(l / 1461)
        i = l - 365 * n + 30
        j = int((80 * i) / 2447)
        d = i - int((2447 * j) / 80)
        i = int(j / 11)
        m = j + 2 - 12 * i
        y = 4 * k + n + i - 4716

    return datetime(y, m, d)
