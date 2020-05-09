import logging
import re

from bs4 import BeautifulSoup
from ..const import EMAIL_ATTR_BODY


_LOGGER = logging.getLogger(__name__)
EMAIL_DOMAIN_ROCKAUTO = 'rockauto.com'
ATTR_ROCKAUTO = 'rockauto'


def parse_rockauto(email):
    """Parse Rockauto tracking numbers."""
    tracking_numbers = []

    soup = BeautifulSoup(email[EMAIL_ATTR_BODY], 'html.parser')
    links = [link.get('href') for link in soup.find_all('a')]
    for link in links:
        if not link: continue
        match = re.search('tracknumbers=(.*?)$', link)
        if match and match.group(1) not in tracking_numbers:
            tracking_numbers.append(match.group(1))
                
    return tracking_numbers
    
