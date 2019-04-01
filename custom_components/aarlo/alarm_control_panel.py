"""
Support for Arlo Alarm Control Panels.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/alarm_control_panel.arlo/
"""
import logging
import voluptuous as vol
import time
from datetime import timedelta

import homeassistant.helpers.config_validation as cv
import homeassistant.util.dt as dt_util
from homeassistant.helpers.event import track_point_in_time
from homeassistant.core import callback
from homeassistant.components.alarm_control_panel import (
        AlarmControlPanel, PLATFORM_SCHEMA)
from custom_components.aarlo import (
        DATA_ARLO, CONF_ATTRIBUTION )
from homeassistant.const import (
        ATTR_ATTRIBUTION,
        CONF_TRIGGER_TIME,
        STATE_ALARM_ARMED_AWAY, STATE_ALARM_ARMED_HOME, STATE_ALARM_DISARMED, STATE_ALARM_ARMED_NIGHT, STATE_ALARM_TRIGGERED )

_LOGGER = logging.getLogger(__name__)

ARMED = 'armed'

CONF_HOME_MODE_NAME  = 'home_mode_name'
CONF_AWAY_MODE_NAME  = 'away_mode_name'
CONF_NIGHT_MODE_NAME = 'night_mode_name'
CONF_ALARM_VOLUME    = 'alarm_volume'

DEFAULT_TRIGGER_TIME = timedelta(seconds=60)
DISARMED = 'disarmed'
ALARM_VOLUME = '8'

DEPENDENCIES = ['aarlo']


ICON = 'mdi:security'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_HOME_MODE_NAME, default=ARMED): cv.string,
    vol.Optional(CONF_AWAY_MODE_NAME, default=ARMED): cv.string,
    vol.Optional(CONF_NIGHT_MODE_NAME, default=ARMED): cv.string,
    vol.Optional(CONF_ALARM_VOLUME, default=ALARM_VOLUME): cv.string,
    vol.Optional(CONF_TRIGGER_TIME, default=DEFAULT_TRIGGER_TIME): vol.All(cv.time_period, cv.positive_timedelta),
})


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Arlo Alarm Control Panels."""
    arlo = hass.data[DATA_ARLO]

    if not arlo.base_stations:
        return

    home_mode_name  = config.get(CONF_HOME_MODE_NAME)
    away_mode_name  = config.get(CONF_AWAY_MODE_NAME)
    night_mode_name = config.get(CONF_NIGHT_MODE_NAME)
    alarm_volume    = config.get(CONF_ALARM_VOLUME)
    trigger_time    = config.get(CONF_TRIGGER_TIME)
    base_stations   = []
    for base_station in arlo.base_stations:
        base_stations.append( ArloBaseStation( hass,base_station,home_mode_name,away_mode_name,night_mode_name,alarm_volume,trigger_time ))
 
    async_add_entities(base_stations, True)


class ArloBaseStation(AlarmControlPanel):
    """Representation of an Arlo Alarm Control Panel."""

    def __init__(self, hass,device, home_mode_name, away_mode_name,night_mode_name,alarm_volume,trigger_time ):
        """Initialize the alarm control panel."""
        self._hass            = hass
        self._name            = device.name
        self._unique_id       = self._name.lower().replace(' ','_')
        self._base            = device
        self._home_mode_name  = home_mode_name.lower()
        self._away_mode_name  = away_mode_name.lower()
        self._night_mode_name = night_mode_name.lower()
        self._alarm_volume    = alarm_volume
        self._trigger_time    = trigger_time
        self._trigger_till    = None
        self._state           = None
        _LOGGER.info( 'ArloBaseStation: %s created',self._name )

    @property
    def icon(self):
        """Return icon."""
        return ICON

    async def async_added_to_hass(self):
        """Register callbacks."""
        @callback
        def update_state( device,attr,value ):
            _LOGGER.debug( 'callback:' + attr + ':' + str(value))
            self._state = self._get_state_from_mode( self._base.attribute( 'activeMode' ) )
            self.async_schedule_update_ha_state()

        self._state = self._get_state_from_mode( self._base.attribute( 'activeMode' ) )
        self._base.add_attr_callback( 'activeMode',update_state )

    @property
    def state(self):
        """Return the state of the device."""
        if self._trigger_till is not None:
            if self._trigger_till > time.monotonic():
                return STATE_ALARM_TRIGGERED
            self._trigger_till = None
            self._base.siren_off()
        return self._state

    def alarm_disarm(self, code=None):
        self._base.mode = DISARMED

    def alarm_arm_away(self, code=None):
        self._base.mode = self._away_mode_name

    def alarm_arm_home(self, code=None):
        self._base.mode = self._home_mode_name

    async def async_alarm_arm_night(self, code=None):
        self._base.mode = self._night_mode_name

    def alarm_trigger(self, code=None):
        if self._trigger_till is None:
            _LOGGER.info( '%s: triggered',self._name )
            self._trigger_till = time.monotonic() + self._trigger_time.total_seconds()
            self._base.siren_on( duration=self._trigger_time.total_seconds(),volume=self._alarm_volume )
            self.async_schedule_update_ha_state()
            track_point_in_time( self._hass,self.async_update_ha_state, dt_util.utcnow() + self._trigger_time )

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attrs = {}

        attrs[ATTR_ATTRIBUTION] = CONF_ATTRIBUTION
        attrs['device_id']      = self._base.device_id
        attrs['friendly_name']  = self._name

        return attrs

    def _get_state_from_mode(self, mode):
        """Convert Arlo mode to Home Assistant state."""
        if mode == ARMED:
            return STATE_ALARM_ARMED_AWAY
        if mode == DISARMED:
            return STATE_ALARM_DISARMED
        if mode == self._home_mode_name:
            return STATE_ALARM_ARMED_HOME
        if mode == self._away_mode_name:
            return STATE_ALARM_ARMED_AWAY
        if mode == self._night_mode_name:
            return STATE_ALARM_ARMED_NIGHT
        return mode

