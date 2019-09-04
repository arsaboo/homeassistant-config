import logging
import re

from bs4 import BeautifulSoup
from ..const import EMAIL_ATTR_FROM, EMAIL_ATTR_BODY


_LOGGER = logging.getLogger(__name__)
EMAIL_ADDRESS = 'express-orders@google.com'
ATTR_GOOGLE_EXPRESS = 'google_express'

def parse_google_express(email):
    """Parse Google Express tracking numbers."""
    tracking_numbers = []

    email_from = email[EMAIL_ATTR_FROM]
    if isinstance(email_from, (list, tuple)):
        email_from = list(email_from)
        email_from = email_from[0]

    if EMAIL_ADDRESS in email_from:
        soup = BeautifulSoup(email[EMAIL_ATTR_BODY], 'html.parser')
        images = soup.find_all('img', alt=True)
        for image in images:
            if image['alt'] == 'UPS':
                link = image.parent.find('a')
                if not link: continue
                tracking_number = link.text
                if tracking_number not in tracking_numbers:
                    tracking_numbers.append(tracking_number)
                
    return tracking_numbers
    
