"""ADB-related exceptions.

"""


from . import constants


class AdbCommandFailureException(Exception):
    """A ``b'FAIL'`` packet was received.

    """


class DeviceAuthError(Exception):
    """Device authentication failed.

    """
    def __init__(self, message, *args):
        message %= args
        super(DeviceAuthError, self).__init__(message, *args)


class InterleavedDataError(Exception):
    """We only support command sent serially.

    """


class InvalidChecksumError(Exception):
    """Checksum of data didn't match expected checksum.

    """


class InvalidCommandError(Exception):
    """Got an invalid command.

    """
    def __init__(self, message, response_header, response_data):
        if response_header == constants.FAIL:
            message = 'Command failed, device said so. (%s)' % message
        super(InvalidCommandError, self).__init__(message, response_header, response_data)


class InvalidResponseError(Exception):
    """Got an invalid response to our command.

    """


class TcpTimeoutException(Exception):
    """TCP connection timed read/write operation exceeded the allowed time.

    """
