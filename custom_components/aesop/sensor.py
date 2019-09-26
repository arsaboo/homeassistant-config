"""Sensor for Aesop packages."""
from collections import defaultdict
import logging

from homeassistant.const import ATTR_ATTRIBUTION, ATTR_DATE
from homeassistant.helpers.entity import Entity
from homeassistant.util import slugify
from homeassistant.util.dt import now

from . import DATA_AESOP
REQUIREMENTS = ['requests_cache']

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Aesop platform."""
    if discovery_info is None:
        return

    aesop = hass.data[DATA_AESOP]
    add_entities([AesopCurrJobs(aesop), AesopAvailJobs(aesop)], True)


class AesopAvailJobs(Entity):
    """Aesop Available Jobs Sensor."""

    def __init__(self, aesop):
        """Initialize the sensor."""
        self._aesop = aesop
        self._name = self._aesop.name
        self._attributes = None
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._name} packages"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    def update(self):
        """Update device state."""
        self._aesop.update()
        status_counts = defaultdict(int)
        for package in self._aesop.availJobs:
            status = 1
        self._attributes = {ATTR_ATTRIBUTION: self._aesop.attribution,'availjobs': self._aesop.availJobs}
        self._attributes.update(status_counts)
        self._state = status

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return "mdi:package-variant-closed"

class AesopCurrJobs(Entity):
    """Aesop Current Jobs Sensor."""

    def __init__(self, aesop):
        """Initialize the sensor."""
        self._aesop = aesop
        self._name = self._aesop.name
        self._attributes = None
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._name} packages"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    def update(self):
        """Update device state."""
        self._aesop.update()
        status_counts = defaultdict(int)
        for package in self._aesop.curJobs:
            status = 1
        self._attributes = {ATTR_ATTRIBUTION: self._aesop.attribution,'curJobs': self._aesop.curJobs}
        self._attributes.update(status_counts)
        self._state = status

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return "mdi:package-variant-closed"
