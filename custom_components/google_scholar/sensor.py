"""
@ Author      : Alok Saboo
@ Description : Obtain citations from Google Scholar
"""

import logging
from datetime import date, datetime, timedelta

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import ATTR_ATTRIBUTION, CONF_NAME
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

ATTRIBUTION = "Data provided by Google.com"
DEFAULT_ICON = 'mdi:school'

SCAN_INTERVAL = timedelta(hours=24)
MIN_TIME_BETWEEN_UPDATES = timedelta(hours=24)

CONF_AUTHOR = 'author'
DEFAULT_NAME = 'Google Scholar'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_AUTHOR): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Google Scholar sensor."""
    author = config.get(CONF_AUTHOR)
    if not author:
        msg = "Warning: No author configured."
        hass.components.persistent_notification.create(msg, "Sensor google_scholar")
        _LOGGER.warning(msg)
        return
    rest = GoogleScholarData(author)
    name = config.get(CONF_NAME)
    add_devices([GoogleScholarSensor(name, rest)], True)


class GoogleScholarSensor(Entity):
    """Implementing the Google Scholar sensor."""

    def __init__(self, name, rest):
        """Initialize the sensor."""
        self._icon = DEFAULT_ICON
        self.rest = rest
        self._state = None
        self._name = name

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name.rstrip()

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        icon = DEFAULT_ICON
        return icon

    @property
    def state(self):
        """Return the state of the sensor."""
        try:
            self._state = float(self.rest.data['Citations'])
        except (KeyError, TypeError):
            self._state = None
        return self._state

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        attr = {}
        attr['Author'] = self.rest.data['Author']
        attr['h-index'] = self.rest.data['hindex']
        attr[ATTR_ATTRIBUTION] = ATTRIBUTION
        return attr

    @property
    def available(self):
        """Could the device be accessed during the last update call."""
        return self.rest.available

    def update(self):
        """Update current date."""
        self.rest.update()

class GoogleScholarData(object):
    """Get data from yahoo.com."""

    def __init__(self, author):
        """Initialize the data object."""
        self._author = author
        self.data = None
        self.available = True

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Get the latest data from Google Scholar."""
        import scholarly
        try:
            results_json = {}
            results_json['Author'] = self._author
            author = self._author
            # Retrieve the author's data, fill-in, and print
            search_query = scholarly.search_author(author)
            author = next(search_query).fill()
            results_json['Citations'] = author.citedby
            results_json['hindex'] = author.hindex
            self.data = results_json
            self.available = True
        except requests.exceptions.ConnectionError:
            _LOGGER.error("Connection error")
            self.data = None
            self.available = False
