"""Support for Tuya Humidifiers."""
from __future__ import annotations

import json
import logging

from homeassistant.components.humidifier import DEVICE_CLASSES
from homeassistant.components.humidifier import DOMAIN as DEVICE_DOMAIN
from homeassistant.components.humidifier import SUPPORT_MODES, HumidifierEntity
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
    "jsq",  # Humidifier
    "cs",  # Dehumidifier
}

# Humidifier(jsq)
# https://developers.home-assistant.io/docs/core/entity/humidifier
DPCODE_MODE = "mode"
DPCODE_SWITCH = "switch"
DPCODE_SWITCH_SPRAY = "switch_spray"
DPCODE_HUMIDITY_SET = "humidity_set"
DPCODE_DEHUMIDITY_SET_VALUE = "dehumidify_set_value"


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Set up tuya sensors dynamically through tuya discovery."""
    _LOGGER.debug("humidifier init")

    hass.data[DOMAIN][entry.entry_id][TUYA_HA_TUYA_MAP][
        DEVICE_DOMAIN
    ] = TUYA_SUPPORT_TYPE

    @callback
    def async_discover_device(dev_ids):
        """Discover and add a discovered tuya sensor."""
        _LOGGER.debug(f"humidifier add-> {dev_ids}")
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

        entities.append(TuyaHaHumidifier(device, device_manager))
        hass.data[DOMAIN][entry.entry_id][TUYA_HA_DEVICES].add(device_id)
    return entities


class TuyaHaHumidifier(TuyaHaEntity, HumidifierEntity):
    """Tuya Switch Device."""

    def __init__(self, device: TuyaDevice, device_manager: TuyaDeviceManager) -> None:
        super().__init__(device, device_manager)
        if (
            DPCODE_SWITCH not in self.tuya_device.status
            and DPCODE_SWITCH_SPRAY in self.tuya_device.status
        ):
            self.dp_switch = DPCODE_SWITCH_SPRAY
        else:
            self.dp_switch = DPCODE_SWITCH

        if (
            DPCODE_HUMIDITY_SET not in self.tuya_device.status
            and DPCODE_DEHUMIDITY_SET_VALUE in self.tuya_device.status
        ):
            self.dp_humidity = DPCODE_DEHUMIDITY_SET_VALUE
        else:
            self.dp_humidity = DPCODE_HUMIDITY_SET

    @property
    def is_on(self):
        """Return the device is on or off."""
        return self.tuya_device.status.get(self.dp_switch, False)

    @property
    def mode(self):
        """Return the current mode."""
        return self.tuya_device.status.get(DPCODE_MODE)

    @property
    def available_modes(self):
        """Return a list of available modes."""
        return json.loads(self.tuya_device.function.get(DPCODE_MODE, {}).values).get(
            "range"
        )

    @property
    def target_humidity(self) -> int | None:
        """Return the humidity or dehumidity we try to reach."""
        if (
            DPCODE_HUMIDITY_SET not in self.tuya_device.status
            and DPCODE_DEHUMIDITY_SET_VALUE not in self.tuya_device.status
        ):
            return None
        if DPCODE_HUMIDITY_SET in self.tuya_device.status:
            return self.tuya_device.status.get(DPCODE_HUMIDITY_SET, 0)
        else:
            return self.tuya_device.status.get(DPCODE_DEHUMIDITY_SET_VALUE, 0)

    @property
    def supported_features(self):
        """Return humidifier or dehumidifier support features."""
        supports = 0
        if DPCODE_MODE in self.tuya_device.status:
            supports = supports | SUPPORT_MODES
        return supports

    @property
    def device_class(self):
        """Return humidifier or dehumidifier device class."""
        if DPCODE_HUMIDITY_SET in self.tuya_device.status:
            return DEVICE_CLASSES[0]
        elif DPCODE_DEHUMIDITY_SET_VALUE in self.tuya_device.status:
            return DEVICE_CLASSES[1]
        else:
            return None

    def set_mode(self, mode):
        """Set new target preset mode."""
        self._send_command([{"code": DPCODE_MODE, "value": mode}])

    def turn_on(self, **kwargs):
        """Turn the device on."""
        self._send_command([{"code": self.dp_switch, "value": True}])

    def turn_off(self, **kwargs):
        """Turn the device off."""
        self._send_command([{"code": self.dp_switch, "value": False}])

    def set_humidity(self, humidity):
        """Set new target humidity."""
        self._send_command([{"code": self.dp_humidity, "value": humidity}])
