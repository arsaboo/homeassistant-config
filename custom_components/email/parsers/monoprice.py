import logging
import re

from bs4 import BeautifulSoup
from ..const import EMAIL_ATTR_BODY


_LOGGER = logging.getLogger(__name__)
ATTR_MONOPRICE = 'monoprice'
EMAIL_DOMAIN_MONOPRICE = 'monoprice.com'


def parse_monoprice(email):
    """Parse Monoprice tracking numbers."""
    tracking_numbers = []

    soup = BeautifulSoup(email[EMAIL_ATTR_BODY], 'html.parser')
    links = [element.get('href') for element in soup.find_all('a')]
    for link in links:
        if not link:
            continue
        match = re.search('TRK=(.*?)&CAR', link)
        if match and match.group(1) not in tracking_numbers:
            tracking_numbers.append(match.group(1))

    return tracking_numbers
