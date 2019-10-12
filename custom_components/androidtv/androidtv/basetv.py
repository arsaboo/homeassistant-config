"""Communicate with an Android TV or Amazon Fire TV device via ADB over a network.

ADB Debugging must be enabled.
"""


import logging
import re

from . import constants
from .adb_manager import ADBPython, ADBServer

_LOGGER = logging.getLogger(__name__)


class BaseTV(object):
    """Base class for representing an Android TV / Fire TV device.

    The ``state_detection_rules`` parameter is of the format:

    .. code-block:: python

       state_detection_rules = {'com.amazon.tv.launcher': ['standby'],
                                'com.netflix.ninja': ['media_session_state'],
                                'com.ellation.vrv': ['audio_state'],
                                'com.hulu.plus': [{'playing': {'wake_lock_size' : 4}},
                                                  {'paused': {'wake_lock_size': 2}}],
                                'com.plexapp.android': [{'playing': {'media_session_state': 3, 'wake_lock_size': 3}},
                                                        {'paused': {'media_session_state': 3, 'wake_lock_size': 1}},
                                                        'standby']}

    The keys are app IDs, and the values are lists of rules that are evaluated in order.

    :py:const:`~androidtv.constants.VALID_STATES`

    .. code-block:: python

       VALID_STATES = ('idle', 'off', 'playing', 'paused', 'standby')


    **Valid rules:**

    * ``'standby'``, ``'playing'``, ``'paused'``, ``'idle'``, or ``'off'`` = always report the specified state when this app is open
    * ``'media_session_state'`` = try to use the :attr:`media_session_state` property to determine the state
    * ``'audio_state'`` = try to use the :attr:`audio_state` property to determine the state
    * ``{'<VALID_STATE>': {'<PROPERTY1>': VALUE1, '<PROPERTY2>': VALUE2, ...}}`` = check if each of the properties is equal to the specified value, and if so return the state

      * The valid properties are ``'media_session_state'``, ``'audio_state'``, and ``'wake_lock_size'``


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
        A dictionary of rules for determining the state (see above)
    auth_timeout_s : float
        Authentication timeout (in seconds)

    """

    def __init__(self, host, adbkey='', adb_server_ip='', adb_server_port=5037, state_detection_rules=None, auth_timeout_s=constants.DEFAULT_AUTH_TIMEOUT_S):
        self.host = host
        self.adbkey = adbkey
        self.adb_server_ip = adb_server_ip
        self.adb_server_port = adb_server_port
        self._state_detection_rules = state_detection_rules

        # make sure the rules are valid
        if self._state_detection_rules:
            for app_id, rules in self._state_detection_rules.items():
                if not isinstance(app_id, str):
                    raise TypeError("{0} is of type {1}, not str".format(app_id, type(app_id).__name__))
                state_detection_rules_validator(rules)

        # the max volume level (determined when first getting the volume level)
        self.max_volume = None

        # the handler for ADB commands
        if not adb_server_ip:
            # python-adb
            self._adb = ADBPython(host, adbkey)
        else:
            # pure-python-adb
            self._adb = ADBServer(host, adb_server_ip, adb_server_port)

        # establish the ADB connection
        self.adb_connect(auth_timeout_s=auth_timeout_s)

        # get device properties
        self.device_properties = self.get_device_properties()

    # ======================================================================= #
    #                                                                         #
    #                               ADB methods                               #
    #                                                                         #
    # ======================================================================= #
    def adb_shell(self, cmd):
        """Send an ADB command.

        This calls :py:meth:`androidtv.adb_manager.ADBPython.shell` or :py:meth:`androidtv.adb_manager.ADBServer.shell`,
        depending on whether the Python ADB implementation or an ADB server is used for communicating with the device.

        Parameters
        ----------
        cmd : str
            The ADB command to be sent

        Returns
        -------
        str, None
            The response from the device, if there is a response

        """
        return self._adb.shell(cmd)

    def adb_connect(self, always_log_errors=True, auth_timeout_s=constants.DEFAULT_AUTH_TIMEOUT_S):
        """Connect to an Android TV / Fire TV device.

        Parameters
        ----------
        always_log_errors : bool
            If True, errors will always be logged; otherwise, errors will only be logged on the first failed reconnect attempt
        auth_timeout_s : float
            Authentication timeout (in seconds)

        Returns
        -------
        bool
            Whether or not the connection was successfully established and the device is available

        """
        if isinstance(self._adb, ADBPython):
            return self._adb.connect(always_log_errors, auth_timeout_s)
        return self._adb.connect(always_log_errors)

    def adb_close(self):
        """Close the ADB connection.

        This only works for the Python ADB implementation (see :meth:`androidtv.adb_manager.ADBPython.close`).
        For the ADB server approach, this doesn't do anything (see :meth:`androidtv.adb_manager.ADBServer.close`).

        """
        self._adb.close()

    def _key(self, key):
        """Send a key event to device.

        Parameters
        ----------
        key : str, int
            The Key constant

        """
        self._adb.shell('input keyevent {0}'.format(key))

    # ======================================================================= #
    #                                                                         #
    #                        Home Assistant device info                       #
    #                                                                         #
    # ======================================================================= #
    def get_device_properties(self):
        """Return a dictionary of device properties.

        Returns
        -------
        props : dict
            A dictionary with keys ``'wifimac'``, ``'ethmac'``, ``'serialno'``, ``'manufacturer'``, ``'model'``, and ``'sw_version'``

        """
        properties = self._adb.shell(constants.CMD_MANUFACTURER + " && " +
                                     constants.CMD_MODEL + " && " +
                                     constants.CMD_SERIALNO + " && " +
                                     constants.CMD_VERSION + " && " +
                                     constants.CMD_MAC_WLAN0 + " && " +
                                     constants.CMD_MAC_ETH0)

        if not properties:
            return {}

        lines = properties.strip().splitlines()
        if len(lines) != 6:
            return {}

        manufacturer, model, serialno, version, mac_wlan0_output, mac_eth0_output = lines

        if not serialno.strip():
            _LOGGER.warning("Could not obtain serialno for %s, got: '%s'", self.host, serialno)
            serialno = None

        mac_wlan0_matches = re.findall(constants.MAC_REGEX_PATTERN, mac_wlan0_output)
        if mac_wlan0_matches:
            wifimac = mac_wlan0_matches[0]
        else:
            wifimac = None

        mac_eth0_matches = re.findall(constants.MAC_REGEX_PATTERN, mac_eth0_output)
        if mac_eth0_matches:
            ethmac = mac_eth0_matches[0]
        else:
            ethmac = None

        props = {'manufacturer': manufacturer,
                 'model': model,
                 'serialno': serialno,
                 'sw_version': version,
                 'wifimac': wifimac,
                 'ethmac': ethmac}

        return props

    # ======================================================================= #
    #                                                                         #
    #                         Custom state detection                          #
    #                                                                         #
    # ======================================================================= #
    def _custom_state_detection(self, current_app=None, media_session_state=None, wake_lock_size=None, audio_state=None):
        """Use the rules in ``self._state_detection_rules`` to determine the state.

        Parameters
        ----------
        current_app : str, None
            The :attr:`current_app` property
        media_session_state : int, None
            The :attr:`media_session_state` property
        wake_lock_size : int, None
            The :attr:`wake_lock_size` property
        audio_state : str, None
            The :attr:`audio_state` property

        Returns
        -------
        str, None
            The state, if it could be determined using the rules in ``self._state_detection_rules``; otherwise, ``None``

        """
        if not self._state_detection_rules or current_app is None or current_app not in self._state_detection_rules:
            return None

        rules = self._state_detection_rules[current_app]

        for rule in rules:
            # The state is always the same for this app
            if rule in constants.VALID_STATES:
                return rule

            # Use the `media_session_state` property
            if rule == 'media_session_state':
                if media_session_state == 2:
                    return constants.STATE_PAUSED
                if media_session_state == 3:
                    return constants.STATE_PLAYING
                if media_session_state is not None:
                    return constants.STATE_STANDBY

            # Use the `audio_state` property
            if rule == 'audio_state' and audio_state in constants.VALID_STATES:
                return audio_state

            # Check conditions and if they are true, return the specified state
            if isinstance(rule, dict):
                for state, conditions in rule.items():
                    if state in constants.VALID_STATES and self._conditions_are_true(conditions, media_session_state, wake_lock_size, audio_state):
                        return state

        return None

    @staticmethod
    def _conditions_are_true(conditions, media_session_state=None, wake_lock_size=None, audio_state=None):
        """Check whether the conditions in ``conditions`` are true.

        Parameters
        ----------
        conditions : dict
            A dictionary of conditions to be checked (see the ``state_detection_rules`` parameter in :class:`~androidtv.basetv.BaseTV`)
        media_session_state : int, None
            The :attr:`media_session_state` property
        wake_lock_size : int, None
            The :attr:`wake_lock_size` property
        audio_state : str, None
            The :attr:`audio_state` property

        Returns
        -------
        bool
            Whether or not all the conditions in ``conditions`` are true

        """
        for key, val in conditions.items():
            if key == 'media_session_state':
                if media_session_state is None or media_session_state != val:
                    return False

            elif key == 'wake_lock_size':
                if wake_lock_size is None or wake_lock_size != val:
                    return False

            elif key == 'audio_state':
                if audio_state is None or audio_state != val:
                    return False

            # key is invalid
            else:
                return False

        return True

    # ======================================================================= #
    #                                                                         #
    #                               Properties                                #
    #                                                                         #
    # ======================================================================= #
    @property
    def audio_state(self):
        """Check if audio is playing, paused, or idle.

        Returns
        -------
        str, None
            The audio state, as determined from the ADB shell command :py:const:`androidtv.constants.CMD_AUDIO_STATE`, or ``None`` if it could not be determined

        """
        audio_state_response = self._adb.shell(constants.CMD_AUDIO_STATE)
        return self._audio_state(audio_state_response)

    @property
    def available(self):
        """Check whether the ADB connection is intact.

        Returns
        -------
        bool
            Whether or not the ADB connection is intact

        """
        return self._adb.available

    @property
    def awake(self):
        """Check if the device is awake (screensaver is not running).

        Returns
        -------
        bool
            Whether or not the device is awake (screensaver is not running)

        """
        return self._adb.shell(constants.CMD_AWAKE + constants.CMD_SUCCESS1_FAILURE0) == '1'

    @property
    def current_app(self):
        """Return the current app.

        Returns
        -------
        str, None
            The ID of the current app, or ``None`` if it could not be determined

        """
        current_app_response = self._adb.shell(constants.CMD_CURRENT_APP)

        return self._current_app(current_app_response)

    @property
    def device(self):
        """Get the current playback device.

        Returns
        -------
        str, None
            The current playback device, or ``None`` if it could not be determined

        """
        stream_music = self._get_stream_music()

        return self._device(stream_music)

    @property
    def is_volume_muted(self):
        """Whether or not the volume is muted.

        Returns
        -------
        bool, None
            Whether or not the volume is muted, or ``None`` if it could not be determined

        """
        stream_music = self._get_stream_music()

        return self._is_volume_muted(stream_music)

    @property
    def media_session_state(self):
        """Get the state from the output of ``dumpsys media_session``.

        Returns
        -------
        int, None
            The state from the output of the ADB shell command ``dumpsys media_session``, or ``None`` if it could not be determined

        """
        media_session_state_response = self._adb.shell(constants.CMD_MEDIA_SESSION_STATE_FULL)

        _, media_session_state = self._current_app_media_session_state(media_session_state_response)

        return media_session_state

    @property
    def running_apps(self):
        """Return a list of running user applications.

        Returns
        -------
        list
            A list of the running apps

        """
        running_apps_response = self._adb.shell(constants.CMD_RUNNING_APPS)

        return self._running_apps(running_apps_response)

    @property
    def screen_on(self):
        """Check if the screen is on.

        Returns
        -------
        bool
            Whether or not the device is on

        """
        return self._adb.shell(constants.CMD_SCREEN_ON + constants.CMD_SUCCESS1_FAILURE0) == '1'

    @property
    def volume(self):
        """Get the absolute volume level.

        Returns
        -------
        int, None
            The absolute volume level, or ``None`` if it could not be determined

        """
        stream_music = self._get_stream_music()
        device = self._device(stream_music)

        return self._volume(stream_music, device)

    @property
    def volume_level(self):
        """Get the relative volume level.

        Returns
        -------
        float, None
            The volume level (between 0 and 1), or ``None`` if it could not be determined

        """
        volume = self.volume

        return self._volume_level(volume)

    @property
    def wake_lock_size(self):
        """Get the size of the current wake lock.

        Returns
        -------
        int, None
            The size of the current wake lock, or ``None`` if it could not be determined

        """
        wake_lock_size_response = self._adb.shell(constants.CMD_WAKE_LOCK_SIZE)

        return self._wake_lock_size(wake_lock_size_response)

    # ======================================================================= #
    #                                                                         #
    #                            Parse properties                             #
    #                                                                         #
    # ======================================================================= #
    @staticmethod
    def _audio_state(audio_state_response):
        """Parse the :attr:`audio_state` property from the output of the command :py:const:`androidtv.constants.CMD_AUDIO_STATE`.

        Parameters
        ----------
        audio_state_response : str, None
            The output of the command :py:const:`androidtv.constants.CMD_AUDIO_STATE`

        Returns
        -------
        str, None
            The audio state, or ``None`` if it could not be determined

        """
        if not audio_state_response:
            return None
        if audio_state_response == '1':
            return constants.STATE_PAUSED
        if audio_state_response == '2':
            return constants.STATE_PLAYING
        return constants.STATE_IDLE

    @staticmethod
    def _current_app(current_app_response):
        """Get the current app from the output of the command :py:const:`androidtv.constants.CMD_CURRENT_APP`.

        Parameters
        ----------
        current_app_response : str, None
            The output from the ADB command :py:const:`androidtv.constants.CMD_CURRENT_APP`

        Returns
        -------
        str, None
            The current app, or ``None`` if it could not be determined

        """
        if not current_app_response or '=' in current_app_response or '{' in current_app_response:
            return None

        return current_app_response

    def _current_app_media_session_state(self, media_session_state_response):
        """Get the current app and the media session state properties from the output of :py:const:`androidtv.constants.CMD_MEDIA_SESSION_STATE_FULL`.

        Parameters
        ----------
        media_session_state_response : str, None
            The output of :py:const:`androidtv.constants.CMD_MEDIA_SESSION_STATE_FULL`

        Returns
        -------
        current_app : str, None
            The current app, or ``None`` if it could not be determined
        media_session_state : int, None
            The state from the output of the ADB shell command, or ``None`` if it could not be determined

        """
        if not media_session_state_response:
            return None, None

        lines = media_session_state_response.splitlines()

        current_app = self._current_app(lines[0].strip())

        if len(lines) > 1:
            media_session_state = self._media_session_state(lines[1], current_app)
        else:
            media_session_state = None

        return current_app, media_session_state

    @staticmethod
    def _device(stream_music):
        """Get the current playback device from the ``STREAM_MUSIC`` block from ``adb shell dumpsys audio``.

        Parameters
        ----------
        stream_music : str, None
            The ``STREAM_MUSIC`` block from ``adb shell dumpsys audio``

        Returns
        -------
        str, None
            The current playback device, or ``None`` if it could not be determined

        """
        if not stream_music:
            return None

        matches = re.findall(constants.DEVICE_REGEX_PATTERN, stream_music, re.DOTALL | re.MULTILINE)
        if matches:
            return matches[0]

        return None

    def _get_stream_music(self, stream_music_raw=None):
        """Get the ``STREAM_MUSIC`` block from the output of the command :py:const:`androidtv.constants.CMD_STREAM_MUSIC`.

        Parameters
        ----------
        stream_music_raw : str, None
            The output of the command :py:const:`androidtv.constants.CMD_STREAM_MUSIC`

        Returns
        -------
        str, None
            The ``STREAM_MUSIC`` block from the output of :py:const:`androidtv.constants.CMD_STREAM_MUSIC`, or ``None`` if it could not be determined

        """
        if not stream_music_raw:
            stream_music_raw = self._adb.shell(constants.CMD_STREAM_MUSIC)

        if not stream_music_raw:
            return None

        matches = re.findall(constants.STREAM_MUSIC_REGEX_PATTERN, stream_music_raw, re.DOTALL | re.MULTILINE)
        if matches:
            return matches[0]

        return None

    @staticmethod
    def _is_volume_muted(stream_music):
        """Determine whether or not the volume is muted from the ``STREAM_MUSIC`` block from ``adb shell dumpsys audio``.

        Parameters
        ----------
        stream_music : str, None
            The ``STREAM_MUSIC`` block from ``adb shell dumpsys audio``

        Returns
        -------
        bool, None
            Whether or not the volume is muted, or ``None`` if it could not be determined

        """
        if not stream_music:
            return None

        matches = re.findall(constants.MUTED_REGEX_PATTERN, stream_music, re.DOTALL | re.MULTILINE)
        if matches:
            return matches[0] == 'true'

        return None

    @staticmethod
    def _media_session_state(media_session_state_response, current_app):
        """Get the state from the output of :py:const:`androidtv.constants.CMD_MEDIA_SESSION_STATE`.

        Parameters
        ----------
        media_session_state_response : str, None
            The output of :py:const:`androidtv.constants.CMD_MEDIA_SESSION_STATE`
        current_app : str, None
            The current app, or ``None`` if it could not be determined

        Returns
        -------
        int, None
            The state from the output of the ADB shell command, or ``None`` if it could not be determined

        """
        if not media_session_state_response or not current_app:
            return None

        matches = constants.REGEX_MEDIA_SESSION_STATE.search(media_session_state_response)
        if matches:
            return int(matches.group('state'))

        return None

    @staticmethod
    def _running_apps(running_apps_response):
        """Get the running apps from the output of :py:const:`androidtv.constants.CMD_RUNNING_APPS`.

        Parameters
        ----------
        running_apps_response : str, None
            The output of :py:const:`androidtv.constants.CMD_RUNNING_APPS`

        Returns
        -------
        list, None
            A list of the running apps, or ``None`` if it could not be determined

        """
        if running_apps_response:
            if isinstance(running_apps_response, list):
                return [line.strip().rsplit(' ', 1)[-1] for line in running_apps_response if line.strip()]
            return [line.strip().rsplit(' ', 1)[-1] for line in running_apps_response.splitlines() if line.strip()]

        return None

    def _volume(self, stream_music, device):
        """Get the absolute volume level from the ``STREAM_MUSIC`` block from ``adb shell dumpsys audio``.

        Parameters
        ----------
        stream_music : str, None
            The ``STREAM_MUSIC`` block from ``adb shell dumpsys audio``
        device : str, None
            The current playback device

        Returns
        -------
        int, None
            The absolute volume level, or ``None`` if it could not be determined

        """
        if not stream_music:
            return None

        if not self.max_volume:
            max_volume_matches = re.findall(constants.MAX_VOLUME_REGEX_PATTERN, stream_music, re.DOTALL | re.MULTILINE)
            if max_volume_matches:
                self.max_volume = float(max_volume_matches[0])
            else:
                self.max_volume = 15.

        if not device:
            return None

        volume_matches = re.findall(device + constants.VOLUME_REGEX_PATTERN, stream_music, re.DOTALL | re.MULTILINE)
        if volume_matches:
            return int(volume_matches[0])

        return None

    def _volume_level(self, volume):
        """Get the relative volume level from the absolute volume level.

        Parameters
        -------
        volume: int, None
            The absolute volume level

        Returns
        -------
        float, None
            The volume level (between 0 and 1), or ``None`` if it could not be determined

        """
        if volume is not None and self.max_volume:
            return volume / self.max_volume

        return None

    @staticmethod
    def _wake_lock_size(wake_lock_size_response):
        """Get the size of the current wake lock from the output of :py:const:`androidtv.constants.CMD_WAKE_LOCK_SIZE`.

        Parameters
        ----------
        wake_lock_size_response : str, None
            The output of :py:const:`androidtv.constants.CMD_WAKE_LOCK_SIZE`

        Returns
        -------
        int, None
            The size of the current wake lock, or ``None`` if it could not be determined

        """
        if wake_lock_size_response:
            wake_lock_size_matches = constants.REGEX_WAKE_LOCK_SIZE.search(wake_lock_size_response)
            if wake_lock_size_matches:
                return int(wake_lock_size_matches.group('size'))

        return None

    # ======================================================================= #
    #                                                                         #
    #                      "key" methods: basic commands                      #
    #                                                                         #
    # ======================================================================= #
    def power(self):
        """Send power action."""
        self._key(constants.KEY_POWER)

    def sleep(self):
        """Send sleep action."""
        self._key(constants.KEY_SLEEP)

    def home(self):
        """Send home action."""
        self._key(constants.KEY_HOME)

    def up(self):
        """Send up action."""
        self._key(constants.KEY_UP)

    def down(self):
        """Send down action."""
        self._key(constants.KEY_DOWN)

    def left(self):
        """Send left action."""
        self._key(constants.KEY_LEFT)

    def right(self):
        """Send right action."""
        self._key(constants.KEY_RIGHT)

    def enter(self):
        """Send enter action."""
        self._key(constants.KEY_ENTER)

    def back(self):
        """Send back action."""
        self._key(constants.KEY_BACK)

    def menu(self):
        """Send menu action."""
        self._key(constants.KEY_MENU)

    def mute_volume(self):
        """Mute the volume."""
        self._key(constants.KEY_MUTE)

    # ======================================================================= #
    #                                                                         #
    #                      "key" methods: media commands                      #
    #                                                                         #
    # ======================================================================= #
    def media_play(self):
        """Send media play action."""
        self._key(constants.KEY_PLAY)

    def media_pause(self):
        """Send media pause action."""
        self._key(constants.KEY_PAUSE)

    def media_play_pause(self):
        """Send media play/pause action."""
        self._key(constants.KEY_PLAY_PAUSE)

    def media_stop(self):
        """Send media stop action."""
        self._key(constants.KEY_STOP)

    def media_next_track(self):
        """Send media next action (results in fast-forward)."""
        self._key(constants.KEY_NEXT)

    def media_previous_track(self):
        """Send media previous action (results in rewind)."""
        self._key(constants.KEY_PREVIOUS)

    # ======================================================================= #
    #                                                                         #
    #                   "key" methods: alphanumeric commands                  #
    #                                                                         #
    # ======================================================================= #
    def space(self):
        """Send space keypress."""
        self._key(constants.KEY_SPACE)

    def key_0(self):
        """Send 0 keypress."""
        self._key(constants.KEY_0)

    def key_1(self):
        """Send 1 keypress."""
        self._key(constants.KEY_1)

    def key_2(self):
        """Send 2 keypress."""
        self._key(constants.KEY_2)

    def key_3(self):
        """Send 3 keypress."""
        self._key(constants.KEY_3)

    def key_4(self):
        """Send 4 keypress."""
        self._key(constants.KEY_4)

    def key_5(self):
        """Send 5 keypress."""
        self._key(constants.KEY_5)

    def key_6(self):
        """Send 6 keypress."""
        self._key(constants.KEY_6)

    def key_7(self):
        """Send 7 keypress."""
        self._key(constants.KEY_7)

    def key_8(self):
        """Send 8 keypress."""
        self._key(constants.KEY_8)

    def key_9(self):
        """Send 9 keypress."""
        self._key(constants.KEY_9)

    def key_a(self):
        """Send a keypress."""
        self._key(constants.KEY_A)

    def key_b(self):
        """Send b keypress."""
        self._key(constants.KEY_B)

    def key_c(self):
        """Send c keypress."""
        self._key(constants.KEY_C)

    def key_d(self):
        """Send d keypress."""
        self._key(constants.KEY_D)

    def key_e(self):
        """Send e keypress."""
        self._key(constants.KEY_E)

    def key_f(self):
        """Send f keypress."""
        self._key(constants.KEY_F)

    def key_g(self):
        """Send g keypress."""
        self._key(constants.KEY_G)

    def key_h(self):
        """Send h keypress."""
        self._key(constants.KEY_H)

    def key_i(self):
        """Send i keypress."""
        self._key(constants.KEY_I)

    def key_j(self):
        """Send j keypress."""
        self._key(constants.KEY_J)

    def key_k(self):
        """Send k keypress."""
        self._key(constants.KEY_K)

    def key_l(self):
        """Send l keypress."""
        self._key(constants.KEY_L)

    def key_m(self):
        """Send m keypress."""
        self._key(constants.KEY_M)

    def key_n(self):
        """Send n keypress."""
        self._key(constants.KEY_N)

    def key_o(self):
        """Send o keypress."""
        self._key(constants.KEY_O)

    def key_p(self):
        """Send p keypress."""
        self._key(constants.KEY_P)

    def key_q(self):
        """Send q keypress."""
        self._key(constants.KEY_Q)

    def key_r(self):
        """Send r keypress."""
        self._key(constants.KEY_R)

    def key_s(self):
        """Send s keypress."""
        self._key(constants.KEY_S)

    def key_t(self):
        """Send t keypress."""
        self._key(constants.KEY_T)

    def key_u(self):
        """Send u keypress."""
        self._key(constants.KEY_U)

    def key_v(self):
        """Send v keypress."""
        self._key(constants.KEY_V)

    def key_w(self):
        """Send w keypress."""
        self._key(constants.KEY_W)

    def key_x(self):
        """Send x keypress."""
        self._key(constants.KEY_X)

    def key_y(self):
        """Send y keypress."""
        self._key(constants.KEY_Y)

    def key_z(self):
        """Send z keypress."""
        self._key(constants.KEY_Z)

    # ======================================================================= #
    #                                                                         #
    #                              volume methods                             #
    #                                                                         #
    # ======================================================================= #
    def set_volume_level(self, volume_level, current_volume_level=None):
        """Set the volume to the desired level.

        .. note::

           This method works by sending volume up/down commands with a 1 second pause in between.  Without this pause,
           the device will do a quick power cycle.  This is the most robust solution I've found so far.


        Parameters
        ----------
        volume_level : float
            The new volume level (between 0 and 1)
        current_volume_level : float, None
            The current volume level (between 0 and 1); if it is not provided, it will be determined

        Returns
        -------
        float, None
            The new volume level (between 0 and 1), or ``None`` if ``self.max_volume`` could not be determined

        """
        # if necessary, determine the current volume and/or the max volume
        if current_volume_level is None or not self.max_volume:
            current_volume = self.volume
        else:
            current_volume = min(max(round(self.max_volume * current_volume_level), 0.), self.max_volume)

        # if `self.max_volume` or `current_volume` could not be determined, do not proceed
        if not self.max_volume or current_volume is None:
            return None

        new_volume = min(max(round(self.max_volume * volume_level), 0.), self.max_volume)

        # Case 1: the new volume is the same as the current volume
        if new_volume == current_volume:
            return new_volume / self.max_volume

        # Case 2: the new volume is less than the current volume
        if new_volume < current_volume:
            cmd = "(" + " && sleep 1 && ".join(["input keyevent {0}".format(constants.KEY_VOLUME_DOWN)] * int(current_volume - new_volume)) + ") &"

        # Case 3: the new volume is greater than the current volume
        else:
            cmd = "(" + " && sleep 1 && ".join(["input keyevent {0}".format(constants.KEY_VOLUME_UP)] * int(new_volume - current_volume)) + ") &"

        # send the volume down/up commands
        self._adb.shell(cmd)

        # return the new volume level
        return new_volume / self.max_volume

    def volume_up(self, current_volume_level=None):
        """Send volume up action.

        Parameters
        ----------
        current_volume_level : float, None
            The current volume level (between 0 and 1); if it is not provided, it will be determined

        Returns
        -------
        float, None
            The new volume level (between 0 and 1), or ``None`` if ``self.max_volume`` could not be determined

        """
        if current_volume_level is None or not self.max_volume:
            current_volume = self.volume
        else:
            current_volume = round(self.max_volume * current_volume_level)

        # send the volume up command
        self._key(constants.KEY_VOLUME_UP)

        # if `self.max_volume` or `current_volume` could not be determined, return `None` as the new `volume_level`
        if not self.max_volume or current_volume is None:
            return None

        # return the new volume level
        return min(current_volume + 1, self.max_volume) / self.max_volume

    def volume_down(self, current_volume_level=None):
        """Send volume down action.

        Parameters
        ----------
        current_volume_level : float, None
            The current volume level (between 0 and 1); if it is not provided, it will be determined

        Returns
        -------
        float, None
            The new volume level (between 0 and 1), or ``None`` if ``self.max_volume`` could not be determined

        """
        if current_volume_level is None or not self.max_volume:
            current_volume = self.volume
        else:
            current_volume = round(self.max_volume * current_volume_level)

        # send the volume down command
        self._key(constants.KEY_VOLUME_DOWN)

        # if `self.max_volume` or `current_volume` could not be determined, return `None` as the new `volume_level`
        if not self.max_volume or current_volume is None:
            return None

        # return the new volume level
        return max(current_volume - 1, 0.) / self.max_volume


# ======================================================================= #
#                                                                         #
#                    Validate the state detection rules                   #
#                                                                         #
# ======================================================================= #
def state_detection_rules_validator(rules, exc=KeyError):
    """Validate the rules (i.e., the ``state_detection_rules`` value) for a given app ID (i.e., a key in ``state_detection_rules``).

    For each ``rule`` in ``rules``, this function checks that:

    * ``rule`` is a string or a dictionary
    * If ``rule`` is a string:

        * Check that ``rule`` is in :py:const:`~androidtv.constants.VALID_STATES` or :py:const:`~androidtv.constants.VALID_STATE_PROPERTIES`

    * If ``rule`` is a dictionary:

        * Check that each key is in :py:const:`~androidtv.constants.VALID_STATES`
        * Check that each value is a dictionary

            * Check that each key is in :py:const:`~androidtv.constants.VALID_PROPERTIES`
            * Check that each value is of the right type, according to :py:const:`~androidtv.constants.VALID_PROPERTIES_TYPES`

    See :class:`~androidtv.basetv.BaseTV` for more info about the ``state_detection_rules`` parameter.

    Parameters
    ----------
    rules : list
        A list of the rules that will be used to determine the state
    exc : Exception
        The exception that will be raised if a rule is invalid

    Returns
    -------
    rules : list
        The provided list of rules

    """
    for rule in rules:
        # A rule must be either a string or a dictionary
        if not isinstance(rule, (str, dict)):
            raise exc("Expected a string or a map, got {}".format(type(rule).__name__))

        # If a rule is a string, check that it is valid
        if isinstance(rule, str):
            if rule not in constants.VALID_STATE_PROPERTIES + constants.VALID_STATES:
                raise exc("Invalid rule '{0}' is not in {1}".format(rule, constants.VALID_STATE_PROPERTIES + constants.VALID_STATES))

        # If a rule is a dictionary, check that it is valid
        else:
            for state, conditions in rule.items():
                # The keys of the dictionary must be valid states
                if state not in constants.VALID_STATES:
                    raise exc("'{0}' is not a valid state for the 'state_detection_rules' parameter".format(state))

                # The values of the dictionary must be dictionaries
                if not isinstance(conditions, dict):
                    raise exc("Expected a map for entry '{0}' in 'state_detection_rules', got {1}".format(state, type(conditions).__name__))

                for prop, value in conditions.items():
                    # The keys of the dictionary must be valid properties that can be checked
                    if prop not in constants.VALID_PROPERTIES:
                        raise exc("Invalid property '{0}' is not in {1}".format(prop, constants.VALID_PROPERTIES))

                    # Make sure the value is of the right type
                    if not isinstance(value, constants.VALID_PROPERTIES_TYPES[prop]):
                        raise exc("Conditional value for property '{0}' must be of type {1}, not {2}".format(prop, constants.VALID_PROPERTIES_TYPES[prop].__name__, type(value).__name__))

    return rules
