"""
Support for getting sector performance information from Alphavantage.

"""
import logging
import json
from datetime import timedelta

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_API_KEY, CONF_MONITORED_CONDITIONS
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)
_ENDPOINT = 'https://www.alphavantage.co/query?function=SECTOR&apikey='

DEFAULT_NAME = 'Alphavantage'

SCAN_INTERVAL = timedelta(minutes=5)
MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=15)

MONITORED_CONDITIONS = {
    'information_technology': ['Information Technology', '%', 'mdi:currency-usd'],
    'health_care': ['Health Care', '%', 'mdi:currency-usd'],
    'consumer_discretionary': ['Consumer Discretionary', '%', 'mdi:currency-usd'],
    'financials': ['Financials', '%', 'mdi:currency-usd'],
    'industrials': ['Industrials', '%', 'mdi:currency-usd'],
    'utilities': ['Utilities', '%', 'mdi:currency-usd'],
    'consumer_staples': ['Consumer Staples', '%', 'mdi:currency-usd'],
    'materials': ['Materials', '%', 'mdi:currency-usd'],
    'communication_services': ['Communication Services', '%', 'mdi:currency-usd'],
    'energy': ['Energy', '%', 'mdi:currency-usd'],
    'real_estate': ['Real Estate', '%', 'mdi:currency-usd'],
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_API_KEY): cv.string
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Sector performance sensor."""
    api_key = config.get(CONF_API_KEY)
    api = SectorPerfAPI(api_key)
    sensors = [SectorPerfSensor(hass, api, condition)
               for condition in MONITORED_CONDITIONS]

    add_devices(sensors, True)


class SectorPerfSensor(Entity):
    """Representation of a SectorPerf sensor."""

    def __init__(self, hass, api, variable):
        """Initialize a Sector Performance sensor."""
        self._hass = hass
        self._api = api
        self._var_id = variable

        variable_info = MONITORED_CONDITIONS[variable]
        self._var_name = variable_info[0]
        self._var_units = variable_info[1]
        self._var_icon = variable_info[2]

    @property
    def name(self):
        """Return the name of the sensor."""
        return "{}".format(self._var_name)

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._var_icon

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return self._var_units

    # pylint: disable=no-member
    @property
    def state(self):
        """Return the state of the device."""
        try:
            return_value = self._api.data[
                'Rank A: Real-Time Performance'][self._var_name]
            return float(return_value[:-1])
        except TypeError:
            return None

    @property
    def available(self):
        """Could the device be accessed during the last update call."""
        return self._api.available

    def update(self):
        """Get the latest data from Alphavantage."""
        self._api.update()


class SectorPerfAPI(object):
    """Get the latest data and update the states."""

    def __init__(self, api_key):
        """Initialize the data object."""
        from homeassistant.components.sensor.rest import RestData

        resource = "{}{}".format(_ENDPOINT, api_key)
        self._rest = RestData('GET', resource, None, None, None, False)
        self.data = None
        self.available = True
        self.update()

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Get the latest data from Alphavantage."""
        try:
            self._rest.update()
            self.data = json.loads(self._rest.data)
            self.available = True
        except TypeError:
            _LOGGER.error("Unable to fetch data from Alphavantage")
            self.available = False
