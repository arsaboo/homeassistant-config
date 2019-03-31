# -*- coding: utf-8 -*-

"""Remote control Samsung televisions via TCP/IP connection"""

import logging
from logging import NullHandler

LOGGING_FORMAT = '''\
[%(levelname)s][%(thread)d] %(name)s.%(module)s.%(funcName)s
%(message)s
'''

logger = logging.getLogger(__name__)
logger.addHandler(NullHandler())
logging.basicConfig(format=LOGGING_FORMAT, level=None)


__title__ = "samsungctl"
__version__ = "0.8.65b"
__url__ = "https://github.com/kdschlosser/samsungctl"
__author__ = "Lauri Niskanen, Kevin Schlosser"
__author_email__ = "kevin.g.schlosser@gmail.com"
__license__ = "MIT"

from .config import Config # NOQA
from .remote import Remote  # NOQA


def discover(timeout=8):
    from .upnp.discover import discover as _discover
    res = list(_discover(timeout=timeout))

    return res
