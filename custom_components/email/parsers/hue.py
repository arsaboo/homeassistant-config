import logging
import re

from bs4 import BeautifulSoup
from ..const import EMAIL_ATTR_FROM, EMAIL_ATTR_BODY


_LOGGER = logging.getLogger(__name__)
EMAIL_ADDRESS = 'luzernsolutions'
ATTR_HUE = 'hue'


def parse_hue(email):
    """Parse Phillips Hue tracking numbers."""
    tracking_numbers = []

    email_from = email[EMAIL_ATTR_FROM]
    if isinstance(email_from, (list, tuple)):
        email_from = list(email_from)
        email_from = ''.join(list(email_from[0]))
    if EMAIL_ADDRESS in email_from:
        body = email[EMAIL_ATTR_BODY]
        matches = re.findall(r'tracking number is: (.*?)<', body)
        for tracking_number in matches:
            if tracking_number not in tracking_numbers:
                tracking_numbers.append(tracking_number)
                
    return tracking_numbers
    
