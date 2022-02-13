"""Support for Tuya Select entities."""
from __future__ import annotations

import json
import logging

from homeassistant.components.select import DOMAIN as DEVICE_DOMAIN
from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
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
    "xxj", # Diffuser
    "kfj", # Coffee Maker
    "sd",  # Vacuum Robot
}

DPCODE_MODE = "mode"
DPCODE_COUNTDOWN = "countdown"
DPCODE_WORK_MODE = "work_mode"
DPCODE_DIRECTIONCONTROL = "direction_control"

# Coffee Maker
# https://developer.tuya.com/en/docs/iot/f?id=K9gf4701ox167
DPCODE_MATERIAL = "material"
DPCODE_CONCENTRATIONSET = "concentration_set"
DPCODE_CUPNUMBER = "cup_number"


AUTO_GENERATE_DP_LIST = [
    DPCODE_MODE,
    DPCODE_COUNTDOWN,
    DPCODE_WORK_MODE,
    DPCODE_MATERIAL,
    DPCODE_CONCENTRATIONSET,
    DPCODE_CUPNUMBER,
    DPCODE_DIRECTIONCONTROL
]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up tuya select dynamically through tuya discovery."""
    _LOGGER.info("select init")

    hass.data[DOMAIN][entry.entry_id][TUYA_HA_TUYA_MAP][
        DEVICE_DOMAIN
    ] = TUYA_SUPPORT_TYPE

    @callback
    def async_discover_device(dev_ids):
        _LOGGER.info(f"select add-> {dev_ids}")
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


def get_auto_generate_data_points(status) -> list:
    dps = []
    for data_point in AUTO_GENERATE_DP_LIST:
        if data_point in status:
            dps.append(data_point)

    return dps


def _setup_entities(
    hass, entry: ConfigEntry, device_ids: list[str]
) -> list[Entity]:
    """Set up Tuya Select."""
    device_manager = hass.data[DOMAIN][entry.entry_id][TUYA_DEVICE_MANAGER]
    entities:list[Entity] = []
    for device_id in device_ids:
        device = device_manager.device_map[device_id]
        if device is None:
            continue

        for data_point in get_auto_generate_data_points(device.status):
            entities.append(TuyaHaSelect(device, device_manager, data_point))
            hass.data[DOMAIN][entry.entry_id][TUYA_HA_DEVICES].add(device_id)
    return entities


class TuyaHaSelect(TuyaHaEntity, SelectEntity):
    """Tuya Select Device."""

    def __init__(
        self, device: TuyaDevice, device_manager: TuyaDeviceManager, code: str = ""
    ):
        self._code = code
        self._attr_current_option = None
        super().__init__(device, device_manager)

    @property
    def unique_id(self) -> str | None:
        return f"{super().unique_id}{self._code}"

    @property
    def name(self) -> str | None:
        """Return Tuya device name."""
        return self.tuya_device.name + self._code

    @property
    def current_option(self) -> str:
        return self.tuya_device.status.get(self._code, None)

    def select_option(self, option: str) -> None:
        self._send_command([{"code": self._code, "value": option}])

    @property
    def options(self) -> list:
        dp_range = json.loads(self.tuya_device.function.get(self._code).values)
        return dp_range.get("range", [])
