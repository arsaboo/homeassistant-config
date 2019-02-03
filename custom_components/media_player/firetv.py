"""
Support for functionality to interact with FireTV devices.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/media_player.firetv/
"""
import functools
import logging
import threading
import voluptuous as vol

from homeassistant.components.media_player import (
    DOMAIN, MediaPlayerDevice, PLATFORM_SCHEMA, SUPPORT_NEXT_TRACK,
    SUPPORT_PAUSE, SUPPORT_PLAY, SUPPORT_PREVIOUS_TRACK, SUPPORT_SELECT_SOURCE,
    SUPPORT_STOP, SUPPORT_TURN_OFF, SUPPORT_TURN_ON)
from homeassistant.const import (
    ATTR_ENTITY_ID, CONF_HOST, CONF_NAME, CONF_PORT, STATE_IDLE, STATE_OFF,
    STATE_PAUSED, STATE_PLAYING, STATE_STANDBY)
import homeassistant.helpers.config_validation as cv

REQUIREMENTS = ['https://github.com/JeffLIrion/python-firetv/zipball/pure-python-adb#firetv==1.0.8']

_LOGGER = logging.getLogger(__name__)

SUPPORT_FIRETV = SUPPORT_PAUSE | SUPPORT_PLAY | \
    SUPPORT_TURN_ON | SUPPORT_TURN_OFF | SUPPORT_PREVIOUS_TRACK | \
    SUPPORT_NEXT_TRACK | SUPPORT_SELECT_SOURCE | SUPPORT_STOP

CONF_ADBKEY = 'adbkey'
CONF_ADB_SERVER_IP = 'adb_server_ip'
CONF_ADB_SERVER_PORT = 'adb_server_port'
CONF_GET_SOURCE = 'get_source'
CONF_GET_SOURCES = 'get_sources'
CONF_SET_STATES = 'set_states'

DEFAULT_NAME = 'Amazon Fire TV'
DEFAULT_PORT = 5555
DEFAULT_ADB_SERVER_PORT = 5037
DEFAULT_GET_SOURCE = True
DEFAULT_GET_SOURCES = True
DEFAULT_SET_STATES = True


def has_adb_files(value):
    """Check that ADB key files exist."""
    priv_key = value
    pub_key = '{}.pub'.format(value)
    cv.isfile(pub_key)
    return cv.isfile(priv_key)


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
    vol.Optional(CONF_ADBKEY): has_adb_files,
    vol.Optional(CONF_ADB_SERVER_IP): cv.string,
    vol.Optional(
        CONF_ADB_SERVER_PORT, default=DEFAULT_ADB_SERVER_PORT): cv.port,
    vol.Optional(CONF_GET_SOURCE, default=DEFAULT_GET_SOURCE): cv.boolean,
    vol.Optional(CONF_GET_SOURCES, default=DEFAULT_GET_SOURCES): cv.boolean,
    vol.Optional(CONF_SET_STATES, default=DEFAULT_SET_STATES): cv.boolean
})

SERVICE_ADB_SHELL = 'firetv_adb_shell'
SERVICE_ADB_STREAMING_SHELL = 'firetv_adb_streaming_shell'

SERVICE_ADB_SHELL_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
    vol.Required('cmd'): cv.string
})

SERVICE_ADB_STREAMING_SHELL_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
    vol.Required('cmd'): cv.string
})

DATA_FIRETV = 'firetv'

PACKAGE_LAUNCHER = "com.amazon.tv.launcher"
PACKAGE_SETTINGS = "com.amazon.tv.settings"


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the FireTV platform."""
    if DATA_FIRETV not in hass.data:
        hass.data[DATA_FIRETV] = dict()

    from firetv import FireTV

    host = '{0}:{1}'.format(config[CONF_HOST], config[CONF_PORT])

    if CONF_ADB_SERVER_IP not in config:
        # "python-adb"
        if CONF_ADBKEY in config:
            ftv = FireTV(host, config[CONF_ADBKEY])
            adb_log = " using adbkey='{0}'".format(config[CONF_ADBKEY])
        else:
            ftv = FireTV(host)
            adb_log = ""
    else:
        # "pure-python-adb"
        ftv = FireTV(host, adb_server_ip=config[CONF_ADB_SERVER_IP],
                     adb_server_port=config[CONF_ADB_SERVER_PORT])
        adb_log = " using ADB server at {0}:{1}".format(
            config[CONF_ADB_SERVER_IP], config[CONF_ADB_SERVER_PORT])

    if not ftv.available:
        _LOGGER.warning("Could not connect to Fire TV at %s%s", host, adb_log)
        return

    name = config[CONF_NAME]
    get_source = config[CONF_GET_SOURCE]
    get_sources = config[CONF_GET_SOURCES]
    set_states = config[CONF_SET_STATES]

    device = FireTVDevice(ftv, name, get_source, get_sources, set_states)
    add_entities([device])
    hass.data[DATA_FIRETV][host] = device
    _LOGGER.info("Setup Fire TV at %s%s", host, adb_log)

    if hass.services.has_service(DOMAIN, SERVICE_ADB_SHELL):
        return

    def service_adb_shell(service):
        """Run ADB shell commands and log the output."""
        params = {key: value for key, value in service.data.items()
                  if key != ATTR_ENTITY_ID}

        entity_id = service.data.get(ATTR_ENTITY_ID)
        target_devices = [dev for dev in hass.data[DATA_FIRETV].values()
                          if dev.entity_id in entity_id]

        for target_device in target_devices:
            cmd = params['cmd']
            output = target_device.firetv.adb_shell(cmd)
            _LOGGER.info("Output from command '%s' to %s: '%s'",
                         cmd, target_device.entity_id, repr(output))

    def service_adb_streaming_shell(service):
        """Run ADB streaming shell commands and log the output."""
        params = {key: value for key, value in service.data.items()
                  if key != ATTR_ENTITY_ID}

        entity_id = service.data.get(ATTR_ENTITY_ID)
        target_devices = [dev for dev in hass.data[DATA_FIRETV].values()
                          if dev.entity_id in entity_id]

        for target_device in target_devices:
            cmd = params['cmd']
            output = list(target_device.firetv.adb_streaming_shell(cmd))
            _LOGGER.info("Output from command '%s' to %s: '%s'",
                         cmd, target_device.entity_id, repr(output))

    hass.services.register(DOMAIN, SERVICE_ADB_SHELL, service_adb_shell,
                           schema=SERVICE_ADB_SHELL_SCHEMA)

    hass.services.register(DOMAIN, SERVICE_ADB_STREAMING_SHELL,
                           service_adb_streaming_shell,
                           schema=SERVICE_ADB_STREAMING_SHELL_SCHEMA)


def adb_decorator(override_available=False):
    """Send an ADB command if the device is available and catch exceptions."""
    def _adb_decorator(func):
        """Wait if previous ADB commands haven't finished."""
        @functools.wraps(func)
        def __adb_decorator(self, *args, **kwargs):
            # If the device is unavailable, don't do anything
            if not self.available and not override_available:
                return None

            try:
                return func(self, *args, **kwargs)
            except self.exceptions:
                _LOGGER.error('Failed to execute an ADB command; will attempt '
                              'to re-establish the ADB connection in the next '
                              'update')
                self._available = False  # pylint: disable=protected-access
                return None

        return __adb_decorator

    return _adb_decorator


class FireTVDevice(MediaPlayerDevice):
    """Representation of an Amazon Fire TV device on the network."""

    def __init__(self, ftv, name, get_source, get_sources, set_states):
        """Initialize the FireTV device."""
        self.firetv = ftv

        self._name = name
        self._get_source = get_source
        self._get_sources = get_sources
        self._set_states = set_states

        # whether or not the ADB connection is currently in use
        self.adb_lock = threading.Lock()

        # ADB exceptions to catch
        if not self.firetv.adb_server_ip:
            # "python-adb"
            from adb.adb_protocol import (InvalidChecksumError,
                                          InvalidCommandError,
                                          InvalidResponseError)
            from adb.usb_exceptions import TcpTimeoutException

            self.exceptions = (AttributeError, BrokenPipeError, TypeError,
                               ValueError, InvalidChecksumError,
                               InvalidCommandError, InvalidResponseError,
                               TcpTimeoutException)
        else:
            # "pure-python-adb"
            self.exceptions = (ConnectionResetError,)

        self._state = None
        self._available = self.firetv.available
        self._current_app = None
        self._running_apps = None

    @property
    def name(self):
        """Return the device name."""
        return self._name

    @property
    def should_poll(self):
        """Device should be polled."""
        return True

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return SUPPORT_FIRETV

    @property
    def state(self):
        """Return the state of the player."""
        return self._state

    @property
    def available(self):
        """Return whether or not the ADB connection is valid."""
        return self._available

    @property
    def source(self):
        """Return the current app."""
        return self._current_app

    @property
    def source_list(self):
        """Return a list of running apps."""
        return self._running_apps

    @adb_decorator(override_available=True)
    def update(self):
        """Get the latest date and update device state."""
        # Check if device is disconnected.
        if not self._available:
            self._running_apps = None
            self._current_app = None

            # Try to connect
            self._available = self.firetv.connect()

            # To be safe, wait until the next update to run ADB commands.
            return

        # If the ADB connection is not intact, don't update.
        if not self._available:
            return

        # The `screen_on`, `awake`, `wake_lock`, and `current_app` properties.
        screen_on, awake, wake_lock, current_app = self.firetv.get_properties()

        # Check if device is off.
        if not screen_on:
            self._state = STATE_OFF
            self._running_apps = None
            self._current_app = None

        # Check if screen saver is on.
        elif not awake:
            self._state = STATE_IDLE
            self._running_apps = None
            self._current_app = None

        else:
            # Get the current app.
            if isinstance(current_app, dict) and 'package' in current_app:
                self._current_app = current_app['package']
            else:
                self._current_app = current_app

            # Get the running apps.
            if self._get_sources:
                self._running_apps = self.firetv.running_apps
            elif self._current_app:
                self._running_apps = [self._current_app]
            else:
                self._running_apps = None

            # Check if the launcher is active.
            if self._current_app in [PACKAGE_LAUNCHER, PACKAGE_SETTINGS]:
                self._state = STATE_STANDBY

            # Check for a wake lock (device is playing).
            elif wake_lock:
                self._state = STATE_PLAYING

            # Otherwise, device is paused.
            else:
                self._state = STATE_PAUSED

    @adb_decorator()
    def turn_on(self):
        """Turn on the device."""
        self.firetv.turn_on()
        if self._set_states:
            self._state = STATE_IDLE

    @adb_decorator()
    def turn_off(self):
        """Turn off the device."""
        self.firetv.turn_off()
        if self._set_states:
            self._state = STATE_OFF

    @adb_decorator()
    def media_play(self):
        """Send play command."""
        self.firetv.media_play()

    @adb_decorator()
    def media_pause(self):
        """Send pause command."""
        self.firetv.media_pause()

    @adb_decorator()
    def media_play_pause(self):
        """Send play/pause command."""
        self.firetv.media_play_pause()

    @adb_decorator()
    def media_stop(self):
        """Send stop (back) command."""
        self.firetv.back()

    @adb_decorator()
    def volume_up(self):
        """Send volume up command."""
        self.firetv.volume_up()

    @adb_decorator()
    def volume_down(self):
        """Send volume down command."""
        self.firetv.volume_down()

    @adb_decorator()
    def media_previous_track(self):
        """Send previous track command (results in rewind)."""
        self.firetv.media_previous()

    @adb_decorator()
    def media_next_track(self):
        """Send next track command (results in fast-forward)."""
        self.firetv.media_next()

    @adb_decorator()
    def select_source(self, source):
        """Select input source.

        If the source starts with a '!', then it will close the app instead of
        opening it.
        """
        if isinstance(source, str):
            if not source.startswith('!'):
                self.firetv.launch_app(source)
                if self._set_states:
                    self._current_app = source
            else:
                self.firetv.stop_app(source[1:].lstrip())
                if self._set_states:
                    self._current_app = PACKAGE_LAUNCHER
                    self._state = STATE_STANDBY
