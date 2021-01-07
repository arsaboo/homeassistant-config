import logging
import re

from bs4 import BeautifulSoup
from ..const import EMAIL_ATTR_BODY


_LOGGER = logging.getLogger(__name__)
ATTR_GEORGIA_POWER = 'georgia_power'
EMAIL_DOMAIN_GEORGIA_POWER = 'southernco.com'


def parse_georgia_power(email):
    """Parse Georgia power usage numbers."""

    usage_numbers = {
        'yesterday_use': '',
        'yesterday_cost': 0,
        'monthly_use': '',
        'monthly_cost': 0,
    }

    soup = BeautifulSoup(email[EMAIL_ATTR_BODY], 'html.parser')
    elements = soup.find_all('td')

    for idx, element in enumerate(elements):
        text = element.getText()

        if("Yesterday's Energy" in text):
            usage_numbers['yesterday_use'] = elements[idx +
                                                      1].getText().strip()

        elif("Yesterday's estimated" in text):
            usage_numbers['yesterday_cost'] = elements[idx +
                                                       1].getText().strip()

        elif("Monthly Energy" in text):
            usage_numbers['monthly_use'] = elements[idx + 1].getText().strip()

        elif("Monthly estimated" in text):
            usage_numbers['monthly_cost'] = elements[idx + 1].getText().strip()

    return [usage_numbers]
