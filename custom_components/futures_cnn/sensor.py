"""
@ Author      : Alok Saboo
@ Description : CNN Futures - It queries CNN website to obtain futures data

@ Notes:        Copy this file and place it in your
                "Home Assistant Config folder\futures_cnn\" folder
                The following resources are supported: sp, sp_change_pct, sp_change, dow, dow_change_pct, dow_change, nasdaq, nasdaq_change_pct, nasdaq_change
                Check the configuration in sensor.yaml (search for futures_cnn).
"""

from datetime import datetime, timedelta
import logging
import requests

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (CONF_NAME, CONF_RESOURCES, ATTR_ATTRIBUTION)
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

REQUIREMENTS = ['beautifulsoup4==4.7.1']

_LOGGER = logging.getLogger(__name__)
_RESOURCE = 'http://money.cnn.com/data/premarket/'

ATTRIBUTION = "Data provided by CNN.com"
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
        attr[ATTR_ATTRIBUTION] = ATTRIBUTION
        return attr

    @property
    def available(self):
        """Could the device be accessed during the last update call."""
        return self.rest.available

    def futures_change(self, position):
        fut_ch = self.rest.data[position]
        if "+" in fut_ch:
            value = float(fut_ch.split("+")[1])
        else:
            value = -1 * float(fut_ch.split("-")[1])
        return value


    def futures_change_pct(self, position):
        fut_ch = self.rest.data[position].strip().split("%")[0]
        if "+" in fut_ch:
            value = float(fut_ch.split("+")[1])
        else:
            value = -1 * float(fut_ch.split("-")[1])
        return value

    def update(self):
        """Update current date."""
        self.rest.update()
        if self.type == 'sp':
            self._state = float(self.rest.data[2])
        elif self.type == 'sp_change_pct':
            self._state = self.futures_change_pct(1)
        elif self.type == 'sp_change':
            self._state = self.futures_change(0)
        elif self.type == 'dow':
            self._state = float(self.rest.data[8])
        elif self.type == 'dow_change_pct':
            self._state = self.futures_change_pct(7)
        elif self.type == 'dow_change':
            self._state = self.futures_change(6)
        elif self.type == 'nasdaq':
            self._state = float(self.rest.data[5])
        elif self.type == 'nasdaq_change_pct':
            self._state = self.futures_change_pct(4)
        elif self.type == 'nasdaq_change':
            self._state = self.futures_change(3)

class CNNFuturesData(object):
    """Get data from cnn.com."""

    def __init__(self, resource):
        """Initialize the data object."""
        self._resource = resource
        self.data = None
        self.available = True

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Get the latest data from CNN."""
        from bs4 import BeautifulSoup
        if (self.data is None or datetime.today().isoweekday() != 6 or (datetime.today().isoweekday() == 7 and datetime.today().hour > 17)):
            try:
                r = requests.get(self._resource, timeout=10)
                soup = BeautifulSoup(r.text, 'html.parser')
                req_soup = soup.find('div',class_='wsod_fLeft wsod_marketsLeftCol')
                soup_info = req_soup.find_all('tr')
                cnn_market_data = []
                for i in range(0,len(soup_info),5):
                    # Change
                    cnn_market_data.append(soup_info[i].find('span', {'class': ['posData', 'negData', 'unchData']}).text.strip())
                    # ChangePct
                    cnn_market_data.append(soup_info[i].find('span', {'class': ['posChangePct', 'negChangePct', 'unchChangePct']}).text.strip())
                    # Level
                    cnn_market_data.append(soup_info[i+1].find('span').text.strip().replace(',',''))
                    self.data = cnn_market_data
                    self.available = True
            except requests.exceptions.ConnectionError:
                _LOGGER.error("Connection error")
                self.data = None
                self.available = False
