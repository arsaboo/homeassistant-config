#!/usr/bin/python3

"""Platform for light integration."""
import asyncio
import logging
# Import the device class from the component that you want to support
from datetime import timedelta
from typing import Any, Callable, List

import homeassistant.util.color as color_util
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP,
    ATTR_HS_COLOR,
    SUPPORT_BRIGHTNESS,
    SUPPORT_COLOR_TEMP,
    SUPPORT_COLOR,
    LightEntity
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.core import HomeAssistant, callback
from wyzeapy import Wyzeapy, BulbService
from wyzeapy.services.bulb_service import Bulb
from wyzeapy.types import DeviceTypes, PropertyIDs
from wyzeapy.utils import create_pid_pair

from .const import DOMAIN, CONF_CLIENT
from .token_manager import token_exception_handler

_LOGGER = logging.getLogger(__name__)
ATTRIBUTION = "Data provided by Wyze"
SCAN_INTERVAL = timedelta(seconds=30)


@token_exception_handler
async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry,
                            async_add_entities: Callable[[List[Any], bool], None]) -> None:
    """
    This function sets up the entities in the config entry

    :param hass: The Home Assistant instance
    :param config_entry: The config entry
    :param async_add_entities: A function that adds entities
    """

    _LOGGER.debug("""Creating new WyzeApi light component""")
    client: Wyzeapy = hass.data[DOMAIN][config_entry.entry_id][CONF_CLIENT]

    bulb_service = await client.bulb_service

    lights = [WyzeLight(bulb_service, light) for light in await bulb_service.get_bulbs()]

    async_add_entities(lights, True)


class WyzeLight(LightEntity):
    """
    Representation of a Wyze Bulb.
    """

    _just_updated = False

    def __init__(self, bulb_service: BulbService, bulb: Bulb):
        """Initialize a Wyze Bulb."""
        self._bulb = bulb
        self._device_type = DeviceTypes(self._bulb.product_type)
        if self._device_type not in [
            DeviceTypes.LIGHT,
            DeviceTypes.MESH_LIGHT,
            DeviceTypes.LIGHTSTRIP
        ]:
            raise AttributeError("Device type not supported")

        self._bulb_service = bulb_service

    def turn_on(self, **kwargs: Any) -> None:
        raise NotImplementedError

    def turn_off(self, **kwargs: Any) -> None:
        raise NotImplementedError

    @property
    def device_info(self):
        return {
            "identifiers": {
                (DOMAIN, self._bulb.mac)
            },
            "name": self.name,
            "manufacturer": "WyzeLabs",
            "model": self._bulb.product_model
        }

    @property
    def should_poll(self) -> bool:
        return False

    @token_exception_handler
    async def async_turn_on(self, **kwargs: Any) -> None:
        options = []
        if kwargs.get(ATTR_BRIGHTNESS) is not None:
            _LOGGER.debug("Setting brightness")
            brightness = round((kwargs.get(ATTR_BRIGHTNESS) / 255) * 100)

            options.append(create_pid_pair(PropertyIDs.BRIGHTNESS, str(brightness)))

            _LOGGER.debug("Setting brightness to %s" % brightness)
            _LOGGER.debug("Options: %s" % options)

            self._bulb.brightness = brightness
        if kwargs.get(ATTR_COLOR_TEMP) is not None:
            _LOGGER.debug("Setting color temp")
            color_temp = color_util.color_temperature_mired_to_kelvin(kwargs.get(ATTR_COLOR_TEMP))

            options.append(create_pid_pair(PropertyIDs.COLOR_TEMP, str(color_temp)))

            self._bulb.color_temp = color_temp
            self._bulb.color = color_util.color_rgb_to_hex(*color_util.color_temperature_to_rgb(color_temp))
        if (
            kwargs.get(ATTR_HS_COLOR) is not None
            and (
                self._device_type is DeviceTypes.MESH_LIGHT
                or self._device_type is DeviceTypes.LIGHTSTRIP
            )
        ):
            _LOGGER.debug("Setting color")
            color = color_util.color_rgb_to_hex(*color_util.color_hs_to_RGB(*kwargs.get(ATTR_HS_COLOR)))

            options.append(create_pid_pair(PropertyIDs.COLOR, str(color)))

            self._bulb.color = color

        _LOGGER.debug("Turning on light")
        loop = asyncio.get_event_loop()
        loop.create_task(self._bulb_service.turn_on(self._bulb, options))

        self._bulb.on = True
        self._just_updated = True
        self.async_schedule_update_ha_state()

    @token_exception_handler
    async def async_turn_off(self, **kwargs: Any) -> None:
        loop = asyncio.get_event_loop()
        loop.create_task(self._bulb_service.turn_off(self._bulb))

        self._bulb.on = False
        self._just_updated = True
        self.async_schedule_update_ha_state()

    @property
    def name(self):
        """Return the display name of this light."""
        return self._bulb.nickname

    @property
    def unique_id(self):
        return self._bulb.mac

    @property
    def available(self):
        """Return the connection status of this light"""
        return self._bulb.available

    @property
    def hs_color(self):
        return color_util.color_RGB_to_hs(*color_util.rgb_hex_to_rgb_list(self._bulb.color))

    @property
    def extra_state_attributes(self):
        """Return device attributes of the entity."""
        dev_info = {
            ATTR_ATTRIBUTION: ATTRIBUTION,
            "state": self.is_on,
            "available": self.available,
            "device model": self._bulb.product_model,
            "mac": self.unique_id
        }

        # noinspection DuplicatedCode
        if self._bulb.device_params.get("ip"):
            dev_info["IP"] = str(self._bulb.device_params.get("ip"))
        if self._bulb.device_params.get("rssi"):
            dev_info["RSSI"] = str(self._bulb.device_params.get("rssi"))
        if self._bulb.device_params.get("ssid"):
            dev_info["SSID"] = str(self._bulb.device_params.get("ssid"))

        return dev_info

    @property
    def brightness(self):
        """Return the brightness of the light.

        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """
        return round(self._bulb.brightness * 2.55, 1)

    @property
    def color_temp(self):
        """Return the CT color value in mired."""
        return color_util.color_temperature_kelvin_to_mired(self._bulb.color_temp)

    @property
    def max_mireds(self) -> int:
        if self._device_type is DeviceTypes.MESH_LIGHT:
            return color_util.color_temperature_kelvin_to_mired(1800) - 1
        return color_util.color_temperature_kelvin_to_mired(2700) - 1

    @property
    def min_mireds(self) -> int:
        return color_util.color_temperature_kelvin_to_mired(6500) + 1

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._bulb.on

    @property
    def supported_features(self):
        if (
            self._bulb.type is DeviceTypes.MESH_LIGHT
            or self._bulb.type is DeviceTypes.LIGHTSTRIP
        ):
            return SUPPORT_BRIGHTNESS | SUPPORT_COLOR_TEMP | SUPPORT_COLOR
        return SUPPORT_BRIGHTNESS | SUPPORT_COLOR_TEMP

    @token_exception_handler
    async def async_update(self):
        """
        This function updates the lock to be up to date with the Wyze Servers
        """

        if not self._just_updated:
            self._bulb = await self._bulb_service.update(self._bulb)
        else:
            self._just_updated = False

    @callback
    def async_update_callback(self, bulb: Bulb):
        """Update the bulb's state."""
        self._bulb = bulb
        self.async_schedule_update_ha_state()

    async def async_added_to_hass(self) -> None:
        """Subscribe to update events."""
        self._bulb.callback_function = self.async_update_callback
        self._bulb_service.register_updater(self._bulb, 30)
        await self._bulb_service.start_update_manager()
        return await super().async_added_to_hass()

    async def async_will_remove_from_hass(self) -> None:
        self._bulb_service.unregister_updater()
