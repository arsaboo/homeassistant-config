"""
This component provides HA alarm_control_panel support for Abode System.

For more details about this platform, please refer to the documentation at

"""
import logging
from datetime import timedelta

import homeassistant.helpers.config_validation as cv

from homeassistant.util import Throttle
from custom_components.abode import (DATA_ABODE, DEFAULT_NAME)
from homeassistant.components.alarm_control_panel import DOMAIN
#from homeassistant.components.abode import (CONF_ATTRIBUTION, DATA_ABODE)
from homeassistant.const import (STATE_UNKNOWN)
import homeassistant.components.alarm_control_panel as alarm

DEPENDENCIES = ['abode']

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=5)
ALARM_STATE_HOME = 'home'
ALARM_STATE_STANDBY = 'standby'
ALARM_STATE_AWAY = 'away'
SERVICE_ABODE_REFRESH_STATE = 'abode_refresh_state'
ICON = 'mdi:security'


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up a sensor for an Abode device."""
    abode = hass.data.get(DATA_ABODE)
    if not abode:
        _LOGGER.debug('No DATA_ABODE')
        return False

    alarm = AbodeAlarm(hass, abode)
    hass.services.register(
        DOMAIN, SERVICE_ABODE_REFRESH_STATE, alarm.abode_refresh_state)
    add_devices([alarm], True)
    return True


class AbodeAlarm(alarm.AlarmControlPanel):
    """An alarm_control_panel implementation for Abode."""

    def __init__(self, hass, data):
        """Initialize a alarm control panel for Abode."""
        super(AbodeAlarm, self).__init__()
        self._data = data
        self._name = "{0}".format(DEFAULT_NAME)
        self._state = STATE_UNKNOWN

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Return icon."""
        return ICON

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    def update(self):
        """Return the state of the device."""
        status = self._data.get_alarm().mode
        _LOGGER.debug("Abode status is %s", status)
        if status == 'standby':
            state = ALARM_STATE_STANDBY
        elif status == 'home':
            state = ALARM_STATE_HOME
        elif status == 'away':
            state = ALARM_STATE_AWAY
        else:
            state = STATE_UNKNOWN
        self._state = state
        self._data.get_devices()

    def alarm_disarm(self, code=None):
        """Send disarm command."""
        self._data.get_alarm().set_mode(mode=ALARM_STATE_STANDBY)
        self._state = ALARM_STATE_STANDBY
        self.schedule_update_ha_state()
        _LOGGER.debug("Abode security disarmed")

    def alarm_arm_home(self, code=None):
        """Send arm home command."""
        self._data.get_alarm().set_mode(mode=ALARM_STATE_HOME)
        self._state = ALARM_STATE_HOME
        self.schedule_update_ha_state()
        _LOGGER.debug("Abode security home")

    def alarm_arm_away(self, code=None):
        """Send arm away command."""
        self._data.get_alarm().set_mode(mode=ALARM_STATE_AWAY)
        self._state = ALARM_STATE_AWAY
        self.schedule_update_ha_state()
        _LOGGER.debug("Abode security armed")

    def abode_refresh_state(self, code=None):
        """Return the state of the device."""
        status = self._data.get_alarm().mode
        _LOGGER.debug("Abode status is %s", status)
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
        self._data.get_devices()
