# -*- coding: utf-8 -*-

import base64
import logging
import socket
import threading
import sys
# noinspection PyCompatibility
from . import exceptions
from . import upnp
from . import wake_on_lan
from .upnp.discover import auto_discover
from .utils import LogIt, LogItWithReturn


logger = logging.getLogger(__name__)

PY3 = sys.version_info[0] > 2

if PY3:
    PAYLOAD_HEADER = b"\x64\x00"
    PACKET_HEADER = b"\x00\x00\x00"
    RESULTS = [
        b"\x64\x00\x01\x00",
        b"\x64\x00\x00\x00",
        b"\x0a",
        b"\x65",
        b"\x00\x00\x00\x00"
    ]
else:
    PAYLOAD_HEADER = "\x64\x00"
    PACKET_HEADER = "\x00\x00\x00"
    RESULTS = [
        "\x64\x00\x01\x00",
        "\x64\x00\x00\x00",
        "\x0a",
        "\x65",
        "\x00\x00\x00\x00"
    ]


# noinspection PyAbstractClass
class RemoteLegacy(upnp.UPNPTV):
    """Object for remote control connection."""

    @LogIt
    def __init__(self, config):
        """Make a new connection."""
        self.sock = None
        self.config = config
        self._auth_lock = threading.RLock()
        self._connect_lock = threading.Lock()
        self._loop_event = threading.Event()
        self._receive_lock = threading.Lock()
        self._receive_event = threading.Event()
        self._power_event = threading.Event()
        self._registered_callbacks = []
        self._thread = None
        self.is_powering_on = False
        self.is_powering_off = False
        upnp.UPNPTV.__init__(self, config)

        auto_discover.register_callback(
            self._connect,
            config.uuid
        )

    @LogIt
    def _connect(self, config, power):
        with self._connect_lock:
            if config is None:
                return
            if power:
                if not self._thread:
                    self.config.copy(config)
                    self.open()
                elif not self.is_connected:
                    self.connect()

            elif not power:
                self._close_connection()

    @property
    @LogItWithReturn
    def mac_address(self):
        """
        MAC Address.

        **Get:** Gets the MAC address.

            *Returns:* None or the MAC address of the TV formatted
            ``"00:00:00:00:00"``

            *Return type:* `None` or `str`
        """
        if self.config.mac is None:
            self.config.mac = wake_on_lan.get_mac_address(self.config.host)
            if self.config.mac is None:
                if not self.power:
                    logger.error(
                        self.config.host +
                        ' -- unable to acquire MAC address'
                    )
            if self.config.path:
                self.config.save()
        return self.config.mac

    @property
    @LogItWithReturn
    def power(self):
        with self._auth_lock:
            return self.sock is not None

    @power.setter
    @LogIt
    def power(self, value):
        with self._auth_lock:
            if value and not self.power:
                if self.is_powering_off and self.open():
                    self._send_key('KEY_POWERON')
                else:
                    self.is_powering_on = True
                    if self._cec is not None:
                        self._cec.tv.power = True
                    elif self.mac_address:
                        wake_on_lan.send_wol(self.mac_address)
                    else:
                        logging.error(
                            self.config.host +
                            ' -- unable to get TV\'s mac address'
                        )
                        self.is_powering_on = False

            elif not value and self.power:
                self.is_powering_off = True
                if self._cec is not None:
                    self._cec.tv.power = False
                else:
                    self.control('KEY_POWEROFF')

    def loop(self):
        while self.sock is None and not self._loop_event.isSet():
            self._loop_event.wait(0.1)

        while not self._loop_event.isSet():
            try:
                header = self.sock.recv(3)
                logger.debug(
                    self.config.host +
                    ' --> (header) ' +
                    repr(header)
                )

                tv_name_len = ord(header[1:2].decode('utf-8'))
                logger.debug(
                    self.config.host +
                    ' --> (tv_name_len) ' +
                    repr(tv_name_len)
                )

                tv_name = self.sock.recv(tv_name_len)
                logger.debug(
                    self.config.host +
                    ' --> (tv_name) ' +
                    repr(tv_name)
                )

                response_len = self.sock.recv(2)
                logger.debug(
                    self.config.host +
                    ' --> (response_len(hex)) ' +
                    repr(response_len)
                )

                response_len = ord(response_len[:1].decode('utf-8'))
                logger.debug(
                    self.config.host +
                    ' --> (response_len(int)) ' +
                    repr(response_len)
                )

                response = self.sock.recv(response_len)
                logger.debug(
                    self.config.host +
                    ' --> (response) ' +
                    repr(response)
                )

                if len(response) == 0:
                    continue

                if response == RESULTS[4]:
                    if self._registered_callbacks:
                        self._registered_callbacks[0]()
            except (socket.error, TypeError):
                break

        if self.sock is not None:
            self.sock.close()
            self.sock = None

        self._thread = None
        self._loop_event.clear()
        self.is_powering_off = False

    @LogIt
    def open(self):
        with self._auth_lock:
            if self.sock is not None:
                return True

            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self.config.host, self.config.port))

                payload = (
                    PAYLOAD_HEADER +
                    self._serialize_string(self.config.description) +
                    self._serialize_string(self.config.id) +
                    self._serialize_string(self.config.name)
                )
                packet = PACKET_HEADER + self._serialize_string(payload, True)

                logger.debug(
                    self.config.host +
                    ' <-- (handshake) ' +
                    repr(packet)
                )

                sock.send(packet)
                import time
                loop_timer = None

                while True:
                    header = sock.recv(3)

                    logger.debug(
                        self.config.host +
                        ' --> (header) ' +
                        repr(header)
                    )

                    tv_name_len = ord(header[1:2].decode('utf-8'))
                    logger.debug(
                        self.config.host +
                        ' --> (tv_name_len) ' +
                        repr(tv_name_len)
                    )

                    tv_name = sock.recv(tv_name_len)
                    logger.debug(
                        self.config.host +
                        ' --> (tv name) ' +
                        repr(tv_name)
                    )

                    response_len = sock.recv(2)
                    logger.debug(
                        self.config.host +
                        ' --> (response_len(hex)) ' +
                        repr(response_len)
                    )

                    response_len = ord(response_len[:1].decode('utf-8'))
                    logger.debug(
                        self.config.host +
                        ' --> (response_len(int)) ' +
                        repr(response_len)
                    )

                    response = sock.recv(response_len)
                    logger.debug(
                        self.config.host +
                        ' --> (response) ' +
                        repr(response)
                    )

                    if response == RESULTS[0]:
                        logger.debug(self.config.host + ' -- access granted')
                        self.config.paired = True
                        if self.config.path:
                            self.config.save()

                        self._thread = threading.Thread(target=self.loop)
                        self._thread.start()
                        self.connect()
                        self.sock = sock
                        self.is_powering_on = False
                        self.is_powering_off = False
                        return True

                    elif response == RESULTS[1]:
                        raise exceptions.AccessDenied()
                    elif response[0:1] == RESULTS[2]:
                        if (
                            loop_timer is None or
                            (time.time() - loop_timer) >= 5
                        ):
                            loop_timer = time.time()
                            logger.debug(
                                self.config.host +
                                ' -- waiting for user authorization...'
                            )

                        continue
                    elif response[0:1] == RESULTS[3]:
                        raise RuntimeError('Authorization cancelled')
                    else:
                        return False

            except socket.error:
                if not self.config.paired:
                    raise RuntimeError(
                        'Unable to pair with TV.. Is the TV on?!?'
                    )
                else:
                    self.sock = None
                    return False

    def _close_connection(self):
        if self._thread is not None:
            self._loop_event.set()
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
                self.sock.close()
            except socket.error:
                pass

            if self._thread is not None:
                self._thread.join(2.0)

    @LogIt
    def close(self):
        """Close the connection."""
        with self._auth_lock:
            self._close_connection()
            auto_discover.unregister_callback(self._connect, self.config.uuid)

    @LogIt
    def control(self, key):
        """Send a control command."""
        with self._auth_lock:
            if self.sock is None:
                return False

            with self._receive_lock:
                payload = PACKET_HEADER + self._serialize_string(key)
                packet = PACKET_HEADER + self._serialize_string(payload, True)

                logger.info(
                    self.config.host +
                    ' <--' +
                    repr(packet)

                )

                def callback():
                    self._receive_event.set()

                self._registered_callbacks += [callback]
                self._receive_event.clear()

                self.sock.send(packet)
                self._receive_event.wait(self._key_interval)
                self._registered_callbacks.remove(callback)

    _key_interval = 0.3

    @staticmethod
    @LogItWithReturn
    def _serialize_string(string, raw=False):
        if PY3:
            if isinstance(string, str):
                string = str.encode(string)

        if not raw:
            string = base64.b64encode(string)

        if PY3:
            return bytes([len(string)]) + b"\x00" + string
        else:
            return chr(len(string)) + "\x00" + string

    def __enter__(self):
        # noinspection PyUnresolvedReferences
        """
        Open the connection to the TV. use in a `with` statement

        >>> with samsungctl.Remote(config) as remote:
        >>>     remote.KEY_MENU()


        :return: self
        :rtype: :class: `samsungctl.Remote` instance
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        This gets called automatically when exiting a `with` statement
        see `samsungctl.Remote.__enter__` for more information

        :param exc_type: Not Used
        :param exc_val: Not Used
        :param exc_tb: Not Used
        :return: `None`
        """
        self.close()
