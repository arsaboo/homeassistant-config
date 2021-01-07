import logging
import re

from bs4 import BeautifulSoup
from ..const import EMAIL_ATTR_BODY


_LOGGER = logging.getLogger(__name__)
ATTR_DSW = 'DSW'
EMAIL_DOMAIN_DSW = 'dsw.com'


def parse_dsw(email):
    """Parse DSW tracking numbers."""
    tracking_numbers = []

    matches = re.findall(r'tracking_numbers=(.*?)&', email[EMAIL_ATTR_BODY])
    for tracking_number in matches:
        if tracking_number not in tracking_numbers:
            tracking_numbers.append(tracking_number)

    return tracking_numbers
