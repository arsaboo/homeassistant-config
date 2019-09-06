"""
This component provides support for a Aarlo switches.

"""

import logging
import time
from datetime import timedelta

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
import homeassistant.util.dt as dt_util
from homeassistant.components.switch import SwitchDevice
from homeassistant.helpers.config_validation import (PLATFORM_SCHEMA)
from homeassistant.helpers.event import track_point_in_time
from . import DATA_ARLO

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['aarlo']

SIRENS_DEFAULT = False
SIREN_DURATION_DEFAULT = timedelta(seconds=30)
SIREN_VOLUME_DEFAULT = "5"
SIREN_ALLOW_OFF_DEFAULT = True
ALL_SIRENS_DEFAULT = False
SNAPSHOTS_DEFAULT = False
SNAPSHOT_TIMEOUT_DEFAULT = timedelta(seconds=30)

CONF_SIRENS = "siren"
CONF_ALL_SIRENS = "all_sirens"
CONF_SIREN_DURATION = "siren_duration"
CONF_SIREN_VOLUME = "siren_volume"
CONF_SIREN_ALLOW_OFF = "siren_allow_off"
CONF_SNAPSHOT = "snapshot"
CONF_SNAPSHOT_TIMEOUT = "snapshot_timeout"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_SIRENS, default=SIRENS_DEFAULT): cv.boolean,
    vol.Optional(CONF_ALL_SIRENS, default=ALL_SIRENS_DEFAULT): cv.boolean,
    vol.Optional(CONF_SIREN_DURATION, default=SIREN_DURATION_DEFAULT): vol.All(cv.time_period, cv.positive_timedelta),
    vol.Optional(CONF_SIREN_VOLUME, default=SIREN_VOLUME_DEFAULT): cv.string,
    vol.Optional(CONF_SIREN_ALLOW_OFF, default=SIREN_ALLOW_OFF_DEFAULT): cv.boolean,
    vol.Optional(CONF_SNAPSHOT, default=SNAPSHOTS_DEFAULT): cv.boolean,
    vol.Optional(CONF_SNAPSHOT_TIMEOUT, default=SNAPSHOT_TIMEOUT_DEFAULT): vol.All(cv.time_period,
                                                                                   cv.positive_timedelta),
})


async def async_setup_platform(hass, config, async_add_entities, _discovery_info=None):
    arlo = hass.data.get(DATA_ARLO)
    if not arlo:
        return

    switches = []

    if config.get(CONF_SIRENS) is True:
        for base in arlo.base_stations:
            if base.has_capability('siren'):
                switches.append(AarloSirenSwitch(config, base))
        for camera in arlo.cameras:
            if camera.has_capability('siren'):
                switches.append(AarloSirenSwitch(config, camera))

    if config.get(CONF_SNAPSHOT) is True:
        for camera in arlo.cameras:
            switches.append(AarloSnapshotSwitch(config, camera))

    if config.get(CONF_ALL_SIRENS) is True:
        switches.append(AarloSingleSirenSwitch(config))

    async_add_entities(switches, True)


class AarloSwitch(SwitchDevice):
    """Representation of a Aarlo switch."""

    def __init__(self, name, icon):
        """Initialize the Aarlo switch device."""
        self._name = name
        self._unique_id = self._name.lower().replace(' ', '_')
        self._icon = "mdi:{}".format(icon)
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


class AarloMomentarySwitch(AarloSwitch):
    """Representation of a Aarlo Momentary switch."""

    def __init__(self, name, icon, on_for, allow_off):
        """Initialize the Aarlo Momentary switch device."""
        super().__init__(name, icon)
        self._on_for = on_for
        self._allow_off = allow_off
        self._on_until = None
        _LOGGER.debug("on={}, allow={}".format(on_for, allow_off))

    @property
    def state(self):
        """Return the state of the switch."""
        if self._on_until is not None:
            if self._on_until > time.monotonic():
                return "on"
            _LOGGER.debug('turned off')
            self.do_off()
            self._on_until = None
        return "off"

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

    def do_on(self):
        _LOGGER.debug("implement do on")

    def do_off(self):
        _LOGGER.debug("implement do off")


class AarloSirenSwitch(AarloMomentarySwitch):
    """Representation of a Aarlo switch."""

    def __init__(self, config, base):
        """Initialize the Aarlo siren switch device."""
        super().__init__("{0} Siren".format(base.name), "alarm-bell", config.get(CONF_SIREN_DURATION),
                         config.get(CONF_SIREN_ALLOW_OFF))
        self._base = base
        self._volume = config.get(CONF_SIREN_VOLUME)
        _LOGGER.debug("{0}".format(str(config)))

    def do_on(self):
        _LOGGER.debug("turned siren {} on".format(self._name))
        self._base.siren_on(duration=self._on_for.total_seconds(), volume=self._volume)

    def do_off(self):
        _LOGGER.debug("turned siren {} off".format(self._name))
        self._base.siren_off()


class AarloSingleSirenSwitch(AarloMomentarySwitch):
    """Representation of a Aarlo switch."""

    def __init__(self, config):
        """Initialize the Aarlo siren switch device."""
        super().__init__("All Sirens", "alarm-light", config.get(CONF_SIREN_DURATION), config.get(CONF_SIREN_ALLOW_OFF))
        self._volume = config.get(CONF_SIREN_VOLUME)

    def do_on(self):
        arlo = self.hass.data.get(DATA_ARLO)
        if arlo:
            _LOGGER.debug("turned all sirens on")
            for base in arlo.base_stations:
                if base.has_capability('siren'):
                    _LOGGER.debug("turned sirens on {}".format(base.name))
                    base.siren_on(duration=self._on_for.total_seconds(), volume=self._volume)
            for camera in arlo.cameras:
                if camera.has_capability('siren'):
                    camera.siren_on(duration=self._on_for.total_seconds(), volume=self._volume)

    def do_off(self):
        arlo = self.hass.data.get(DATA_ARLO)
        if arlo:
            _LOGGER.debug("turned all sirens off")
            for base in arlo.base_stations:
                if base.has_capability('siren'):
                    _LOGGER.debug("turned sirens off {}".format(base.name))
                    base.siren_off()
            for camera in arlo.cameras:
                if camera.has_capability('siren'):
                    camera.siren_off()


class AarloSnapshotSwitch(AarloSwitch):
    """Representation of a Aarlo switch."""

    def __init__(self, config, camera):
        """Initialize the Aarlo snapshot switch device."""
        super().__init__("{0} Snapshot".format(camera.name), "camera")
        self._timeout = config.get(CONF_SNAPSHOT_TIMEOUT)
