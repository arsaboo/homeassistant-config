"""
Support for interface with an Samsung TV.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/media_player.samsungtv/
"""
import asyncio
from datetime import timedelta
import logging
import socket
import threading
import os

import voluptuous as vol

from homeassistant.components.media_player import (
    MEDIA_TYPE_CHANNEL, PLATFORM_SCHEMA, SUPPORT_NEXT_TRACK, SUPPORT_PAUSE,
    SUPPORT_PLAY, SUPPORT_PLAY_MEDIA, SUPPORT_PREVIOUS_TRACK, SUPPORT_TURN_OFF,
    SUPPORT_TURN_ON, SUPPORT_VOLUME_MUTE, SUPPORT_VOLUME_STEP,
    SUPPORT_VOLUME_SET, SUPPORT_SELECT_SOURCE, MediaPlayerDevice)
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_METHOD,
    STATE_OFF,
    STATE_ON
)
import homeassistant.helpers.config_validation as cv
from homeassistant.util import dt as dt_util


REQUIREMENTS = [
    'https://github.com/kdschlosser/'
    'samsungctl/archive/develop.zip#samsungctl==0.8.4b'
]

SAMSUNG_CONFIG_PATH = 'samsung_tv'

ICON = 'mdi:television'

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = 'Samsung TV Remote'
DEFAULT_DESCRIPTION = socket.gethostname()

CONF_DESCRIPTION =  'description'

KEY_PRESS_TIMEOUT = 1.2
KNOWN_DEVICES_KEY = 'samsungtv_known_devices'

SUPPORT_SAMSUNGTV = (
    SUPPORT_PAUSE |
    SUPPORT_VOLUME_STEP |
    SUPPORT_VOLUME_MUTE |
    SUPPORT_PREVIOUS_TRACK |
    SUPPORT_NEXT_TRACK |
    SUPPORT_TURN_OFF |
    SUPPORT_PLAY |
    SUPPORT_PLAY_MEDIA |
    SUPPORT_VOLUME_SET |
    SUPPORT_SELECT_SOURCE
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_METHOD): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_DESCRIPTION, default=DEFAULT_DESCRIPTION): cv.string,
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Samsung TV platform."""
    known_devices = hass.data.get(KNOWN_DEVICES_KEY)
    if known_devices is None:
        known_devices = set()
        hass.data[KNOWN_DEVICES_KEY] = known_devices

    config_path = hass.config.path(SAMSUNG_CONFIG_PATH)

    if not os.path.exists(config_path):
        os.mkdir(config_path)

    import samsungctl

    uuid = None
    # Is this a manual configuration?
    if config.get(CONF_HOST) is not None:
        host = config.get(CONF_HOST)
        name = config.get(CONF_NAME)
        description = config.get(CONF_DESCRIPTION)
        method = config.get(CONF_METHOD)

    elif discovery_info is not None:
        tv_name = discovery_info.get('name')
        model = discovery_info.get('model_name')
        host = discovery_info.get('host')
        name = "{} ({})".format(tv_name, model)
        description = DEFAULT_DESCRIPTION
        method = None
        udn = discovery_info.get('udn')
        if udn and udn.startswith('uuid:'):
            uuid = udn[len('uuid:'):]
    else:
        _LOGGER.warning("Cannot determine device")
        return

    # Only add a device once, so discovered devices do not override manual
    # config.
    ip_addr = socket.gethostbyname(host)
    if ip_addr not in known_devices:
        known_devices.add(ip_addr)

        samsung_config = samsungctl.Config.load(config_path)(
            host=host,
            name=name,
            description=description,
            method=method,
        )

        if not samsung_config.paired and samsung_config.method == 'encrypted':
            request_configuration(samsung_config, uuid, hass, add_entities)
        else:
            add_entities([SamsungTVDevice(samsung_config, uuid)])
        _LOGGER.debug("Samsung TV %s added as '%s'", host, config.get(CONF_NAME))
    else:
        _LOGGER.debug("Ignoring duplicate Samsung TV %s", host)

_CONFIGURING = {}


def request_configuration(samsung_config, uuid, hass, add_entities):
    """Request configuration steps from the user."""
    host = samsung_config.host
    name = samsung_config.name

    configurator = hass.components.configurator

    import samsungctl
    event = threading.Event()
    pin = []
    count = 0

    def get_pin():
        global count

        def samsung_configuration_callback(data):
            """Handle the entry of user PIN."""
            pin.append(data.get('pin'))
            event.set()

        if count == 3:
            _LOGGER.error(name + " TV: Pin entry failed")
            return False

        if host in _CONFIGURING:
            count += 1
            configurator.notify_errors(
                _CONFIGURING[host], "Failed to register, please try again."
            )
            del pin[:]
            event.clear()
        else:
            _CONFIGURING[host] = configurator.request_config(
                name,
                samsung_configuration_callback,
                description='Enter the Pin shown on your Samsung TV.',
                description_image="/static/images/smart-tv.png",
                submit_caption="Confirm",
                fields=[{'id': 'pin', 'name': 'Enter the pin', 'type': ''}]
            )

        event.wait(30)

        if not event.isSet():
            count += 1
            return None

        return pin[0]

    samsung_config.get_pin = get_pin
    try:
        remote = samsungctl.Remote(samsung_config)
        remote.open()
        add_entities(
            [SamsungTVDevice(samsung_config, uuid)]
        )
    except:
        return


class SamsungTVDevice(MediaPlayerDevice):
    """Representation of a Samsung TV."""

    def __init__(self, config, uuid):
        """Initialize the Samsung device."""
        from samsungctl import exceptions
        from samsungctl import Remote

        # Save a reference to the imported classes
        self._exceptions_class = exceptions
        self._remote_class = Remote
        self._config = config

        self._name = self._config.name
        self._mac = self._config.mac
        self._uuid = uuid
        self._playing = True
        self._state = None
        self._remote = None
        self._key_source = False
        self._mute = False
        self._sources = []
        self._source = ''
        self._volume = 0.0

        self._supported_features = SUPPORT_SAMSUNGTV
        if self._config.method != 'legacy':
            self._supported_features |= SUPPORT_TURN_ON

        # Mark the end of a shutdown command (need to wait 15 seconds before
        # sending the next command to avoid turning the TV back ON).
        self._end_of_power_off = None

        # Mark the end of the TV powering on.need to wait 20 seconds before
        # sending any commands.
        self._end_of_power_on = None
        # Generate a configuration for the Samsung library

        self._remote = self._remote_class(self._config)
        self._config.save()

    def update(self):
        """Update state of device."""

        if self._power_off_in_progress():
            _LOGGER.debug(self._name + ' TV: Powering Off')
            self._state = STATE_OFF

        elif self._power_on_in_progress():
            _LOGGER.debug(self._name + ' TV: Powering On')
            self._state = STATE_ON
        else:
            power = self._remote.power
            if power is True:
                _LOGGER.debug(self._name + ' TV: Power is On')
                self._state = STATE_ON
            else:
                _LOGGER.debug(self._name + ' TV: Power is Off')
                self._state = STATE_OFF

        sources = self._remote.sources
        if sources is None:
            if self._state == STATE_OFF:
                self._sources = []
            else:
                self._sources = [
                    'Source',
                    'Component 1',
                    'Component 2',
                    'AV 1',
                    'AV 2',
                    'AV 3',
                    'S Video 1',
                    'S Video 2',
                    'S Video 3',
                    'HDMI',
                    'HDMI 1',
                    'HDMI 2',
                    'HDMI 3',
                    'HDMI 4',
                    'FM-Radio',
                    'DVI',
                    'DVR',
                    'TV',
                    'Analog TV',
                    'Digital TV'
                ]

                self._key_source = True

        source = self._remote.source
        if source is None:
            if self._state == STATE_OFF:
                self._source = 'TV OFF'
            else:
                self._source = 'Unknown'
        else:
            label = source.label
            name = source.name

            if name != label:
                name = label + ':' + name

            self._source = name

        volume = self._remote.volume
        _LOGGER.debug(self._name + ' TV: Volume = ' + str(volume))
        if volume is not None:
            self._volume = volume / 100.0

        mute = self._remote.mute
        _LOGGER.debug(self._name + ' TV: Mute = ' + str(mute))
        if mute is None:
            self._mute = False
        else:
            self._mute = mute

    def send_key(self, key):
        """Send a key to the tv and handles exceptions."""
        if self._power_off_in_progress():
            _LOGGER.debug(self._name + " TV: powering off, not sending command: %s", key)
            return

        elif self._power_on_in_progress():
            _LOGGER.debug(self._name + " TV: powering on, not sending command: %s", key)
            return

        if self._state == STATE_OFF:
            _LOGGER.debug(self._name + " TV: powered off, not sending command: %s", key)
            return

        self._remote.control(key)

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the device."""
        return self._uuid

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return self._supported_features

    def select_source(self, source):
        """Select input source."""
        if self._key_source:
            if source == 'Analog TV':
                source = 'ANTENA'

            elif source == 'Digital TV':
                source = 'DTV'

            source = source.upper().replace('-', '_').replace(' ', '')
            source = 'KEY_' + source
            _LOGGER.debug(self._name + ' TV: changing source to ' + source)
            self.send_key(source)
        else:
            if ':' in source:
                source = source.rsplit(':', 1)[-1]
            _LOGGER.debug(self._name + ' TV: changing source to ' + source)
            self._remote.source = source

    @property
    def source(self):
        """Name of the current input source."""
        return self._source

    @property
    def source_list(self):
        """List of available input sources."""
        return self._sources

    def volume_up(self):
        """Volume up the media player."""
        self.send_key('KEY_VOLUP')

    def volume_down(self):
        """Volume down media player."""
        self.send_key('KEY_VOLDOWN')

    @property
    def volume_level(self):
        """Volume level of the media player scalar volume. 0.0-1.0."""
        return self._volume

    def set_volume_level(self, volume):
        """Set volume level, convert scalar volume. 0.0-1.0 to percent 0-100"""
        self._remote.volume = int(volume * 100)

    def mute_volume(self, mute):
        """Send mute command."""
        self._remote.mute = mute

    @property
    def is_volume_muted(self):
        """Boolean if volume is currently muted."""
        return self._mute

    def media_play_pause(self):
        """Simulate play pause media player."""
        if self._playing:
            self.media_pause()
        else:
            self.media_play()

    def media_play(self):
        """Send play command."""
        self._playing = True
        self.send_key('KEY_PLAY')

    def media_pause(self):
        """Send media pause command to media player."""
        self._playing = False
        self.send_key('KEY_PAUSE')

    def media_next_track(self):
        """Send next track command."""
        self.send_key('KEY_FF')

    def media_previous_track(self):
        """Send the previous track command."""
        self.send_key('KEY_REWIND')

    async def async_play_media(self, media_type, media_id, **kwargs):
        """Support changing a channel."""
        if media_type != MEDIA_TYPE_CHANNEL:
            _LOGGER.error(self._name + ' TV: Unsupported media type')
            return

        # media_id should only be a channel number
        try:
            cv.positive_int(media_id)
        except vol.Invalid:
            _LOGGER.error(self._name + ' TV: Media ID must be positive integer')
            return

        for digit in media_id:
            await self.hass.async_add_job(self.send_key, 'KEY_' + digit)
            await asyncio.sleep(KEY_PRESS_TIMEOUT, self.hass.loop)

    @property
    def app_id(self):
        """ID of the current running app."""
        return None

    @property
    def app_name(self):
        """Name of the current running app."""
        return None

    def turn_on(self):
        """Turn the media player on."""

        if self._power_on_in_progress():
            return

        if self._config.mac:
            self._end_of_power_on = dt_util.utcnow() + timedelta(seconds=20)

            if self._power_off_in_progress():
                self._end_of_power_on += (
                    dt_util.utcnow() - self._end_of_power_off
                )

            def do():
                _LOGGER.debug(self._name + ' TV: Power on process started')
                event = threading.Event()
                while self._power_off_in_progress():
                    event.wait(0.5)

                self._remote.power = True

            t = threading.Thread(target=do)
            t.daemon = True
            t.start()
        elif self._config.method != 'legacy':
            _LOGGER.debug(
                self._name + " TV: There was a problem detecting the TV's MAC address, "
                "you will have to update the MAC address in the Home "
                "Assistant config file manually."
            )

        else:
            _LOGGER.debug(
                self._name + " TV: Legacy TV's (2008 - 2013) do not support "
                "being powered on remotely."
            )

    def _power_on_in_progress(self):
        return (
            self._end_of_power_on is not None and
            self._end_of_power_on > dt_util.utcnow()
        )

    def turn_off(self):
        """Turn off media player."""

        if self._power_off_in_progress():
            return

        self._end_of_power_off = dt_util.utcnow() + timedelta(seconds=15)

        if self._power_on_in_progress():
            self._end_of_power_off += (
                dt_util.utcnow() - self._end_of_power_on
            )

        def do():
            _LOGGER.debug(self._name + ' TV: Power off process started')
            event = threading.Event()
            while self._power_on_in_progress():
                event.wait(0.5)

            self._remote.power = False

        t = threading.Thread(target=do)
        t.daemon = True
        t.start()

    def _power_off_in_progress(self):
        return (
            self._end_of_power_off is not None and
            self._end_of_power_off > dt_util.utcnow()
        )
