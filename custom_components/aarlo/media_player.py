"""Provide functionality to interact with vlc devices on the network."""
import logging

from homeassistant.components.media_player import DEVICE_CLASS_SPEAKER, MediaPlayerDevice
from homeassistant.components.media_player.const import (MEDIA_TYPE_MUSIC,
                                                         SUPPORT_PAUSE,
                                                         SUPPORT_PLAY,
                                                         SUPPORT_PLAY_MEDIA,
                                                         SUPPORT_PREVIOUS_TRACK,
                                                         SUPPORT_NEXT_TRACK,
                                                         SUPPORT_SHUFFLE_SET,
                                                         SUPPORT_VOLUME_MUTE,
                                                         SUPPORT_VOLUME_SET)
from homeassistant.const import (ATTR_ATTRIBUTION,
                                 STATE_IDLE,
                                 STATE_PAUSED,
                                 STATE_PLAYING)
from homeassistant.core import callback
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    STATE_IDLE,
    STATE_PAUSED,
    STATE_PLAYING
)
import homeassistant.helpers.config_validation as cv
from . import COMPONENT_ATTRIBUTION, COMPONENT_DATA, COMPONENT_BRAND
from .pyaarlo.constant import MEDIA_PLAYER_KEY

_LOGGER = logging.getLogger(__name__)

SUPPORT_ARLO = (
        SUPPORT_PAUSE
        | SUPPORT_PLAY_MEDIA
        | SUPPORT_PLAY
        | SUPPORT_PREVIOUS_TRACK
        | SUPPORT_NEXT_TRACK
        | SUPPORT_SHUFFLE_SET
        | SUPPORT_VOLUME_MUTE
        | SUPPORT_VOLUME_SET

)

""" Unsupported features:

    SUPPORT_CLEAR_PLAYLIST
    SUPPORT_SEEK
    SUPPORT_SELECT_SOUND_MODE
    SUPPORT_SELECT_SOURCE
    SUPPORT_STOP
    SUPPORT_TURN_OFF
    SUPPORT_TURN_ON
    SUPPORT_VOLUME_STEP
"""


async def async_setup_platform(hass, config, async_add_entities, _discovery_info=None):
    """Set up an Arlo media player."""
    arlo = hass.data.get(COMPONENT_DATA)
    if not arlo:
        return

    players = []
    for camera in arlo.cameras:
        if camera.has_capability(MEDIA_PLAYER_KEY):
            name = '{0}'.format(camera.name)
            players.append(ArloMediaPlayerDevice(name, camera))

    async_add_entities(players, True)


class ArloMediaPlayerDevice(MediaPlayerDevice):
    """Representation of an arlo media player."""

    def __init__(self, name, device):
        """Initialize an Arlo media player."""
        self._name = name
        self._unique_id = self._name.lower().replace(' ', '_')

        self._device = device
        self._name = name
        self._volume = None
        self._muted = None
        self._state = None
        self._shuffle = None
        self._position = 0
        self._track_id = None
        self._playlist = []

        _LOGGER.info('ArloMediaPlayerDevice: %s created', self._name)

    async def async_added_to_hass(self):
        """Register callbacks."""

        @callback
        def update_state(_device, attr, props):
            _LOGGER.info('callback:' + self._name + ':' + attr + ':' + str(props)[:80])
            if attr == "status":
                status = props.get('status')
                if status == 'playing':
                    self._state = STATE_PLAYING
                elif status == 'paused':
                    self._state = STATE_PAUSED
                else:
                    _LOGGER.debug('Unknown status:' + status)
                    self._state = STATE_IDLE
                self._position = props.get('position', 0)
                self._track_id = props.get('trackId', None)
            elif attr == "speaker":
                vol = props.get('volume')
                if vol is not None:
                    self._volume = vol / 100
                self._muted = props.get('mute', self._muted)
            elif attr == "config":
                config = props.get('config', {})
                self._shuffle = config.get('shuffleActive', self._shuffle)
            elif attr == "playlist":
                self._playlist = props

            self.async_schedule_update_ha_state()

        self._device.add_attr_callback("config", update_state)
        self._device.add_attr_callback("speaker", update_state)
        self._device.add_attr_callback("status", update_state)
        self._device.add_attr_callback("playlist", update_state)
        self._device.get_audio_playback_status()

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def volume_level(self):
        """Volume level of the media player (0..1)."""
        return self._volume

    @property
    def is_volume_muted(self):
        """Boolean if volume is currently muted."""
        return self._muted

    @property
    def media_title(self):
        """Title of current playing media."""
        if self._track_id is not None and self._playlist:
            for track in self._playlist:
                if track.get("id") == self._track_id:
                    return track.get("title")
        return None

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return SUPPORT_ARLO

    @property
    def media_content_type(self):
        """Content type of current playing media."""
        return MEDIA_TYPE_MUSIC

    @property
    def device_class(self):
        """Return the device class of the media player."""
        return DEVICE_CLASS_SPEAKER

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return "mdi:speaker"

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        attrs = {}

        attrs[ATTR_ATTRIBUTION] = COMPONENT_ATTRIBUTION
        attrs['brand'] = COMPONENT_BRAND
        attrs['friendly_name'] = self._name

        return attrs

    @property
    def shuffle(self):
        """Boolean if shuffle is enabled."""
        return self._shuffle

    def set_shuffle(self, shuffle):
        """Enable/disable shuffle mode."""
        self._device.set_shuffle(shuffle=shuffle)
        self._shuffle = shuffle

    def media_previous_track(self):
        """Send next track command."""
        self._device.previous_track()

    def media_next_track(self):
        """Send next track command."""
        self._device.next_track()

    def mute_volume(self, mute):
        """Mute the volume."""
        self._device.set_volume(mute=mute, volume=int(self._volume * 100))
        self._muted = mute

    def set_volume_level(self, volume):
        """Set volume level, range 0..1."""
        self._device.set_volume(mute=False, volume=int(volume * 100))
        self._volume = volume

    def media_play(self):
        """Send play command."""
        self._device.play_track()
        self._state = STATE_PLAYING

    def media_pause(self):
        """Send pause command."""
        self._device.pause_track()
        self._state = STATE_PAUSED

    def play_media(self, media_type, media_id, **kwargs):
        """Play media from a URL or file."""
        if not media_type == MEDIA_TYPE_MUSIC:
            _LOGGER.error(
                "Invalid media type %s. Only %s is supported",
                media_type,
                MEDIA_TYPE_MUSIC,
            )
            return
        self._device.play_track()
        self._state = STATE_PLAYING
