#!/usr/bin/python3

"""Platform for sensor integration."""

import logging
from typing import Any, Callable, List

from wyzeapy import Wyzeapy
from wyzeapy.services.camera_service import Camera
from wyzeapy.services.lock_service import Lock

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION, DEVICE_CLASS_BATTERY, PERCENTAGE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import CONF_CLIENT, DOMAIN, LOCK_UPDATED, CAMERA_UPDATED
from .token_manager import token_exception_handler

_LOGGER = logging.getLogger(__name__)
ATTRIBUTION = "Data provided by Wyze"
CAMERAS_WITH_BATTERIES = ["WVOD1"]


@token_exception_handler
async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry,
                            async_add_entities: Callable[[List[Any], bool], None]) -> None:
    """
    This function sets up the config_entry

    :param hass: Home Assistant instance
    :param config_entry: The current config_entry
    :param async_add_entities: This function adds entities to the config_entry
    :return:
    """
    _LOGGER.debug("""Creating new WyzeApi sensor component""")
    client: Wyzeapy = hass.data[DOMAIN][config_entry.entry_id][CONF_CLIENT]

    # Get the list of locks so that we can create lock and keypad battery sensors
    lock_service = await client.lock_service
    camera_service = await client.camera_service

    locks = await lock_service.get_locks()
    sensors = []
    for lock in locks:
        sensors.append(WyzeLockBatterySensor(lock, WyzeLockBatterySensor.LOCK_BATTERY))
        sensors.append(WyzeLockBatterySensor(lock, WyzeLockBatterySensor.KEYPAD_BATTERY))

    cameras = await camera_service.get_cameras()
    for camera in cameras:
        if camera.product_model in CAMERAS_WITH_BATTERIES:
            sensors.append(WyzeCameraBatterySensor(camera))

    async_add_entities(sensors, True)


class WyzeLockBatterySensor(SensorEntity):
    """Representation of a Wyze Lock or Lock Keypad Battery"""

    @property
    def enabled(self):
        return self._enabled

    LOCK_BATTERY = "lock_battery"
    KEYPAD_BATTERY = "keypad_battery"

    _attr_device_class = DEVICE_CLASS_BATTERY
    _attr_native_unit_of_measurement = PERCENTAGE

    # make the battery unavailable by default, this will be toggled after the first upate from the battery entity that
    # has battery data.
    _available = False

    def __init__(self, lock, battery_type):
        self._enabled = None
        self._lock = lock
        self._battery_type = battery_type

    @callback
    def handle_lock_update(self, lock: Lock) -> None:
        self._lock = lock
        if self._lock.raw_dict.get("power") and self._battery_type == self.LOCK_BATTERY:
            self._available = True
        if self._lock.raw_dict.get("keypad", {}).get("power") and self._battery_type == self.KEYPAD_BATTERY:
            if self.enabled is False | self.enabled is None:
                self.enabled = True
            self._available = True
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                f"{LOCK_UPDATED}-{self._lock.mac}",
                self.handle_lock_update,
            )
        )

    @property
    def name(self) -> str:
        battery_type = self._battery_type.replace("_", " ").title()
        return f"{self._lock.nickname} {battery_type}"

    @property
    def unique_id(self):
        return f"{self._lock.nickname}.{self._battery_type}"

    @property
    def available(self) -> bool:
        return self._available

    @property
    def should_poll(self) -> bool:
        return False

    @property
    def entity_registry_enabled_default(self) -> bool:
        if self._battery_type == self.KEYPAD_BATTERY:
            # The keypad battery may not be available if the lock has no keypad
            return False
        # The battery voltage will always be available for the lock
        return True

    @property
    def device_info(self):
        return {
            "identifiers": {
                (DOMAIN, self._lock.mac)
            },
            "name": f"{self._lock.nickname}.{self._battery_type}",
            "type": f"lock.{self._battery_type}"
        }

    @property
    def extra_state_attributes(self):
        """Return device attributes of the entity."""
        return {
            ATTR_ATTRIBUTION: ATTRIBUTION,
            "available": self.available,
            "device model": f"{self._lock.product_model}.{self._battery_type}",
        }

    @property
    def native_value(self):
        """Return the state of the device."""
        if self._battery_type == self.LOCK_BATTERY:
            return str(self._lock.raw_dict.get("power"))
        elif self._battery_type == self.KEYPAD_BATTERY:
            return str(self._lock.raw_dict.get("keypad", {}).get("power"))
        return 0

    @enabled.setter
    def enabled(self, value):
        self._enabled = value


class WyzeCameraBatterySensor(SensorEntity):
    """Representation of a Wyze Camera Battery"""
    _attr_device_class = DEVICE_CLASS_BATTERY
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, camera):
        self._camera = camera

    @callback
    def handle_camera_update(self, camera: Camera) -> None:
        self._camera = camera
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                f"{CAMERA_UPDATED}-{self._camera.mac}",
                self.handle_camera_update,
            )
        )

    @property
    def name(self) -> str:
        return f"{self._camera.nickname} Battery"

    @property
    def unique_id(self):
        return f"{self._camera.nickname}.battery"

    @property
    def should_poll(self) -> bool:
        return False

    @property
    def device_info(self):
        return {
            "identifiers": {
                (DOMAIN, self._camera.mac)
            },
            "name": f"{self._camera.nickname}.battery",
            "type": "camera.battery"
        }

    @property
    def extra_state_attributes(self):
        """Return device attributes of the entity."""
        return {
            ATTR_ATTRIBUTION: ATTRIBUTION,
            "available": self.available,
            "device model": f"{self._camera.product_model}.battery",
        }

    @property
    def native_value(self):
        return self._camera.device_params.get("electricity")
