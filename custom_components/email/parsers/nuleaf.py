import logging
import re

from bs4 import BeautifulSoup
from ..const import EMAIL_ATTR_BODY


_LOGGER = logging.getLogger(__name__)
EMAIL_DOMAIN_NULEAF = 'nuleafnaturals.com'
ATTR_NULEAF = 'nuleaf'


def parse_nuleaf(email):
    """Parse NuLeaf tracking numbers."""
    tracking_numbers = []

    soup = BeautifulSoup(email[EMAIL_ATTR_BODY], 'html.parser')
    elements = soup.find_all('a')
    for element in elements:
        link = element.get('href')
        if not link: continue
        if 'emailtrk' in link:
            tracking_number = element.text
            if tracking_number and tracking_number not in tracking_numbers:
                tracking_numbers.append(tracking_number)

    return tracking_numbers
