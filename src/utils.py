"""Custom utils and helpers for poolbot - including exceptions."""

from datetime import datetime


class MissingConfigurationException(Exception):
    """Raised when a required setting is missing from the config.yaml file."""
    pass


def format_datetime_to_date(date):
    """Returns only the date representation of a datetime string."""
    return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ").date()
