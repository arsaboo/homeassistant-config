# -*- coding: utf-8 -*-

"""Remote control Samsung televisions via TCP/IP connection"""

import logging
from logging import NullHandler

logger = logging.getLogger('samsungctl')
logger.addHandler(NullHandler())
logging.basicConfig(format="%(message)s", level=None)

__title__ = "samsungctl"
__version__ = "0.8.0b"
__url__ = "https://github.com/kdschlosser/samsungctl"
__author__ = "Lauri Niskanen, Kevin Schlosser"
__author_email__ = "kevin.g.schlosser@gmail.com"
__license__ = "MIT"

from .remote import Remote # NOQA
