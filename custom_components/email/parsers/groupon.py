import logging
import re

from bs4 import BeautifulSoup
from ..const import EMAIL_ATTR_BODY


_LOGGER = logging.getLogger(__name__)
ATTR_GROUPON = 'groupon'
EMAIL_DOMAIN_GROUPON = 'groupon.com'


def parse_groupon(email):
    """Parse groupon tracking numbers."""
    tracking_numbers = []

    soup = BeautifulSoup(email[EMAIL_ATTR_BODY], 'html.parser')
    elements = soup.find_all('a')
    for element in elements:
        link = element.get('href')
        if not link:
            continue
        if 'track_order' in link:
            tracking_number = element.text
            if tracking_number != 'here' and tracking_number and tracking_number not in tracking_numbers:
                tracking_numbers.append(tracking_number)

    return tracking_numbers
