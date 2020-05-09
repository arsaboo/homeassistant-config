import logging
import re

from bs4 import BeautifulSoup
from ..const import EMAIL_ATTR_BODY


_LOGGER = logging.getLogger(__name__)
EMAIL_DOMAIN_DHL = 'dhl'
ATTR_DHL = 'dhl'


def parse_dhl(email):
    """Parse DHL tracking numbers."""
    tracking_numbers = []

    matches = re.findall(r'idc=(.*?)"', email[EMAIL_ATTR_BODY])
    for tracking_number in matches:
        if tracking_number not in tracking_numbers:
            tracking_numbers.append(tracking_number)
                
    return tracking_numbers
    
