class SamsungTVError(Exception):
    """Samsung TV Exception Base Class"""

    def __init__(self, *args):
        self._args = args

    def __str__(self):

        if self._args:
            return self.__class__.__doc__ % self._args

        return self.__class__.__doc__


class AccessDenied(SamsungTVError):
    """Connection was denied."""


class ConnectionClosed(SamsungTVError):
    """Connection was closed."""


class UnhandledResponse(SamsungTVError):
    """Received unknown response."""


class NoTVFound(SamsungTVError):
    """ Unable to locate a TV."""


class ConfigError(SamsungTVError):
    """Base class for config exceptions."""


class ConfigUnknownMethod(ConfigError):
    """Unknown connection method."""


class ConfigParseError(ConfigError):
    """Config data is not json formatted or is not a formatted flat file."""


class ConfigLoadError(ConfigError):
    """Config path specified cannot be located."""


class ConfigSavePathError(ConfigError):
    """Config save path %s is not valid."""


class ConfigSaveError(ConfigError):
    """Error saving config."""


class ConfigSavePathNotSpecified(ConfigError):
    """Config save path was not specified."""


class ConfigParameterError(ConfigError):
    """Parameter %s is not a config parameter."""
