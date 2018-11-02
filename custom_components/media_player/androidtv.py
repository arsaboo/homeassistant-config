"""
Provide functionality to interact with AndroidTV devices on the network.

Example config:
media_player:
  - platform: androidtv
    host: 192.168.1.37
    name: MIBOX3 ANDROID TV


For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/media_player.androidtv/
"""

import functools
import logging
import os
import time
import voluptuous as vol

from homeassistant.components.media_player import (
    DOMAIN, SUPPORT_NEXT_TRACK, SUPPORT_PAUSE, SUPPORT_PREVIOUS_TRACK,
    PLATFORM_SCHEMA, SUPPORT_SELECT_SOURCE, SUPPORT_STOP, SUPPORT_TURN_OFF,
    SUPPORT_TURN_ON, SUPPORT_VOLUME_SET, SUPPORT_VOLUME_MUTE,
    SUPPORT_VOLUME_STEP, SUPPORT_PLAY, MediaPlayerDevice)

from homeassistant.const import (
    ATTR_ENTITY_ID, CONF_HOST, CONF_NAME, CONF_PORT, STATE_IDLE, STATE_PAUSED,
    STATE_PLAYING, STATE_OFF, STATE_STANDBY, STATE_UNKNOWN)
import homeassistant.helpers.config_validation as cv

REQUIREMENTS = ['androidtv==0.0.2']

_LOGGER = logging.getLogger(__name__)

SUPPORT_ANDROIDTV = (SUPPORT_NEXT_TRACK | SUPPORT_PAUSE |
                     SUPPORT_PLAY | SUPPORT_PREVIOUS_TRACK |
                     SUPPORT_TURN_OFF | SUPPORT_TURN_ON |
                     SUPPORT_VOLUME_MUTE | SUPPORT_VOLUME_STEP |
                     SUPPORT_VOLUME_SET | SUPPORT_STOP)

CONF_ADBKEY = 'adbkey'

DEFAULT_NAME = 'Android'
DEFAULT_PORT = '5555'
DEFAULT_ADBKEY = ''

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): vol.All(cv.port, cv.string),
    vol.Optional(CONF_ADBKEY, default=DEFAULT_ADBKEY): cv.string,
})

ACTIONS = {
    "back": "4",
    "blue": "186",
    "component1": "249",
    "component2": "250",
    "composite1": "247",
    "composite2": "248",
    "down": "20",
    "end": "123",
    "enter": "66",
    "green": "184",
    "hdmi1": "243",
    "hdmi2": "244",
    "hdmi3": "245",
    "hdmi4": "246",
    "home": "3",
    "input": "178",
    "left": "21",
    "menu": "82",
    "move_home": "122",
    "mute": "164",
    "pairing": "225",
    "power": "26",
    "resume": "224",
    "right": "22",
    "sat": "237",
    "search": "84",
    "settings": "176",
    "sleep": "223",
    "suspend": "276",
    "sysdown": "281",
    "sysleft": "282",
    "sysright": "283",
    "sysup": "280",
    "text": "233",
    "top": "122",
    "up": "19",
    "vga": "251",
    "voldown": "25",
    "volup": "24",
    "yellow": "185"
}

KNOWN_APPS = {
    "dream": "Screensaver",
    "kodi": "Kodi",
    "netflix": "Netflix",
    "plex": "Plex",
    "spotify": "Spotify",
    "tvlauncher": "Homescreen",
    "youtube": "Youtube"
}

ACTION_SERVICE = 'androidtv_action'
INTENT_SERVICE = 'androidtv_intent'
KEY_SERVICE = 'androidtv_key'

SERVICE_ACTION_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
    vol.Required('action'): vol.In(ACTIONS),
})

SERVICE_INTENT_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
    vol.Required('intent'): cv.string,
})

SERVICE_KEY_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
    vol.Required('key'): cv.string,
})

DATA_KEY = '{}.androidtv'.format(DOMAIN)


# pylint: disable=protected-access
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the AndroidTV platform."""
    host = '{0}:{1}'.format(config.get(CONF_HOST), config.get(CONF_PORT))
    name = config.get(CONF_NAME)
    adbkey = config.get(CONF_ADBKEY)

    device = AndroidTVDevice(host, name, adbkey)
    adb_log = " using adbkey='{0}'".format(adbkey) if adbkey else ""
    if not device._androidtv._adb:
        _LOGGER.warning("Could not connect to Android TV at %s%s",
                        host, adb_log)

        # Debugging
        if adbkey != "":
            # Check whether the key files exist
            if not os.path.exists(adbkey):
                raise FileNotFoundError(
                    "ADB private key {} does not exist".format(adbkey))
            if not os.path.exists(adbkey + ".pub"):
                raise FileNotFoundError(
                    "ADB public key {} does not exist".format(adbkey + '.pub'))

            # Check whether the key files can be read
            with open(adbkey):
                pass
            with open(adbkey + '.pub'):
                pass

    else:
        _LOGGER.info("Setup Android TV at %s%s", host, adb_log)
        add_devices([device])

    def service_action(service):
        """Dispatch service calls to target entities."""
        params = {key: value for key, value in service.data.items()
                  if key != ATTR_ENTITY_ID}

        entity_id = service.data.get(ATTR_ENTITY_ID)
        target_devices = [dev for dev in hass.data[DATA_KEY].values()
                          if dev.entity_id in entity_id]

        for target_device in target_devices:
            target_device.do_action(params['action'])

    def service_intent(service):
        """Dispatch service calls to target entities."""
        params = {key: value for key, value in service.data.items()
                  if key != ATTR_ENTITY_ID}

        entity_id = service.data.get(ATTR_ENTITY_ID)
        target_devices = [dev for dev in hass.data[DATA_KEY].values()
                          if dev.entity_id in entity_id]

        for target_device in target_devices:
            target_device.start_intent(params['intent'])

    def service_key(service):
        """Dispatch service calls to target entities."""
        params = {key: value for key, value in service.data.items()
                  if key != ATTR_ENTITY_ID}

        entity_id = service.data.get(ATTR_ENTITY_ID)
        target_devices = [dev for dev in hass.data[DATA_KEY].values()
                          if dev.entity_id in entity_id]

        for target_device in target_devices:
            target_device.input_key(params['key'])

    hass.services.register(
        DOMAIN, ACTION_SERVICE, service_action, schema=SERVICE_ACTION_SCHEMA)
    hass.services.register(
        DOMAIN, INTENT_SERVICE, service_intent, schema=SERVICE_INTENT_SCHEMA)
    hass.services.register(
        DOMAIN, KEY_SERVICE, service_key, schema=SERVICE_KEY_SCHEMA)


def adb_wrapper(func):
    """Wait if previous ADB commands haven't finished."""
    @functools.wraps(func)
    def _adb_wrapper(self, *args, **kwargs):
        attempts = 0
        while self._adb_lock and attempts < 5:
            attempts += 1
            time.sleep(1)

        if attempts == 5 and self._adb_lock:
            try:
                self._androidtv.connect()
            except self._exceptions:
                _LOGGER.error('Failed to re-establish the ADB connection; '
                              'will re-attempt in the next update.')
                self._androidtv._adb = None
                self._adb_lock = False
                return

        self._adb_lock = True
        try:
            returns = func(self, *args, **kwargs)
        except self._exceptions:
            returns = None
            _LOGGER.error('Failed to execute an ADB command; will attempt to '
                          're-establish the ADB connection in the next update')
            self._androidtv._adb = None
        finally:
            self._adb_lock = False

        return returns

    return _adb_wrapper


def get_app_name(app_id):
    """Return the app name from its id and known apps."""
    if not app_id:
        return

    for app in KNOWN_APPS:
        if app in app_id:
            return KNOWN_APPS[app]

    return


class AndroidTVDevice(MediaPlayerDevice):
    """Representation of an AndroidTv device."""

    def __init__(self, host, name, adbkey):
        """Initialize the AndroidTV device."""
        from androidtv import AndroidTV  # pylint: disable=no-name-in-module
        from adb.adb_protocol import (
            InvalidCommandError, InvalidResponseError, InvalidChecksumError)

        self._host = host
        self._adbkey = adbkey
        self._androidtv = AndroidTV(host, adbkey)
        self._adb_lock = False

        self._exceptions = (TypeError, ValueError, AttributeError,
                            InvalidCommandError, InvalidResponseError,
                            InvalidChecksumError)

        self._name = name
        self._state = STATE_UNKNOWN
        self._app_name = None
        # self._running_apps = None
        # self._current_app = None

    @adb_wrapper
    def update(self):
        """Get the latest details from the device."""
        self._androidtv.update()

        if self._androidtv.state == 'off':
            self._state = STATE_OFF
        elif self._androidtv.state == 'idle':
            self._state = STATE_IDLE
        elif self._androidtv.state == 'play':
            self._state = STATE_PLAYING
        elif self._androidtv.state == 'pause':
            self._state = STATE_PAUSED
        elif self._androidtv.state == 'standby':
            self._state = STATE_STANDBY
        elif self._androidtv.state == 'unknown':
            self._state = STATE_UNKNOWN

        self._app_name = get_app_name(self._androidtv.app_id)

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        return self._androidtv.state

    @property
    def is_volume_muted(self):
        """Boolean if volume is currently muted."""
        return self._androidtv.muted

    @property
    def volume_level(self):
        """Return the volume level."""
        return self._androidtv.volume

    # @property
    # def source(self):
    #     """Return the current playback device."""
    #     return self._device

    @property
    def app_id(self):
        """ID of the current running app."""
        return self._androidtv.app_id

    @property
    def app_name(self):
        """Name of the current running app."""
        return self._app_name

    # @property
    # def available(self):
    #     """Return True if entity is available."""
    #     return self._available

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return SUPPORT_ANDROIDTV

    def turn_on(self):
        """Instruct the tv to turn on."""
        self._androidtv.turn_on()

    def turn_off(self):
        """Instruct the tv to turn off."""
        self._androidtv.turn_off()

    def media_play(self):
        """Send play command."""
        self._androidtv.media_play()
        self._state = STATE_PLAYING

    def media_pause(self):
        """Send pause command."""
        self._androidtv.media_pause()
        self._state = STATE_PAUSED

    def media_play_pause(self):
        """Send play/pause command."""
        self._androidtv.media_play_pause()

    def media_stop(self):
        """Send stop command."""
        self._androidtv.media_stop()
        self._state = STATE_IDLE

    def mute_volume(self, mute):
        """Mute the volume."""
        self._androidtv.mute_volume()
        self._androidtv.muted = mute

    def volume_up(self):
        """Increment the volume level."""
        self._androidtv.volume_up()

    def volume_down(self):
        """Decrement the volume level."""
        self._androidtv.volume_down()

    def media_previous_track(self):
        """Send previous track command."""
        self._androidtv.media_previous()

    def media_next_track(self):
        """Send next track command."""
        self._androidtv.media_next()

    def input_key(self, key):
        """Input the key to the device."""
        self._androidtv._key(key)

    def start_intent(self, uri):
        """Start an intent on the device."""
        self._androidtv._adb.Shell(
            "am start -a android.intent.action.VIEW -d {}".format(uri))

    def do_action(self, action):
        """Input the key corresponding to the action."""
        self._androidtv._adb.Shell("input keyevent {}".format(ACTIONS[action]))
