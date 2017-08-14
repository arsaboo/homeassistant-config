"""
Interfaces with Abode Home Security System.

"""

import logging
import abodepy
from datetime import datetime, timedelta

import voluptuous as vol

import homeassistant.components.alarm_control_panel as alarm
from homeassistant.util import Throttle
from homeassistant.components.alarm_control_panel import PLATFORM_SCHEMA, DOMAIN
from homeassistant.const import (CONF_SCAN_INTERVAL,
    CONF_PASSWORD, CONF_USERNAME, STATE_UNKNOWN, CONF_NAME)
import homeassistant.helpers.config_validation as cv
import homeassistant.loader as loader

REQUIREMENTS = ['abodepy==0.5.1']

_LOGGER = logging.getLogger(__name__)

SERVICE_ABODE_REFRESH_STATE='abode_refresh_state'
DEFAULT_NAME = 'Abode'
ALARM_STATE_HOME = 'home'
ALARM_STATE_STANDBY = 'standby'
ALARM_STATE_AWAY = 'away'
ICON = 'mdi:security'
SCAN_INTERVAL = timedelta(minutes=2)


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Required(CONF_USERNAME): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string
})

def abode(uname, passwd):
    return abodepy.Abode(username=uname, password=passwd, get_devices=True)

def get_abode_mode(uname, passwd):
    """Get Abode mode."""
    return abode(uname, passwd).get_alarm().mode

def set_abode_mode(uname, passwd, mode):
    """Set Abode mode."""
    abode(uname, passwd).get_alarm().set_mode(mode)

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Abode platform."""

    name = config.get(CONF_NAME)
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    add_devices([AbodeAlarm(hass, name, username, password)],True)


class AbodeAlarm(alarm.AlarmControlPanel):
    """Representation a Abode alarm."""

    def __init__(self, hass, name, username, password):
        """Initialize the Abode alarm."""
        self._hass = hass
        self._name = name
        self._username = username
        self._password = password
        self._state = STATE_UNKNOWN
        self._hass.services.register(DOMAIN, SERVICE_ABODE_REFRESH_STATE, self.abode_refresh_state)

    @property
    def name(self):
        """Return the name of the device."""
        if self._name is not None:
            return self._name
        else:
            return 'Abode'

    @property
    def icon(self):
        """Return icon."""
        return ICON

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @Throttle(SCAN_INTERVAL)
    def update(self):
        """Return the state of the device."""
        status = get_abode_mode(self._username, self._password)
        if status == 'standby':
            state = ALARM_STATE_STANDBY
        elif status == 'home':
            state = ALARM_STATE_HOME
        elif status == 'away':
            state = ALARM_STATE_AWAY
        else:
            state = STATE_UNKNOWN
        self._state = state


    def alarm_disarm(self, code=None):
        """Send disarm command."""
        set_abode_mode(self._username, self._password, ALARM_STATE_STANDBY)
        self._state = ALARM_STATE_STANDBY
        self.schedule_update_ha_state()
        _LOGGER.info("Abode security disarmed")

    def alarm_arm_home(self, code=None):
        """Send arm home command."""
        set_abode_mode(self._username, self._password, ALARM_STATE_HOME)
        self._state = ALARM_STATE_HOME
        self.schedule_update_ha_state()
        _LOGGER.info("Abode security home")

    def alarm_arm_away(self, code=None):
        """Send arm away command."""
        set_abode_mode(self._username, self._password, ALARM_STATE_AWAY)
        self._state = ALARM_STATE_AWAY
        self.schedule_update_ha_state()
        _LOGGER.info("Abode security armed")

    def abode_refresh_state(self):
        """Return the state of the device."""
        status = get_abode_mode(self._username, self._password)
        if status == 'standby':
            state = ALARM_STATE_STANDBY
        elif status == 'home':
            state = ALARM_STATE_HOME
        elif status == 'away':
            state = ALARM_STATE_AWAY
        else:
            state = STATE_UNKNOWN
        self._state = state
        self.schedule_update_ha_state()
