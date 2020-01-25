# Copyright (c) 2020 Jeff Irion and contributors
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

"""Functions and an :class:`AdbMessage` class for packing and unpacking ADB messages.

.. rubric:: Contents

* :class:`AdbMessage`

    * :attr:`AdbMessage.checksum`
    * :meth:`AdbMessage.pack`

* :func:`checksum`
* :func:`unpack`

"""


import struct

from . import constants


def checksum(data):
    """Calculate the checksum of the provided data.

    Parameters
    ----------
    data : bytearray, bytes, str
        The data

    Returns
    -------
    int
        The checksum

    """
    # The checksum is just a sum of all the bytes. I swear.
    if isinstance(data, bytearray):
        total = sum(data)

    elif isinstance(data, bytes):
        if data and isinstance(data[0], bytes):
            # Python 2 bytes (str) index as single-character strings.
            total = sum((ord(d) for d in data))  # pragma: no cover
        else:
            # Python 3 bytes index as numbers (and PY2 empty strings sum() to 0)
            total = sum(data)

    else:
        # Unicode strings (should never see?)
        total = sum((ord(d) for d in data))

    return total & 0xFFFFFFFF


def unpack(message):
    """Unpack a received ADB message.

    Parameters
    ----------
    message : bytes
        The received message

    Returns
    -------
    cmd : int
        The ADB command
    arg0 : int
        TODO
    arg1 : int
        TODO
    data_length : int
        The length of the data sent by the device (used by :meth:`adb_shell.adb_device._read`)
    data_checksum : int
        The checksum of the data sent by the device

    Raises
    ------
    ValueError
        Unable to unpack the ADB command.

    """
    try:
        cmd, arg0, arg1, data_length, data_checksum, _ = struct.unpack(constants.MESSAGE_FORMAT, message)
    except struct.error as e:
        raise ValueError('Unable to unpack ADB command. (length={})'.format(len(message)), constants.MESSAGE_FORMAT, message, e)

    return cmd, arg0, arg1, data_length, data_checksum


class AdbMessage(object):
    """A helper class for packing ADB messages.

    Parameters
    ----------
    command : bytes
        A command; examples used in this package include :const:`adb_shell.constants.AUTH`, :const:`adb_shell.constants.CNXN`, :const:`adb_shell.constants.CLSE`, :const:`adb_shell.constants.OPEN`, and :const:`adb_shell.constants.OKAY`
    arg0 : int
        Usually the local ID, but :meth:`~adb_shell.adb_device.AdbDevice.connect` provides :const:`adb_shell.constants.VERSION`, :const:`adb_shell.constants.AUTH_SIGNATURE`, and :const:`adb_shell.constants.AUTH_RSAPUBLICKEY`
    arg1 : int
        Usually the remote ID, but :meth:`~adb_shell.adb_device.AdbDevice.connect` provides :const:`adb_shell.constants.MAX_ADB_DATA`
    data : bytes
        The data that will be sent

    Attributes
    ----------
    arg0 : int
        Usually the local ID, but :meth:`~adb_shell.adb_device.AdbDevice.connect` provides :const:`adb_shell.constants.VERSION`, :const:`adb_shell.constants.AUTH_SIGNATURE`, and :const:`adb_shell.constants.AUTH_RSAPUBLICKEY`
    arg1 : int
        Usually the remote ID, but :meth:`~adb_shell.adb_device.AdbDevice.connect` provides :const:`adb_shell.constants.MAX_ADB_DATA`
    command : int
        The input parameter ``command`` converted to an integer via :const:`adb_shell.constants.ID_TO_WIRE`
    data : bytes
        The data that will be sent
    magic : int
        ``self.command`` with its bits flipped; in other words, ``self.command + self.magic == 2**32 - 1``

    """
    def __init__(self, command, arg0, arg1, data=b''):
        self.command = constants.ID_TO_WIRE[command]
        self.magic = self.command ^ 0xFFFFFFFF
        self.arg0 = arg0
        self.arg1 = arg1
        self.data = data

    def pack(self):
        """Returns this message in an over-the-wire format.

        Returns
        -------
        bytes
            The message packed into the format required by ADB

        """
        return struct.pack(constants.MESSAGE_FORMAT, self.command, self.arg0, self.arg1, len(self.data), self.checksum, self.magic)

    @property
    def checksum(self):
        """Return ``checksum(self.data)``

        Returns
        -------
        int
            The checksum of ``self.data``

        """
        return checksum(self.data)
