"""Communicate with an Android TV device via ADB over a network.

ADB Debugging must be enabled.
"""


import logging

from .basetv import BaseTV
from . import constants

_LOGGER = logging.getLogger(__name__)


class AndroidTV(BaseTV):
    """Representation of an Android TV device.

    Parameters
    ----------
    host : str
        The address of the device in the format ``<ip address>:<host>``
    adbkey : str
        The path to the ``adbkey`` file for ADB authentication
    adb_server_ip : str
        The IP address of the ADB server
    adb_server_port : int
        The port for the ADB server
    state_detection_rules : dict, None
        A dictionary of rules for determining the state (see :class:`~androidtv.basetv.BaseTV`)
    auth_timeout_s : float
        Authentication timeout (in seconds)

    """

    DEVICE_CLASS = 'androidtv'

    def __init__(self, host, adbkey='', adb_server_ip='', adb_server_port=5037, state_detection_rules=None, auth_timeout_s=constants.DEFAULT_AUTH_TIMEOUT_S):
        BaseTV.__init__(self, host, adbkey, adb_server_ip, adb_server_port, state_detection_rules, auth_timeout_s)

    # ======================================================================= #
    #                                                                         #
    #                               ADB methods                               #
    #                                                                         #
    # ======================================================================= #
    def start_intent(self, uri):
        """Start an intent on the device.

        Parameters
        ----------
        uri : str
            The intent that will be sent is ``am start -a android.intent.action.VIEW -d <uri>``

        """
        self._adb.shell("am start -a android.intent.action.VIEW -d {}".format(uri))

    # ======================================================================= #
    #                                                                         #
    #                          Home Assistant Update                          #
    #                                                                         #
    # ======================================================================= #
    def update(self):
        """Get the info needed for a Home Assistant update.

        Returns
        -------
        state : str
            The state of the device
        current_app : str
            The current running app
        device : str
            The current playback device
        is_volume_muted : bool
            Whether or not the volume is muted
        volume_level : float
            The volume level (between 0 and 1)

        """
        # Get the properties needed for the update
        screen_on, awake, audio_state, wake_lock_size, current_app, media_session_state, device, is_volume_muted, volume = self.get_properties(lazy=True)

        # Get the volume (between 0 and 1)
        volume_level = self._volume_level(volume)

        # Check if device is unavailable
        if screen_on is None:
            state = None

        # Check if device is off
        elif not screen_on or current_app == 'off':
            state = constants.STATE_OFF

        # Check if screen saver is on
        elif not awake:
            state = constants.STATE_IDLE

        else:
            # Determine the state using custom rules
            state = self._custom_state_detection(current_app=current_app, media_session_state=media_session_state, wake_lock_size=wake_lock_size, audio_state=audio_state)
            if state:
                return state, current_app, device, is_volume_muted, volume_level

            # ATV Launcher
            if current_app in [constants.APP_ATV_LAUNCHER, None]:
                state = constants.STATE_STANDBY

            # BELL Fibe
            elif current_app == constants.APP_BELL_FIBE:
                state = audio_state

            # Netflix
            elif current_app == constants.APP_NETFLIX:
                if media_session_state == 2:
                    state = constants.STATE_PAUSED
                elif media_session_state == 3:
                    state = constants.STATE_PLAYING
                else:
                    state = constants.STATE_STANDBY

            # Plex
            elif current_app == constants.APP_PLEX:
                state = audio_state

            # TVheadend
            elif current_app == constants.APP_TVHEADEND:
                if wake_lock_size == 5:
                    state = constants.STATE_PAUSED
                elif wake_lock_size == 6:
                    state = constants.STATE_PLAYING
                else:
                    state = constants.STATE_STANDBY

            # VLC
            elif current_app == constants.APP_VLC:
                if media_session_state == 2:
                    state = constants.STATE_PAUSED
                elif media_session_state == 3:
                    state = constants.STATE_PLAYING
                else:
                    state = constants.STATE_STANDBY

            # VRV
            elif current_app == constants.APP_VRV:
                state = audio_state

            # YouTube
            elif current_app == constants.APP_YOUTUBE:
                if media_session_state == 2:
                    state = constants.STATE_PAUSED
                elif media_session_state == 3:
                    state = constants.STATE_PLAYING
                else:
                    state = constants.STATE_STANDBY

            # Get the state from `media_session_state`
            elif media_session_state:
                if media_session_state == 2:
                    state = constants.STATE_PAUSED
                elif media_session_state == 3:
                    state = constants.STATE_PLAYING
                else:
                    state = constants.STATE_STANDBY

            # Get the state from `audio_state`
            elif audio_state != constants.STATE_IDLE:
                state = audio_state

            # Get the state from `wake_lock_size`
            else:
                if wake_lock_size == 1:
                    state = constants.STATE_PAUSED
                elif wake_lock_size == 2:
                    state = constants.STATE_PLAYING
                else:
                    state = constants.STATE_STANDBY

        return state, current_app, device, is_volume_muted, volume_level

    # ======================================================================= #
    #                                                                         #
    #                               properties                                #
    #                                                                         #
    # ======================================================================= #
    def get_properties(self, lazy=False):
        """Get the properties needed for Home Assistant updates.

        This will send one of the following ADB commands:

        * :py:const:`androidtv.constants.CMD_ANDROIDTV_PROPERTIES_LAZY`
        * :py:const:`androidtv.constants.CMD_ANDROIDTV_PROPERTIES_NOT_LAZY`

        Parameters
        ----------
        lazy : bool
            Whether or not to continue retrieving properties if the device is off or the screensaver is running

        Returns
        -------
        screen_on : bool, None
            Whether or not the device is on, or ``None`` if it was not determined
        awake : bool, None
            Whether or not the device is awake (screensaver is not running), or ``None`` if it was not determined
        audio_state : str, None
            The audio state, as determined from "dumpsys audio", or ``None`` if it was not determined
        wake_lock_size : int, None
            The size of the current wake lock, or ``None`` if it was not determined
        current_app : str, None
            The current app property, or ``None`` if it was not determined
        media_session_state : int, None
            The state from the output of ``dumpsys media_session``, or ``None`` if it was not determined
        device : str, None
            The current playback device, or ``None`` if it was not determined
        is_volume_muted : bool, None
            Whether or not the volume is muted, or ``None`` if it was not determined
        volume : int, None
            The absolute volume level, or ``None`` if it was not determined

        """
        if lazy:
            output = self._adb.shell(constants.CMD_ANDROIDTV_PROPERTIES_LAZY)
        else:
            output = self._adb.shell(constants.CMD_ANDROIDTV_PROPERTIES_NOT_LAZY)
        _LOGGER.debug("Android TV %s update response: %s", self.host, output)

        # ADB command was unsuccessful
        if output is None:
            return None, None, None, None, None, None, None, None, None

        # `screen_on` property
        if not output:
            return False, False, None, -1, None, None, None, None, None
        screen_on = output[0] == '1'

        # `awake` property
        if len(output) < 2:
            return screen_on, False, None, -1, None, None, None, None, None
        awake = output[1] == '1'

        # `audio_state` property
        if len(output) < 3:
            return screen_on, awake, None, -1, None, None, None, None, None
        audio_state = self._audio_state(output[2])

        lines = output.strip().splitlines()

        # `wake_lock_size` property
        if len(lines[0]) < 4:
            return screen_on, awake, audio_state, -1, None, None, None, None, None
        wake_lock_size = self._wake_lock_size(lines[0])

        # `current_app` property
        if len(lines) < 2:
            return screen_on, awake, audio_state, wake_lock_size, None, None, None, None, None
        current_app = self._current_app(lines[1])

        # `media_session_state` property
        if len(lines) < 3:
            return screen_on, awake, audio_state, wake_lock_size, current_app, None, None, None, None
        media_session_state = self._media_session_state(lines[2], current_app)

        # "STREAM_MUSIC" block
        if len(lines) < 4:
            return screen_on, awake, audio_state, wake_lock_size, current_app, media_session_state, None, None, None

        # reconstruct the output of `constants.CMD_STREAM_MUSIC`
        stream_music_raw = "\n".join(lines[3:])

        # the "STREAM_MUSIC" block from `adb shell dumpsys audio`
        stream_music = self._get_stream_music(stream_music_raw)

        # `device` property
        device = self._device(stream_music)

        # `volume` property
        volume = self._volume(stream_music, device)

        # `is_volume_muted` property
        is_volume_muted = self._is_volume_muted(stream_music)

        return screen_on, awake, audio_state, wake_lock_size, current_app, media_session_state, device, is_volume_muted, volume

    def get_properties_dict(self, lazy=True):
        """Get the properties needed for Home Assistant updates and return them as a dictionary.

        Parameters
        ----------
        lazy : bool
            Whether or not to continue retrieving properties if the device is off or the screensaver is running

        Returns
        -------
        dict
            A dictionary with keys ``'screen_on'``, ``'awake'``, ``'wake_lock_size'``, ``'current_app'``,
            ``'media_session_state'``, ``'audio_state'``, ``'device'``, ``'is_volume_muted'``, and ``'volume'``

        """
        screen_on, awake, audio_state, wake_lock_size, current_app, media_session_state, device, is_volume_muted, volume = self.get_properties(lazy=lazy)

        return {'screen_on': screen_on,
                'awake': awake,
                'audio_state': audio_state,
                'wake_lock_size': wake_lock_size,
                'current_app': current_app,
                'media_session_state': media_session_state,
                'device': device,
                'is_volume_muted': is_volume_muted,
                'volume': volume}

    # ======================================================================= #
    #                                                                         #
    #                           turn on/off methods                           #
    #                                                                         #
    # ======================================================================= #
    def turn_on(self):
        """Send ``POWER`` action if the device is off."""
        self._adb.shell(constants.CMD_SCREEN_ON + " || input keyevent {0}".format(constants.KEY_POWER))

    def turn_off(self):
        """Send ``POWER`` action if the device is not off."""
        self._adb.shell(constants.CMD_SCREEN_ON + " && input keyevent {0}".format(constants.KEY_POWER))
