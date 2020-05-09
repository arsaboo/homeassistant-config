"""Support for Google - Calendar Event Devices."""
from datetime import timedelta
import logging

from imapclient import IMAPClient
from mailparser import parse_from_bytes
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity

from .const import (
    CONF_EMAIL, CONF_PASSWORD, CONF_SHOW_ALL, CONF_IMAP_SERVER,
    CONF_IMAP_PORT, CONF_EMAIL_FOLDER, ATTR_EMAILS, ATTR_COUNT,
    ATTR_TRACKING_NUMBERS, EMAIL_ATTR_FROM, EMAIL_ATTR_SUBJECT,
    EMAIL_ATTR_BODY)

from .parsers.ups import ATTR_UPS, EMAIL_DOMAIN_UPS, parse_ups
from .parsers.fedex import ATTR_FEDEX, EMAIL_DOMAIN_FEDEX, parse_fedex
from .parsers.paypal import ATTR_PAYPAL, EMAIL_DOMAIN_PAYPAL, parse_paypal
from .parsers.usps import ATTR_USPS, EMAIL_DOMAIN_USPS, parse_usps
from .parsers.ali_express import ATTR_ALI_EXPRESS, EMAIL_DOMAIN_ALI_EXPRESS, parse_ali_express
from .parsers.newegg import ATTR_NEWEGG, EMAIL_DOMAIN_NEWEGG, parse_newegg
from .parsers.rockauto import ATTR_ROCKAUTO, EMAIL_DOMAIN_ROCKAUTO, parse_rockauto
from .parsers.bh_photo import ATTR_BH_PHOTO, EMAIL_DOMAIN_BH_PHOTO, parse_bh_photo
from .parsers.ebay import ATTR_EBAY, EMAIL_DOMAIN_EBAY, parse_ebay
from .parsers.dhl import ATTR_DHL, EMAIL_DOMAIN_DHL, parse_dhl
from .parsers.hue import ATTR_HUE, EMAIL_DOMAIN_HUE, parse_hue
from .parsers.google_express import ATTR_GOOGLE_EXPRESS, EMAIL_DOMAIN_GOOGLE_EXPRESS, parse_google_express
from .parsers.western_digital import ATTR_WESTERN_DIGITAL, EMAIL_DOMAIN_WESTERN_DIGITAL, parse_western_digital
from .parsers.monoprice import ATTR_MONOPRICE, EMAIL_DOMAIN_MONOPRICE, parse_monoprice
from .parsers.georgia_power import ATTR_GEORGIA_POWER, EMAIL_DOMAIN_GEORGIA_POWER, parse_georgia_power
from .parsers.best_buy import ATTR_BEST_BUY, EMAIL_DOMAIN_BEST_BUY, parse_best_buy
from .parsers.dollar_shave_club import ATTR_DOLLAR_SHAVE_CLUB, EMAIL_DOMAIN_DOLLAR_SHAVE_CLUB, parse_dollar_shave_club
from .parsers.nuleaf import ATTR_NULEAF, EMAIL_DOMAIN_NULEAF, parse_nuleaf
from .parsers.timeless import ATTR_TIMELESS, EMAIL_DOMAIN_TIMLESS, parse_timeless

parsers = [
    (ATTR_UPS, EMAIL_DOMAIN_UPS, parse_ups),
    (ATTR_FEDEX, EMAIL_DOMAIN_FEDEX, parse_fedex),
    (ATTR_PAYPAL, EMAIL_DOMAIN_PAYPAL, parse_paypal),
    (ATTR_USPS, EMAIL_DOMAIN_USPS, parse_usps),
    (ATTR_ALI_EXPRESS, EMAIL_DOMAIN_ALI_EXPRESS, parse_ali_express),
    (ATTR_NEWEGG, EMAIL_DOMAIN_NEWEGG, parse_newegg),
    (ATTR_ROCKAUTO, EMAIL_DOMAIN_ROCKAUTO, parse_rockauto),
    (ATTR_BH_PHOTO, EMAIL_DOMAIN_BH_PHOTO, parse_bh_photo),
    (ATTR_EBAY, EMAIL_DOMAIN_EBAY, parse_ebay),
    (ATTR_DHL, EMAIL_DOMAIN_DHL, parse_dhl),
    (ATTR_HUE, EMAIL_DOMAIN_HUE, parse_hue),
    (ATTR_GOOGLE_EXPRESS, EMAIL_DOMAIN_GOOGLE_EXPRESS, parse_google_express),
    (ATTR_WESTERN_DIGITAL, EMAIL_DOMAIN_WESTERN_DIGITAL, parse_western_digital),
    (ATTR_MONOPRICE, EMAIL_DOMAIN_MONOPRICE, parse_monoprice),
    (ATTR_GEORGIA_POWER, EMAIL_DOMAIN_GEORGIA_POWER, parse_georgia_power),
    (ATTR_BEST_BUY, EMAIL_DOMAIN_BEST_BUY, parse_best_buy),
    (ATTR_DOLLAR_SHAVE_CLUB, EMAIL_DOMAIN_DOLLAR_SHAVE_CLUB, parse_dollar_shave_club),
    (ATTR_NULEAF, EMAIL_DOMAIN_NULEAF, parse_nuleaf),
    (ATTR_TIMELESS, EMAIL_DOMAIN_TIMLESS, parse_timeless),
]

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'email'
SCAN_INTERVAL = timedelta(seconds=5*60)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_EMAIL): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Required(CONF_IMAP_SERVER, default='imap.gmail.com'): cv.string,
    vol.Required(CONF_IMAP_PORT, default=993): cv.positive_int,
    vol.Required(CONF_EMAIL_FOLDER, default='INBOX'): cv.string,
    vol.Required(CONF_SHOW_ALL, default=False): cv.boolean,
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Email platform."""
    add_entities([EmailEntity(config)], True)


class EmailEntity(Entity):
    """Email Entity."""

    def __init__(self, config):
        """Init the Email Entity."""
        self._attr = None

        self.imap_server = config[CONF_IMAP_SERVER]
        self.imap_port = config[CONF_IMAP_PORT]
        self.email_address = config[CONF_EMAIL]
        self.password = config[CONF_PASSWORD]
        self.email_folder = config[CONF_EMAIL_FOLDER]

        self.flag = 'ALL' if config[CONF_SHOW_ALL] else 'UNSEEN'

    def update(self):
        """Update data from Email API."""
        self._attr = {
            ATTR_EMAILS: [],
            ATTR_TRACKING_NUMBERS: {}
        }
        emails = []
        server = IMAPClient(self.imap_server, use_uid=True)

        try:
            server.login(self.email_address, self.password)
            server.select_folder(self.email_folder, readonly=True)
        except Exception as err:
            _LOGGER.error('IMAPClient login error {}'.format(err))
            return False

        try:
            messages = server.search(self.flag)
            for uid, message_data in server.fetch(messages, 'RFC822').items():
                try:
                    mail = parse_from_bytes(message_data[b'RFC822'])
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
                    _LOGGER.error(
                        'mailparser parse_from_bytes error: {}'.format(err))

        except Exception as err:
            _LOGGER.error('IMAPClient update error: {}'.format(err))

        self._attr[ATTR_COUNT] = len(emails)
        self._attr[ATTR_TRACKING_NUMBERS] = {}

        # empty out all parser arrays
        for ATTR, EMAIL_DOMAIN, parser in parsers:
            self._attr[ATTR_TRACKING_NUMBERS][ATTR] = []

        # for each email run each parser and save in the corresponding ATTR
        for email in emails:
            email_from = email[EMAIL_ATTR_FROM]
            if isinstance(email_from, (list, tuple)):
                email_from = list(email_from)
                email_from = ''.join(list(email_from[0]))

            for ATTR, EMAIL_DOMAIN, parser in parsers:
                try:
                    if EMAIL_DOMAIN in email_from:
                        self._attr[ATTR_TRACKING_NUMBERS][ATTR] = self._attr[ATTR_TRACKING_NUMBERS][ATTR] + parser(
                            email=email)
                except Exception as err:
                    _LOGGER.error('{} error: {}'.format(ATTR, err))

        # remove duplicates
        for ATTR, EMAIL_DOMAIN, parser in parsers:
            tracking_domain = self._attr[ATTR_TRACKING_NUMBERS][ATTR]
            if len(tracking_domain) > 0 and isinstance(tracking_domain[0], str):
                self._attr[ATTR_TRACKING_NUMBERS][ATTR] = list(
                    dict.fromkeys(tracking_domain))

        server.logout()

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'email_{}'.format(self.email_address)

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
