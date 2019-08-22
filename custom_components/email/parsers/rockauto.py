import logging
import re

from bs4 import BeautifulSoup
from ..const import EMAIL_ATTR_FROM, EMAIL_ATTR_BODY


_LOGGER = logging.getLogger(__name__)
EMAIL_ADDRESS = 'service@rockauto.com'
ATTR_ROCKAUTO = 'rockauto'


def parse_rockauto(email):
    """Parse Rockauto tracking numbers."""
    tracking_numbers = []

    email_from = email[EMAIL_ATTR_FROM]
    if isinstance(email_from, (list, tuple)):
        email_from = list(email_from)
        email_from = email_from[0]

    if EMAIL_ADDRESS in email_from:
        soup = BeautifulSoup(email[EMAIL_ATTR_BODY], 'html.parser')
        links = [link.get('href') for link in soup.find_all('a')]
        for link in links:
            if not link: continue
            match = re.search('tracknumbers=(.*?)$', link)
            if match and match.group(1) not in tracking_numbers:
                tracking_numbers.append(match.group(1))
                
    return tracking_numbers
    
