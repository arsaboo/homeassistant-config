import logging
import re

from bs4 import BeautifulSoup
from ..const import EMAIL_ATTR_FROM, EMAIL_ATTR_BODY


_LOGGER = logging.getLogger(__name__)
EMAIL_ADDRESS = 'info@newegg.com'
ATTR_NEWEGG = 'newegg'


def parse_newegg(email):
    """Parse Newegg tracking numbers."""
    tracking_numbers = []

    email_from = email[EMAIL_ATTR_FROM]
    if isinstance(email_from, (list, tuple)):
        email_from = list(email_from)
        email_from = email_from[0]

    if EMAIL_ADDRESS in email_from:
        soup = BeautifulSoup(email[EMAIL_ATTR_BODY], 'html.parser')

        link_urls = [link.get('href') for link in soup.find_all('a')]
        for link in link_urls:
            if not link: 
                continue
            match = re.search('TrackingNumber=(.*?)&type=0', link)
            if match and match.group(1) not in tracking_numbers:
                tracking_numbers.append(match.group(1))
        
        # sometimes tracking numbers are text in a link
        strongs = [link for link in soup.find_all('strong')]
        for strong in strongs:
            if not strong.get_text():
                continue
            match = re.search('Tracking Number', strong.get_text())
            if match:
                link_texts = [link.get_text() for link in 
                                strong.findChildren("a", recursive=False)]
                for link_text in link_texts:
                    if not link_text:
                        continue
                    if link_text not in tracking_numbers:
                        tracking_numbers.append(link_text)

    return tracking_numbers
