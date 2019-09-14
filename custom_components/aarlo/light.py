"""
This component provides A light for Netgear Arlo IP cameras.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.arlo/
"""

import logging

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import (Light)
from homeassistant.const import (ATTR_ATTRIBUTION)
from homeassistant.core import callback

from . import CONF_ATTRIBUTION, DATA_ARLO, DEFAULT_BRAND

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['aarlo']


async def async_setup_platform(hass, config, async_add_entities, _discovery_info=None):
    """Set up an Arlo IP light."""
    arlo = hass.data.get(DATA_ARLO)
    if not arlo:
        return

    lights = []
    for light in arlo.lights:
        lights.append(ArloLight(light))

    async_add_entities(lights, True)


class ArloLight(Light):

    def __init__(self, light):
        """Initialize an Arlo light."""
        self._name = light.name
        self._unique_id = self._name.lower().replace(' ', '_')
        self._state = "off"
        self._light = light
        _LOGGER.info('ArloLight: %s created', self._name)

    async def async_added_to_hass(self):
        """Register callbacks."""

        @callback
        def update_state(_light, attr, value):
            _LOGGER.debug('callback:' + attr + ':' + str(value)[:80])
            self._state = value
            self.async_schedule_update_ha_state()

        self._state = self._light.attribute("lampState",default="off")
        self._light.add_attr_callback("lampState", update_state)

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def is_on(self) -> bool:
        """Return True if entity is on."""
        _LOGGER.debug("is_on:{}".format(self._state))
        return self._state.lower() == "on"

    def turn_on(self, **kwargs):
        """Turn the entity on."""
        _LOGGER.debug("turn_on:{}".format(self._state))
        self._light.turn_on()

    def turn_off(self, **kwargs):
        """Turn the entity off."""
        _LOGGER.debug("turn_off:{}".format(self._state))
        self._light.turn_off()

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attrs = {}

        attrs[ATTR_ATTRIBUTION] = CONF_ATTRIBUTION
        attrs['brand'] = DEFAULT_BRAND
        attrs['friendly_name'] = self._name

        return attrs
