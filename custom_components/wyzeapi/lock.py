#!/usr/bin/python3

"""Platform for light integration."""
from abc import ABC
from datetime import timedelta
import logging
from typing import Any, Callable, List

from wyzeapy import LockService, Wyzeapy
from wyzeapy.services.lock_service import Lock
from wyzeapy.types import DeviceTypes

import homeassistant.components.lock
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import CONF_CLIENT, DOMAIN, LOCK_UPDATED
from .token_manager import token_exception_handler

_LOGGER = logging.getLogger(__name__)
ATTRIBUTION = "Data provided by Wyze"
SCAN_INTERVAL = timedelta(seconds=10)
MAX_OUT_OF_SYNC_COUNT = 5


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

    _LOGGER.debug("""Creating new WyzeApi lock component""")
    client: Wyzeapy = hass.data[DOMAIN][config_entry.entry_id][CONF_CLIENT]
    lock_service = await client.lock_service

    locks = [WyzeLock(lock_service, lock) for lock in await lock_service.get_locks()]

    async_add_entities(locks, True)


class WyzeLock(homeassistant.components.lock.LockEntity, ABC):
    """Representation of a Wyze Lock."""

    def __init__(self, lock_service: LockService, lock: Lock):
        """Initialize a Wyze lock."""
        self._lock = lock
        if self._lock.type not in [
            DeviceTypes.LOCK
        ]:
            raise AttributeError("Device type not supported")

        self._lock_service = lock_service

        self._out_of_sync_count = 0

    @property
    def device_info(self):
        return {
            "identifiers": {
                (DOMAIN, self._lock.mac)
            },
            "name": self.name,
            "manufacturer": "WyzeLabs",
            "model": self._lock.product_model
        }

    def lock(self, **kwargs):
        raise NotImplementedError

    def unlock(self, **kwargs):
        raise NotImplementedError

    @property
    def should_poll(self) -> bool:
        return False

    @token_exception_handler
    async def async_lock(self, **kwargs):
        _LOGGER.debug("Turning on lock")
        await self._lock_service.lock(self._lock)

        self._lock.unlocked = False
        self.async_schedule_update_ha_state()

    @token_exception_handler
    async def async_unlock(self, **kwargs):
        await self._lock_service.unlock(self._lock)

        self._lock.unlocked = True
        self.async_schedule_update_ha_state()

    @property
    def is_locked(self):
        return not self._lock.unlocked

    @property
    def name(self):
        """Return the display name of this lock."""
        return self._lock.nickname

    @property
    def unique_id(self):
        return self._lock.mac

    @property
    def available(self):
        """Return the connection status of this lock"""
        return self._lock.available

    @property
    def extra_state_attributes(self):
        """Return device attributes of the entity."""
        dev_info = {
            ATTR_ATTRIBUTION: ATTRIBUTION,
            "state": self.state,
            "available": self.available,
            "door_open": self._lock.door_open,
            "device_model": self._lock.product_model,
            "mac": self.unique_id
        }

        # Add the lock battery value if it exists
        if self._lock.raw_dict.get("power"):
            dev_info["lock battery"] = str(self._lock.raw_dict.get("power")) + "%"

        # Add the keypad's battery value if it exists
        if self._lock.raw_dict.get("keypad", {}).get("power"):
            dev_info["keypad battery"] = str(self._lock.raw_dict.get("keypad", {}).get("power")) + "%"

        return dev_info

    @property
    def supported_features(self):
        return None

    @token_exception_handler
    async def async_update(self):
        """
        This function updates the entity
        """
        lock = await self._lock_service.update(self._lock)
        if lock.unlocked == self._lock.unlocked or self._out_of_sync_count >= MAX_OUT_OF_SYNC_COUNT:
            self._lock = lock
            self._out_of_sync_count = 0
        else:
            self._out_of_sync_count += 1

    @callback
    def async_update_callback(self, lock: Lock):
        """Update the switch's state."""
        self._lock = lock
        async_dispatcher_send(
            self.hass,
            f"{LOCK_UPDATED}-{self._lock.mac}",
            lock,
        )
        self.async_schedule_update_ha_state()

    async def async_added_to_hass(self) -> None:
        """Subscribe to update events."""
        self._lock.callback_function = self.async_update_callback
        self._lock_service.register_updater(self._lock, 10)
        await self._lock_service.start_update_manager()
        return await super().async_added_to_hass()

    async def async_will_remove_from_hass(self) -> None:
        self._lock_service.unregister_updater()
