"""Support for Tuya Number entities."""
from __future__ import annotations

import json
import logging

from homeassistant.components.number import DOMAIN as DEVICE_DOMAIN
from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import Entity
from tuya_iot import TuyaDevice, TuyaDeviceManager

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
    "hps",  # Human Presence Sensor
    "kfj",  # Coffee Maker
}

# Switch(kg), Socket(cz), Power Strip(pc)
# https://developer.tuya.com/docs/iot/open-api/standard-function/electrician-category/categorykgczpc?categoryId=486118
DPCODE_SENSITIVITY = "sensitivity"

# Coffee Maker
# https://developer.tuya.com/en/docs/iot/f?id=K9gf4701ox167
DPCODE_TEMPSET = "temp_set"
DPCODE_WARMTIME = "warm_time"
DPCODE_WATERSET = "water_set"
DPCODE_POWDERSET = "powder_set"
DPCODE_CLOUDRECIPE = "cloud_recipe_number"


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up tuya number dynamically through tuya discovery."""
    _LOGGER.debug("number init")

    hass.data[DOMAIN][entry.entry_id][TUYA_HA_TUYA_MAP][
        DEVICE_DOMAIN
    ] = TUYA_SUPPORT_TYPE

    @callback
    def async_discover_device(dev_ids):
        """Discover and add a discovered tuya number."""
        _LOGGER.debug(f"number add-> {dev_ids}")
        if not dev_ids:
            return
        entities = _setup_entities(hass, entry, dev_ids)
        for entrty in entitier:
            hass.data[DOMAIN][entry.entry_id][TUYA_HA_DEVICES].add(entrty.unique_id)
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

        if DPCODE_SENSITIVITY in device.status:
            entities.append(TuyaHaNumber(device, device_manager, DPCODE_SENSITIVITY))

        if DPCODE_TEMPSET in device.status:
            entities.append(TuyaHaNumber(device, device_manager, DPCODE_TEMPSET))

        if DPCODE_WARMTIME in device.status:
            entities.append(TuyaHaNumber(device, device_manager, DPCODE_WARMTIME))

        if DPCODE_WATERSET in device.status:
            entities.append(TuyaHaNumber(device, device_manager, DPCODE_WATERSET))

        if DPCODE_POWDERSET in device.status:
            entities.append(TuyaHaNumber(device, device_manager, DPCODE_POWDERSET))

        if DPCODE_CLOUDRECIPE in device.status:
            entities.append(TuyaHaNumber(device, device_manager, DPCODE_CLOUDRECIPE))

    return entities


class TuyaHaNumber(TuyaHaEntity, NumberEntity):
    """Tuya Device Number."""

    def __init__(
        self, device: TuyaDevice, device_manager: TuyaDeviceManager, code: str = ""
    ) -> None:
        """Init tuya number device."""
        self._code = code
        super().__init__(device, device_manager)

    def set_value(self, value: float) -> None:
        """Update the current value."""
        self._send_command([{"code": self._code, "value": int(value)}])

    @property
    def unique_id(self) -> str | None:
        """Return a unique ID."""
        return f"{super().unique_id}{self._code}"

    @property
    def name(self) -> str | None:
        """Return Tuya device name."""
        return f"{self.tuya_device.name}{self._code}"

    @property
    def value(self) -> float:
        """Return current value."""
        return self.tuya_device.status.get(self._code, 0)

    @property
    def min_value(self) -> float:
        """Return min value."""
        return self._get_code_range()[0]

    @property
    def max_value(self) -> float:
        """Return max value."""
        return self._get_code_range()[1]

    @property
    def step(self) -> float:
        """Return step."""
        return self._get_code_range()[2]

    def _get_code_range(self) -> tuple[int, int, int]:
        dp_range = json.loads(self.tuya_device.function.get(self._code).values)
        return dp_range.get("min", 0), dp_range.get("max", 0), dp_range.get("step", 0)
