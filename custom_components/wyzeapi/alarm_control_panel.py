"""
This module handles the Wyze Home Monitoring system
"""

import logging
from datetime import timedelta
from typing import Optional, Callable, List, Any

from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    SUPPORT_ALARM_ARM_HOME,
    SUPPORT_ALARM_ARM_AWAY
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.core import HomeAssistant
from wyzeapy import Wyzeapy, HMSService
from wyzeapy.services.hms_service import HMSMode
from .token_manager import token_exception_handler

from .const import DOMAIN, CONF_CLIENT

_LOGGER = logging.getLogger(__name__)
ATTRIBUTION = "Data provided by Wyze"
SCAN_INTERVAL = timedelta(seconds=15)


@token_exception_handler
async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry,
                            async_add_entities: Callable[[List[Any], bool], None]):
    """
    This function sets up the integration

    :param hass: Reference to the HomeAssistant instance
    :param config_entry: Reference to the config entry we are setting up
    :param async_add_entities:
    """

    _LOGGER.debug("""Creating new WyzeApi Home Monitoring System component""")
    client: Wyzeapy = hass.data[DOMAIN][config_entry.entry_id][CONF_CLIENT]

    hms_service = await client.hms_service
    if await hms_service.has_hms:
        async_add_entities([WyzeHomeMonitoring(hms_service)], True)


class WyzeHomeMonitoring(AlarmControlPanelEntity):
    """
    A representation of the Wyze Home Monitoring system that works for wyze
    """
    DEVICE_MODEL = "HMS"
    NAME = "Wyze Home Monitoring System"
    AVAILABLE = True
    _state = "disarmed"
    _server_out_of_sync = False

    def __init__(self, hms_service: HMSService):
        self._hms_service = hms_service

    def alarm_arm_vacation(self, code: Optional[str] = None) -> None:
        raise NotImplementedError

    @property
    def state(self):
        return self._state

    def alarm_disarm(self, code: Optional[str] = None) -> None:
        raise NotImplementedError

    def alarm_arm_home(self, code: Optional[str] = None) -> None:
        raise NotImplementedError

    def alarm_arm_away(self, code: Optional[str] = None) -> None:
        raise NotImplementedError

    @token_exception_handler
    async def async_alarm_disarm(self, code=None) -> None:
        """Send disarm command."""
        await self._hms_service.set_mode(HMSMode.DISARMED)
        self._state = "disarmed"
        self._server_out_of_sync = True

    @token_exception_handler
    async def async_alarm_arm_home(self, code=None):
        await self._hms_service.set_mode(HMSMode.HOME)
        self._state = "armed_home"
        self._server_out_of_sync = True

    @token_exception_handler
    async def async_alarm_arm_away(self, code=None):
        await self._hms_service.set_mode(HMSMode.AWAY)
        self._state = "armed_away"
        self._server_out_of_sync = True

    def alarm_arm_night(self, code=None):
        raise NotImplementedError

    def alarm_trigger(self, code=None):
        raise NotImplementedError

    def alarm_arm_custom_bypass(self, code=None):
        raise NotImplementedError

    @property
    def supported_features(self) -> int:
        return SUPPORT_ALARM_ARM_HOME | SUPPORT_ALARM_ARM_AWAY

    @property
    def device_info(self):
        return {
            "identifiers": {
                (DOMAIN, self.unique_id)
            },
            "name": self.NAME,
            "manufacturer": "WyzeLabs",
            "model": self.DEVICE_MODEL
        }

    @property
    def name(self) -> str:
        return self.NAME

    @property
    def unique_id(self):
        return self._hms_service.hms_id

    @property
    def extra_state_attributes(self):
        """Return device attributes of the entity."""
        return {
            ATTR_ATTRIBUTION: ATTRIBUTION,
            "state": self.state,
            "available": self.AVAILABLE,
            "device model": self.DEVICE_MODEL,
            "mac": self.unique_id
        }

    @token_exception_handler
    async def async_update(self):
        """Update the entity with data from the Wyze servers"""

        if not self._server_out_of_sync:
            state = await self._hms_service.update(self._hms_service.hms_id)
            if state is HMSMode.DISARMED:
                self._state = "disarmed"
            elif state is HMSMode.AWAY:
                self._state = "armed_away"
            elif state is HMSMode.HOME:
                self._state = "armed_home"
            elif state is HMSMode.CHANGING:
                self._state = "disarmed"
            else:
                _LOGGER.warning(f"Received {state} from server")

        self._server_out_of_sync = False
