"""
Support for Arlo Alarm Control Panels.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/alarm_control_panel.arlo/
"""
import logging
import re
import time
from datetime import timedelta

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
import homeassistant.util.dt as dt_util
from homeassistant.components import websocket_api
from homeassistant.components.alarm_control_panel import (DOMAIN,
                                                          AlarmControlPanelEntity,
                                                          FORMAT_NUMBER,
                                                          FORMAT_TEXT)
from homeassistant.components.alarm_control_panel.const import (
    SUPPORT_ALARM_ARM_HOME,
    SUPPORT_ALARM_ARM_AWAY,
    SUPPORT_ALARM_ARM_NIGHT,
    SUPPORT_ALARM_TRIGGER)
from homeassistant.const import (ATTR_ATTRIBUTION,
                                 ATTR_ENTITY_ID,
                                 CONF_CODE,
                                 CONF_TRIGGER_TIME,
                                 STATE_ALARM_ARMED_AWAY,
                                 STATE_ALARM_ARMED_HOME,
                                 STATE_ALARM_ARMED_NIGHT,
                                 STATE_ALARM_DISARMED,
                                 STATE_ALARM_TRIGGERED)
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.config_validation import (PLATFORM_SCHEMA)
from homeassistant.helpers.event import track_point_in_time
from . import COMPONENT_ATTRIBUTION, COMPONENT_DATA, COMPONENT_BRAND, COMPONENT_DOMAIN, COMPONENT_SERVICES, \
    get_entity_from_domain
from .pyaarlo.constant import (MODE_KEY,
                               SIREN_STATE_KEY)

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = [COMPONENT_DOMAIN]

ARMED = 'armed'
DISARMED = 'disarmed'
ICON = 'mdi:security'

CONF_CODE_ARM_REQUIRED = "code_arm_required"
CONF_CODE_DISARM_REQUIRED = "code_disarm_required"
CONF_HOME_MODE_NAME = 'home_mode_name'
CONF_AWAY_MODE_NAME = 'away_mode_name'
CONF_NIGHT_MODE_NAME = 'night_mode_name'
CONF_ALARM_VOLUME = 'alarm_volume'
CONF_COMMAND_TEMPLATE = "command_template"

DEFAULT_COMMAND_TEMPLATE = "{{action}}"
DEFAULT_TRIGGER_TIME = timedelta(seconds=60)
DEFAULT_HOME = 'home'
DEFAULT_NIGHT = 'night'
DEFAULT_ALARM_VOLUME = '8'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_CODE): cv.string,
    vol.Optional(CONF_CODE_ARM_REQUIRED, default=True): cv.boolean,
    vol.Optional(CONF_CODE_DISARM_REQUIRED, default=True): cv.boolean,
    vol.Optional(
        CONF_COMMAND_TEMPLATE, default=DEFAULT_COMMAND_TEMPLATE
    ): cv.template,
    vol.Optional(CONF_HOME_MODE_NAME, default=DEFAULT_HOME): cv.string,
    vol.Optional(CONF_AWAY_MODE_NAME, default=ARMED): cv.string,
    vol.Optional(CONF_NIGHT_MODE_NAME, default=DEFAULT_NIGHT): cv.string,
    vol.Optional(CONF_ALARM_VOLUME, default=DEFAULT_ALARM_VOLUME): cv.string,
    vol.Optional(CONF_TRIGGER_TIME, default=DEFAULT_TRIGGER_TIME): vol.All(cv.time_period, cv.positive_timedelta),
})

ATTR_MODE = 'mode'
ATTR_VOLUME = 'volume'
ATTR_DURATION = 'duration'
ATTR_TIME_ZONE = 'time_zone'

SERVICE_MODE = 'alarm_set_mode'
OLD_SERVICE_MODE = 'aarlo_set_mode'
OLD_SERVICE_SIREN_ON = 'aarlo_siren_on'
OLD_SERVICE_SIREN_OFF = 'aarlo_siren_off'
SERVICE_MODE_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.comp_entity_ids,
    vol.Required(ATTR_MODE): cv.string,
})
SERVICE_SIREN_ON_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.comp_entity_ids,
    vol.Required(ATTR_DURATION): cv.positive_int,
    vol.Required(ATTR_VOLUME): cv.positive_int,
})
SERVICE_SIREN_OFF_SCHEMA = vol.Schema({
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
    arlo = hass.data[COMPONENT_DATA]
    if not arlo.base_stations:
        return

    base_stations = []
    base_stations_with_sirens = False
    for base_station in arlo.base_stations:
        base_stations.append(ArloBaseStation(base_station, config))
        if base_station.has_capability(SIREN_STATE_KEY):
            base_stations_with_sirens = True

    async_add_entities(base_stations, True)

    # Component Services
    async def async_alarm_service(call):
        """Call aarlo service handler."""
        _LOGGER.info("{} service called".format(call.service))
        if call.service == SERVICE_MODE:
            await async_alarm_mode_service(hass, call)

    if not hasattr(hass.data[COMPONENT_SERVICES], DOMAIN):
        _LOGGER.info("installing handlers")
        hass.data[COMPONENT_SERVICES][DOMAIN] = 'installed'

        hass.services.async_register(
            COMPONENT_DOMAIN, SERVICE_MODE, async_alarm_service, schema=SERVICE_MODE_SCHEMA,
        )

    # Deprecated Services.
    if not arlo.cfg.hide_deprecated_services:
        component = hass.data[DOMAIN]
        component.async_register_entity_service(
            OLD_SERVICE_MODE, SERVICE_MODE_SCHEMA,
            aarlo_mode_service_handler
        )
        if base_stations_with_sirens:
            component.async_register_entity_service(
                OLD_SERVICE_SIREN_ON, SERVICE_SIREN_ON_SCHEMA,
                aarlo_siren_on_service_handler
            )
            component.async_register_entity_service(
                OLD_SERVICE_SIREN_OFF, SERVICE_SIREN_OFF_SCHEMA,
                aarlo_siren_off_service_handler
            )

    # Websockets.
    if base_stations_with_sirens:
        hass.components.websocket_api.async_register_command(
            WS_TYPE_SIREN_ON, websocket_siren_on,
            SCHEMA_WS_SIREN_ON
        )
        hass.components.websocket_api.async_register_command(
            WS_TYPE_SIREN_OFF, websocket_siren_off,
            SCHEMA_WS_SIREN_OFF
        )


class ArloBaseStation(AlarmControlPanelEntity):
    """Representation of an Arlo Alarm Control Panel."""

    def __init__(self, device, config):
        """Initialize the alarm control panel."""
        self._config = config
        self._name = device.name
        self._unique_id = device.entity_id
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
            _LOGGER.debug('callback:' + self._name + ':' + attr + ':' + str(value))
            self._state = self._get_state_from_ha(self._base.attribute(MODE_KEY))
            self.async_schedule_update_ha_state()

        self._state = self._get_state_from_ha(self._base.attribute(MODE_KEY, ARMED))
        self._base.add_attr_callback(MODE_KEY, update_state)

    @property
    def state(self):
        """Return the state of the device."""
        if self._trigger_till is not None:
            if self._trigger_till > time.monotonic():
                return STATE_ALARM_TRIGGERED
            self.alarm_clear()
        return self._state

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        return SUPPORT_ALARM_ARM_HOME | SUPPORT_ALARM_ARM_AWAY | SUPPORT_ALARM_ARM_NIGHT | SUPPORT_ALARM_TRIGGER

    @property
    def code_format(self):
        """Return one or more digits/characters."""
        code = self._config.get(CONF_CODE)
        if code is None:
            return None
        if isinstance(code, str) and re.search("^\\d+$", code):
            return FORMAT_NUMBER
        return FORMAT_TEXT

    @property
    def code_arm_required(self):
        """Whether the code is required for arm actions."""
        code_required = self._config.get(CONF_CODE_ARM_REQUIRED)
        return code_required

    def alarm_disarm(self, code=None):
        code_required = self._config[CONF_CODE_DISARM_REQUIRED]
        if code_required and not self._validate_code(code, "disarming"):
            return
        self.set_mode_in_ha(DISARMED)

    def alarm_arm_away(self, code=None):
        code_required = self._config[CONF_CODE_ARM_REQUIRED]
        if code_required and not self._validate_code(code, "arming away"):
            return
        self.set_mode_in_ha(self._away_mode_name)

    def alarm_arm_home(self, code=None):
        code_required = self._config[CONF_CODE_ARM_REQUIRED]
        if code_required and not self._validate_code(code, "arming home"):
            return
        self.set_mode_in_ha(self._home_mode_name)

    def alarm_arm_night(self, code=None):
        code_required = self._config[CONF_CODE_ARM_REQUIRED]
        if code_required and not self._validate_code(code, "arming night"):
            return
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

    def restart(self):
        self._base.restart()

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return {
            ATTR_ATTRIBUTION: COMPONENT_ATTRIBUTION,
            ATTR_TIME_ZONE: self._base.timezone,
            'brand': COMPONENT_BRAND,
            'device_id': self._base.device_id,
            'model_id': self._base.model_id,
            'friendly_name': self._name,
            'on_schedule': self._base.on_schedule,
            'siren': self._base.has_capability(SIREN_STATE_KEY)
        }

    def _get_state_from_ha(self, mode):
        """Convert Arlo mode to Home Assistant state."""
        lmode = mode.lower()
        if lmode == DISARMED:
            return STATE_ALARM_DISARMED
        if lmode == self._away_mode_name:
            return STATE_ALARM_ARMED_AWAY
        if lmode == self._home_mode_name:
            return STATE_ALARM_ARMED_HOME
        if lmode == self._night_mode_name:
            return STATE_ALARM_ARMED_NIGHT
        if lmode == ARMED:
            return STATE_ALARM_ARMED_AWAY
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
        if self._base.has_capability(SIREN_STATE_KEY):
            _LOGGER.debug("{0} siren on {1}/{2}".format(self.unique_id, volume, duration))
            self._base.siren_on(duration=duration, volume=volume)
            return True
        return False

    def siren_off(self):
        if self._base.has_capability(SIREN_STATE_KEY):
            _LOGGER.debug("{0} siren off".format(self.unique_id))
            self._base.siren_off()
            return True
        return False

    async def async_siren_on(self, duration, volume):
        return await self.hass.async_add_executor_job(self.siren_on, duration, volume)

    async def async_siren_off(self):
        return await self.hass.async_add_executor_job(self.siren_off)

    def _validate_code(self, code, state):
        """Validate given code."""
        conf_code = self._config.get(CONF_CODE)
        check = conf_code is None or code == conf_code
        if not check:
            _LOGGER.warning("Wrong code entered for %s", state)
        return check


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

    await base.async_siren_on(duration=msg['duration'], volume=msg['volume'])
    connection.send_message(websocket_api.result_message(
        msg['id'], {
            'siren': 'on'
        }
    ))


@websocket_api.async_response
async def websocket_siren_off(hass, connection, msg):
    base = _get_base_from_entity_id(hass, msg['entity_id'])
    _LOGGER.debug('stop_activity for ' + str(base.unique_id))

    await base.async_siren_off()
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


async def async_alarm_mode_service(hass, call):
    for entity_id in call.data['entity_id']:
        try:
            mode = call.data['mode']
            get_entity_from_domain(hass, DOMAIN, entity_id).set_mode_in_ha(mode)
            _LOGGER.info("{0} setting mode to {1}".format(entity_id, mode))
        except HomeAssistantError:
            _LOGGER.warning("{0} is not an aarlo alarm device".format(entity_id))


async def async_alarm_siren_on_service(hass, call):
    for entity_id in call.data['entity_id']:
        try:
            volume = call.data['volume']
            duration = call.data['duration']
            get_entity_from_domain(hass, DOMAIN, entity_id).siren_on(duration=duration, volume=volume)
            _LOGGER.info("{0} siren on {1}/{2}".format(entity_id, volume, duration))
        except HomeAssistantError:
            _LOGGER.warning("{0} is not an aarlo alarm device".format(entity_id))


async def async_alarm_siren_off_service(hass, call):
    for entity_id in call.data['entity_id']:
        try:
            get_entity_from_domain(hass, DOMAIN, entity_id).siren_off()
            _LOGGER.info("{0} siren off".format(entity_id))
        except HomeAssistantError:
            _LOGGER.warning("{0} is not an aarlo alarm device".format(entity_id))
