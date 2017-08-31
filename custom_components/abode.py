"""
This component provides basic support for Abode Home Security system.

For more details about this component, please refer to the documentation at
https://home-assistant.io/components/abode/
"""
import asyncio
import logging
from functools import partial
from os import path

import voluptuous as vol
from requests.exceptions import HTTPError, ConnectTimeout
from homeassistant.helpers import discovery
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.config import load_yaml_config_file
from homeassistant.const import (ATTR_ATTRIBUTION, ATTR_DATE, ATTR_TIME,
                                 CONF_USERNAME, CONF_PASSWORD,
                                 CONF_NAME, EVENT_HOMEASSISTANT_STOP,
                                 EVENT_HOMEASSISTANT_START)

REQUIREMENTS = ['abodepy==0.10.0']

_LOGGER = logging.getLogger(__name__)

CONF_ATTRIBUTION = "Data provided by goabode.com"

DOMAIN = 'abode'
DEFAULT_NAME = 'Abode'
DATA_ABODE = 'abode'

NOTIFICATION_ID = 'abode_notification'
NOTIFICATION_TITLE = 'Abode Security Setup'

EVENT_ABODE_ALARM = 'abode_alarm'
EVENT_ABODE_ALARM_END = 'abode_alarm_end'
EVENT_ABODE_AUTOMATION = 'abode_automation'
EVENT_ABODE_FAULT = 'abode_panel_fault'
EVENT_ABODE_RESTORE = 'abode_panel_restore'

SERVICE_CHANGE_ABODE_SETTING = 'change_abode_setting'

ATTR_DEVICE_ID = 'device_id'
ATTR_DEVICE_NAME = 'device_name'
ATTR_DEVICE_TYPE = 'device_type'
ATTR_EVENT_CODE = 'event_code'
ATTR_EVENT_NAME = 'event_name'
ATTR_EVENT_TYPE = 'event_type'
ATTR_EVENT_UTC = 'event_utc'
ATTR_SETTING = 'setting'
ATTR_USER_NAME = 'user_name'
ATTR_VALUE = 'value'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }),
}, extra=vol.ALLOW_EXTRA)

CHANGE_SETTING_SCHEMA = vol.Schema({
    vol.Required(ATTR_SETTING): cv.string,
    vol.Required(ATTR_VALUE): cv.string
})

ABODE_PLATFORMS = [
    'alarm_control_panel', 'binary_sensor', 'lock', 'switch', 'cover'
]


def setup(hass, config):
    """Set up Abode component."""
    import abodepy
    import abodepy.helpers.timeline as TIMELINE
    from abodepy.exceptions import AbodeException

    conf = config[DOMAIN]
    username = conf.get(CONF_USERNAME)
    password = conf.get(CONF_PASSWORD)

    try:
        hass.data[DATA_ABODE] = abode = abodepy.Abode(username, password,
                                                      auto_login=True,
                                                      get_devices=True)

    except (ConnectTimeout, HTTPError) as ex:
        _LOGGER.error("Unable to connect to Abode: %s", str(ex))
        hass.components.persistent_notification.create(
            'Error: {}<br />'
            'You will need to restart hass after fixing.'
            ''.format(ex),
            title=NOTIFICATION_TITLE,
            notification_id=NOTIFICATION_ID)
        return False

    for platform in ABODE_PLATFORMS:
        discovery.load_platform(hass, platform, DOMAIN, {}, config)

    # Start, stop, and event callbacks
    def startup(event):
        """Listen for push events."""
        abode.get_event_controller().start()

    def logout(event):
        """Logout of Abode."""
        abode.get_event_controller().stop()
        abode.logout()
        _LOGGER.info("Logged out of Abode")

    hass.bus.listen_once(EVENT_HOMEASSISTANT_START, startup)
    hass.bus.listen_once(EVENT_HOMEASSISTANT_STOP, logout)

    def event_callback(event_json, event=None):
        """Handle an event callback from Abode."""
        if event:
            data = {
                ATTR_DEVICE_ID: event_json.get(ATTR_DEVICE_ID, ''),
                ATTR_DEVICE_NAME: event_json.get(ATTR_DEVICE_NAME, ''),
                ATTR_DEVICE_TYPE: event_json.get(ATTR_DEVICE_TYPE, ''),
                ATTR_EVENT_CODE: event_json.get(ATTR_EVENT_CODE, ''),
                ATTR_EVENT_NAME: event_json.get(ATTR_EVENT_NAME, ''),
                ATTR_EVENT_TYPE: event_json.get(ATTR_EVENT_TYPE, ''),
                ATTR_EVENT_UTC: event_json.get(ATTR_EVENT_UTC, ''),
                ATTR_USER_NAME: event_json.get(ATTR_USER_NAME, ''),
                ATTR_DATE: event_json.get(ATTR_DATE, ''),
                ATTR_TIME: event_json.get(ATTR_TIME, ''),
            }
            _LOGGER.info(data)
            hass.bus.fire(event, data)

    abode.get_event_controller().add_event_group_callback(
        TIMELINE.ALARM_GROUP,
        partial(event_callback, event=EVENT_ABODE_ALARM))

    abode.get_event_controller().add_event_group_callback(
        TIMELINE.ALARM_END_GROUP,
        partial(event_callback, event=EVENT_ABODE_ALARM_END))

    abode.get_event_controller().add_event_group_callback(
        TIMELINE.PANEL_FAULT_GROUP,
        partial(event_callback, event=EVENT_ABODE_FAULT))

    abode.get_event_controller().add_event_group_callback(
        TIMELINE.PANEL_RESTORE_GROUP,
        partial(event_callback, event=EVENT_ABODE_RESTORE))

    abode.get_event_controller().add_event_group_callback(
        TIMELINE.AUTOMATION_GROUP,
        partial(event_callback, event=EVENT_ABODE_AUTOMATION))

    # Services
    def change_setting(call):
        """Change an Abode system setting."""
        setting = call.data.get(ATTR_SETTING, None)
        value = call.data.get(ATTR_VALUE, None)
        if setting and value:
            try:
                abode.set_setting(setting, value)
            except AbodeException as ex:
                _LOGGER.warning(ex)

    descriptions = load_yaml_config_file(
        path.join(path.dirname(__file__), 'services.yaml'))

    hass.services.register(
        DOMAIN, SERVICE_CHANGE_ABODE_SETTING, change_setting,
        descriptions.get(SERVICE_CHANGE_ABODE_SETTING),
        schema=CHANGE_SETTING_SCHEMA)

    return True


class AbodeDevice(Entity):
    """Representation of an Abode device."""

    def __init__(self, controller, device):
        """Initialize a sensor for Abode device."""
        self._controller = controller
        self._device = device

    @asyncio.coroutine
    def async_added_to_hass(self):
        """Subscribe Abode events."""
        self.hass.async_add_job(
            self._controller.get_event_controller().add_device_callback,
            self._device.device_id, self._update_callback
        )

    @property
    def should_poll(self):
        """Return the polling state."""
        return False

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._device.name

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return {
            ATTR_ATTRIBUTION: CONF_ATTRIBUTION,
            'device_id': self._device.device_id,
            'battery_low': self._device.battery_low,
            'no_response': self._device.no_response
        }

    def _update_callback(self, device):
        """Update the device state."""
        self.schedule_update_ha_state()
