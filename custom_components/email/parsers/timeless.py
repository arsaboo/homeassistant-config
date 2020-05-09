import logging
import re

from bs4 import BeautifulSoup
from ..const import EMAIL_ATTR_BODY

_LOGGER = logging.getLogger(__name__)
EMAIL_DOMAIN_TIMLESS = 'timelessha.com'
ATTR_TIMELESS = 'timelessha'


def parse_timeless(email):
    """Parse timeless tracking numbers."""
    tracking_numbers = []

    soup = BeautifulSoup(email[EMAIL_ATTR_BODY], 'html.parser')
    elements = soup.find_all('a')
    for element in elements:
        link = element.get('href')
        _LOGGER.error(link)
        if not link: continue
        match = re.search(r'TrackConfirmAction\.action\?tLabels=(.*?)$', link)
        if match and match.group(1) not in tracking_numbers:
            tracking_numbers.append(match.group(1))

    return tracking_numbers
