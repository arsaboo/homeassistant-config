"""Constants used throughout the code.

"""


import struct


#: From adb.h
CLASS = 0xFF

#: From adb.h
SUBCLASS = 0x42

#: From adb.h
PROTOCOL = 0x01

#: Maximum amount of data in an ADB packet.
MAX_ADB_DATA = 4096

#: ADB protocol version.
VERSION = 0x01000000

#: AUTH constant for ``arg0``
AUTH_TOKEN = 1

#: AUTH constant for ``arg0``
AUTH_SIGNATURE = 2

#: AUTH constant for ``arg0``
AUTH_RSAPUBLICKEY = 3

AUTH = b'AUTH'
CLSE = b'CLSE'
CNXN = b'CNXN'
FAIL = b'FAIL'
OKAY = b'OKAY'
OPEN = b'OPEN'
SYNC = b'SYNC'
WRTE = b'WRTE'

#: Commands that are recognized by :meth:`adb_shell.adb_device.AdbDevice._read`
IDS = (AUTH, CLSE, CNXN, OKAY, OPEN, SYNC, WRTE)

#: A dictionary where the keys are the commands in :const:`IDS` and the values are the keys converted to integers
ID_TO_WIRE = {cmd_id: sum(c << (i * 8) for i, c in enumerate(bytearray(cmd_id))) for cmd_id in IDS}

#: A dictionary where the keys are integers and the values are their corresponding commands (type = bytes) from :const:`IDS`
WIRE_TO_ID = {wire: cmd_id for cmd_id, wire in ID_TO_WIRE.items()}

#: An ADB message is 6 words in little-endian.
MESSAGE_FORMAT = b'<6I'

#: The size of an ADB message
MESSAGE_SIZE = struct.calcsize(MESSAGE_FORMAT)

#: Default authentication timeout (in s) for :meth:`adb_shell.tcp_handle.TcpHandle.connect`
DEFAULT_AUTH_TIMEOUT_S = 10.

#: Default total timeout (in s) for :meth:`adb_shell.adb_device.AdbDevice._read`
DEFAULT_TOTAL_TIMEOUT_S = 10.
