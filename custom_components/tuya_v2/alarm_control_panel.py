"""Support for Tuya Alarm Control."""

import logging
from typing import Callable

from homeassistant.components.alarm_control_panel import DOMAIN as DEVICE_DOMAIN
from homeassistant.components.alarm_control_panel import (
    SUPPORT_ALARM_TRIGGER,
    AlarmControlPanelEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_ALARM_ARMING, STATE_ALARM_TRIGGERED
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
    "ywbj",  # Smoke Detector
    "rqbj",  # Gas Detector
    "pir",  # PIR Detector
]

# Smoke Detector
# https://developer.tuya.com/en/docs/iot/s?id=K9gf48r5i2iiy

DPCODE_SMOKE_SENSOR_STATE = "smoke_sensor_state"
DPCODE_GAS_SENSOR_STATE = "gas_sensor_state"
DPCODE_PIR = "pir"


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up tuya alarm dynamically through tuya discovery."""
    _LOGGER.debug("alarm init")

    hass.data[DOMAIN][entry.entry_id][TUYA_HA_TUYA_MAP][
         DEVICE_DOMAIN
    ] = TUYA_SUPPORT_TYPE

    @callback
    def async_discover_device(dev_ids):
        """Discover and add a discovered tuya sensor."""
        _LOGGER.debug("alarm add->", dev_ids)
        if not dev_ids:
            return
        entities = entities = _setup_entities(hass, entry, dev_ids)
        for entity in entities:
            hass.data[DOMAIN][entry.entry_id][TUYA_HA_DEVICES].add(entity.unique_id)
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

        if DPCODE_SMOKE_SENSOR_STATE in device.status:
            entities.append(
                TuyaHaAlarm(
                    device,
                    device_manager,
                    (
                        lambda d: STATE_ALARM_TRIGGERED
                        if d.status.get(DPCODE_SMOKE_SENSOR_STATE, 1) == "1"
                        else STATE_ALARM_ARMING
                    ),
                )
            )
        if DPCODE_GAS_SENSOR_STATE in device.status:
            entities.append(
                TuyaHaAlarm(
                    device,
                    device_manager,
                    (
                        lambda d: STATE_ALARM_TRIGGERED
                        if d.status.get(DPCODE_GAS_SENSOR_STATE, 1) == "1"
                        else STATE_ALARM_ARMING
                    ),
                )
            )
        if DPCODE_PIR in device.stastus:
            entities.append(
                TuyaHaAlarm(
                    device,
                    device_manager,
                    (
                        lambda d: STATE_ALARM_TRIGGERED
                        if d.status.get(DPCODE_GAS_SENSOR_STATE, "none") == "pir"
                        else STATE_ALARM_ARMING
                    ),
                )
            )

    return entities


class TuyaHaAlarm(TuyaHaEntity, AlarmControlPanelEntity):
    """Tuya Alarm Device."""

    def __init__(self, device: TuyaDevice, device_manager: TuyaDeviceManager, sensor_is_on: Callable[..., str]) -> None:
        """Init TuyaHaAlarm."""
        super().__init__(device, device_manager)
        self._is_on = sensor_is_on

    @property
    def state(self):
        """Return is alarm on."""
        return self._is_on(self.tuya_device)

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        return SUPPORT_ALARM_TRIGGER
