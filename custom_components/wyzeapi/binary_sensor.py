"""
This module describes the connection between Home Assistant and Wyze for the Sensors
"""

import logging
import time
from typing import Callable, List, Any

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    DEVICE_CLASS_MOTION,
    DEVICE_CLASS_DOOR
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.core import HomeAssistant
from wyzeapy import Wyzeapy, CameraService, SensorService
from wyzeapy.services.camera_service import Camera
from wyzeapy.services.sensor_service import Sensor
from wyzeapy.types import DeviceTypes
from .token_manager import token_exception_handler

from .const import DOMAIN, CONF_CLIENT

_LOGGER = logging.getLogger(__name__)
ATTRIBUTION = "Data provided by Wyze"


@token_exception_handler
async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry,
                            async_add_entities: Callable[[List[Any], bool], None]):
    """
    This function sets up the config entry for use in Home Assistant

    :param hass: Home Assistant instance
    :param config_entry: The current config_entry
    :param async_add_entities: This function adds entities to the config_entry
    :return:
    """

    _LOGGER.debug("""Creating new WyzeApi binary sensor component""")
    client: Wyzeapy = hass.data[DOMAIN][config_entry.entry_id][CONF_CLIENT]

    sensor_service = await client.sensor_service
    camera_service = await client.camera_service

    cameras = [WyzeCameraMotion(camera_service, camera) for camera in await camera_service.get_cameras()]
    sensors = [WyzeSensor(sensor_service, sensor) for sensor in await sensor_service.get_sensors()]

    async_add_entities(cameras, True)
    async_add_entities(sensors, True)


class WyzeSensor(BinarySensorEntity):
    """
    A representation of the WyzeSensor for use in Home Assistant
    """

    def __init__(self, sensor_service: SensorService, sensor: Sensor):
        """Initializes the class"""
        self._sensor_service = sensor_service
        self._sensor = sensor
        self._last_event = int(str(int(time.time())) + "000")

    async def async_added_to_hass(self) -> None:
        """Registers for updates when the entity is added to Home Assistant"""
        await self._sensor_service.register_for_updates(self._sensor, self.process_update)

    async def async_will_remove_from_hass(self) -> None:
        await self._sensor_service.deregister_for_updates(self._sensor)

    def process_update(self, sensor: Sensor):
        """
        This function processes an update for the Wyze Sensor

        :param sensor: The sensor with the updated values
        """
        self._sensor = sensor
        self.schedule_update_ha_state()

    @property
    def device_info(self):
        return {
            "identifiers": {
                (DOMAIN, self._sensor.mac)
            },
            "name": self.name,
            "manufacturer": "WyzeLabs",
            "model": self._sensor.product_model
        }

    @property
    def available(self) -> bool:
        return True

    @property
    def name(self):
        """Return the display name of this switch."""
        return self._sensor.nickname

    @property
    def should_poll(self) -> bool:
        return False

    @property
    def is_on(self):
        """Return true if sensor detects motion"""
        return self._sensor.detected

    @property
    def unique_id(self):
        return "{}-motion".format(self._sensor.mac)

    @property
    def extra_state_attributes(self):
        """Return device attributes of the entity."""
        return {
            ATTR_ATTRIBUTION: ATTRIBUTION,
            "state": self.is_on,
            "available": self.available,
            "device model": self._sensor.product_model,
            "mac": self.unique_id
        }

    @property
    def device_class(self):
        # pylint: disable=R1705
        if self._sensor.type is DeviceTypes.MOTION_SENSOR:
            return DEVICE_CLASS_MOTION
        elif self._sensor.type is DeviceTypes.CONTACT_SENSOR:
            return DEVICE_CLASS_DOOR
        else:
            raise RuntimeError(
                f"The device type {self._sensor.type} is not supported by this class")


class WyzeCameraMotion(BinarySensorEntity):
    """
    A representation of the Wyze Camera for use as a binary sensor in Home Assistant
    """
    _is_on = False
    _last_event = time.time() * 1000

    def __init__(self, camera_service: CameraService, camera: Camera):
        self._camera_service = camera_service
        self._camera = camera

    @property
    def device_info(self):
        return {
            "identifiers": {
                (DOMAIN, self._camera.mac)
            },
            "name": self.name,
            "manufacturer": "WyzeLabs",
            "model": self._camera.product_model
        }

    @property
    def available(self) -> bool:
        return self._camera.available

    @property
    def name(self):
        """Return the display name of this switch."""
        return self._camera.nickname

    @property
    def should_poll(self) -> bool:
        return False

    @property
    def is_on(self):
        """Return true if the binary sensor is on"""
        return self._is_on

    @property
    def unique_id(self):
        return "{}-motion".format(self._camera.mac)

    @property
    def extra_state_attributes(self):
        """Return device attributes of the entity."""
        return {
            ATTR_ATTRIBUTION: ATTRIBUTION,
            "state": self.is_on,
            "available": self.available,
            "device model": self._camera.product_model,
            "mac": self.unique_id
        }

    @property
    def device_class(self):
        return DEVICE_CLASS_MOTION

    async def async_added_to_hass(self) -> None:
        await self._camera_service.register_for_updates(self._camera, self.process_update)

    async def async_will_remove_from_hass(self) -> None:
        await self._camera_service.deregister_for_updates(self._camera)

    @token_exception_handler
    def process_update(self, camera: Camera) -> None:
        """
        Is called by the update worker for events to update the values in this sensor

        :param camera: An updated version of the current camera
        """
        self._camera = camera

        if camera.last_event_ts > self._last_event:
            self._is_on = True
            self._last_event = camera.last_event_ts
        else:
            self._is_on = False
            self._last_event = camera.last_event_ts

        self.schedule_update_ha_state()
