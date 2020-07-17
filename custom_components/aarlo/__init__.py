"""
This component provides support for Netgear Arlo IP cameras.

For more details about this component, please refer to the documentation at
https://home-assistant.io/components/arlo/
"""
import os.path
import logging
import json
import pprint
from datetime import timedelta
from traceback import extract_stack

import voluptuous as vol
from requests.exceptions import HTTPError, ConnectTimeout

from homeassistant.const import (
    ATTR_ENTITY_ID,
    CONF_USERNAME, CONF_PASSWORD, CONF_SCAN_INTERVAL, CONF_HOST)
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.components.camera import DOMAIN as CAMERA_DOMAIN
from homeassistant.components.alarm_control_panel import DOMAIN as ALARM_DOMAIN
from .pyaarlo.constant import SIREN_STATE_KEY, DEFAULT_HOST, DEFAULT_AUTH_HOST

__version__ = '0.7.0.alpha.5'

_LOGGER = logging.getLogger(__name__)


COMPONENT_DOMAIN = 'aarlo'
COMPONENT_DATA = 'aarlo-data'
COMPONENT_SERVICES = 'aarlo-services'
COMPONENT_ATTRIBUTION = "Data provided by my.arlo.com"
COMPONENT_BRAND = 'Netgear Arlo'

NOTIFICATION_ID = 'aarlo_notification'
NOTIFICATION_TITLE = 'aarlo Component Setup'

CONF_PACKET_DUMP = 'packet_dump'
CONF_CACHE_VIDEOS = 'cache_videos'
CONF_DB_MOTION_TIME = 'db_motion_time'
CONF_DB_DING_TIME = 'db_ding_time'
CONF_RECENT_TIME = 'recent_time'
CONF_LAST_FORMAT = 'last_format'
CONF_CONF_DIR = 'conf_dir'
CONF_REQ_TIMEOUT = 'request_timeout'
CONF_STR_TIMEOUT = 'stream_timeout'
CONF_NO_MEDIA_UP = 'no_media_upload'
CONF_MEDIA_RETRY = 'media_retry'
CONF_USER_AGENT = 'user_agent'
CONF_MODE_API = 'mode_api'
CONF_DEVICE_REFRESH = 'refresh_devices_every'
CONF_HTTP_CONNECTIONS = 'http_connections'
CONF_HTTP_MAX_SIZE = 'http_max_size'
CONF_RECONNECT_EVERY = 'reconnect_every'
CONF_VERBOSE_DEBUG = 'verbose_debug'
CONF_HIDE_DEPRECATED_SERVICES = 'hide_deprecated_services'
CONF_INJECTION_SERVICE = 'injection_service'
CONF_SNAPSHOT_TIMEOUT = 'snapshot_timeout'
CONF_TFA_SOURCE = 'tfa_source'
CONF_TFA_TYPE = 'tfa_type'
CONF_TFA_HOST = 'tfa_host'
CONF_TFA_USERNAME = 'tfa_username'
CONF_TFA_PASSWORD = 'tfa_password'
CONF_LIBRARY_DAYS = 'library_days'
CONF_AUTH_HOST = 'auth_host'

SCAN_INTERVAL = timedelta(seconds=60)
PACKET_DUMP = False
CACHE_VIDEOS = False
DB_MOTION_TIME = timedelta(seconds=30)
DB_DING_TIME = timedelta(seconds=10)
RECENT_TIME = timedelta(minutes=10)
LAST_FORMAT = '%m-%d %H:%M'
CONF_DIR = ''
REQ_TIMEOUT = timedelta(seconds=60)
STR_TIMEOUT = timedelta(seconds=0)
NO_MEDIA_UP = False
MEDIA_RETRY = None
USER_AGENT = 'apple'
MODE_API = 'auto'
DEVICE_REFRESH = 0
HTTP_CONNECTIONS = 5
HTTP_MAX_SIZE = 10
RECONNECT_EVERY = 0
VERBOSE_DEBUG = False
HIDE_DEPRECATED_SERVICES = False
DEFAULT_INJECTION_SERVICE = False
SNAPSHOT_TIMEOUT = timedelta(seconds=45)
DEFAULT_TFA_SOURCE = 'imap'
DEFAULT_TFA_TYPE = 'email'
DEFAULT_TFA_HOST = 'unknown.imap.com'
DEFAULT_TFA_USERNAME = 'unknown@unknown.com'
DEFAULT_TFA_PASSWORD = 'unknown'
DEFAULT_LIBRARY_DAYS = 30

CONFIG_SCHEMA = vol.Schema({
    COMPONENT_DOMAIN: vol.Schema({
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_HOST, default=DEFAULT_HOST): cv.url,
        vol.Optional(CONF_AUTH_HOST, default=DEFAULT_AUTH_HOST): cv.url,
        vol.Optional(CONF_SCAN_INTERVAL, default=SCAN_INTERVAL): cv.time_period,
        vol.Optional(CONF_PACKET_DUMP, default=PACKET_DUMP): cv.boolean,
        vol.Optional(CONF_CACHE_VIDEOS, default=CACHE_VIDEOS): cv.boolean,
        vol.Optional(CONF_DB_MOTION_TIME, default=DB_MOTION_TIME): cv.time_period,
        vol.Optional(CONF_DB_DING_TIME, default=DB_DING_TIME): cv.time_period,
        vol.Optional(CONF_RECENT_TIME, default=RECENT_TIME): cv.time_period,
        vol.Optional(CONF_LAST_FORMAT, default=LAST_FORMAT): cv.string,
        vol.Optional(CONF_CONF_DIR, default=CONF_DIR): cv.string,
        vol.Optional(CONF_REQ_TIMEOUT, default=REQ_TIMEOUT): cv.time_period,
        vol.Optional(CONF_STR_TIMEOUT, default=STR_TIMEOUT): cv.time_period,
        vol.Optional(CONF_NO_MEDIA_UP, default=NO_MEDIA_UP): cv.boolean,
        vol.Optional(CONF_MEDIA_RETRY, default=list()): vol.All(cv.ensure_list,[cv.positive_int]),
        vol.Optional(CONF_USER_AGENT, default=USER_AGENT): cv.string,
        vol.Optional(CONF_MODE_API, default=MODE_API): cv.string,
        vol.Optional(CONF_DEVICE_REFRESH, default=DEVICE_REFRESH): cv.positive_int,
        vol.Optional(CONF_HTTP_CONNECTIONS, default=HTTP_CONNECTIONS): cv.positive_int,
        vol.Optional(CONF_HTTP_MAX_SIZE, default=HTTP_MAX_SIZE): cv.positive_int,
        vol.Optional(CONF_RECONNECT_EVERY, default=RECONNECT_EVERY): cv.positive_int,
        vol.Optional(CONF_VERBOSE_DEBUG, default=VERBOSE_DEBUG): cv.boolean,
        vol.Optional(CONF_HIDE_DEPRECATED_SERVICES, default=HIDE_DEPRECATED_SERVICES): cv.boolean,
        vol.Optional(CONF_INJECTION_SERVICE, default=DEFAULT_INJECTION_SERVICE): cv.boolean,
        vol.Optional(CONF_SNAPSHOT_TIMEOUT, default=SNAPSHOT_TIMEOUT): cv.time_period,
        vol.Optional(CONF_TFA_SOURCE, default=DEFAULT_TFA_SOURCE): cv.string,
        vol.Optional(CONF_TFA_TYPE, default=DEFAULT_TFA_TYPE): cv.string,
        vol.Optional(CONF_TFA_HOST, default=DEFAULT_TFA_HOST): cv.string,
        vol.Optional(CONF_TFA_USERNAME, default=DEFAULT_TFA_USERNAME): cv.string,
        vol.Optional(CONF_TFA_PASSWORD, default=DEFAULT_TFA_PASSWORD): cv.string,
        vol.Optional(CONF_LIBRARY_DAYS, default=DEFAULT_LIBRARY_DAYS): cv.positive_int,
    }),
}, extra=vol.ALLOW_EXTRA)

ATTR_VOLUME = 'volume'
ATTR_DURATION = 'duration'

SERVICE_SIREN_ON = 'siren_on'
SERVICE_SIRENS_ON = 'sirens_on'
SERVICE_SIREN_OFF = 'siren_off'
SERVICE_SIRENS_OFF = 'sirens_off'
SERVICE_INJECT_RESPONSE = 'inject_response'
SIREN_ON_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.comp_entity_ids,
    vol.Required(ATTR_DURATION): cv.positive_int,
    vol.Required(ATTR_VOLUME): cv.positive_int,
})
SIRENS_ON_SCHEMA = vol.Schema({
    vol.Required(ATTR_DURATION): cv.positive_int,
    vol.Required(ATTR_VOLUME): cv.positive_int,
})
SIREN_OFF_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.comp_entity_ids,
})
SIRENS_OFF_SCHEMA = vol.Schema({
})
INJECT_RESPONSE_SCHEMA = vol.Schema({
    vol.Required('filename'): cv.string,
})


def setup(hass, config):
    """Set up an Arlo component."""

    # Read config
    conf = config[COMPONENT_DOMAIN]
    username = conf.get(CONF_USERNAME)
    password = conf.get(CONF_PASSWORD)
    host = conf.get(CONF_HOST)
    auth_host = conf.get(CONF_AUTH_HOST)
    packet_dump = conf.get(CONF_PACKET_DUMP)
    cache_videos = conf.get(CONF_CACHE_VIDEOS)
    motion_time = conf.get(CONF_DB_MOTION_TIME).total_seconds()
    ding_time = conf.get(CONF_DB_DING_TIME).total_seconds()
    recent_time = conf.get(CONF_RECENT_TIME).total_seconds()
    last_format = conf.get(CONF_LAST_FORMAT)
    conf_dir = conf.get(CONF_CONF_DIR)
    req_timeout = conf.get(CONF_REQ_TIMEOUT).total_seconds()
    str_timeout = conf.get(CONF_STR_TIMEOUT).total_seconds()
    no_media_up = conf.get(CONF_NO_MEDIA_UP)
    media_retry = conf.get(CONF_MEDIA_RETRY)
    user_agent = conf.get(CONF_USER_AGENT)
    mode_api = conf.get(CONF_MODE_API)
    device_refresh = conf.get(CONF_DEVICE_REFRESH)
    http_connections = conf.get(CONF_HTTP_CONNECTIONS)
    http_max_size = conf.get(CONF_HTTP_MAX_SIZE)
    reconnect_every = conf.get(CONF_RECONNECT_EVERY)
    verbose_debug = conf.get(CONF_VERBOSE_DEBUG)
    hide_deprecated_services = conf.get(CONF_HIDE_DEPRECATED_SERVICES)
    injection_service = conf.get(CONF_INJECTION_SERVICE)
    snapshot_timeout = conf.get(CONF_SNAPSHOT_TIMEOUT).total_seconds()
    tfa_source = conf.get(CONF_TFA_SOURCE)
    tfa_type = conf.get(CONF_TFA_TYPE)
    tfa_host = conf.get(CONF_TFA_HOST)
    tfa_username = conf.get(CONF_TFA_USERNAME)
    tfa_password = conf.get(CONF_TFA_PASSWORD)
    library_days = conf.get(CONF_LIBRARY_DAYS)

    _LOGGER.info("retry={}".format(pprint.pformat(media_retry)))

    # Fix up config
    if conf_dir == '':
        conf_dir = hass.config.config_dir + '/.aarlo'

    # Fix up streaming...
    patch_file = hass.config.config_dir + '/aarlo.patch'
    if os.path.isfile(patch_file):
        _LOGGER.error("/usr/bin/patch -p0 -N < '{}'".format(patch_file))
        os.system("/usr/bin/patch -p0 -N < '{}'".format(patch_file))

    try:
        from .pyaarlo import PyArlo

        arlo = PyArlo(username=username, password=password,
                      cache_videos=cache_videos,
                      storage_dir=conf_dir,
                      dump=packet_dump,
                      host=host,
                      auth_host=auth_host,
                      db_motion_time=motion_time, db_ding_time=ding_time,
                      request_timeout=req_timeout, stream_timeout=str_timeout,
                      recent_time=recent_time,
                      last_format=last_format,
                      no_media_upload=no_media_up, media_retry=media_retry,
                      user_agent=user_agent,
                      mode_api=mode_api,
                      refresh_devices_every=device_refresh,
                      reconnect_every=reconnect_every,
                      http_connections=http_connections, http_max_size=http_max_size,
                      hide_deprecated_services=hide_deprecated_services,
                      snapshot_timeout=snapshot_timeout,
                      tfa_source=tfa_source, tfa_type=tfa_type,
                      tfa_host=tfa_host, tfa_username=tfa_username, tfa_password=tfa_password,
                      library_days=library_days,
                      wait_for_initial_setup=False,
                      verbose_debug=verbose_debug)
        if not arlo.is_connected:
            _LOGGER.error("Unable to connect to Arlo: %s", arlo.last_error)
            hass.components.persistent_notification.create(
                'Error: {}<br />You will need to restart hass after fixing.'.format(arlo.last_error),
                title=NOTIFICATION_TITLE,
                notification_id=NOTIFICATION_ID)
            return False

        hass.data[COMPONENT_DATA] = arlo
        hass.data[COMPONENT_SERVICES] = {}

    except (ConnectTimeout, HTTPError) as ex:
        _LOGGER.error("Unable to connect to Netgear Arlo: %s", str(ex))
        hass.components.persistent_notification.create(
            'Error: {}<br />You will need to restart hass after fixing.'.format(ex),
            title=NOTIFICATION_TITLE,
            notification_id=NOTIFICATION_ID)
        return False

    # Component Services
    has_sirens = False
    for device in arlo.cameras + arlo.base_stations:
        if device.has_capability(SIREN_STATE_KEY):
            has_sirens = True

    async def async_aarlo_service(call):
        """Call aarlo service handler."""
        _LOGGER.info("{} service called".format(call.service))
        if has_sirens:
            if call.service == SERVICE_SIREN_ON:
                await async_aarlo_siren_on(hass, call)
            if call.service == SERVICE_SIRENS_ON:
                await async_aarlo_sirens_on(hass, call)
            if call.service == SERVICE_SIREN_OFF:
                await async_aarlo_siren_off(hass, call)
            if call.service == SERVICE_SIRENS_OFF:
                await async_aarlo_sirens_off(hass, call)
        if call.service == SERVICE_INJECT_RESPONSE:
            await async_aarlo_inject_response(hass, call)

    hass.services.async_register(
        COMPONENT_DOMAIN, SERVICE_SIREN_ON, async_aarlo_service, schema=SIREN_ON_SCHEMA,
    )
    hass.services.async_register(
        COMPONENT_DOMAIN, SERVICE_SIRENS_ON, async_aarlo_service, schema=SIRENS_ON_SCHEMA,
    )
    hass.services.async_register(
        COMPONENT_DOMAIN, SERVICE_SIREN_OFF, async_aarlo_service, schema=SIREN_OFF_SCHEMA,
    )
    hass.services.async_register(
        COMPONENT_DOMAIN, SERVICE_SIRENS_OFF, async_aarlo_service, schema=SIRENS_OFF_SCHEMA,
    )
    if injection_service:
        hass.services.async_register(
            COMPONENT_DOMAIN, SERVICE_INJECT_RESPONSE, async_aarlo_service, schema=INJECT_RESPONSE_SCHEMA,
        )

    return True

def is_homekit():
    for frame in reversed(extract_stack()):
        try:
            frame.filename.index("homeassistant/components/homekit")
            _LOGGER.debug("homekit detected")
            return True
        except ValueError:
            continue
    _LOGGER.debug("not homekit detected")
    return False


def get_entity_from_domain(hass, domains, entity_id):
    domains = domains if isinstance(domains, list) else [domains]
    for domain in domains:
        component = hass.data.get(domain)
        if component is None:
            raise HomeAssistantError("{} component not set up".format(domain))
        entity = component.get_entity(entity_id)
        if entity is not None:
            return entity
    raise HomeAssistantError("{} not found in {}".format(entity_id, ",".join(domains)))


async def async_aarlo_siren_on(hass, call):
    for entity_id in call.data['entity_id']:
        try:
            volume = call.data['volume']
            duration = call.data['duration']
            device = get_entity_from_domain(hass, [ALARM_DOMAIN, CAMERA_DOMAIN], entity_id)
            device.siren_on(duration=duration, volume=volume)
            _LOGGER.info("{} siren on {}/{}".format(entity_id, volume, duration))
        except HomeAssistantError:
            _LOGGER.info("{} siren device not found".format(entity_id))


async def async_aarlo_sirens_on(hass, call):
    arlo = hass.data[COMPONENT_DATA]
    volume = call.data['volume']
    duration = call.data['duration']
    for device in arlo.cameras + arlo.base_stations:
        if device.has_capability(SIREN_STATE_KEY):
            device.siren_on(duration=duration, volume=volume)
            _LOGGER.info("{} siren on {}/{}".format(device.unique_id, volume, duration))


async def async_aarlo_siren_off(hass, call):
    for entity_id in call.data['entity_id']:
        try:
            device = get_entity_from_domain(hass, [ALARM_DOMAIN, CAMERA_DOMAIN], entity_id)
            device.siren_off()
            _LOGGER.info("{} siren off".format(entity_id))
        except HomeAssistantError:
            _LOGGER.info("{} siren not found".format(entity_id))


async def async_aarlo_sirens_off(hass, _call):
    arlo = hass.data[COMPONENT_DATA]
    for device in arlo.cameras + arlo.base_stations:
        if device.has_capability(SIREN_STATE_KEY):
            device.siren_off()
            _LOGGER.info("{} siren off".format(device.unique_id))


async def async_aarlo_inject_response(hass, call):
    patch_file = hass.config.config_dir + '/' + call.data['filename']
    with open(patch_file) as file:
        packet = json.load(file)

    if packet is not None:
        _LOGGER.debug("injecting->{}".format(pprint.pformat(packet)))
        hass.data[COMPONENT_DATA].inject_response(packet)
