"""
Support for getting sector performance information from Wunderground.
Use the following configuration:
sensor:
  - platform: wunderground
    api_key: !secret wunderground_key
    pws_id: !secret wunderground_pws
"""
import logging
import json
from datetime import timedelta

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_API_KEY, CONF_MONITORED_CONDITIONS, TEMP_FAHRENHEIT
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)
_ENDPOINT = 'https://api.weather.com/v2/pws/observations/current?format=json&units=e&stationId='

DEFAULT_NAME = 'Wunderground'
CONF_PWS_ID = 'pws_id'

SCAN_INTERVAL = timedelta(minutes=5)
MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=15)

MONITORED_CONDITIONS = {
    'uv': ['UV', '', 'mdi:sunglasses'],
    'humidity': ['Relative Humidity', '%', 'mdi:water-percent'],
    'temp': ['Temperature', TEMP_FAHRENHEIT, 'mdi:thermometer'],
    'pressure': ['Pressure', 'in', 'mdi:gauge'],
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_API_KEY): cv.string,
    vol.Required(CONF_PWS_ID): cv.string
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Sector performance sensor."""
    api_key = config.get(CONF_API_KEY)
    pws_id = config.get(CONF_PWS_ID)
    api = WundergroundAPI(api_key, pws_id)
    sensors = [WundergroundSensor(hass, api, condition)
               for condition in MONITORED_CONDITIONS]

    add_devices(sensors, True)


class WundergroundSensor(Entity):
    """Representation of a Wunderground sensor."""

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
            if self._var_id in ('uv', 'humidity'):
                return_value = self._api.data[
                    "observations"][0][self._var_id]
            else:
                return_value = self._api.data[
                    "observations"][0]["imperial"][self._var_id]
            return float(return_value)
        except TypeError:
            return None

    @property
    def available(self):
        """Could the device be accessed during the last update call."""
        return self._api.available

    def update(self):
        """Get the latest data from Wunderground."""
        self._api.update()


class WundergroundAPI(object):
    """Get the latest data and update the states."""

    def __init__(self, api_key, pws_id):
        """Initialize the data object."""
        from homeassistant.components.sensor.rest import RestData

        resource = "{}{}&apiKey={}".format(_ENDPOINT, pws_id, api_key)
        self._rest = RestData('GET', resource, None, None, None, False)
        self.data = None
        self.available = True
        self.update()

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Get the latest data from Wunderground."""
        try:
            self._rest.update()
            self.data = json.loads(self._rest.data)
            self.available = True
        except TypeError:
            _LOGGER.error("Unable to fetch data from Wunderground")
            self.available = False
