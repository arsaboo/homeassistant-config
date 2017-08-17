"""
This component provides HA binary_sensor support for Abode Security System.

For more details about this platform, please refer to the documentation at

"""
import logging
from datetime import timedelta

import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from custom_components.abode import (CONF_ATTRIBUTION, DATA_ABODE)
#from homeassistant.components.abode import (CONF_ATTRIBUTION, DATA_ABODE)
from homeassistant.const import (ATTR_ATTRIBUTION, CONF_MONITORED_CONDITIONS)
from homeassistant.components.binary_sensor import (BinarySensorDevice)

DEPENDENCIES = ['abode']

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=60)

# Sensor types: Name, Friendly Name, device_class
SENSOR_TYPES = {
    'Door Contact': ['door_contact', 'Door Contact', 'opening'],
    'Motion Camera': ['motion_camera', 'Motion Camera', 'motion'],
}


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up a sensor for an Abode device."""
    abode = hass.data.get(DATA_ABODE)
    if not abode:
        _LOGGER.debug('No DATA_ABODE')
        return False

    sensors = []
    for sensor in abode.get_devices():
        _type = sensor.type
        _LOGGER.debug('Sensor type %s', _type)
        if _type in ['Door Contact', 'Motion Camera']:
            sensors.append(AbodeBinarySensor(hass, sensor,
                                             SENSOR_TYPES[_type][1]))
    add_devices(sensors, True)
    return True


class AbodeBinarySensor(BinarySensorDevice):
    """A binary sensor implementation for Abode device."""

    def __init__(self, hass, data, sensor_type):
        """Initialize a sensor for Abode device."""
        super(AbodeBinarySensor, self).__init__()
        self._sensor_type = sensor_type
        self._data = data
        self._name = "{0} {1}".format(SENSOR_TYPES.get(self._sensor_type)[1],
                                      self._data.name)
        self._device_class = SENSOR_TYPES.get(self._sensor_type)[2]
        self._state = None
        self.update()

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def is_on(self):
        """Return True if the binary sensor is on."""
        if self._sensor_type == 'Door Contact':
            return self._data.status != 'Closed'
        elif self._sensor_type == 'Motion Camera':
            return self._data._json_state.get('motion_event') == '1'

    @property
    def device_class(self):
        """Return the class of the binary sensor."""
        return self._device_class

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attrs = {}
        attrs[ATTR_ATTRIBUTION] = CONF_ATTRIBUTION
        attrs['device_id'] = self._data.device_id
        attrs['battery_low'] = self._data.battery_low

        return attrs

    def update(self):
        """Request an update from the Abode."""
        self._data.refresh()
        #_LOGGER.debug('%s is %s', self._name, self._data.status)
