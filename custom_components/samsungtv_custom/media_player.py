import asyncio
import homeassistant.helpers.config_validation as cv
from homeassistant import util
import logging
from datetime import timedelta
import voluptuous as vol
import os
import threading

from homeassistant.const import (
    CONF_HOST, CONF_NAME, CONF_PORT, CONF_TIMEOUT, CONF_PASSWORD, CONF_MAC, STATE_ON, STATE_OFF,
    STATE_PLAYING)
from homeassistant.components.media_player import (
    MediaPlayerDevice, PLATFORM_SCHEMA)
from homeassistant.util import dt as dt_util
from homeassistant.components.media_player.const import (
    MEDIA_TYPE_CHANNEL, SUPPORT_NEXT_TRACK, SUPPORT_PAUSE,
    SUPPORT_PLAY, SUPPORT_PLAY_MEDIA, SUPPORT_PREVIOUS_TRACK, SUPPORT_TURN_OFF,
    SUPPORT_TURN_ON, SUPPORT_VOLUME_MUTE, SUPPORT_VOLUME_STEP)

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = 'Samsung TV Remote'
DEFAULT_PORT = 8002
DEFAULT_TIMEOUT = 1
DEFAULT_PASSWORD = ''
DEFAULT_MAC = ''
MIN_TIME_BETWEEN_SCANS = timedelta(seconds=10)
MIN_TIME_BETWEEN_FORCED_SCANS = timedelta(seconds=1)

SUPPORT_SAMSUNGTV = SUPPORT_PAUSE | SUPPORT_VOLUME_STEP | \
    SUPPORT_VOLUME_MUTE | SUPPORT_PREVIOUS_TRACK | \
    SUPPORT_NEXT_TRACK | SUPPORT_TURN_OFF | SUPPORT_PLAY | SUPPORT_PLAY_MEDIA | \
    SUPPORT_TURN_ON

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
    vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): cv.positive_int,
    vol.Optional(CONF_PASSWORD, default=DEFAULT_PASSWORD): cv.string,
    vol.Optional(CONF_MAC, default=DEFAULT_MAC): cv.string,
})


def check_state(host):
  return os.system("ping -c 1 " + host + " > /dev/null 2>&1")

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the media player platform."""
    host = config[CONF_HOST]
    name = config[CONF_NAME]
    port = config[CONF_PORT]
    timeout = config[CONF_TIMEOUT]
    token = config[CONF_PASSWORD]
    mac = config[CONF_MAC]
    add_devices([SamsungTVCustomMediaPlayer(
        host, name, port, timeout, token, mac)])

class SamsungTVCustomMediaPlayer(MediaPlayerDevice):
    """Representation of a Media Player."""

    def __init__(self, host, name, port, timeout, token, mac):
        from samsungtv import SamsungTV
        import wakeonlan
        # Save a reference to the imported classes
        response = check_state(host)
        """Initialize the media player."""
        self._remote_class = SamsungTV
        self._remote = None
        self._state = STATE_OFF if response else STATE_ON
        self._host = host
        self._name = name
        self._port = port
        self._timeout = timeout
        self._token = token
        self._mac = mac
        self._end_of_power_off = None
        self._wol = wakeonlan
        self._playing = True

    @util.Throttle(MIN_TIME_BETWEEN_SCANS, MIN_TIME_BETWEEN_FORCED_SCANS)
    def update(self):
        """Retrieve the latest data."""
        from websockets.exceptions import ConnectionClosed
        try:
            response = check_state(self._host)
            self._state = STATE_OFF if response else STATE_ON

        except (OSError, ConnectionClosed, TypeError,
                asyncio.TimeoutError):
            self._state = STATE_OFF
            _LOGGER.info("SamsungTV off by error")

    def get_remote(self):
        """Create or return a remote control instance."""
        if self._remote is None:
            # We need to create a new instance to reconnect.
            self._remote = self._remote_class(self._host, self._token)

        return self._remote

    def _power_off_in_progress(self):
        return self._end_of_power_off is not None and \
            self._end_of_power_off > dt_util.utcnow()

    def send_key(self, key):
        """Send a key to the tv and handles exceptions."""
        if self._power_off_in_progress():
            if key not in ('KEY_POWER', 'KEY_POWEROFF'):
                _LOGGER.info(
                    "TV is powering off, not sending command: %s", key)
            else:
              self.get_remote().send_key(key)
              self._state = STATE_OFF
        return
        try:
            # recreate connection if connection was dead
            retry_count = 1
            for _ in range(retry_count + 1):
                try:
                    self.get_remote().send_key(key)
                    break
                except:
                    self._remote = None
            self._state = STATE_ON
        except (OSError, ConnectionClosed, TypeError,
                asyncio.TimeoutError):
            self._state = STATE_OFF
            self._remote = None
        self._state = STATE_ON

    def media_play(self):
        """Send play command."""
        self._playing = True
        self.send_key('KEY_PLAY')

    def media_pause(self):
        """Send media pause command to media player."""
        self._playing = False
        self.send_key('KEY_PAUSE')

    def turn_on(self):
        _LOGGER.info("Turning on")
        if self._mac:
            _LOGGER.info("Sending magic packet")
            self._wol.send_magic_packet(self._mac)
            self._state = STATE_ON
        else:
            self.send_key('KEY_POWER')

    def turn_off(self):
        """Turn off media player."""
        _LOGGER.info("Turning off")
        self._end_of_power_off = dt_util.utcnow() + timedelta(seconds=1)
        self.send_key('KEY_POWER')

    def volume_up(self):
        """Volume up the media player."""
        self.send_key('KEY_VOLUP')

    def volume_down(self):
        """Volume down media player."""
        self.send_key('KEY_VOLDOWN')

    def mute_volume(self, mute):
        """Send mute command."""
        self.send_key('KEY_MUTE')

    def media_play_pause(self):
        """Simulate play pause media player."""
        if self._playing:
            self.media_pause()
        else:
            self.media_play()

    async def async_play_media(self, media_type, media_id, **kwargs):
        """Support changing a channel."""
        if media_type != MEDIA_TYPE_CHANNEL:
            _LOGGER.error('Unsupported media type')
            return

        # media_id should only be a channel number
        try:
            cv.positive_int(media_id)
        except vol.Invalid:
            _LOGGER.error('Media ID must be positive integer')
            return

        for digit in media_id:
            await self.hass.async_add_job(self.send_key, 'KEY_' + digit)
            await asyncio.sleep(KEY_PRESS_TIMEOUT, self.hass.loop)

    @property
    def name(self):
        """Return the name of the media player."""
        return self._name

    @property
    def state(self):
        """Return the state of the media player."""
        return self._state

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return SUPPORT_SAMSUNGTV
