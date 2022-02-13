"""Support for Tuya Binary Sensor."""
from __future__ import annotations

import json
import logging
from threading import Timer
from typing import Callable

from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_BATTERY,
    DEVICE_CLASS_DOOR,
    DEVICE_CLASS_GARAGE_DOOR,
    DEVICE_CLASS_GAS,
    DEVICE_CLASS_MOISTURE,
    DEVICE_CLASS_MOTION,
    DEVICE_CLASS_PROBLEM,
    DEVICE_CLASS_SMOKE,
)
from homeassistant.components.binary_sensor import DOMAIN as DEVICE_DOMAIN
from homeassistant.components.binary_sensor import BinarySensorEntity
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

TUYA_SUPPORT_TYPE = [
    "mcs",  # Door Window Sensor
    "ywbj",  # Smoke Detector
    "rqbj",  # Gas Detector
    "pir",  # PIR Detector
    "sj",  # Water Detector
    "sos",  # Emergency Button
    "hps",  # Human Presence Sensor
    "ms",  # Residential Lock
    "ckmkzq",  # Garage Door Opener
]

# Door Window Sensor
# https://developer.tuya.com/en/docs/iot/s?id=K9gf48hm02l8m

DPCODE_SWITCH = "switch"


DPCODE_BATTERY_STATE = "battery_state"

DPCODE_DOORCONTACT_STATE = "doorcontact_state"
DPCODE_SMOKE_SENSOR_STATE = "smoke_sensor_state"
DPCODE_SMOKE_SENSOR_STATUS = "smoke_sensor_status"
DPCODE_GAS_SENSOR_STATE = "gas_sensor_state"
DPCODE_PIR = "pir"
DPCODE_WATER_SENSOR_STATE = "watersensor_state"
DPCODE_SOS_STATE = "sos_state"
DPCODE_PRESENCE_STATE = "presence_state"
DPCODE_TEMPER_ALRAM = "temper_alarm"
DPCODE_DOORLOCK_STATE = "closed_opened"


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up tuya binary sensors dynamically through tuya discovery."""
    _LOGGER.debug("binary sensor init")

    hass.data[DOMAIN][entry.entry_id][TUYA_HA_TUYA_MAP][
        DEVICE_DOMAIN
    ] = TUYA_SUPPORT_TYPE

    @callback
    def async_discover_device(dev_ids):
        """Discover and add a discovered tuya sensor."""
        _LOGGER.debug(f"binary sensor add->{dev_ids}")
        if not dev_ids:
            return
        entities = _setup_entities(hass, entry, dev_ids)
        for entity in entities:
            hass.data[DOMAIN][entry.entry_id][TUYA_HA_DEVICES].add(entity._attr_unique_id)
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

        if DPCODE_DOORLOCK_STATE in device.status:
            entities.append(
                TuyaHaBSensor(
                    device,
                    device_manager,
                    DEVICE_CLASS_DOOR,
                    DPCODE_DOORLOCK_STATE,
                    (lambda d: d.status.get(DPCODE_DOORLOCK_STATE, "none") != "closed"),
                )
            )
        if DPCODE_DOORCONTACT_STATE in device.status:
            if device.category == "ckmkzq":
                device_class_d = DEVICE_CLASS_GARAGE_DOOR
            else:
                device_class_d = DEVICE_CLASS_DOOR
            entities.append(
                TuyaHaBSensor(
                    device,
                    device_manager,
                    device_class_d,
                    DPCODE_DOORCONTACT_STATE,
                    (lambda d: d.status.get(DPCODE_DOORCONTACT_STATE, False)),
                )
            )
        if DPCODE_SWITCH in device.status:
            entities.append(
                TuyaHaBSensor(
                    device,
                    device_manager,
                    DEVICE_CLASS_DOOR,
                    DPCODE_SWITCH,
                    (lambda d: d.status.get(DPCODE_SWITCH, False)),
                )
            )
        if DPCODE_SMOKE_SENSOR_STATE in device.status:
            entities.append(
                TuyaHaBSensor(
                    device,
                    device_manager,
                    DEVICE_CLASS_SMOKE,
                    DPCODE_SMOKE_SENSOR_STATE,
                    (lambda d: d.status.get(DPCODE_SMOKE_SENSOR_STATE, 1) == "1"),
                )
            )
        if DPCODE_SMOKE_SENSOR_STATUS in device.status:
            entities.append(
                TuyaHaBSensor(
                    device,
                    device_manager,
                    DEVICE_CLASS_SMOKE,
                    DPCODE_SMOKE_SENSOR_STATUS,
                    (
                        lambda d: d.status.get(DPCODE_SMOKE_SENSOR_STATUS, "normal")
                        == "alarm"
                    ),
                )
            )
        if DPCODE_BATTERY_STATE in device.status:
            entities.append(
                TuyaHaBSensor(
                    device,
                    device_manager,
                    DEVICE_CLASS_BATTERY,
                    DPCODE_BATTERY_STATE,
                    (lambda d: d.status.get(DPCODE_BATTERY_STATE, "normal") == "low"),
                )
            )
        if DPCODE_TEMPER_ALRAM in device.status:
            entities.append(
                TuyaHaBSensor(
                    device,
                    device_manager,
                    DEVICE_CLASS_MOTION,
                    DPCODE_TEMPER_ALRAM,
                    (lambda d: d.status.get(DPCODE_TEMPER_ALRAM, False)),
                )
            )
        if DPCODE_GAS_SENSOR_STATE in device.status:
            entities.append(
                TuyaHaBSensor(
                    device,
                    device_manager,
                    DEVICE_CLASS_GAS,
                    DPCODE_GAS_SENSOR_STATE,
                    (lambda d: d.status.get(DPCODE_GAS_SENSOR_STATE, 1) == "1"),
                )
            )
        if DPCODE_PIR in device.status:
            entities.append(
                TuyaHaBSensor(
                    device,
                    device_manager,
                    DEVICE_CLASS_MOTION,
                    DPCODE_PIR,
                    (lambda d: d.status.get(DPCODE_PIR, "none") == "pir"),
                )
            )
        if DPCODE_WATER_SENSOR_STATE in device.status:
            entities.append(
                TuyaHaBSensor(
                    device,
                    device_manager,
                    DEVICE_CLASS_MOISTURE,
                    DPCODE_WATER_SENSOR_STATE,
                    (
                        lambda d: d.status.get(DPCODE_WATER_SENSOR_STATE, "normal")
                        == "alarm"
                    ),
                )
            )
        if DPCODE_SOS_STATE in device.status:
            entities.append(
                TuyaHaBSensor(
                    device,
                    device_manager,
                    DEVICE_CLASS_PROBLEM,
                    DPCODE_SOS_STATE,
                    (lambda d: d.status.get(DPCODE_SOS_STATE, False)),
                )
            )
        if DPCODE_PRESENCE_STATE in device.status:
            entities.append(
                TuyaHaBSensor(
                    device,
                    device_manager,
                    DEVICE_CLASS_MOTION,
                    DPCODE_PRESENCE_STATE,
                    (
                        lambda d: d.status.get(DPCODE_PRESENCE_STATE, "none")
                        == "presence"
                    ),
                )
            )

    return entities


class TuyaHaBSensor(TuyaHaEntity, BinarySensorEntity):
    """Tuya Binary Sensor Device."""

    def __init__(
        self,
        device: TuyaDevice,
        device_manager: TuyaDeviceManager,
        sensor_type: str,
        sensor_code: str,
        sensor_is_on: Callable[..., bool],
    ) -> None:
        """Init TuyaHaBSensor."""
        super().__init__(device, device_manager)
        self._type = sensor_type
        self._code = sensor_code
        self._is_on = sensor_is_on
        self._attr_unique_id = f"{super().unique_id}{self._code}"
        self._attr_name = f"{self.tuya_device.name}_{self._code}"
        self._attr_device_class = self._type
        self._attr_available = True

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self._is_on(self.tuya_device)

    @property
    def unique_id(self) -> str | None:
        """Return a unique ID."""
        return self._attr_unique_id

    def reset_pir(self):
        self.tuya_device.status[DPCODE_PIR] = "none"
        self.schedule_update_ha_state()

    def schedule_update_ha_state(self, force_refresh: bool = False) -> None:

        if self._code == DPCODE_PIR:
            pir_range = json.loads(
                self.tuya_device.status_range.get(DPCODE_PIR, {}).values
            ).get("range")
            if len(pir_range) == 1 and self.tuya_device.status[DPCODE_PIR] == "pir":
                timer = Timer(10, lambda: self.reset_pir())
                timer.start()

        super().schedule_update_ha_state(force_refresh)
