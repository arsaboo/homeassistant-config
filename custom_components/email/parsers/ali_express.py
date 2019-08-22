import logging
import re

from bs4 import BeautifulSoup
from ..const import EMAIL_ATTR_FROM, EMAIL_ATTR_BODY


_LOGGER = logging.getLogger(__name__)
EMAIL_ADDRESS = 'transaction@notice.aliexpress.com'
ATTR_ALI_EXPRESS = 'ali_express'


def parse_ali_express(email):
    """Parse Ali Express tracking numbers."""
    tracking_numbers = []

    email_from = email[EMAIL_ATTR_FROM]
    if isinstance(email_from, (list, tuple)):
        email_from = list(email_from)
        email_from = email_from[0]

    if EMAIL_ADDRESS in email_from:
        soup = BeautifulSoup(email[EMAIL_ATTR_BODY], 'html.parser')
        lines = [p_element.text for p_element in soup.find_all('p')]
        for line in lines:
            if not line: continue
            match = re.search('TRACKING NUMBER :(.*?)\.', line)
            if match and match.group(1) not in tracking_numbers:
                tracking_numbers.append(match.group(1))
                
    return tracking_numbers
    

