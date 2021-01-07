import logging
import re

from bs4 import BeautifulSoup
from ..const import EMAIL_ATTR_BODY


_LOGGER = logging.getLogger(__name__)
ATTR_BEST_BUY = 'best_buy'
EMAIL_DOMAIN_BEST_BUY = 'bestbuy.com'


def parse_best_buy(email):
    """Parse Best Buy tracking numbers."""
    tracking_numbers = []

    soup = BeautifulSoup(email[EMAIL_ATTR_BODY], 'html.parser')
    elements = soup.find_all('a')
    for element in elements:
        link = element.get('href')
        if not link:
            continue
        if 'shipment/tracking' in link:
            tracking_number = element.text
            if tracking_number and tracking_number not in tracking_numbers:
                tracking_numbers.append(tracking_number)

    return tracking_numbers
