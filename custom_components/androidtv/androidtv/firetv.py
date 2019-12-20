"""Communicate with an Amazon Fire TV device via ADB over a network.

ADB Debugging must be enabled.
"""


import logging

from .basetv import BaseTV
from . import constants

_LOGGER = logging.getLogger(__name__)


class FireTV(BaseTV):
    """Representation of an Amazon Fire TV device.

    Parameters
    ----------
    host : str
        The address of the device; may be an IP address or a host name
    port : int
        The device port to which we are connecting (default is 5555)
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

    DEVICE_CLASS = 'firetv'

    def __init__(self, host, port=5555, adbkey='', adb_server_ip='', adb_server_port=5037, state_detection_rules=None, auth_timeout_s=constants.DEFAULT_AUTH_TIMEOUT_S):
        BaseTV.__init__(self, host, port, adbkey, adb_server_ip, adb_server_port, state_detection_rules, auth_timeout_s)

    # ======================================================================= #
    #                                                                         #
    #                          Home Assistant Update                          #
    #                                                                         #
    # ======================================================================= #
    def update(self, get_running_apps=True):
        """Get the info needed for a Home Assistant update.

        Parameters
        ----------
        get_running_apps : bool
            Whether or not to get the :attr:`~androidtv.basetv.BaseTV.running_apps` property

        Returns
        -------
        state : str
            The state of the device
        current_app : str
            The current running app
        running_apps : list
            A list of the running apps if ``get_running_apps`` is True, otherwise the list ``[current_app]``

        """
        # Get the properties needed for the update
        screen_on, awake, wake_lock_size, current_app, media_session_state, running_apps = self.get_properties(get_running_apps=get_running_apps, lazy=True)

        # Check if device is unavailable
        if screen_on is None:
            state = None
            current_app = None
            running_apps = None

        # Check if device is off
        elif not screen_on:
            state = constants.STATE_OFF
            current_app = None
            running_apps = None

        # Check if screen saver is on
        elif not awake:
            state = constants.STATE_IDLE
            current_app = None
            running_apps = None

        else:
            # Get the running apps
            if not running_apps and current_app:
                running_apps = [current_app]

            # Determine the state using custom rules
            state = self._custom_state_detection(current_app=current_app, media_session_state=media_session_state, wake_lock_size=wake_lock_size)
            if state:
                return state, current_app, running_apps

            # Determine the state based on the `current_app`
            if current_app in [constants.APP_FIRETV_PACKAGE_LAUNCHER, constants.APP_FIRETV_PACKAGE_SETTINGS, None]:
                state = constants.STATE_STANDBY

            # Amazon Video
            elif current_app == constants.APP_AMAZON_VIDEO:
                if wake_lock_size == 5:
                    state = constants.STATE_PLAYING
                else:
                    # wake_lock_size == 2
                    state = constants.STATE_PAUSED

            # Firefox
            elif current_app == constants.APP_FIREFOX:
                if wake_lock_size == 3:
                    state = constants.STATE_PLAYING
                else:
                    state = constants.STATE_STANDBY

            # Hulu
            elif current_app == constants.APP_HULU:
                if wake_lock_size == 4:
                    state = constants.STATE_PLAYING
                elif wake_lock_size == 2:
                    state = constants.STATE_PAUSED
                else:
                    state = constants.STATE_STANDBY

            # Jellyfin
            elif current_app == constants.APP_JELLYFIN_TV:
                if wake_lock_size == 2:
                    state = constants.STATE_PLAYING
                else:
                    state = constants.STATE_PAUSED

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
                if media_session_state == 3:
                    if wake_lock_size == 2:
                        state = constants.STATE_PAUSED
                    else:
                        state = constants.STATE_PLAYING
                else:
                    state = constants.STATE_STANDBY

            # Sport 1
            elif current_app == constants.APP_SPORT1:
                if wake_lock_size == 2:
                    state = constants.STATE_PAUSED
                elif wake_lock_size == 3:
                    state = constants.STATE_PLAYING
                else:
                    state = constants.STATE_STANDBY

            # Spotify
            elif current_app == constants.APP_SPOTIFY:
                if media_session_state == 2:
                    state = constants.STATE_PAUSED
                elif media_session_state == 3:
                    state = constants.STATE_PLAYING
                else:
                    state = constants.STATE_STANDBY

            # Twitch
            elif current_app == constants.APP_TWITCH:
                if wake_lock_size == 2:
                    state = constants.STATE_PAUSED
                elif media_session_state == 3:
                    state = constants.STATE_PLAYING
                elif media_session_state == 4:
                    state = constants.STATE_PLAYING
                else:
                    state = constants.STATE_STANDBY

            # Waipu TV
            elif current_app == constants.APP_WAIPU_TV:
                if wake_lock_size == 2:
                    state = constants.STATE_PAUSED
                elif wake_lock_size == 3:
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

            # Get the state from `wake_lock_size`
            else:
                if wake_lock_size == 1:
                    state = constants.STATE_PLAYING
                else:
                    state = constants.STATE_PAUSED

        return state, current_app, running_apps

    # ======================================================================= #
    #                                                                         #
    #                               properties                                #
    #                                                                         #
    # ======================================================================= #
    def get_properties(self, get_running_apps=True, lazy=False):
        """Get the properties needed for Home Assistant updates.

        This will send one of the following ADB commands:

        * :py:const:`androidtv.constants.CMD_FIRETV_PROPERTIES_LAZY_RUNNING_APPS`
        * :py:const:`androidtv.constants.CMD_FIRETV_PROPERTIES_LAZY_NO_RUNNING_APPS`
        * :py:const:`androidtv.constants.CMD_FIRETV_PROPERTIES_NOT_LAZY_RUNNING_APPS`
        * :py:const:`androidtv.constants.CMD_FIRETV_PROPERTIES_NOT_LAZY_NO_RUNNING_APPS`

        Parameters
        ----------
        get_running_apps : bool
            Whether or not to get the :attr:`~androidtv.basetv.BaseTV.running_apps` property
        lazy : bool
            Whether or not to continue retrieving properties if the device is off or the screensaver is running

        Returns
        -------
        screen_on : bool, None
            Whether or not the device is on, or ``None`` if it was not determined
        awake : bool, None
            Whether or not the device is awake (screensaver is not running), or ``None`` if it was not determined
        wake_lock_size : int, None
            The size of the current wake lock, or ``None`` if it was not determined
        current_app : str, None
            The current app property, or ``None`` if it was not determined
        media_session_state : int, None
            The state from the output of ``dumpsys media_session``, or ``None`` if it was not determined
        running_apps : list, None
            A list of the running apps, or ``None`` if it was not determined

        """
        if lazy:
            if get_running_apps:
                output = self._adb.shell(constants.CMD_FIRETV_PROPERTIES_LAZY_RUNNING_APPS)
            else:
                output = self._adb.shell(constants.CMD_FIRETV_PROPERTIES_LAZY_NO_RUNNING_APPS)
        else:
            if get_running_apps:
                output = self._adb.shell(constants.CMD_FIRETV_PROPERTIES_NOT_LAZY_RUNNING_APPS)
            else:
                output = self._adb.shell(constants.CMD_FIRETV_PROPERTIES_NOT_LAZY_NO_RUNNING_APPS)
        _LOGGER.debug("Fire TV %s:%d `get_properties` response: %s", self.host, self.port, output)

        # ADB command was unsuccessful
        if output is None:
            return None, None, None, None, None, None

        # `screen_on` property
        if not output:
            return False, False, -1, None, None, None
        screen_on = output[0] == '1'

        # `awake` property
        if len(output) < 2:
            return screen_on, False, -1, None, None, None
        awake = output[1] == '1'

        lines = output.strip().splitlines()

        # `wake_lock_size` property
        if len(lines[0]) < 3:
            return screen_on, awake, -1, None, None, None
        wake_lock_size = self._wake_lock_size(lines[0])

        # `current_app` property
        if len(lines) < 2:
            return screen_on, awake, wake_lock_size, None, None, None
        current_app = self._current_app(lines[1])

        # `media_session_state` property
        if len(lines) < 3:
            return screen_on, awake, wake_lock_size, current_app, None, None
        media_session_state = self._media_session_state(lines[2], current_app)

        # `running_apps` property
        if not get_running_apps or len(lines) < 4:
            return screen_on, awake, wake_lock_size, current_app, media_session_state, None
        running_apps = self._running_apps(lines[3:])

        return screen_on, awake, wake_lock_size, current_app, media_session_state, running_apps

    def get_properties_dict(self, get_running_apps=True, lazy=True):
        """Get the properties needed for Home Assistant updates and return them as a dictionary.

        Parameters
        ----------
        get_running_apps : bool
            Whether or not to get the :attr:`~androidtv.basetv.BaseTV.running_apps` property
        lazy : bool
            Whether or not to continue retrieving properties if the device is off or the screensaver is running

        Returns
        -------
        dict
             A dictionary with keys ``'screen_on'``, ``'awake'``, ``'wake_lock_size'``, ``'current_app'``,
             ``'media_session_state'``, and ``'running_apps'``

        """
        screen_on, awake, wake_lock_size, current_app, media_session_state, running_apps = self.get_properties(get_running_apps=get_running_apps, lazy=lazy)

        return {'screen_on': screen_on,
                'awake': awake,
                'wake_lock_size': wake_lock_size,
                'current_app': current_app,
                'media_session_state': media_session_state,
                'running_apps': running_apps}

    # ======================================================================= #
    #                                                                         #
    #                               Properties                                #
    #                                                                         #
    # ======================================================================= #
    @property
    def running_apps(self):
        """Return a list of running user applications.

        Returns
        -------
        list
            A list of the running apps

        """
        running_apps_response = self._adb.shell(constants.CMD_FIRETV_RUNNING_APPS)

        return self._running_apps(running_apps_response)

    # ======================================================================= #
    #                                                                         #
    #                           turn on/off methods                           #
    #                                                                         #
    # ======================================================================= #
    def turn_on(self):
        """Send ``POWER`` and ``HOME`` actions if the device is off."""
        self._adb.shell(constants.CMD_SCREEN_ON + " || (input keyevent {0} && input keyevent {1})".format(constants.KEY_POWER, constants.KEY_HOME))

    def turn_off(self):
        """Send ``SLEEP`` action if the device is not off."""
        self._adb.shell(constants.CMD_SCREEN_ON + " && input keyevent {0}".format(constants.KEY_SLEEP))
