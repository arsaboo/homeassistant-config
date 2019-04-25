"""Support for Google - Calendar Event Devices."""
from datetime import timedelta
import logging

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity

from .const import (
    CONF_EMAIL, CONF_PASSWORD, CONFIG_SEARCH, CONF_SMTP_SERVER, 
    CONF_SMTP_PORT, CONF_EMAIL_FOLDER, ATTR_EMAILS, ATTR_COUNT, 
    ATTR_TRACKING_NUMBERS, EMAIL_ATTR_FROM, EMAIL_ATTR_SUBJECT, 
    EMAIL_ATTR_BODY)

from .parsers.ups import parse_ups, ATTR_UPS
from .parsers.fedex import parse_fedex, ATTR_FEDEX
from .parsers.usps import parse_usps, ATTR_USPS
from .parsers.ali_express import parse_ali_express, ATTR_ALI_EXPRESS
from .parsers.newegg import parse_newegg, ATTR_NEWEGG
from .parsers.rockauto import parse_rockauto, ATTR_ROCKAUTO
from .parsers.bh_photo import ATTR_BH_PHOTO, parse_bh_photo
from .parsers.paypal import ATTR_PAYPAL, parse_paypal

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'email'
SCAN_INTERVAL = timedelta(seconds=30)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_EMAIL): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Required(CONF_SMTP_SERVER, default='imap.gmail.com'): cv.string,
    vol.Required(CONF_SMTP_PORT, default=993): cv.positive_int,
    vol.Required(CONF_EMAIL_FOLDER, default='INBOX'): cv.string,
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Email platform."""
    from imapclient import IMAPClient
    
    smtp_server = config[CONF_SMTP_SERVER]
    smtp_port = config[CONF_SMTP_PORT]

    email_address = config[CONF_EMAIL]
    password = config[CONF_PASSWORD]
    email_folder = config[CONF_EMAIL_FOLDER]

    try:
        server = IMAPClient(smtp_server, use_uid=True)
        server.login(email_address, password)
        select_info = server.select_folder(email_folder, readonly=True)
        add_entities([EmailEntity(server, config)], True)
        return True

    except Exception as err:
        _LOGGER.error(f'IMAPClient setup_platform error: {err}')
        return False


class EmailEntity(Entity):
    """Email Entity."""

    def __init__(self, server, config):
        """Init the Email Entity."""
        self.server = server
        self.email_address = config[CONF_EMAIL]
        self._attr = None

    def update(self):
        """Update data from Email API."""
        import mailparser
        self._attr = {
            ATTR_EMAILS: [], 
            ATTR_TRACKING_NUMBERS: {}
        }
        emails = []

        try: 
            messages = self.server.search('UNSEEN')
            for uid, message_data in self.server.fetch(messages, 'RFC822').items():
                try:
                    mail = mailparser.parse_from_bytes(message_data[b'RFC822'])
                    emails.append({
                        EMAIL_ATTR_FROM: mail.from_,
                        EMAIL_ATTR_SUBJECT: mail.subject,
                        EMAIL_ATTR_BODY: mail.body
                    })
                    self._attr[ATTR_EMAILS].append({
                        EMAIL_ATTR_FROM: mail.from_,
                        EMAIL_ATTR_SUBJECT: mail.subject,
                    })
                except Exception as err:
                    _LOGGER.error(f'mailparser parse_from_bytes error: {err}')

        except Exception as err:
            _LOGGER.error(f'IMAPClient update error: {err}')

        self._attr[ATTR_COUNT] = len(emails)

        try:
            self._attr[ATTR_TRACKING_NUMBERS][ATTR_UPS] = parse_ups(emails)
            self._attr[ATTR_TRACKING_NUMBERS][ATTR_FEDEX] = parse_fedex(emails)
            self._attr[ATTR_TRACKING_NUMBERS][ATTR_USPS] = parse_usps(emails)
            self._attr[ATTR_TRACKING_NUMBERS][ATTR_ALI_EXPRESS] = parse_ali_express(emails)
            self._attr[ATTR_TRACKING_NUMBERS][ATTR_NEWEGG] = parse_newegg(emails)
            self._attr[ATTR_TRACKING_NUMBERS][ATTR_ROCKAUTO] = parse_rockauto(emails)
            self._attr[ATTR_TRACKING_NUMBERS][ATTR_BH_PHOTO] = parse_bh_photo(emails)
            self._attr[ATTR_TRACKING_NUMBERS][ATTR_PAYPAL] = parse_paypal(emails)
        except Exception as err:
            _LOGGER.error(f'Parsers error: {err}')

    @property
    def name(self):
        """Return the name of the sensor."""
        return f'email_{self.email_address}'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._attr.get('count', 0)

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._attr

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return 'mdi:email'