"""
This component provides support for Aarlo switches.

"""

import logging
import time
from datetime import timedelta

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
import homeassistant.util.dt as dt_util
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import (ATTR_ATTRIBUTION)
from homeassistant.core import callback
from homeassistant.helpers.config_validation import (PLATFORM_SCHEMA)
from homeassistant.helpers.event import track_point_in_time
from . import COMPONENT_ATTRIBUTION, COMPONENT_DATA, COMPONENT_BRAND
from .pyaarlo.constant import (ACTIVITY_STATE_KEY, SILENT_MODE_KEY,
                               SILENT_MODE_ACTIVE_KEY, SILENT_MODE_CALL_KEY,
                               SIREN_STATE_KEY)

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['aarlo']

SIRENS_DEFAULT = False
SIREN_DURATION_DEFAULT = timedelta(seconds=300)
SIREN_VOLUME_DEFAULT = "8"
SIREN_ALLOW_OFF_DEFAULT = True
ALL_SIRENS_DEFAULT = False
SNAPSHOTS_DEFAULT = False
SILENT_MODE_DEFAULT = False
SNAPSHOT_TIMEOUT_DEFAULT = timedelta(seconds=60)

CONF_SIRENS = "siren"
CONF_ALL_SIRENS = "all_sirens"
CONF_SIREN_DURATION = "siren_duration"
CONF_SIREN_VOLUME = "siren_volume"
CONF_SIREN_ALLOW_OFF = "siren_allow_off"
CONF_SNAPSHOT = "snapshot"
CONF_SNAPSHOT_TIMEOUT = "snapshot_timeout"
CONF_DOORBELL_SILENCE = "doorbell_silence"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_SIRENS, default=SIRENS_DEFAULT): cv.boolean,
    vol.Optional(CONF_ALL_SIRENS, default=ALL_SIRENS_DEFAULT): cv.boolean,
    vol.Optional(CONF_SIREN_DURATION, default=SIREN_DURATION_DEFAULT): vol.All(cv.time_period, cv.positive_timedelta),
    vol.Optional(CONF_SIREN_VOLUME, default=SIREN_VOLUME_DEFAULT): cv.string,
    vol.Optional(CONF_SIREN_ALLOW_OFF, default=SIREN_ALLOW_OFF_DEFAULT): cv.boolean,
    vol.Optional(CONF_SNAPSHOT, default=SNAPSHOTS_DEFAULT): cv.boolean,
    vol.Optional(CONF_SNAPSHOT_TIMEOUT, default=SNAPSHOT_TIMEOUT_DEFAULT): vol.All(cv.time_period,
                                                                                   cv.positive_timedelta),
    vol.Optional(CONF_DOORBELL_SILENCE, default=SILENT_MODE_DEFAULT): cv.boolean,
})


async def async_setup_platform(hass, config, async_add_entities, _discovery_info=None):
    arlo = hass.data.get(COMPONENT_DATA)
    if not arlo:
        return

    devices = []
    adevices = []

    # See what cameras and bases have sirens.
    for base in arlo.base_stations:
        if base.has_capability(SIREN_STATE_KEY):
            adevices.append(base)
    for camera in arlo.cameras:
        if camera.has_capability(SIREN_STATE_KEY):
            adevices.append(camera)

    # Create individual switches if asked for
    if config.get(CONF_SIRENS) is True:
        for adevice in adevices:
            devices.append(AarloSirenSwitch(config, adevice))

    # Then create all_sirens if asked for.
    if config.get(CONF_ALL_SIRENS) is True:
        if len(adevices) != 0:
            devices.append(AarloAllSirensSwitch(config, arlo, adevices))

    # Add snapshot for each camera
    if config.get(CONF_SNAPSHOT) is True:
        for camera in arlo.cameras:
            devices.append(AarloSnapshotSwitch(config, camera))

    if config.get(CONF_DOORBELL_SILENCE) is True:
        for doorbell in arlo.doorbells:
            if doorbell.has_capability(SILENT_MODE_KEY):
                devices.append(AarloSilentModeChimeSwitch(doorbell))
                devices.append(AarloSilentModeChimeCallSwitch(doorbell))

    async_add_entities(devices, True)


class AarloSwitch(SwitchEntity):
    """Representation of an Aarlo switch."""

    def __init__(self, name, identifier, icon):
        """Initialize the Aarlo switch device."""
        self._name = name
        self._unique_id = identifier
        self._icon = "mdi:{}".format(icon)
        self._device = None
        _LOGGER.info('AarloSwitch: {} created'.format(self._name))

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def state(self):
        return "off"

    @property
    def is_on(self):
        """Return true if switch is on."""
        return self.state

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        _LOGGER.debug('implement turn on')

    def turn_off(self, **kwargs):
        """Turn the switch off."""
        _LOGGER.debug('implement turn off')

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        attrs = {
            ATTR_ATTRIBUTION: COMPONENT_ATTRIBUTION,
            'brand': COMPONENT_BRAND,
            'friendly_name': self._name,
            'icon': self._icon
        }

        if self._device is not None:
            attrs['device_id'] = self._device.device_id
            attrs['model_id'] = self._device.model_id

        return attrs


class AarloSirenBaseSwitch(AarloSwitch):
    """Representation of an Aarlo Momentary switch."""

    def __init__(self, name, identifier, icon, on_for, allow_off):
        """Initialize the Aarlo Momentary switch device."""
        super().__init__(name, identifier, icon)
        self._on_for = on_for
        self._allow_off = allow_off
        self._on_until = None
        _LOGGER.debug("on={}, allow={}".format(on_for, allow_off))

    @property
    def state(self):
        """Return the state of the switch."""
        if self._on_until is not None:
            if self._on_until < time.monotonic():
                _LOGGER.debug('turned off')
                self.do_off()
                self._on_until = None
        return self.get_state()

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        if self._on_until is None:
            self.do_on()
            self._on_until = time.monotonic() + self._on_for.total_seconds()
            self.async_schedule_update_ha_state()
            track_point_in_time(self.hass, self.async_update_ha_state, dt_util.utcnow() + self._on_for)
            _LOGGER.debug('turned on')

    def turn_off(self, **kwargs):
        """Turn the switch off."""
        if self._allow_off:
            self.do_off()
            self._on_until = None
            _LOGGER.debug('forced off')
        self.async_schedule_update_ha_state()

    def get_state(self):
        _LOGGER.debug("implement get state")

    def do_on(self):
        _LOGGER.debug("implement do on")

    def do_off(self):
        _LOGGER.debug("implement do off")


class AarloSirenSwitch(AarloSirenBaseSwitch):
    """Representation of an Aarlo switch."""

    def __init__(self, config, device):
        """Initialize the Aarlo siren switch device."""
        super().__init__("{0} Siren".format(device.name), "siren_{}".format(device.entity_id), "alarm-bell",
                         config.get(CONF_SIREN_DURATION),
                         config.get(CONF_SIREN_ALLOW_OFF))
        self._device = device
        self._volume = config.get(CONF_SIREN_VOLUME)
        self._state = "off"
        _LOGGER.debug("{0}".format(str(config)))

    async def async_added_to_hass(self):
        """Register callbacks."""

        @callback
        def update_state(_device, attr, value):
            _LOGGER.debug('siren-callback:' + self._name + ':' + attr + ':' + str(value)[:80])
            self._state = value
            self.async_schedule_update_ha_state()

        _LOGGER.debug("register siren callbacks for {}".format(self._device.name))
        self._device.add_attr_callback(SIREN_STATE_KEY, update_state)

    def get_state(self):
        _LOGGER.debug("get state {} form".format(self._name))
        return self._state

    def do_on(self):
        _LOGGER.debug("turned siren {} on".format(self._name))
        self._device.siren_on(duration=self._on_for.total_seconds(), volume=self._volume)
        self._state = "on"

    def do_off(self):
        _LOGGER.debug("turned siren {} off".format(self._name))
        self._device.siren_off()
        self._state = "off"


class AarloAllSirensSwitch(AarloSirenBaseSwitch):
    """Representation of an Aarlo switch."""

    def __init__(self, config, arlo, devices):
        """Initialize the Aarlo siren switch device."""
        super().__init__("All Sirens", "all_sirens", "alarm-light", config.get(CONF_SIREN_DURATION),
                         config.get(CONF_SIREN_ALLOW_OFF))
        self._volume = config.get(CONF_SIREN_VOLUME)
        self._devices = devices
        self._device = arlo
        self._state = "off"

    async def async_added_to_hass(self):
        """Register callbacks."""

        @callback
        def update_state(_device, attr, value):
            _LOGGER.debug('all-siren-callback:' + self._name + ':' + attr + ':' + str(value)[:80])

            state = "off"
            for device in self._devices:
                if device.siren_state == "on":
                    state = "on"
            self._state = state

            self.async_schedule_update_ha_state()

        for device in self._devices:
            _LOGGER.debug("register all siren callbacks for {}".format(device.name))
            device.add_attr_callback(SIREN_STATE_KEY, update_state)

    def get_state(self):
        _LOGGER.debug("get state for {}".format(self._name))
        return self._state

    def do_on(self):
        for device in self._devices:
            _LOGGER.debug("turned sirens on {}".format(device.name))
            device.siren_on(duration=self._on_for.total_seconds(), volume=self._volume)
        self._state = "on"

    def do_off(self):
        for device in self._devices:
            _LOGGER.debug("turned sirens off {}".format(device.name))
            device.siren_off()
        self._state = "on"


class AarloSnapshotSwitch(AarloSwitch):
    """Representation of an Aarlo switch."""

    def __init__(self, config, camera):
        """Initialize the Aarlo snapshot switch device."""
        super().__init__("{0} Snapshot".format(camera.name), "snapshot_{}".format(camera.entity_id), "camera")
        self._device = camera
        self._timeout = config.get(CONF_SNAPSHOT_TIMEOUT)

    async def async_added_to_hass(self):
        """Register callbacks."""

        @callback
        def update_state(_device, attr, value):
            _LOGGER.debug('callback:' + self._name + ':' + attr + ':' + str(value)[:80])
            self.async_schedule_update_ha_state()

        self._device.add_attr_callback(ACTIVITY_STATE_KEY, update_state)

    @property
    def state(self):
        """Return the state of the switch."""
        if self._device.is_taking_snapshot:
            return "on"
        return "off"

    def turn_on(self, **kwargs):
        _LOGGER.debug("starting snapshot for {}".format(self._name))
        if not self._device.is_taking_snapshot:
            self._device.request_snapshot()

    def turn_off(self, **kwargs):
        _LOGGER.debug("cancelling snapshot for {}".format(self._name))
        if self._device.is_taking_snapshot:
            self._device.stop_activity()


class AarloSilentModeBaseSwitch(AarloSwitch):
    """Representation of an Aarlo switch."""

    def __init__(self, name, identifier, doorbell, block_call):
        """Initialize the Aarlo silent mode switch device."""
        super().__init__(name, identifier, "doorbell")
        self._doorbell = doorbell
        self._state = False
        self._block_call = block_call

    @property
    def state(self):
        """Return the state of the switch."""
        if self._state:
          return 'on'
        else:
          return 'off'

    def turn_on(self, **kwargs):
        _LOGGER.debug("Turning on silent mode for {}".format(self._name))
        self._doorbell.silent_mode(active=True, block_call=self._block_call)

    def turn_off(self, **kwargs):
        _LOGGER.debug("Turning off silent mode for {}".format(self._name))
        self._doorbell.silent_mode(active=False, block_call=self._block_call)

    async def async_added_to_hass(self):
        """Register callbacks."""

        @callback
        def update_state(_device, attr, value):
            active = value.get(SILENT_MODE_ACTIVE_KEY, None)
            block_call = value.get(SILENT_MODE_CALL_KEY, None)

            # If active isn't present -- we cannot assert any state.
            if active is None:
              return
            # If active is False, OR if this object doesn't block calls, then
            # simply mirror that state.
            elif not active or not self._block_call:
              self._state = active
            # If it falls through to here, then silent mode has moved to
            # active, and this object does block calls. If we do not have fresh
            # block_call information, we cannot assert any state.
            elif block_call is None:
              return
            # Silent mode is active, this object does block calls and there is
            # block_call information -- use that state.
            else:
              self._state = block_call

            self.async_schedule_update_ha_state()
        self._doorbell.add_attr_callback(SILENT_MODE_KEY, update_state)


class AarloSilentModeChimeSwitch(AarloSilentModeBaseSwitch):
    """Representation of an Aarlo switch to silence chimes."""

    def __init__(self, doorbell):
        """Initialize the Aarlo silent mode switch device."""
        super().__init__("{0} Silent Mode Chime".format( doorbell.name), 
            "{0} Silent Mode Chime".format(doorbell.entity_id),
            doorbell, block_call=False)


class AarloSilentModeChimeCallSwitch(AarloSilentModeBaseSwitch):
    """Representation of an Aarlo switch to silence chimes and calls"""

    def __init__(self, doorbell):
        """Initialize the Aarlo silent mode switch device."""
        super().__init__("{0} Silent Mode Chime Call".format(doorbell.name),
            "{0} Silent Mode Chime Call".format(doorbell.entity_id),
            doorbell, block_call=True)
