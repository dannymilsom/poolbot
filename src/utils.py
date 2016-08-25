"""Custom utils and helpers for poolbot - including exceptions."""

from datetime import datetime


class MissingConfigurationException(Exception):
    """Raised when a required setting is missing from the config.yaml file."""
    pass


def format_datetime_to_date(date):
    """Returns only the date representation of a datetime string."""
    return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ").date()


def get_ordinal_extension(number):
    """Returns the extension for a date - for example 1->1st, 5->5th."""
    return "%d%s" % (number, "tsnrhtdd"[(number/10%10!=1)*(number%10<4)*number%10::4])
