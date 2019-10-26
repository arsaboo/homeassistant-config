"""Classes to manage ADB connections.

* :py:class:`ADBPython` utilizes a Python implementation of the ADB protocol.
* :py:class:`ADBServer` utilizes an ADB server to communicate with the device.

"""


import logging
from socket import error as socket_error
import sys
import threading

from .adb_shell.adb_device import AdbDevice
from .adb_shell.auth.sign_pythonrsa import PythonRSASigner
from custom_components.androidtv.androidtv.ppadb.client import Client

from .constants import DEFAULT_AUTH_TIMEOUT_S

_LOGGER = logging.getLogger(__name__)

#: Use a timeout for the ADB threading lock if it is supported
LOCK_KWARGS = {'timeout': 3} if sys.version_info[0] > 2 and sys.version_info[1] > 1 else {}

if sys.version_info[0] == 2:  # pragma: no cover
    FileNotFoundError = IOError  # pylint: disable=redefined-builtin


class ADBPython(object):
    """A manager for ADB connections that uses a Python implementation of the ADB protocol.

    Parameters
    ----------
    host : str
        The address of the device in the format ``<ip address>:<host>``
    adbkey : str
        The path to the ``adbkey`` file for ADB authentication

    """
    def __init__(self, host, adbkey=''):
        self.host = host
        self.adbkey = adbkey
        self._adb = AdbDevice(serial=self.host, default_timeout_s=9.)

        # keep track of whether the ADB connection is intact
        self._available = False

        # use a lock to make sure that ADB commands don't overlap
        self._adb_lock = threading.Lock()

    @property
    def available(self):
        """Check whether the ADB connection is intact.

        Returns
        -------
        bool
            Whether or not the ADB connection is intact

        """
        return self._adb.available

    def close(self):
        """Close the ADB socket connection.

        """
        self._adb.close()

    def connect(self, always_log_errors=True, auth_timeout_s=DEFAULT_AUTH_TIMEOUT_S):
        """Connect to an Android TV / Fire TV device.

        Parameters
        ----------
        always_log_errors : bool
            If True, errors will always be logged; otherwise, errors will only be logged on the first failed reconnect attempt
        auth_timeout_s : float
            Authentication timeout (in seconds)

        Returns
        -------
        bool
            Whether or not the connection was successfully established and the device is available

        """
        self._adb_lock.acquire(**LOCK_KWARGS)  # pylint: disable=unexpected-keyword-arg

        # Make sure that we release the lock
        try:
            # Catch errors
            try:
                if self.adbkey:
                    # private key
                    with open(self.adbkey) as f:
                        priv = f.read()

                    # public key
                    try:
                        with open(self.adbkey + '.pub') as f:
                            pub = f.read()
                    except FileNotFoundError:
                        pub = ''

                    signer = PythonRSASigner(pub, priv)

                    # Connect to the device
                    self._adb.connect(rsa_keys=[signer], auth_timeout_s=auth_timeout_s)
                else:
                    self._adb.connect(auth_timeout_s=auth_timeout_s)

                # ADB connection successfully established
                self._available = True
                _LOGGER.debug("ADB connection to %s successfully established", self.host)

            except socket_error as serr:
                if self._available or always_log_errors:
                    if serr.strerror is None:
                        serr.strerror = "Timed out trying to connect to ADB device."
                    _LOGGER.warning("Couldn't connect to host %s, error: %s", self.host, serr.strerror)

                # ADB connection attempt failed
                self._adb.close()
                self._available = False

            finally:
                return self._available

        finally:
            self._adb_lock.release()

    def shell(self, cmd):
        """Send an ADB command using the Python ADB implementation.

        Parameters
        ----------
        cmd : str
            The ADB command to be sent

        Returns
        -------
        str, None
            The response from the device, if there is a response

        """
        if not self.available:
            _LOGGER.debug("ADB command not sent to %s because python-adb connection is not established: %s", self.host, cmd)
            return None

        if self._adb_lock.acquire(**LOCK_KWARGS):  # pylint: disable=unexpected-keyword-arg
            _LOGGER.debug("Sending command to %s via python-adb: %s", self.host, cmd)
            try:
                return self._adb.shell(cmd)
            finally:
                self._adb_lock.release()
        else:
            _LOGGER.debug("ADB command not sent to %s because python-adb lock not acquired: %s", self.host, cmd)

        return None


class ADBServer(object):
    """A manager for ADB connections that uses an ADB server.

    Parameters
    ----------
    host : str
        The address of the device in the format ``<ip address>:<host>``
    adbkey : str
        The path to the ``adbkey`` file for ADB authentication
    adb_server_ip : str
        The IP address of the ADB server
    adb_server_port : int
        The port for the ADB server

    """
    def __init__(self, host, adb_server_ip='', adb_server_port=5037):
        self.host = host
        self.adb_server_ip = adb_server_ip
        self.adb_server_port = adb_server_port
        self._adb_client = None
        self._adb_device = None

        # keep track of whether the ADB connection is intact
        self._available = False

        # use a lock to make sure that ADB commands don't overlap
        self._adb_lock = threading.Lock()

    @property
    def available(self):
        """Check whether the ADB connection is intact.

        Returns
        -------
        bool
            Whether or not the ADB connection is intact

        """
        if not self._adb_client:
            return False

        try:
            # make sure the server is available
            adb_devices = self._adb_client.devices()

            # make sure the device is available
            try:
                # case 1: the device is currently available
                if any([self.host in dev.get_serial_no() for dev in adb_devices]):
                    if not self._available:
                        self._available = True
                    return True

                # case 2: the device is not currently available
                if self._available:
                    _LOGGER.error('ADB server is not connected to the device.')
                    self._available = False
                return False

            except RuntimeError:
                if self._available:
                    _LOGGER.error('ADB device is unavailable; encountered an error when searching for device.')
                    self._available = False
                return False

        except RuntimeError:
            if self._available:
                _LOGGER.error('ADB server is unavailable.')
                self._available = False
            return False

    def close(self):
        """Close the ADB server socket connection.

        Currently, this doesn't do anything.

        """

    def connect(self, always_log_errors=True):
        """Connect to an Android TV / Fire TV device.

        Parameters
        ----------
        always_log_errors : bool
            If True, errors will always be logged; otherwise, errors will only be logged on the first failed reconnect attempt

        Returns
        -------
        bool
            Whether or not the connection was successfully established and the device is available

        """
        self._adb_lock.acquire(**LOCK_KWARGS)  # pylint: disable=unexpected-keyword-arg

        # Make sure that we release the lock
        try:
            try:
                self._adb_client = Client(host=self.adb_server_ip, port=self.adb_server_port)
                self._adb_device = self._adb_client.device(self.host)

                # ADB connection successfully established
                if self._adb_device:
                    _LOGGER.debug("ADB connection to %s via ADB server %s:%s successfully established", self.host, self.adb_server_ip, self.adb_server_port)
                    self._available = True

                # ADB connection attempt failed (without an exception)
                else:
                    if self._available or always_log_errors:
                        _LOGGER.warning("Couldn't connect to host %s via ADB server %s:%s", self.host, self.adb_server_ip, self.adb_server_port)
                    self._available = False

            except Exception as exc:  # noqa pylint: disable=broad-except
                if self._available or always_log_errors:
                    _LOGGER.warning("Couldn't connect to host %s via ADB server %s:%s, error: %s", self.host, self.adb_server_ip, self.adb_server_port, exc)

                # ADB connection attempt failed
                self._available = False

            finally:
                return self._available

        finally:
            self._adb_lock.release()

    def shell(self, cmd):
        """Send an ADB command using an ADB server.

        Parameters
        ----------
        cmd : str
            The ADB command to be sent

        Returns
        -------
        str, None
            The response from the device, if there is a response

        """
        if not self._available:
            _LOGGER.debug("ADB command not sent to %s via ADB server %s:%s because pure-python-adb connection is not established: %s", self.host, self.adb_server_ip, self.adb_server_port, cmd)
            return None

        if self._adb_lock.acquire(**LOCK_KWARGS):  # pylint: disable=unexpected-keyword-arg
            _LOGGER.debug("Sending command to %s via ADB server %s:%s: %s", self.host, self.adb_server_ip, self.adb_server_port, cmd)
            try:
                return self._adb_device.shell(cmd)
            finally:
                self._adb_lock.release()
        else:
            _LOGGER.debug("ADB command not sent to %s via ADB server %s:%s because pure-python-adb lock not acquired: %s", self.host, self.adb_server_ip, self.adb_server_port, cmd)

        return None
