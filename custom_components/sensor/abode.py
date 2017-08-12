"""
Get current Abode security mode.
"""
import os
import logging
from datetime import datetime, timedelta

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.util import Throttle
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (CONF_USERNAME, CONF_PASSWORD, CONF_NAME, CONF_SCAN_INTERVAL)
from homeassistant.helpers.entity import Entity

REQUIREMENTS = ['abodepy==0.5.1']

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = 'Abode'
DEFAULT_SCAN_INTERVAL = timedelta(seconds=600)

TIMEOUT = 10.0

SENSOR_TYPES = {
    'mode': ['mode']
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.positive_int
})

def get_abode_mode(uname, passwd):
    """Get Abode mode."""
    abode_mode_command = 'python3 /home/arsaboo/abodepy/abodecl.py --username ' + '{}'.format(uname) + ' --password ' + '{}'.format(passwd) + ' --mode'
    res = os.popen(abode_mode_command).readline()
    mode = res.split(" ")
    return mode[1]

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up Abode sensor."""
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    sensor_name = config.get(CONF_NAME)
    add_devices([Abode(sensor_name, username, password)], True)

class Abode(Entity):
    """Implementation of the Abode security mode sensor."""

    def __init__(self, sensor_name, username, password):
        """Initialize the sensor."""
        self.username = username
        self.password = password
        self._name = sensor_name
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return 'mdi:security-home'

    @Throttle(CONF_SCAN_INTERVAL)
    def update(self):
        """Get the latest data and updates the states."""
        t_mode = get_abode_mode(self.username, self.password)
        self._state = t_mode
