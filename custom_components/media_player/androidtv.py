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
import asyncio
import voluptuous as vol

from homeassistant.components.media_player import (
    DOMAIN, SUPPORT_NEXT_TRACK, SUPPORT_PAUSE, SUPPORT_PREVIOUS_TRACK,
    PLATFORM_SCHEMA, SUPPORT_SELECT_SOURCE, SUPPORT_STOP, SUPPORT_TURN_OFF,
    SUPPORT_TURN_ON, SUPPORT_VOLUME_SET, SUPPORT_VOLUME_MUTE,
    SUPPORT_VOLUME_STEP, SUPPORT_PLAY, SUPPORT_PLAY_MEDIA, MediaPlayerDevice)

from homeassistant.const import (
    ATTR_ENTITY_ID, CONF_HOST, CONF_NAME, CONF_PORT, STATE_IDLE, STATE_PAUSED,
    STATE_PLAYING, STATE_OFF, STATE_ON, STATE_STANDBY, STATE_UNKNOWN)
import homeassistant.helpers.config_validation as cv

REQUIREMENTS = ['androidtv==0.0.2']

_LOGGER = logging.getLogger(__name__)

SUPPORT_ANDROIDTV = (SUPPORT_NEXT_TRACK | SUPPORT_PAUSE |
                     SUPPORT_PLAY | SUPPORT_PREVIOUS_TRACK |
                     SUPPORT_TURN_OFF | SUPPORT_TURN_ON |
                     SUPPORT_VOLUME_MUTE | SUPPORT_VOLUME_STEP |
                     SUPPORT_VOLUME_SET | SUPPORT_STOP |
                     SUPPORT_PLAY_MEDIA)

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
    "adultswim": "Adult Swim",
    "android.videos": "Play Movies",
    "crackle": "Crackle",
    "crunchyroll": "Crunchyroll",
    "dream": "Screensaver",
    "fxnow": "FXNOW",
    "hulu": "Hulu",
    "kodi": "Kodi",
    "netflix": "Netflix",
    "plex": "Plex",
    "spotify": "Spotify",
    "tvlauncher": "Homescreen",
    "xfinity": "Xfinity Stream",
    "youtube": "Youtube"
}

SERVICE_ACTION = 'androidtv_action'
SERVICE_INTENT = 'androidtv_intent'
SERVICE_KEY = 'androidtv_key'

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

SERVICE_TO_METHOD = {
    SERVICE_ACTION: {
        'method': 'async_do_action',
        'schema': SERVICE_ACTION_SCHEMA},
    SERVICE_INTENT: {
        'method': 'async_start_intent',
        'schema': SERVICE_INTENT_SCHEMA},
    SERVICE_KEY: {
        'method': 'async_input_key',
        'schema': SERVICE_KEY_SCHEMA},
}

DATA_KEY = '{}.androidtv'.format(DOMAIN)


# pylint: disable=protected-access
async def async_setup_platform(hass, config, async_add_entities,
                               discovery_info=None):
    """Set up the AndroidTV platform."""
    if DATA_KEY not in hass.data:
        hass.data[DATA_KEY] = dict()
    host = '{0}:{1}'.format(config.get(CONF_HOST), config.get(CONF_PORT))
    name = config.get(CONF_NAME)
    adbkey = config.get(CONF_ADBKEY)

    device = AndroidTVDevice(hass, host, name, adbkey)
    await device._androidtv.connect()

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
        hass.data[DATA_KEY][config.get(CONF_HOST)] = device
        async_add_entities([device], update_before_add=True)

    async def async_service_handler(service):
        """Map services to methods on MediaPlayerDevice."""
        method = SERVICE_TO_METHOD.get(service.service)
        if not method:
            return

        params = {key: value for key, value in service.data.items()
                  if key != 'entity_id'}
        entity_ids = service.data.get('entity_id')
        if entity_ids:
            target_players = [player
                              for player in hass.data[DATA_KEY].values()
                              if player.entity_id in entity_ids]
        else:
            target_players = hass.data[DATA_KEY].values()

        update_tasks = []
        for player in target_players:
            await getattr(player, method['method'])(**params)

        for player in target_players:
            if player.should_poll:
                update_coro = player.async_update_ha_state(True)
                update_tasks.append(update_coro)

        if update_tasks:
            await asyncio.wait(update_tasks, loop=hass.loop)

    for service in SERVICE_TO_METHOD:
        schema = SERVICE_TO_METHOD[service]['schema']
        hass.services.async_register(
            DOMAIN, service, async_service_handler,
            schema=schema)


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

    def __init__(self, hass, host, name, adbkey):
        """Initialize the AndroidTV device."""
        from androidtv import AndroidTV  # pylint: disable=no-name-in-module

        self._hass = hass
        self._host = host
        self._adbkey = adbkey
        self._androidtv = AndroidTV(host, adbkey)

        self._name = name
        self._state = STATE_UNKNOWN
        self._app_name = None

    async def async_update(self):
        """Get the latest details from the device."""
        await self._androidtv.update()

        if self._androidtv.state == 'off':
            self._state = STATE_OFF
        elif self._androidtv.state == 'idle':
            self._state = STATE_IDLE
        elif self._androidtv.state == 'playing':
            self._state = STATE_PLAYING
        elif self._androidtv.state == 'paused':
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
    def should_poll(self):
        """Return True if entity has to be polled for state."""
        return not (self._androidtv is None or self._androidtv._adb is None)

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

    @property
    def app_id(self):
        """ID of the current running app."""
        return self._androidtv.app_id

    @property
    def app_name(self):
        """Name of the current running app."""
        return self._app_name

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return SUPPORT_ANDROIDTV

    async def async_turn_on(self):
        """Instruct the tv to turn on."""
        await self._androidtv.turn_on()

    async def async_turn_off(self):
        """Instruct the tv to turn off."""
        await self._androidtv.turn_off()

    async def async_media_play(self):
        """Send play command."""
        await self._androidtv.media_play()

    async def async_media_pause(self):
        """Send pause command."""
        await self._androidtv.media_pause()

    async def async_media_play_pause(self):
        """Send play/pause command."""
        await self._androidtv.media_play_pause()

    async def async_media_stop(self):
        """Send stop command."""
        await self._androidtv.media_stop()

    async def async_play_media(self, media_type, media_id, **kwargs):
        """Play media from a URL."""
        await self._androidtv.cast_media(media_id)

    async def async_mute_volume(self, mute):
        """Mute the volume."""
        await self._androidtv.mute_volume()
        self._androidtv.muted = mute

    async def async_volume_up(self):
        """Increment the volume level."""
        await self._androidtv.volume_up()

    async def async_volume_down(self):
        """Decrement the volume level."""
        await self._androidtv.volume_down()

    async def async_media_previous_track(self):
        """Send previous track command."""
        await self._androidtv.media_previous()

    async def async_media_next_track(self):
        """Send next track command."""
        await self._androidtv.media_next()

    async def async_input_key(self, key):
        """Input the key to the device."""
        await self._androidtv._key(key)

    async def async_start_intent(self, uri):
        """Start an intent on the device."""
        await self._androidtv.start_intent(uri)

    async def async_do_action(self, action):
        """Input the key corresponding to the action."""
        await self._androidtv._key(ACTIONS[action])
