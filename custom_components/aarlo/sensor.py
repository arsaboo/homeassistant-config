"""
This component provides HA sensor for Netgear Arlo IP cameras.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.arlo/
"""
import logging

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.const import (ATTR_ATTRIBUTION,
                                 CONF_MONITORED_CONDITIONS,
                                 DEVICE_CLASS_HUMIDITY,
                                 DEVICE_CLASS_TEMPERATURE,
                                 TEMP_CELSIUS)
from homeassistant.core import callback
from homeassistant.helpers.config_validation import (PLATFORM_SCHEMA)
from homeassistant.helpers.entity import (Entity)
from homeassistant.helpers.icon import icon_for_battery_level
from . import COMPONENT_ATTRIBUTION, COMPONENT_DATA, COMPONENT_BRAND, COMPONENT_DOMAIN
from .pyaarlo.constant import (AIR_QUALITY_KEY,
                               BATTERY_KEY,
                               CAPTURED_TODAY_KEY,
                               HUMIDITY_KEY,
                               LAST_CAPTURE_KEY,
                               RECENT_ACTIVITY_KEY,
                               SIGNAL_STR_KEY,
                               TEMPERATURE_KEY,
                               TOTAL_CAMERAS_KEY)

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = [COMPONENT_DOMAIN]

# sensor_type [ description, unit, icon, attribute ]
SENSOR_TYPES = {
    'last_capture': ['Last', None, 'run-fast', LAST_CAPTURE_KEY],
    'total_cameras': ['Arlo Cameras', None, 'video', TOTAL_CAMERAS_KEY],
    'recent_activity': ['Recent Activity', None, 'run-fast', RECENT_ACTIVITY_KEY],
    'captured_today': ['Captured Today', None, 'file-video', CAPTURED_TODAY_KEY],
    'battery_level': ['Battery Level', '%', 'battery-50', BATTERY_KEY],
    'signal_strength': ['Signal Strength', None, 'signal', SIGNAL_STR_KEY],
    'temperature': ['Temperature', TEMP_CELSIUS, 'thermometer', TEMPERATURE_KEY],
    'humidity': ['Humidity', '%', 'water-percent', HUMIDITY_KEY],
    'air_quality': ['Air Quality', 'ppm', 'biohazard', AIR_QUALITY_KEY]
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_MONITORED_CONDITIONS, default=list(SENSOR_TYPES)):
        vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
})


async def async_setup_platform(hass, config, async_add_entities, _discovery_info=None):
    """Set up an Arlo IP sensor."""
    arlo = hass.data.get(COMPONENT_DATA)
    if not arlo:
        return

    sensors = []
    for sensor_type in config.get(CONF_MONITORED_CONDITIONS):
        if sensor_type == 'total_cameras':
            sensors.append(ArloSensor(SENSOR_TYPES[sensor_type][0], arlo, sensor_type))
        else:
            for camera in arlo.cameras:
                if camera.has_capability(SENSOR_TYPES[sensor_type][3]):
                    name = '{0} {1}'.format(SENSOR_TYPES[sensor_type][0], camera.name)
                    sensors.append(ArloSensor(name, camera, sensor_type))
            for doorbell in arlo.doorbells:
                if doorbell.has_capability(SENSOR_TYPES[sensor_type][3]):
                    name = '{0} {1}'.format(SENSOR_TYPES[sensor_type][0], doorbell.name)
                    sensors.append(ArloSensor(name, doorbell, sensor_type))
            for light in arlo.lights:
                if light.has_capability(SENSOR_TYPES[sensor_type][3]):
                    name = '{0} {1}'.format(SENSOR_TYPES[sensor_type][0], light.name)
                    sensors.append(ArloSensor(name, light, sensor_type))

    async_add_entities(sensors, True)


class ArloSensor(Entity):
    """An implementation of a Netgear Arlo IP sensor."""

    def __init__(self, name, device, sensor_type):
        """Initialize an Arlo sensor."""
        self._name = name
        self._unique_id = self._name.lower().replace(' ', '_')
        self._device = device
        self._sensor_type = sensor_type
        self._icon = 'mdi:{}'.format(SENSOR_TYPES.get(self._sensor_type)[2])
        self._state = None
        self._attr = SENSOR_TYPES.get(self._sensor_type)[3]
        _LOGGER.info('ArloSensor: %s created', self._name)

    async def async_added_to_hass(self):
        """Register callbacks."""

        @callback
        def update_state(_device, attr, value):
            _LOGGER.debug('callback:' + self._name + ':' + attr + ':' + str(value)[:80])
            self._state = value
            self.async_schedule_update_ha_state()

        if self._attr is not None:
            self._state = self._device.attribute(self._attr)
            self._device.add_attr_callback(self._attr, update_state)

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        if self._sensor_type == 'battery_level' and self._state is not None:
            return icon_for_battery_level(battery_level=int(self._state), charging=False)
        return self._icon

    @property
    def unit_of_measurement(self):
        """Return the units of measurement."""
        return SENSOR_TYPES.get(self._sensor_type)[1]

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        if self._sensor_type == 'temperature':
            return DEVICE_CLASS_TEMPERATURE
        if self._sensor_type == 'humidity':
            return DEVICE_CLASS_HUMIDITY
        return None

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        attrs = {}

        attrs[ATTR_ATTRIBUTION] = COMPONENT_ATTRIBUTION
        attrs['brand'] = COMPONENT_BRAND
        attrs['friendly_name'] = self._name

        if self._sensor_type != 'total_cameras':
            attrs['camera_name'] = self._device.name
            attrs['model'] = self._device.model_id
        if self._sensor_type == 'last_capture':
            video = self._device.last_video
            if video is not None:
                attrs['object_type'] = video.object_type
                attrs['object_region'] = video.object_region
                attrs['thumbnail_url'] = video.thumbnail_url
            else:
                attrs['object_type'] = None

        return attrs
