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

"""Constants used throughout the code.

"""


import stat
import struct


#: From adb.h
CLASS = 0xFF

#: From adb.h
SUBCLASS = 0x42

#: From adb.h
PROTOCOL = 0x01

#: ADB protocol version.
VERSION = 0x01000000

#: Maximum amount of data in an ADB packet.
MAX_ADB_DATA = 4096

#: Maximum size of a filesync DATA packet.
MAX_PUSH_DATA = 2048

#: Default mode for pushed files.
DEFAULT_PUSH_MODE = stat.S_IFREG | stat.S_IRWXU | stat.S_IRWXG

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

DATA = b'DATA'
DENT = b'DENT'
DONE = b'DONE'
LIST = b'LIST'
QUIT = b'QUIT'
RECV = b'RECV'
SEND = b'SEND'
STAT = b'STAT'

#: Commands that are recognized by :meth:`adb_shell.adb_device.AdbDevice._read`
IDS = (AUTH, CLSE, CNXN, OKAY, OPEN, SYNC, WRTE)

#: A dictionary where the keys are the commands in :const:`IDS` and the values are the keys converted to integers
ID_TO_WIRE = {cmd_id: sum(c << (i * 8) for i, c in enumerate(bytearray(cmd_id))) for cmd_id in IDS}

#: A dictionary where the keys are integers and the values are their corresponding commands (type = bytes) from :const:`IDS`
WIRE_TO_ID = {wire: cmd_id for cmd_id, wire in ID_TO_WIRE.items()}

#: Commands that are recognized by :meth:`adb_shell.adb_device.AdbDevice._filesync_read`
FILESYNC_IDS = (DATA, DENT, DONE, FAIL, LIST, OKAY, QUIT, RECV, SEND, STAT)

#: A dictionary where the keys are the commands in :const:`FILESYNC_IDS` and the values are the keys converted to integers
FILESYNC_ID_TO_WIRE = {cmd_id: sum(c << (i * 8) for i, c in enumerate(bytearray(cmd_id))) for cmd_id in FILESYNC_IDS}

#: A dictionary where the keys are integers and the values are their corresponding commands (type = bytes) from :const:`FILESYNC_IDS`
FILESYNC_WIRE_TO_ID = {wire: cmd_id for cmd_id, wire in FILESYNC_ID_TO_WIRE.items()}

#: An ADB message is 6 words in little-endian.
MESSAGE_FORMAT = b'<6I'

#: The format for FileSync "list" messages
FILESYNC_LIST_FORMAT = b'<5I'

#: The format for FileSync "pull" messages
FILESYNC_PULL_FORMAT = b'<2I'

#: The format for FileSync "push" messages
FILESYNC_PUSH_FORMAT = b'<2I'

#: The format for FileSync "stat" messages
FILESYNC_STAT_FORMAT = b'<4I'

#: The size of an ADB message
MESSAGE_SIZE = struct.calcsize(MESSAGE_FORMAT)

#: Default authentication timeout (in s) for :meth:`adb_shell.tcp_handle.TcpHandle.connect`
DEFAULT_AUTH_TIMEOUT_S = 10.

#: Default total timeout (in s) for :meth:`adb_shell.adb_device.AdbDevice._read`
DEFAULT_TOTAL_TIMEOUT_S = 10.
