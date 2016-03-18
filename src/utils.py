"""Custom utils and helpers for poolbot - including exceptions."""


class MissingConfigurationException(Exception):
    """Raised when a required setting is missing from the config.yaml file."""
    pass

