import logging
import re

from bs4 import BeautifulSoup
from ..const import EMAIL_ATTR_FROM, EMAIL_ATTR_BODY


_LOGGER = logging.getLogger(__name__)
EMAIL_ADDRESS = 'paperless-support@southernco.com'
ATTR_NEWEGG = 'georgia_power'


def parse_georgia_power(email):
    """Parse Georgia Power energy usage."""
    tracking_numbers = []

    email_from = email[EMAIL_ATTR_FROM]
    if isinstance(email_from, (list, tuple)):
        email_from = list(email_from)
        email_from = ''.join(list(email_from[0]))
    if EMAIL_ADDRESS in email_from:
        body = email[EMAIL_ATTR_BODY]
        _LOGGER.error('{}'.format(body))
        matches = re.findall(r'Energy Use: (.*?)<', body)
        for tracking_number in matches:
            if tracking_number not in tracking_numbers:
                tracking_numbers.append(tracking_number)

    return tracking_numbers
