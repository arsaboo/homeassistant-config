"""
Support for tracking the moon phases.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.moon/
"""
import calendar
import datetime
import json
import logging
import time
from datetime import timedelta

import homeassistant.helpers.config_validation as cv
import homeassistant.util.dt as dt_util
import pytz
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_NAME
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
from pytz import timezone

_LOGGER = logging.getLogger(__name__)
_ENDPOINT = 'https://weather.api.here.com/weather/1.0/report.json?product=forecast_astronomy&'

SCAN_INTERVAL = timedelta(minutes=5)
MIN_TIME_BETWEEN_UPDATES = timedelta(hours=6)
eastern = timezone('US/Eastern')

DEFAULT_NAME = 'Moon'
CONF_APP_ID = "app_id"
CONF_APP_CODE = "app_code"
CONF_ZIPCODE = 'zipcode'
ATTR_FORECAST = 'forecast'
ATTR_MOONRISE = 'moonrise'
ATTR_MOONSET = 'moonset'
ATTR_SUNRISE = "sunrise"
ATTR_SUNSET = "sunset"
ATTR_MOONPHASE = "moonPhase"
ATTR_MOONPHASE_DESC = "moonPhaseDesc"
ATTR_ICON_NAME = "iconName"
ATTR_FEED_CREATION = "feedCreation"
ATTR_LAST_UPDATED = 'last_updated'
ICON = 'mdi:brightness-3'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_APP_ID): cv.string,
    vol.Required(CONF_APP_CODE): cv.string,
    vol.Required(CONF_ZIPCODE): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})


def setup_platform(
        hass, config, add_devices, discovery_info=None):
    """Set up the Moon sensor."""
    app_id = config.get(CONF_APP_ID)
    app_code = config.get(CONF_APP_CODE)
    zipcode = config.get(CONF_ZIPCODE)
    name = config.get(CONF_NAME)
    moon_here = MoonPhaseHereAPI(app_id, app_code, zipcode)
    add_devices([MoonSensor(name, moon_here)], True)


class MoonSensor(Entity):
    """Representation of a Moon sensor."""

    def __init__(self, name, moon_here):
        """Initialize the sensor."""
        self._name = name
        self._state = None
        self._moon_here = moon_here

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        return self._moon_here.data['astronomy']['astronomy'][0][ATTR_MOONPHASE_DESC]

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return ICON

    @property
    def available(self):
        """Could the device be accessed during the last update call."""
        return self._moon_here.available

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        attributes = {
            ATTR_MOONRISE: self.format_time(self._moon_here.data['astronomy']['astronomy'][0][ATTR_MOONRISE]),
            ATTR_MOONSET: self.format_time(self._moon_here.data['astronomy']['astronomy'][0][ATTR_MOONSET]),
            ATTR_SUNRISE: self.format_time(self._moon_here.data['astronomy']['astronomy'][0][ATTR_SUNRISE]),
            ATTR_SUNSET: self.format_time(self._moon_here.data['astronomy']['astronomy'][0][ATTR_SUNSET]),
            ATTR_FEED_CREATION: datetime.datetime.strptime(self._moon_here.data[ATTR_FEED_CREATION], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.timezone('UTC')),
            ATTR_LAST_UPDATED: self._moon_here._last_updated,
            ATTR_FORECAST: self.hass.data['forecasts']
        }
        return attributes

    def format_time(self, strtime):
        try:
            unaware = datetime.datetime.strptime(strtime, "%I:%M%p")
            return eastern.localize(unaware)
        except ValueError:
            _LOGGER.debug("Invalid time encountered: %s", strtime)
            return "NA"

    def update(self):
        """Get the time and updates the states."""
        forecasts = self._moon_here.data['astronomy']['astronomy']
        self.hass.data['forecasts'] = []
        for forecast in forecasts:
            self.hass.data.get('forecasts').append({
                ATTR_MOONRISE: self.format_time(forecast.get(ATTR_MOONRISE)),
                ATTR_MOONSET: self.format_time(forecast.get(ATTR_MOONSET)),
                ATTR_SUNRISE: self.format_time(forecast.get(ATTR_SUNRISE)),
                ATTR_SUNSET: self.format_time(forecast.get(ATTR_SUNSET)),
                ATTR_MOONPHASE: forecast.get(ATTR_MOONPHASE),
                ATTR_MOONPHASE_DESC: forecast.get(ATTR_MOONPHASE_DESC),
                ATTR_ICON_NAME: forecast.get(ATTR_ICON_NAME),
            })
        self.hass.data['forecasts'].pop(0)
        self._moon_here.update()



class MoonPhaseHereAPI(object):
    """Get the latest data and update the states."""

    def __init__(self, app_id, app_code, zipcode):
        """Initialize the data object."""
        from homeassistant.components.sensor.rest import RestData

        resource = "{}app_id={}&app_code={}&zipcode={}".format(
            _ENDPOINT, app_id, app_code, zipcode)
        self._rest = RestData('GET', resource, None, None, None, False)
        self.data = None
        self.available = True
        self.update()

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Get the latest data from Here."""
        try:
            self._rest.update()
            self.data = json.loads(self._rest.data)
            self._last_updated = dt_util.now().isoformat()
            _LOGGER.debug("Moon sensor updated")
            self.available = True
        except TypeError:
            _LOGGER.debug("Unable to fetch data from Here")
            self.available = False
