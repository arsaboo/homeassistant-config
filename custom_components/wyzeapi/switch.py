#!/usr/bin/python3

"""Platform for switch integration."""
import logging
from datetime import timedelta
# Import the device class from the component that you want to support
from typing import Any, Callable, List, Union

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from wyzeapy import CameraService, SwitchService, Wyzeapy
from wyzeapy.services.camera_service import Camera
from wyzeapy.services.switch_service import Switch
from wyzeapy.types import Device, Event

from .const import CAMERA_UPDATED
from .const import DOMAIN, CONF_CLIENT, WYZE_CAMERA_EVENT, WYZE_NOTIFICATION_TOGGLE
from .token_manager import token_exception_handler

_LOGGER = logging.getLogger(__name__)
ATTRIBUTION = "Data provided by Wyze"
SCAN_INTERVAL = timedelta(seconds=30)


# noinspection DuplicatedCode
@token_exception_handler
async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry,
                            async_add_entities: Callable[[List[Any], bool], None]) -> None:
    """
    This function sets up the config entry

    :param hass: The Home Assistant Instance
    :param config_entry: The current config entry
    :param async_add_entities: This function adds entities to the config entry
    :return:
    """

    _LOGGER.debug("""Creating new WyzeApi light component""")
    client: Wyzeapy = hass.data[DOMAIN][config_entry.entry_id][CONF_CLIENT]
    switch_service = await client.switch_service
    camera_service = await client.camera_service

    switches: List[SwitchEntity] = [WyzeSwitch(switch_service, switch) for switch in
                                    await switch_service.get_switches()]
    switches.extend([WyzeSwitch(camera_service, switch) for switch in await camera_service.get_cameras()])

    switches.append(WyzeNotifications(client))

    async_add_entities(switches, True)


class WyzeNotifications(SwitchEntity):
    def __init__(self, client: Wyzeapy):
        self._client = client
        self._is_on = False
        self._uid = WYZE_NOTIFICATION_TOGGLE
        self._just_updated = False

    @property
    def is_on(self) -> bool:
        return self._is_on

    def turn_on(self, **kwargs: Any) -> None:
        pass

    def turn_off(self, **kwargs: Any) -> None:
        pass

    @property
    def device_info(self):
        return {
            "identifiers": {
                (DOMAIN, self._uid)
            },
            "name": "Wyze Notifications",
            "manufacturer": "WyzeLabs",
            "model": "WyzeNotificationToggle"
        }

    @property
    def should_poll(self) -> bool:
        return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._client.enable_notifications()

        self._is_on = True
        self._just_updated = True
        self.async_schedule_update_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._client.disable_notifications()

        self._is_on = False
        self._just_updated = True
        self.async_schedule_update_ha_state()

    @property
    def name(self):
        """Return the display name of this switch."""
        return "Wyze Notifications"

    @property
    def available(self):
        """Return the connection status of this switch"""
        return True

    @property
    def unique_id(self):
        return self._uid

    @property
    def extra_state_attributes(self):
        """Return device attributes of the entity."""
        return {
            ATTR_ATTRIBUTION: ATTRIBUTION,
            "state": self.is_on,
            "available": self.available,
            "mac": self.unique_id
        }

    async def async_update(self):
        if not self._just_updated:
            self._is_on = await self._client.notifications_are_on
        else:
            self._just_updated = False


class WyzeSwitch(SwitchEntity):
    """Representation of a Wyze Switch."""

    def turn_on(self, **kwargs: Any) -> None:
        pass

    def turn_off(self, **kwargs: Any) -> None:
        pass

    _on: bool
    _available: bool
    _just_updated = False
    _old_event_ts: int = 0  # preload with 0 so that we know when it's been updated

    def __init__(self, service: Union[CameraService, SwitchService], device: Device):
        """Initialize a Wyze Bulb."""
        self._device = device
        self._service = service

        if type(self._device) is Camera:
            self._device = Camera(self._device.raw_dict)
        elif type(self._device) is Switch:
            self._device = Switch(self._device.raw_dict)

    @property
    def device_info(self):
        return {
            "identifiers": {
                (DOMAIN, self._device.mac)
            },
            "name": self.name,
            "manufacturer": "WyzeLabs",
            "model": self._device.product_model
        }

    @property
    def should_poll(self) -> bool:
        return False

    @token_exception_handler
    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._service.turn_on(self._device)

        self._device.on = True
        self._just_updated = True
        self.async_schedule_update_ha_state()

    @token_exception_handler
    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._service.turn_off(self._device)

        self._device.on = False
        self._just_updated = True
        self.async_schedule_update_ha_state()

    @property
    def name(self):
        """Return the display name of this switch."""
        return self._device.nickname

    @property
    def available(self):
        """Return the connection status of this switch"""
        return self._device.available

    @property
    def is_on(self):
        """Return true if switch is on."""
        return self._device.on

    @property
    def unique_id(self):
        return "{}-switch".format(self._device.mac)

    @property
    def extra_state_attributes(self):
        """Return device attributes of the entity."""
        dev_info = {
            ATTR_ATTRIBUTION: ATTRIBUTION,
            "state": self.is_on,
            "available": self.available,
            "device model": self._device.product_model,
            "mac": self.unique_id
        }

        if self._device.device_params.get("electricity"):
            dev_info["Battery"] = str(self._device.device_params.get("electricity") + "%")
        # noinspection DuplicatedCode
        if self._device.device_params.get("ip"):
            dev_info["IP"] = str(self._device.device_params.get("ip"))
        if self._device.device_params.get("rssi"):
            dev_info["RSSI"] = str(self._device.device_params.get("rssi"))
        if self._device.device_params.get("ssid"):
            dev_info["SSID"] = str(self._device.device_params.get("ssid"))

        return dev_info

    @token_exception_handler
    async def async_update(self):
        """
        This function updates the entity
        """

        if not self._just_updated:
            self._device = await self._service.update(self._device)
        else:
            self._just_updated = False

    @callback
    def async_update_callback(self, switch: Switch):
        """Update the switch's state."""
        self._device = switch
        async_dispatcher_send(
            self.hass,
            f"{CAMERA_UPDATED}-{switch.mac}",
            switch,
        )
        self.async_schedule_update_ha_state()
        # if the switch is from a camera, lets check for new events
        if isinstance(switch, Camera):
            if self._old_event_ts > 0 and self._old_event_ts != switch.last_event_ts and switch.last_event is not None:
                event: Event = switch.last_event
                # The screenshot/video urls are not always in the same positions in the lists, so we have to loop
                # through them
                _screenshot_url = None
                _video_url = None
                _ai_tag_list = []
                for resource in event.file_list:
                    _ai_tag_list = _ai_tag_list + resource["ai_tag_list"]
                    if resource["type"] == 1:
                        _screenshot_url = resource["url"]
                    elif resource["type"] == 2:
                        _video_url = resource["url"]
                _LOGGER.debug("Camera: %s has a new event", switch.nickname)
                self.hass.bus.fire(WYZE_CAMERA_EVENT, {
                    "device_name": switch.nickname,
                    "device_mac": switch.mac,
                    "ai_tag_list": _ai_tag_list,
                    "tag_list": event.tag_list,
                    "event_screenshot": _screenshot_url,
                    "event_video": _video_url
                })
            self._old_event_ts = switch.last_event_ts

    async def async_added_to_hass(self) -> None:
        """Subscribe to update events."""
        self._device.callback_function = self.async_update_callback
        self._service.register_updater(self._device, 30)
        await self._service.start_update_manager()
        return await super().async_added_to_hass()

    async def async_will_remove_from_hass(self) -> None:
        self._service.unregister_updater()
