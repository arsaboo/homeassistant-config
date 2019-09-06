"""
Support for Arlo Alarm Control Panels.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/alarm_control_panel.arlo/
"""
import logging
import time
from datetime import timedelta

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
import homeassistant.util.dt as dt_util
from homeassistant.components import websocket_api
from homeassistant.components.alarm_control_panel import (DOMAIN,
                                                          AlarmControlPanel)
from homeassistant.const import (ATTR_ATTRIBUTION,
                                 ATTR_ENTITY_ID,
                                 CONF_TRIGGER_TIME,
                                 STATE_ALARM_ARMED_AWAY,
                                 STATE_ALARM_ARMED_HOME,
                                 STATE_ALARM_ARMED_NIGHT,
                                 STATE_ALARM_DISARMED,
                                 STATE_ALARM_TRIGGERED)
from homeassistant.core import callback
from homeassistant.helpers.config_validation import (PLATFORM_SCHEMA)
from homeassistant.helpers.event import track_point_in_time
from . import CONF_ATTRIBUTION, DATA_ARLO, DEFAULT_BRAND

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['aarlo']
ARMED = 'armed'
DISARMED = 'disarmed'
ICON = 'mdi:security'

CONF_HOME_MODE_NAME = 'home_mode_name'
CONF_AWAY_MODE_NAME = 'away_mode_name'
CONF_NIGHT_MODE_NAME = 'night_mode_name'
CONF_ALARM_VOLUME = 'alarm_volume'

DEFAULT_TRIGGER_TIME = timedelta(seconds=60)
ALARM_VOLUME = '8'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_HOME_MODE_NAME, default=ARMED): cv.string,
    vol.Optional(CONF_AWAY_MODE_NAME, default=ARMED): cv.string,
    vol.Optional(CONF_NIGHT_MODE_NAME, default=ARMED): cv.string,
    vol.Optional(CONF_ALARM_VOLUME, default=ALARM_VOLUME): cv.string,
    vol.Optional(CONF_TRIGGER_TIME, default=DEFAULT_TRIGGER_TIME): vol.All(cv.time_period, cv.positive_timedelta),
})

ATTR_MODE = 'mode'
ATTR_VOLUME = 'volume'
ATTR_DURATION = 'duration'

SERVICE_MODE = 'aarlo_set_mode'
SERVICE_SIREN_ON = 'aarlo_siren_on'
SERVICE_SIREN_OFF = 'aarlo_siren_off'
SERVICE_MODE_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.comp_entity_ids,
    vol.Required(ATTR_MODE): cv.string,
})
SIREN_ON_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.comp_entity_ids,
    vol.Required(ATTR_DURATION): cv.positive_int,
    vol.Required(ATTR_VOLUME): cv.positive_int,
})
SIREN_OFF_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.comp_entity_ids,
})

WS_TYPE_SIREN_ON = 'aarlo_alarm_siren_on'
WS_TYPE_SIREN_OFF = 'aarlo_alarm_siren_off'
SCHEMA_WS_SIREN_ON = websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend({
    vol.Required('type'): WS_TYPE_SIREN_ON,
    vol.Required('entity_id'): cv.entity_id,
    vol.Required(ATTR_DURATION): cv.positive_int,
    vol.Required(ATTR_VOLUME): cv.positive_int
})
SCHEMA_WS_SIREN_OFF = websocket_api.BASE_COMMAND_MESSAGE_SCHEMA.extend({
    vol.Required('type'): WS_TYPE_SIREN_OFF,
    vol.Required('entity_id'): cv.entity_id
})

async def async_setup_platform(hass, config, async_add_entities, _discovery_info=None):
    """Set up the Arlo Alarm Control Panels."""
    arlo = hass.data[DATA_ARLO]
    component = hass.data[DOMAIN]

    if not arlo.base_stations:
        return

    base_stations = []
    for base_station in arlo.base_stations:
        base_stations.append(ArloBaseStation(base_station, config))

    async_add_entities(base_stations, True)

    component.async_register_entity_service(
        SERVICE_MODE, SERVICE_MODE_SCHEMA,
        aarlo_mode_service_handler
    )
    component.async_register_entity_service(
        SERVICE_SIREN_ON, SIREN_ON_SCHEMA,
        aarlo_siren_on_service_handler
    )
    component.async_register_entity_service(
        SERVICE_SIREN_OFF, SIREN_OFF_SCHEMA,
        aarlo_siren_off_service_handler
    )
    hass.components.websocket_api.async_register_command(
        WS_TYPE_SIREN_ON, websocket_siren_on,
        SCHEMA_WS_SIREN_ON
    )
    hass.components.websocket_api.async_register_command(
        WS_TYPE_SIREN_OFF, websocket_siren_off,
        SCHEMA_WS_SIREN_OFF
    )


class ArloBaseStation(AlarmControlPanel):
    """Representation of an Arlo Alarm Control Panel."""

    def __init__(self, device, config):
        """Initialize the alarm control panel."""
        self._name = device.name
        self._unique_id = self._name.lower().replace(' ', '_')
        self._base = device
        self._home_mode_name = config.get(CONF_HOME_MODE_NAME).lower()
        self._away_mode_name = config.get(CONF_AWAY_MODE_NAME).lower()
        self._night_mode_name = config.get(CONF_NIGHT_MODE_NAME).lower()
        self._alarm_volume = config.get(CONF_ALARM_VOLUME)
        self._trigger_time = config.get(CONF_TRIGGER_TIME)
        self._trigger_till = None
        self._state = None
        _LOGGER.info('ArloBaseStation: %s created', self._name)

    @property
    def icon(self):
        """Return icon."""
        return ICON

    async def async_added_to_hass(self):
        """Register callbacks."""

        @callback
        def update_state(_device, attr, value):
            _LOGGER.debug('callback:' + attr + ':' + str(value))
            self._state = self._get_state_from_ha(self._base.attribute('activeMode'))
            self.async_schedule_update_ha_state()

        self._state = self._get_state_from_ha(self._base.attribute('activeMode', ARMED))
        self._base.add_attr_callback('activeMode', update_state)

    @property
    def state(self):
        """Return the state of the device."""
        if self._trigger_till is not None:
            if self._trigger_till > time.monotonic():
                return STATE_ALARM_TRIGGERED
            self.alarm_clear()
        return self._state

    def alarm_disarm(self, code=None):
        self.set_mode_in_ha(DISARMED)

    def alarm_arm_away(self, code=None):
        self.set_mode_in_ha(self._away_mode_name)

    def alarm_arm_home(self, code=None):
        self.set_mode_in_ha(self._home_mode_name)

    def alarm_arm_night(self, code=None):
        self.set_mode_in_ha(self._night_mode_name)

    def alarm_trigger(self, code=None):
        if self._trigger_till is None:
            _LOGGER.info('%s: triggered', self._name)
            self._trigger_till = time.monotonic() + self._trigger_time.total_seconds()
            if int(self._alarm_volume) != 0:
                self._base.siren_on(duration=self._trigger_time.total_seconds(), volume=self._alarm_volume)
            self.async_schedule_update_ha_state()
            track_point_in_time(self.hass, self.async_update_ha_state, dt_util.utcnow() + self._trigger_time)

    def alarm_clear(self):
        self._trigger_till = None
        self._base.siren_off()

    def alarm_arm_custom_bypass(self, code=None):
        pass

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attrs = {}

        attrs[ATTR_ATTRIBUTION] = CONF_ATTRIBUTION
        attrs['brand'] = DEFAULT_BRAND
        attrs['device_id'] = self._base.device_id
        attrs['friendly_name'] = self._name
        attrs['on_schedule'] = self._base.on_schedule

        return attrs

    def _get_state_from_ha(self, mode):
        """Convert Arlo mode to Home Assistant state."""
        lmode = mode.lower()
        if lmode == ARMED:
            return STATE_ALARM_ARMED_AWAY
        if lmode == DISARMED:
            return STATE_ALARM_DISARMED
        if lmode == self._home_mode_name:
            return STATE_ALARM_ARMED_HOME
        if lmode == self._away_mode_name:
            return STATE_ALARM_ARMED_AWAY
        if lmode == self._night_mode_name:
            return STATE_ALARM_ARMED_NIGHT
        return mode

    def set_mode_in_ha(self, mode):
        """ convert Home Assistant state to Arlo mode."""
        lmode = mode.lower()
        if lmode == DISARMED:
            if self._trigger_till is not None:
                _LOGGER.debug("{0} disarming/silencing".format(self._name))
                self.alarm_clear()
        _LOGGER.debug("{0} set mode to {1}".format(self._name, lmode))
        self._base.mode = lmode

    def siren_on(self, duration=30, volume=10):
        if self._base.has_capability( 'siren' ):
            _LOGGER.debug("{0} siren on {1}/{2}".format(self.unique_id, volume, duration))
            self._base.siren_on(duration=duration, volume=volume)
            return True
        return False

    def siren_off(self):
        if self._base.has_capability( 'siren' ):
            _LOGGER.debug("{0} siren off".format(self.unique_id))
            self._base.siren_off()
            return True
        return False

    def async_siren_on(self,duration,volume):
        return self.hass.async_add_job(self.siren_on,duration=duration,volume=volume)

    def async_siren_off(self):
        return self.hass.async_add_job(self.siren_off)


def _get_base_from_entity_id(hass, entity_id):
    component = hass.data.get(DOMAIN)
    if component is None:
        raise HomeAssistantError('base component not set up')

    base = component.get_entity(entity_id)
    if base is None:
        raise HomeAssistantError('base not found')

    return base


@websocket_api.async_response
async def websocket_siren_on(hass, connection, msg):
    base = _get_base_from_entity_id(hass, msg['entity_id'])
    _LOGGER.debug('stop_activity for ' + str(base.unique_id))

    siren = await base.async_siren_on(duration=msg['duration'],volume=msg['volume'])
    connection.send_message(websocket_api.result_message(
        msg['id'], {
            'siren': 'on'
        }
    ))


@websocket_api.async_response
async def websocket_siren_off(hass, connection, msg):
    base = _get_base_from_entity_id(hass, msg['entity_id'])
    _LOGGER.debug('stop_activity for ' + str(base.unique_id))

    siren = await base.async_siren_off()
    connection.send_message(websocket_api.result_message(
        msg['id'], {
            'siren': 'off'
        }
    ))


async def aarlo_mode_service_handler(base, service):
    mode = service.data[ATTR_MODE]
    base.set_mode_in_ha(mode)


async def aarlo_siren_on_service_handler(base, service):
    volume = service.data[ATTR_VOLUME]
    duration = service.data[ATTR_DURATION]
    base.siren_on(duration=duration, volume=volume)


async def aarlo_siren_off_service_handler(base, _service):
    base.siren_off()

