"""Module to parse dates"""
import datetime
import re

SPACE = " "
DASH = "-"
DOT = "."
FWD_SLASH = "/"


def match_date(date):
    """Check if a string is a valid date

        Args:
            date(str)

        Returns:
            bool
    """
    date_pattern = re.compile(
        r"^(19|20)\d\d[- /.](0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])"
    )
    if re.match(date_pattern, date):
        return True

    return False


def get_date(date, date_format=None):
    """Return a datetime object if there is a valid date

        Raise exception if date is not valid
        Return todays date if no date where added

        Args:
            date(str)
            date_format(str)

        Returns:
            date_obj(datetime.datetime)
    """
    if not date:
        return datetime.datetime.now()

    if date_format:
        return datetime.datetime.strptime(date, date_format)

    if not match_date(date):
        raise ValueError("Date %s is invalid" % date)

    for separator in [DASH, SPACE, DOT, FWD_SLASH]:
        splited_date = date.split(separator)
        if len(splited_date) == 3:
            return datetime.datetime(*(int(number) for number in splited_date))

    raise ValueError("Date %s is invalid" % date)
