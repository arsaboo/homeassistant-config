"""
@ Author      : Alok Saboo
@ Description : CNN Futures - It queries CNN website to obtain futures data

@ Notes:        Copy this file and place it in your
                "Home Assistant Config folder\custom_components\sensor\" folder
                You may have to install two additional packages
                sudo apt-get install libxslt1.1 libxml2-dev
                The following resources are supported: sp, sp_change_pct, sp_change
                dow, dow_change_pct, dow_change, nasdaq, nasdaq_change_pct, nasdaq_change
                Check the configuration in sensor.yaml (search for futures_cnn).
"""

from datetime import datetime, timedelta
import logging

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (CONF_NAME, CONF_RESOURCES, ATTR_ATTRIBUTION)
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

REQUIREMENTS = ['raschietto']

_LOGGER = logging.getLogger(__name__)
_RESOURCE = 'http://money.cnn.com/data/premarket/'

CONF_ATTRIBUTION = "Data provided by CNN.com"
DEFAULT_ICON = 'mdi:currency-usd'

SCAN_INTERVAL = timedelta(seconds=30)
MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=5)

SENSOR_TYPES = {
    'sp': ['S&P Futures', ' '],
    'sp_change_pct': ['S&P Futures change pct', '%'],
    'sp_change': ['S&P Futures change', ' '],
    'dow': ['DOW Futures', ' '],
    'dow_change_pct': ['DOW Futures change pct', '%'],
    'dow_change': ['DOW Futures change', ' '],
    'nasdaq': ['NASDAQ Futures', ' '],
    'nasdaq_change_pct': ['NASDAQ Futures change pct', '%'],
    'nasdaq_change': ['NASDAQ Futures change', ' '],
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_RESOURCES):
        vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the CNN Futures sensor."""
    rest = CNNFuturesData(_RESOURCE)
    sensors = []
    for resource in config[CONF_RESOURCES]:
        sensors.append(CNNFuturesSensor(resource,rest))

    add_devices(sensors, True)


class CNNFuturesSensor(Entity):
    """Implementing the CNN Futures sensor."""

    def __init__(self, sensor_type, rest):
        """Initialize the sensor."""
        self._name = SENSOR_TYPES[sensor_type][0]
        self._unit_of_measurement = SENSOR_TYPES[sensor_type][1]
        self._icon = DEFAULT_ICON
        self.rest = rest
        self.type = sensor_type
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name.rstrip()

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        if self.type in ['sp', 'dow', 'nasdaq'] or self._state == 0:
            icon = DEFAULT_ICON
        elif self._state > 0:
            icon = 'mdi:arrow-up-bold-circle'
        elif self._state < 0:
            icon = 'mdi:arrow-down-bold-circle'
        return icon

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit_of_measurement

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        attr = {}
        attr[ATTR_ATTRIBUTION] = CONF_ATTRIBUTION
        return attr

    def futures(self, position):
        return float(self.rest.data[position].split("\n")[0].replace(',',''))

    def futures_change(self, position):
        return float(self.rest.data[position].split("\n")[0])

    def futures_change_pct(self, position):
        return float(self.rest.data[position].split("\n")[2].split("%")[0].strip())

    def update(self):
        """Update current date."""
        self.rest.update()
        if self.type == 'sp':
            self._state = self.futures(1)
        elif self.type == 'sp_change_pct':
            self._state = self.futures_change_pct(0)
        elif self.type == 'sp_change':
            self._state = self.futures_change(0)
        elif self.type == 'dow':
            self._state = self.futures(9)
        elif self.type == 'dow_change_pct':
            self._state = self.futures_change_pct(8)
        elif self.type == 'dow_change':
            self._state = self.futures_change(8)
        elif self.type == 'nasdaq':
            self._state = self.futures(5)
        elif self.type == 'nasdaq_change_pct':
            self._state = self.futures_change_pct(4)
        elif self.type == 'nasdaq_change':
            self._state = self.futures_change(4)

class CNNFuturesData(object):
    """Get data from cnn.com."""

    def __init__(self, resource):
        """Initialize the data object."""
        self._resource = resource
        self.data = None

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Get the latest data from CNN."""
        from raschietto import Raschietto, Matcher
        if (self.data is None or datetime.today().isoweekday() != 6 or
            (datetime.today().isoweekday() == 7 and datetime.today().hour > 17)):
            page = Raschietto.from_url(self._resource)
            _LOGGER.debug("CNN page loaded")
            futures_matcher = Matcher(".wsod_bold.wsod_aRight")
            futures = futures_matcher(page, multiple=True)
            sp = futures[0].split("\n")
            self.data = futures
