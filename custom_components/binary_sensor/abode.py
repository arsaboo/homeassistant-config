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

# Sensor types: Name, device_class
SENSOR_TYPES = {
    'Door Contact': 'opening',
    'Motion Camera': 'motion',
}


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up a sensor for an Abode device."""
    data = hass.data.get(DATA_ABODE)
    if not data:
        _LOGGER.debug('No DATA_ABODE')
        return False

    sensors = []
    for sensor in data.devices:
        _LOGGER.debug('Sensor type %s', sensor.type)
        if sensor.type in [ SENSOR_TYPES.keys() ]:
            sensors.append(AbodeBinarySensor(hass, data, sensor))

    _LOGGER.debug('Adding %d sensors', len(sensors))
    add_devices(sensors)
    return True


class AbodeBinarySensor(BinarySensorDevice):
    """A binary sensor implementation for Abode device."""

    def __init__(self, hass, data, device):
        """Initialize a sensor for Abode device."""
        super(AbodeBinarySensor, self).__init__()
        self._device = device

        data.events.register(device, self.refresh)

    @property
    def should_poll(self):
        """Return the polling state."""
        return False

    @property
    def name(self):
        """Return the name of the sensor."""
        return "{0} {1}".format(self._device.type, self._device.name)

    @property
    def is_on(self):
        """Return True if the binary sensor is on."""
        if self._device.type == 'Door Contact':
            return self._device.status != 'Closed'
        elif self._device.type == 'Motion Camera':
            return self._device._json_state.get('motion_event') == '1'

    @property
    def device_class(self):
        """Return the class of the binary sensor."""
        return SENSOR_TYPES.get(self._device.type)

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attrs = {}
        attrs[ATTR_ATTRIBUTION] = CONF_ATTRIBUTION
        attrs['device_id'] = self._device.device_id
        attrs['battery_low'] = self._device.battery_low

        return attrs

    def refresh(self):
        """Refresh HA state when the device has changed."""
        _LOGGER.debug("Abode refresh")
        self.schedule_update_ha_state()
