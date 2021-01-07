import logging
import re

from bs4 import BeautifulSoup
from ..const import EMAIL_ATTR_BODY

_LOGGER = logging.getLogger(__name__)
ATTR_DOLLAR_SHAVE_CLUB = 'dollar_shave_club'
EMAIL_DOMAIN_DOLLAR_SHAVE_CLUB = 'dollarshaveclub.com'


def parse_dollar_shave_club(email):
    """Parse Dollar Shave Club tracking numbers."""
    tracking_numbers = []

    soup = BeautifulSoup(email[EMAIL_ATTR_BODY], 'html.parser')
    elements = soup.find_all('a')
    for element in elements:
        title = element.get('title')
        if not title:
            continue
        if 'Track Package' == title:
            link = element.get('href')
            match = re.search(r'x=(.*?)%7c', link)
            if match and match.group(1) not in tracking_numbers:
                tracking_numbers.append(match.group(1))

    return tracking_numbers
