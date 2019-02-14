import logging

import voluptuous as vol

# # Import the device class from the component that you want to support
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.const import CONF_HOST, CONF_USERNAME, CONF_PASSWORD
from homeassistant.const import CONF_VERIFY_SSL, CONF_NAME
from homeassistant.components.switch import PLATFORM_SCHEMA
from homeassistant.helpers.entity import ToggleEntity
import homeassistant.helpers.config_validation as cv


# Home Assistant depends on 3rd party packages for API specific code.
REQUIREMENTS = ['pyunifi==2.16']

_LOGGER = logging.getLogger(__name__)
CONF_PORT = 'port'
CONF_SITE_ID = 'site_id'
CONF_MAC = 'mac_address'

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 8443
DEFAULT_VERIFY_SSL = True
DEFAULT_NAME = 'AP Device'

NOTIFICATION_ID = 'unifi_notification'
NOTIFICATION_TITLE = 'Unifi Controller Setup'

# Validation of user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_HOST, default=DEFAULT_HOST): cv.string,
    vol.Optional(CONF_SITE_ID, default='default'): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PORT, default=DEFAULT_PORT): cv.port,
    vol.Required(CONF_MAC): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_VERIFY_SSL, default=DEFAULT_VERIFY_SSL): vol.Any(
        cv.boolean, cv.isfile),
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Unifi Controller."""
    from pyunifi.controller import Controller, APIError

    host = config.get(CONF_HOST)
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    site_id = config.get(CONF_SITE_ID)
    port = config.get(CONF_PORT)
    verify_ssl = config.get(CONF_VERIFY_SSL)
    mac = config.get(CONF_MAC)
    device_name = config.get(CONF_NAME)

    try:
        ctrl = Controller(host, username, password, port, version='v4',
                          site_id=site_id, ssl_verify=verify_ssl)
    except APIError as ex:
        _LOGGER.error("Failed to connect to Unifi: %s", ex)
        hass.components.persistent_notification.create(
            'Failed to connect to Unifi. '
            'Error: {}<br />'
            'You will need to restart hass after fixing.'
            ''.format(ex),
            title=NOTIFICATION_TITLE,
            notification_id=NOTIFICATION_ID)
        return False

    add_entities([UnifiController(ctrl, mac, device_name)])


class UnifiController(ToggleEntity):
    "Representation of Unifi AP Client Switch"

    def __init__(self, controller, mac, device_name):
        self._controller = controller
        self._mac = mac
        self._name = device_name
        self._state = STATE_OFF

    @property
    def name(self):
        """Return the name of the device"""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def should_poll(self):
        """Poll for status regularly"""
        return True

    @property
    def is_on(self):
        """Return true if device is blocked"""
        return self._state == STATE_ON

    def turn_on(self):
        """Block the device"""
        _LOGGER.debug("Blocking " + self._mac)
        self._controller.block_client(mac=self._mac)
        self.update

    def turn_off(self):
        """Unblock device"""
        _LOGGER.debug("Unblocking " + self._mac)
        self._controller.unblock_client(mac=self._mac)
        self.update

    def update(self):
        """Get the latest state from the Controller"""
        for client in self._controller.get_clients():
            if client['mac'] == self._mac:
                self._state = STATE_OFF
                break
            else:
                self._state = STATE_ON
