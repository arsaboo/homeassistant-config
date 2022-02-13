#!/usr/bin/env python3
"""Support for Tuya Vacuums."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.vacuum import DOMAIN as DEVICE_DOMAIN
from homeassistant.components.vacuum import (
    STATE_CLEANING,
    STATE_DOCKED,
    STATE_IDLE,
    STATE_PAUSED,
    STATE_RETURNING,
    SUPPORT_BATTERY,
    SUPPORT_PAUSE,
    SUPPORT_RETURN_HOME,
    SUPPORT_START,
    SUPPORT_STATE,
    SUPPORT_STATUS,
    SUPPORT_STOP,
    StateVacuumEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .base import TuyaHaEntity
from .const import (
    DOMAIN,
    TUYA_DEVICE_MANAGER,
    TUYA_DISCOVERY_NEW,
    TUYA_HA_DEVICES,
    TUYA_HA_TUYA_MAP,
)


_LOGGER = logging.getLogger(__name__)

TUYA_SUPPORT_TYPE = {
    "sd",  # Robot Vaccuum
}

# Vacuum(sd),
# https://developer.tuya.com/docs/iot/open-api/standard-function/electrician-category/categorykgczpc?categoryId=486118
DPCODE_MODE = "mode"
DPCODE_POWER = "power"  # Device switch
DPCODE_POWER_GO = "power_go"  # Cleaning switch
DPCODE_STATUS = "status"
DPCODE_PAUSE = "pause"
DPCODE_RETURN_HOME = "switch_charge"

DPCODE_BATTERY = "electricity_left"
DPCODE_LOCATE = "seek"
DPCODE_STATUS_FULL = "status_full"
DPCODE_CLEAN_AREA = "clean_area"
DPCODE_CLEAN_TIME = "clean_time"
DPCODE_CLEAN_RECORD = "clean_record"

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up tuya vacuum dynamically through tuya discovery."""
    _LOGGER.debug("vacuum init")

    hass.data[DOMAIN][entry.entry_id][TUYA_HA_TUYA_MAP][
        DEVICE_DOMAIN
    ] = TUYA_SUPPORT_TYPE

    @callback
    def async_discover_device(dev_ids):
        """Discover and add a discovered tuya sensor."""
        _LOGGER.debug(f"vacuum add -> {dev_ids}")
        if not dev_ids:
            return
        entities = _setup_entities(hass, entry, dev_ids)
        async_add_entities(entities)

    entry.async_on_unload(
        async_dispatcher_connect(
            hass, TUYA_DISCOVERY_NEW.format(DEVICE_DOMAIN), async_discover_device
        )
    )

    device_manager = hass.data[DOMAIN][entry.entry_id][TUYA_DEVICE_MANAGER]
    device_ids = []
    for (device_id, device) in device_manager.device_map.items():
        if device.category in TUYA_SUPPORT_TYPE:
            device_ids.append(device_id)
    async_discover_device(device_ids)


def _setup_entities(
    hass: HomeAssistant, entry: ConfigEntry, device_ids: list[str]
) -> list[Entity]:
    """Set up Tuya Switch device."""
    device_manager = hass.data[DOMAIN][entry.entry_id][TUYA_DEVICE_MANAGER]
    entities: list[Entity] = []
    for device_id in device_ids:
        device = device_manager.device_map[device_id]
        if device is None:
            continue

        entities.append(TuyaHaVacuum(device, device_manager))
        hass.data[DOMAIN][entry.entry_id][TUYA_HA_DEVICES].add(device_id)
    return entities


class TuyaHaVacuum(TuyaHaEntity, StateVacuumEntity):
    """Tuya Vacuum Device."""

    @property
    def name(self) -> str | None:
        """Return Tuya device name."""
        return self.tuya_device.name

    @property
    def battery_level(self) -> int | None:
        """Return Tuya device state."""
        return self.tuya_device.status.get(DPCODE_BATTERY)
		
    @property
    def device_state_attributes(self):
        """Return the optional state attributes with device specific additions."""
        attr = {}
        if self.tuya_device.status.get(DPCODE_MODE):
          attr[DPCODE_MODE] = self.tuya_device.status.get(DPCODE_MODE)
        if self.tuya_device.status.get(DPCODE_STATUS):
          attr[DPCODE_STATUS_FULL] = self.tuya_device.status.get(DPCODE_STATUS)
        if self.tuya_device.status.get(DPCODE_CLEAN_AREA):
          attr[DPCODE_CLEAN_AREA] = self.tuya_device.status.get(DPCODE_CLEAN_AREA)
        if self.tuya_device.status.get(DPCODE_CLEAN_TIME):
          attr[DPCODE_CLEAN_TIME] = self.tuya_device.status.get(DPCODE_CLEAN_TIME)
        if self.tuya_device.status.get(DPCODE_CLEAN_RECORD):
          attr[DPCODE_CLEAN_RECORD] = self.tuya_device.status.get(DPCODE_CLEAN_RECORD)
        return attr
		
    @property
    def state(self):
        """Return Tuya device state."""
        if (
            DPCODE_PAUSE in self.tuya_device.status
            and self.tuya_device.status[DPCODE_PAUSE]
        ):
            return STATE_PAUSED

        status = self.tuya_device.status.get(DPCODE_STATUS)

        if status == "standby":
            return STATE_IDLE
        if status == "goto_charge" or status == "docking":
            return STATE_RETURNING
        if status == "charging" or status == "charge_done" or status == "chargecompleted":
            return STATE_DOCKED
        if status == "pause":
            return STATE_PAUSED
        return STATE_CLEANING

    @property
    def supported_features(self):
        """Flag supported features."""
        supports = 0
        if DPCODE_PAUSE in self.tuya_device.status:
            supports = supports | SUPPORT_PAUSE
        if DPCODE_RETURN_HOME in self.tuya_device.status:
            supports = supports | SUPPORT_RETURN_HOME
        if DPCODE_STATUS in self.tuya_device.status:
            supports = supports | SUPPORT_STATE
            supports = supports | SUPPORT_STATUS
        if DPCODE_POWER_GO in self.tuya_device.status:
            supports = supports | SUPPORT_STOP
            supports = supports | SUPPORT_START
        if DPCODE_BATTERY in self.tuya_device.status:
            supports = supports | SUPPORT_BATTERY
        return supports

    def start(self, **kwargs: Any) -> None:
        """Turn the device on."""
        _LOGGER.debug(f"Starting {self.name}")

        self._send_command([{"code": DPCODE_POWER_GO, "value": True}])

    def stop(self, **kwargs: Any) -> None:
        """Turn the device off."""
        _LOGGER.debug(f"Stopping {self.name}")
        self._send_command([{"code": DPCODE_POWER_GO, "value": False}])

    def pause(self, **kwargs: Any) -> None:
        """Pause the device."""
        _LOGGER.debug(f"Pausing {self.name}")
        self._send_command([{"code": DPCODE_PAUSE, "value": True}])

    def return_to_base(self, **kwargs: Any) -> None:
        """Return device to Dock"""
        _LOGGER.debug(f"Return to base device {self.name}")
        self._send_command([{"code": DPCODE_MODE, "value": "chargego"}])
		
    def locate(self, **kwargs: Any) -> None:
        """Return device to Dock"""
        _LOGGER.debug(f"Locate the device {self.name}")
        self._send_command([{"code": DPCODE_LOCATE, "value": True}])
