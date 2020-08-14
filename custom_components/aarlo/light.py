"""
This component provides A light for Netgear Arlo IP cameras.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.arlo/
"""

import logging
import pprint

from homeassistant.components.light import (ATTR_BRIGHTNESS,
                                            ATTR_COLOR_TEMP,
                                            ATTR_EFFECT,
                                            ATTR_HS_COLOR,
                                            SUPPORT_BRIGHTNESS,
                                            SUPPORT_COLOR,
                                            SUPPORT_COLOR_TEMP,
                                            SUPPORT_EFFECT,
                                            LightEntity)
from homeassistant.const import (ATTR_ATTRIBUTION,
                                 ATTR_BATTERY_CHARGING,
                                 ATTR_BATTERY_LEVEL)
from homeassistant.core import callback
import homeassistant.util.color as color_util
from . import COMPONENT_ATTRIBUTION, COMPONENT_DATA, COMPONENT_BRAND
from .pyaarlo.constant import (
    BRIGHTNESS_KEY,
    FLOODLIGHT_KEY,
    LAMP_STATE_KEY,
    LIGHT_BRIGHTNESS_KEY,
    LIGHT_MODE_KEY,
    NIGHTLIGHT_KEY,
    SPOTLIGHT_KEY,
    SPOTLIGHT_BRIGHTNESS_KEY)

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['aarlo']

ATTR_BATTERY_TECH = 'battery_tech'
ATTR_CHARGER_TYPE = 'charger_type'

LIGHT_EFFECT_RAINBOW = "rainbow"
LIGHT_EFFECT_NONE = "none"


async def async_setup_platform(hass, _config, async_add_entities, _discovery_info=None):
    """Set up an Arlo IP light."""
    arlo = hass.data.get(COMPONENT_DATA)
    if not arlo:
        return

    lights = []
    for light in arlo.lights:
        lights.append(ArloLight(light))
    for camera in arlo.cameras:
        if camera.has_capability(NIGHTLIGHT_KEY):
            lights.append(ArloNightLight(camera))
        if camera.has_capability(FLOODLIGHT_KEY):
            lights.append(ArloFloodLight(camera))
        if camera.has_capability(SPOTLIGHT_KEY):
            lights.append(ArloSpotlight(camera))

    async_add_entities(lights, True)


class ArloLight(LightEntity):

    def __init__(self, light):
        """Initialize an Arlo light."""
        self._name = light.name
        self._unique_id = light.entity_id
        self._state = "off"
        self._brightness = None
        self._light = light
        _LOGGER.info('ArloLight: %s created', self._name)

    async def async_added_to_hass(self):
        """Register callbacks."""

        @callback
        def update_state(_light, attr, value):
            _LOGGER.debug('callback:' + self._name + ':' + attr + ':' + str(value)[:80])
            if attr == LAMP_STATE_KEY:
                self._state = value
            if attr == BRIGHTNESS_KEY:
                self._brightness = value
            self.async_schedule_update_ha_state()

        _LOGGER.info('ArloLight: %s registering callbacks', self._name)
        self._state = self._light.attribute(LAMP_STATE_KEY, default="off")
        self._brightness = self._light.attribute(BRIGHTNESS_KEY, default=255)

        self._light.add_attr_callback(LAMP_STATE_KEY, update_state)
        self._light.add_attr_callback(BRIGHTNESS_KEY, update_state)

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def is_on(self) -> bool:
        """Return True if light is on."""
        return self._state.lower() == "on"

    @property
    def supported_features(self):
        """Flag features that are supported."""
        # return SUPPORT_BRIGHTNESS | SUPPORT_COLOR
        return SUPPORT_BRIGHTNESS

    def turn_on(self, **kwargs):
        """Turn the light on."""
        _LOGGER.info("turn_on: {}".format(pprint.pformat(kwargs)))

        rgb = kwargs.get(ATTR_HS_COLOR, None)
        if rgb is not None:
            rgb = color_util.color_hs_to_RGB(*rgb)
        brightness = kwargs.get(ATTR_BRIGHTNESS, None)

        self._light.turn_on(brightness=brightness, rgb=rgb)
        self._state = "on"

    def turn_off(self, **kwargs):
        """Turn the light off."""
        _LOGGER.info("turn_off: {}".format(pprint.pformat(kwargs)))
        self._light.turn_off()
        self._state = "off"

    @property
    def brightness(self):
        """Return the brightness of the light."""
        return self._brightness

    @property
    def device_state_attributes(self):
        """Return the state attributes."""

        attrs = {
            name: value for name, value in (
                (ATTR_BATTERY_LEVEL, self._light.battery_level),
                (ATTR_BATTERY_TECH, self._light.battery_tech),
                (ATTR_BATTERY_CHARGING, self._light.charging),
                (ATTR_CHARGER_TYPE, self._light.charger_type),
                (BRIGHTNESS_KEY, self._brightness),
            ) if value is not None
        }

        attrs[ATTR_ATTRIBUTION] = COMPONENT_ATTRIBUTION
        attrs['brand'] = COMPONENT_BRAND
        attrs['friendly_name'] = self._name

        return attrs


class ArloNightLight(ArloLight):

    def __init__(self, camera):
        self._brightness = None
        self._color_temp = None
        self._effect = None
        self._hs_color = None

        super().__init__(camera)

        _LOGGER.info('ArloNightLight: %s created', self._name)

    def _set_light_mode(self, light_mode):
        _LOGGER.info('ArloNightLight: {} light mode {}'.format(self._name, light_mode))
        if light_mode is None:
            return

        # {'mode': 'rgb', 'rgb': {'red': 118, 'green': 255, 'blue': 91}}
        # {'mode': 'temperature', 'temperature': 2650}
        # {'mode': 'rainbow'}
        mode = light_mode.get('mode')
        if mode is None:
            return

        if mode == 'rgb':
            rgb = light_mode.get('rgb')
            self._hs_color = color_util.color_RGB_to_hs(rgb.get("red"), rgb.get("green"), rgb.get("blue"))
            self._effect = LIGHT_EFFECT_NONE
        elif mode == 'temperature':
            temperature = light_mode.get('temperature')
            self._color_temp = color_util.color_temperature_kelvin_to_mired(temperature)
            self._hs_color = color_util.color_temperature_to_hs(temperature)
            self._effect = LIGHT_EFFECT_NONE
        elif mode == LIGHT_EFFECT_RAINBOW:
            self._effect = LIGHT_EFFECT_RAINBOW

    async def async_added_to_hass(self):
        """Register callbacks."""

        @callback
        def update_attr(_light, attr, value):
            _LOGGER.debug('callback:' + self._name + ':' + attr + ':' + str(value)[:80])
            if attr == LIGHT_BRIGHTNESS_KEY:
                self._brightness = value
            if attr == LIGHT_MODE_KEY:
                self._set_light_mode(value)
            self.async_schedule_update_ha_state()

        _LOGGER.info('ArloNightLight: %s registering callbacks', self._name)

        self._brightness = self._light.attribute(LIGHT_BRIGHTNESS_KEY, default=255)
        self._set_light_mode(self._light.attribute(LIGHT_MODE_KEY))

        self._light.add_attr_callback(LIGHT_BRIGHTNESS_KEY, update_attr)
        self._light.add_attr_callback(LIGHT_MODE_KEY, update_attr)
        await super().async_added_to_hass()

    def turn_on(self, **kwargs):
        """Turn the entity on."""
        _LOGGER.debug("turn_on: {} {} {}".format(self._name, self._state, kwargs))

        self._light.nightlight_on()
        if ATTR_BRIGHTNESS in kwargs:
            self._light.set_nightlight_brightness(kwargs[ATTR_BRIGHTNESS])

        if ATTR_HS_COLOR in kwargs:
            rgb = color_util.color_hs_to_RGB(*kwargs[ATTR_HS_COLOR])
            self._light.set_nightlight_rgb(red=rgb[0], green=rgb[1], blue=rgb[2])

        if ATTR_COLOR_TEMP in kwargs:
            kelvin = color_util.color_temperature_mired_to_kelvin(kwargs.get(ATTR_COLOR_TEMP))
            self._light.set_nightlight_color_temperature(kelvin)

        if ATTR_EFFECT in kwargs:
            effect = kwargs[ATTR_EFFECT]
            if effect == LIGHT_EFFECT_RAINBOW:
                self._light.set_nightlight_mode("rainbow")
            else:
                self._light.set_nightlight_mode("rgb")

    def turn_off(self, **kwargs):
        """Turn the entity off."""
        self._light.nightlight_off()

    @property
    def brightness(self):
        """Return the brightness of the light."""
        return self._brightness

    @property
    def color_temp(self):
        """Return the color temperature of this light in mireds for HA."""
        return self._color_temp

    @property
    def effect_list(self) -> list:
        """Return the list of supported effects."""
        return [LIGHT_EFFECT_NONE, LIGHT_EFFECT_RAINBOW]

    @property
    def effect(self) -> str:
        """Return the current effect."""
        return self._effect

    @property
    def hs_color(self) -> tuple:
        """Return the hs color value."""
        return self._hs_color

    @property
    def min_mireds(self):
        """Return minimum supported color temperature."""
        return color_util.color_temperature_kelvin_to_mired(9000)

    @property
    def max_mireds(self):
        """Return maximum supported color temperature."""
        return color_util.color_temperature_kelvin_to_mired(2500)

    @property
    def supported_features(self):
        """Flag features that are supported."""
        return SUPPORT_BRIGHTNESS | SUPPORT_COLOR | SUPPORT_COLOR_TEMP | SUPPORT_EFFECT


class ArloFloodLight(ArloLight):
    def __init__(self, camera):
        self._brightness = None
        self._mode = None

        self._duration = None
        self._als_sensitivity = None

        self._sleep_time = None
        self._sleep_time_rel = None

        super().__init__(camera)

        _LOGGER.info("ArloFloodLight: %s created", self._name)

    async def async_added_to_hass(self):
        """Register callbacks."""

        def set_states(state):
            if "on" in state:
                self._state = "on" if state.get("on") else "off"
            if "brightness1" in state:
                self._brightness = int(state.get("brightness1") / 100.0 * 255)
            if "behavior" in state:
                self._mode = state.get("behavior")
            if "alsSensitivity" in state:
                self._als_sensitivity = state.get("alsSensitivity")
            if "duration" in state:
                self._duration = state.get("duration")
            if self._state == 'on':
                if "sleepTime" in state:
                    self._sleep_time = state.get("sleepTime")
                if "sleepTimeRel" in state:
                    self._sleep_time_rel = state.get("sleepTimeRel")
            elif self._state == 'off':
                self._sleep_time = None
                self._sleep_time_rel = None

        @callback
        def update_attr(_light, attr, value):
            _LOGGER.debug("callback:" + self._name + ":" + attr + ":" + str(value)[:80])
            set_states(value)
            self.async_schedule_update_ha_state()

        _LOGGER.info("ArloFloodLight: %s registering callbacks", self._name)
        floodlight = self._light.attribute(FLOODLIGHT_KEY, default={})
        set_states(floodlight)

        self._light.add_attr_callback(FLOODLIGHT_KEY, update_attr)

    def turn_on(self, **kwargs):
        """Turn the entity on."""
        _LOGGER.debug("turn_on: {} {} {}".format(self._name, self._state, kwargs))

        self._light.floodlight_on()
        if ATTR_BRIGHTNESS in kwargs:
            self._light.set_floodlight_brightness(kwargs[ATTR_BRIGHTNESS])

    def turn_off(self, **kwargs):
        """Turn the entity off."""
        self._light.floodlight_off()

    @property
    def brightness(self):
        """Return the brightness of the light."""
        return self._brightness

    @property
    def supported_features(self):
        """Flag features that are supported."""
        return SUPPORT_BRIGHTNESS

    @property
    def device_state_attributes(self):
        """Return the state attributes."""

        super_attrs = super().device_state_attributes
        flood_attrs = {
            name: value
            for name, value in (
                ("duration", self._duration),
                ("sleep_time_rel", self._sleep_time_rel),
                ("sleep_time", self._sleep_time),
                ("mode", self._mode),
                ("als_sensitivity", self._als_sensitivity),
            )
            if value is not None
        }
        attrs = dict()
        attrs.update(super_attrs)
        attrs.update(flood_attrs)

        return attrs


class ArloSpotlight(ArloLight):

    def __init__(self, camera):
        self._brightness = None
        self._effect = None

        super().__init__(camera)

        _LOGGER.info('ArloSpotlight: %s created', self._name)

    async def async_added_to_hass(self):
        """Register callbacks."""

        @callback
        def update_attr(_light, attr, value):
            _LOGGER.debug('callback:' + self._name + ':' + attr + ':' + str(value)[:80])
            if attr == SPOTLIGHT_KEY:
                self._state = value
            if attr == SPOTLIGHT_BRIGHTNESS_KEY:
                self._brightness = value / 100 * 255
            self.async_schedule_update_ha_state()

        _LOGGER.info('ArloSpotlight: %s registering callbacks', self._name)

        self._state = self._light.attribute(SPOTLIGHT_KEY, default="off")
        self._brightness = self._light.attribute(SPOTLIGHT_BRIGHTNESS_KEY, default=255)

        self._light.add_attr_callback(SPOTLIGHT_KEY, update_attr)
        self._light.add_attr_callback(SPOTLIGHT_BRIGHTNESS_KEY, update_attr)
        await super().async_added_to_hass()

    def turn_on(self, **kwargs):
        """Turn the entity on."""
        _LOGGER.debug("turn_on: {} {} {}".format(self._name, self._state, kwargs))

        self._light.set_spotlight_on()
        if ATTR_BRIGHTNESS in kwargs:
            self._light.set_spotlight_brightness(kwargs[ATTR_BRIGHTNESS])

    def turn_off(self, **kwargs):
        """Turn the entity off."""
        self._light.set_spotlight_off()

    @property
    def brightness(self):
        """Return the brightness of the light."""
        return self._brightness

    @property
    def supported_features(self):
        """Flag features that are supported."""
        return SUPPORT_BRIGHTNESS
