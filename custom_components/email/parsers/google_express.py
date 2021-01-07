import logging
import re

from bs4 import BeautifulSoup
from ..const import EMAIL_ATTR_BODY


_LOGGER = logging.getLogger(__name__)
ATTR_GOOGLE_EXPRESS = 'google_express'
EMAIL_DOMAIN_GOOGLE_EXPRESS = 'google.com'


def parse_google_express(email):
    """Parse Google Express tracking numbers."""
    tracking_numbers = []

    soup = BeautifulSoup(email[EMAIL_ATTR_BODY], 'html.parser')
    images = soup.find_all('img', alt=True)
    for image in images:
        if image['alt'] == 'UPS':
            link = image.parent.find('a')
            if not link:
                continue
            tracking_number = link.text
            if tracking_number not in tracking_numbers:
                tracking_numbers.append(tracking_number)

    return tracking_numbers
