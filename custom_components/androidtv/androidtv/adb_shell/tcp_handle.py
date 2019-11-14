# Copyright (c) 2019 Jeff Irion and contributors
#
# This file is part of the adb-shell package.  It incorporates work
# covered by the following license notice:
#
#
#   Copyright 2014 Google Inc. All rights reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""A class for creating a socket connection with the device and sending and receiving data.

* :class:`TcpHandle`

    * :attr:`TcpHandle.available`
    * :attr:`TcpHandle.bulk_read`
    * :attr:`TcpHandle.bulk_write`
    * :meth:`TcpHandle.close`
    * :meth:`TcpHandle.connect`

"""


import select
import socket

from .exceptions import TcpTimeoutException


class TcpHandle(object):
    """TCP connection object.

    Parameters
    ----------
    serial : str, bytes, bytearray
        Android device serial of the form "host" or "host:port".  (Host may be an IP address or a host name.)
    default_timeout_s : float, None
        Default timeout in seconds for TCP packets, or ``None``

    Attributes
    ----------
    _connection : socket.socket, None
        A socket connection to the device
    _default_timeout_s : float, None
        Default timeout in seconds for TCP packets, or ``None``
    host : str
        The address of the device
    port : str
        The device port to which we are connecting (default is 5555)
    serial_number : str
        ``<host>:<port>``

    """
    def __init__(self, serial, default_timeout_s=None):
        if ':' in serial:
            self.host, port = serial.split(':')
            self.port = int(port)
        else:
            self.host = serial
            self.port = 5555

        self.serial = '{}:{}'.format(self.host, self.port)

        self._default_timeout_s = default_timeout_s

        self._connection = None

    def close(self):
        """Close the socket connection.

        """
        if self._connection:
            self._connection.shutdown(socket.SHUT_RDWR)
            self._connection.close()
            self._connection = None

    def connect(self, timeout_s=None):
        """Create a socket connection to the device.

        Parameters
        ----------
        timeout_s : float, None
            Set the timeout on the socket instance

        """
        timeout = self._default_timeout_s if timeout_s is None else timeout_s
        self._connection = socket.create_connection((self.host, self.port), timeout=timeout)
        if timeout:
            # Put the socket in non-blocking mode
            # https://docs.python.org/3/library/socket.html#socket.socket.settimeout
            self._connection.setblocking(0)

    def bulk_read(self, numbytes, timeout_s=None):
        """Receive data from the socket.

        Parameters
        ----------
        numbytes : int
            The maximum amount of data to be received
        timeout_s : float, None
            When the timeout argument is omitted, ``select.select`` blocks until at least one file descriptor is ready. A time-out value of zero specifies a poll and never blocks.

        Returns
        -------
        bytes
            The received data

        Raises
        ------
        TcpTimeoutException
            Reading timed out.

        """
        timeout = self._default_timeout_s if timeout_s is None else timeout_s
        readable, _, _ = select.select([self._connection], [], [], timeout)
        if readable:
            return self._connection.recv(numbytes)

        msg = 'Reading from {} timed out ({} seconds)'.format(self.serial, timeout)
        raise TcpTimeoutException(msg)

    def bulk_write(self, data, timeout_s=None):
        """Send data to the socket.

        Parameters
        ----------
        data : bytes
            The data to be sent
        timeout_s : float, None
            When the timeout argument is omitted, ``select.select`` blocks until at least one file descriptor is ready. A time-out value of zero specifies a poll and never blocks.

        Returns
        -------
        int
            The number of bytes sent

        Raises
        ------
        TcpTimeoutException
            Sending data timed out.  No data was sent.

        """
        timeout = self._default_timeout_s if timeout_s is None else timeout_s
        _, writeable, _ = select.select([], [self._connection], [], timeout)
        if writeable:
            return self._connection.send(data)

        msg = 'Sending data to {} timed out after {} seconds. No data was sent.'.format(self.serial, timeout)
        raise TcpTimeoutException(msg)
