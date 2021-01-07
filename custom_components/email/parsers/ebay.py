import logging

from bs4 import BeautifulSoup
from ..const import EMAIL_ATTR_BODY


_LOGGER = logging.getLogger(__name__)
ATTR_EBAY = 'ebay'
EMAIL_DOMAIN_EBAY = 'ebay.com'


def parse_ebay(email):
    """Parse eBay tracking numbers."""
    tracking_numbers = []

    soup = BeautifulSoup(email[EMAIL_ATTR_BODY], 'html.parser')
    elements = [element for element in soup.find_all('span')]
    for element in elements:
        if 'Tracking Number' in element.text:
            tracking_link = element.find("a", recursive=False)
            tracking_number = tracking_link.text
            if tracking_number not in tracking_numbers:
                tracking_numbers.append(tracking_number)

    return tracking_numbers
