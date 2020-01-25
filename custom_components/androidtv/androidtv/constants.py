"""Constants used in the :class:`~androidtv.basetv.BaseTV`, :class:`~androidtv.androidtv.AndroidTV`, and :class:`~androidtv.firetv.FireTV` classes.

**Links**

* `ADB key event codes <https://developer.android.com/reference/android/view/KeyEvent>`_
* `MediaSession PlaybackState property <https://developer.android.com/reference/android/media/session/PlaybackState.html>`_

"""


import re


# Intents
INTENT_LAUNCH = "android.intent.category.LAUNCHER"
INTENT_HOME = "android.intent.category.HOME"


# echo '1' if the previous shell command was successful
CMD_SUCCESS1 = r" && echo -e '1\c'"

# echo '1' if the previous shell command was successful, echo '0' if it was not
CMD_SUCCESS1_FAILURE0 = r" && echo -e '1\c' || echo -e '0\c'"

#: Get the audio state
CMD_AUDIO_STATE = r"dumpsys audio | grep paused | grep -qv 'Buffer Queue' && echo -e '1\c' || (dumpsys audio | grep started | grep -qv 'Buffer Queue' && echo '2\c' || echo '0\c')"

#: Determine whether the device is awake
CMD_AWAKE = "dumpsys power | grep mWakefulness | grep -q Awake"

#: Get the current app
CMD_CURRENT_APP = "CURRENT_APP=$(dumpsys window windows | grep mCurrentFocus) && CURRENT_APP=${CURRENT_APP#*{* * } && CURRENT_APP=${CURRENT_APP%%/*} && echo $CURRENT_APP"

#: Launch an app if it is not already the current app
CMD_LAUNCH_APP = "CURRENT_APP=$(dumpsys window windows | grep mCurrentFocus) && CURRENT_APP=${{CURRENT_APP#*{{* * }} && CURRENT_APP=${{CURRENT_APP%%/*}} && if [ $CURRENT_APP != '{0}' ]; then monkey -p {0} -c " + INTENT_LAUNCH + " 1; fi"

#: Get the state from ``dumpsys media_session``; this assumes that the variable ``CURRENT_APP`` has been defined
CMD_MEDIA_SESSION_STATE = "dumpsys media_session | grep -A 100 'Sessions Stack' | grep -A 100 $CURRENT_APP | grep -m 1 'state=PlaybackState {'"

#: Determine the current app and get the state from ``dumpsys media_session``
CMD_MEDIA_SESSION_STATE_FULL = CMD_CURRENT_APP + " && " + CMD_MEDIA_SESSION_STATE

#: Get the running apps for an Android TV device
CMD_ANDROIDTV_RUNNING_APPS = "ps -A | grep u0_a"

#: Get the running apps for a Fire TV device
CMD_FIRETV_RUNNING_APPS = "ps | grep u0_a"

#: Determine if the device is on
CMD_SCREEN_ON = "(dumpsys power | grep 'Display Power' | grep -q 'state=ON' || dumpsys power | grep -q 'mScreenOn=true')"

#: Get the "STREAM_MUSIC" block from ``dumpsys audio``
CMD_STREAM_MUSIC = r"dumpsys audio | grep '\- STREAM_MUSIC:' -A 12"

#: Get the wake lock size
CMD_WAKE_LOCK_SIZE = "dumpsys power | grep Locks | grep 'size='"

#: Get the properties for an :py:class:`~androidtv.androidtv.AndroidTV` device (``lazy=True, get_running_apps=True``); see :py:meth:`androidtv.androidtv.AndroidTV.get_properties`
CMD_ANDROIDTV_PROPERTIES_LAZY_RUNNING_APPS = CMD_SCREEN_ON + CMD_SUCCESS1 + " && " + CMD_AWAKE + CMD_SUCCESS1 + " && (" + CMD_AUDIO_STATE + ") && " + CMD_WAKE_LOCK_SIZE + " && " + CMD_CURRENT_APP + " && (" + CMD_MEDIA_SESSION_STATE + " || echo) && " + CMD_STREAM_MUSIC + " && " + CMD_ANDROIDTV_RUNNING_APPS

#: Get the properties for an :py:class:`~androidtv.androidtv.AndroidTV` device (``lazy=True, get_running_apps=False``); see :py:meth:`androidtv.androidtv.AndroidTV.get_properties`
CMD_ANDROIDTV_PROPERTIES_LAZY_NO_RUNNING_APPS = CMD_SCREEN_ON + CMD_SUCCESS1 + " && " + CMD_AWAKE + CMD_SUCCESS1 + " && (" + CMD_AUDIO_STATE + ") && " + CMD_WAKE_LOCK_SIZE + " && " + CMD_CURRENT_APP + " && (" + CMD_MEDIA_SESSION_STATE + " || echo) && " + CMD_STREAM_MUSIC

#: Get the properties for an :py:class:`~androidtv.androidtv.AndroidTV` device (``lazy=False, get_running_apps=True``); see :py:meth:`androidtv.androidtv.AndroidTV.get_properties`
CMD_ANDROIDTV_PROPERTIES_NOT_LAZY_RUNNING_APPS = CMD_SCREEN_ON + CMD_SUCCESS1_FAILURE0 + " && " + CMD_AWAKE + CMD_SUCCESS1_FAILURE0 + " && (" + CMD_AUDIO_STATE + ") && " + CMD_WAKE_LOCK_SIZE + " && " + CMD_CURRENT_APP + " && (" + CMD_MEDIA_SESSION_STATE + " || echo) && " + CMD_STREAM_MUSIC + " && " + CMD_ANDROIDTV_RUNNING_APPS

#: Get the properties for an :py:class:`~androidtv.androidtv.AndroidTV` device (``lazy=False, get_running_apps=False``); see :py:meth:`androidtv.androidtv.AndroidTV.get_properties`
CMD_ANDROIDTV_PROPERTIES_NOT_LAZY_NO_RUNNING_APPS = CMD_SCREEN_ON + CMD_SUCCESS1_FAILURE0 + " && " + CMD_AWAKE + CMD_SUCCESS1_FAILURE0 + " && (" + CMD_AUDIO_STATE + ") && " + CMD_WAKE_LOCK_SIZE + " && " + CMD_CURRENT_APP + " && (" + CMD_MEDIA_SESSION_STATE + " || echo) && " + CMD_STREAM_MUSIC

#: Get the properties for a :py:class:`~androidtv.firetv.FireTV` device (``lazy=True, get_running_apps=True``); see :py:meth:`androidtv.firetv.FireTV.get_properties`
CMD_FIRETV_PROPERTIES_LAZY_RUNNING_APPS = CMD_SCREEN_ON + CMD_SUCCESS1 + " && " + CMD_AWAKE + CMD_SUCCESS1 + " && " + CMD_WAKE_LOCK_SIZE + " && " + CMD_CURRENT_APP + " && (" + CMD_MEDIA_SESSION_STATE + " || echo) && " + CMD_FIRETV_RUNNING_APPS

#: Get the properties for a :py:class:`~androidtv.firetv.FireTV` device (``lazy=True, get_running_apps=False``); see :py:meth:`androidtv.firetv.FireTV.get_properties`
CMD_FIRETV_PROPERTIES_LAZY_NO_RUNNING_APPS = CMD_SCREEN_ON + CMD_SUCCESS1 + " && " + CMD_AWAKE + CMD_SUCCESS1 + " && " + CMD_WAKE_LOCK_SIZE + " && " + CMD_CURRENT_APP + " && (" + CMD_MEDIA_SESSION_STATE + " || echo)"

#: Get the properties for a :py:class:`~androidtv.firetv.FireTV` device (``lazy=False, get_running_apps=True``); see :py:meth:`androidtv.firetv.FireTV.get_properties`
CMD_FIRETV_PROPERTIES_NOT_LAZY_RUNNING_APPS = CMD_SCREEN_ON + CMD_SUCCESS1_FAILURE0 + " && " + CMD_AWAKE + CMD_SUCCESS1_FAILURE0 + " && " + CMD_WAKE_LOCK_SIZE + " && " + CMD_CURRENT_APP + " && (" + CMD_MEDIA_SESSION_STATE + " || echo) && " + CMD_FIRETV_RUNNING_APPS

#: Get the properties for a :py:class:`~androidtv.firetv.FireTV` device (``lazy=False, get_running_apps=False``); see :py:meth:`androidtv.firetv.FireTV.get_properties`
CMD_FIRETV_PROPERTIES_NOT_LAZY_NO_RUNNING_APPS = CMD_SCREEN_ON + CMD_SUCCESS1_FAILURE0 + " && " + CMD_AWAKE + CMD_SUCCESS1_FAILURE0 + " && " + CMD_WAKE_LOCK_SIZE + " && " + CMD_CURRENT_APP + " && (" + CMD_MEDIA_SESSION_STATE + " || echo)"

# `getprop` commands
CMD_MANUFACTURER = "getprop ro.product.manufacturer"
CMD_MODEL = "getprop ro.product.model"
CMD_SERIALNO = "getprop ro.serialno"
CMD_VERSION = "getprop ro.build.version.release"

# Commands for getting the MAC address
CMD_MAC_WLAN0 = "ip addr show wlan0 | grep -m 1 ether"
CMD_MAC_ETH0 = "ip addr show eth0 | grep -m 1 ether"


# ADB key event codes
# https://developer.android.com/reference/android/view/KeyEvent
KEY_BACK = 4
KEY_BLUE = 186
KEY_CENTER = 23
KEY_COMPONENT1 = 249
KEY_COMPONENT2 = 250
KEY_COMPOSITE1 = 247
KEY_COMPOSITE2 = 248
KEY_DOWN = 20
KEY_END = 123
KEY_ENTER = 66
KEY_FAST_FORWARD = 90
KEY_GREEN = 184
KEY_HDMI1 = 243
KEY_HDMI2 = 244
KEY_HDMI3 = 245
KEY_HDMI4 = 246
KEY_HOME = 3
KEY_INPUT = 178
KEY_LEFT = 21
KEY_MENU = 82
KEY_MOVE_HOME = 122
KEY_MUTE = 164
KEY_NEXT = 87
KEY_PAIRING = 225
KEY_PAUSE = 127
KEY_PLAY = 126
KEY_PLAY_PAUSE = 85
KEY_POWER = 26
KEY_PREVIOUS = 88
KEY_RED = 183
KEY_RESUME = 224
KEY_REWIND = 89
KEY_RIGHT = 22
KEY_SAT = 237
KEY_SEARCH = 84
KEY_SETTINGS = 176
KEY_SLEEP = 223
KEY_SPACE = 62
KEY_STOP = 86
KEY_SUSPEND = 276
KEY_SYSDOWN = 281
KEY_SYSLEFT = 282
KEY_SYSRIGHT = 283
KEY_SYSUP = 280
KEY_TEXT = 233
KEY_TOP = 122
KEY_UP = 19
KEY_VGA = 251
KEY_VOLUME_DOWN = 25
KEY_VOLUME_UP = 24
KEY_YELLOW = 185


# Alphanumeric key event codes
KEY_0 = 7
KEY_1 = 8
KEY_2 = 9
KEY_3 = 10
KEY_4 = 11
KEY_5 = 12
KEY_6 = 13
KEY_7 = 14
KEY_8 = 15
KEY_9 = 16
KEY_A = 29
KEY_B = 30
KEY_C = 31
KEY_D = 32
KEY_E = 33
KEY_F = 34
KEY_G = 35
KEY_H = 36
KEY_I = 37
KEY_J = 38
KEY_K = 39
KEY_L = 40
KEY_M = 41
KEY_N = 42
KEY_O = 43
KEY_P = 44
KEY_Q = 45
KEY_R = 46
KEY_S = 47
KEY_T = 48
KEY_U = 49
KEY_V = 50
KEY_W = 51
KEY_X = 52
KEY_Y = 53
KEY_Z = 54


# Android TV keys
KEYS = {"BACK": KEY_BACK,
        "BLUE": KEY_BLUE,
        "CENTER": KEY_CENTER,
        "COMPONENT1": KEY_COMPONENT1,
        "COMPONENT2": KEY_COMPONENT2,
        "COMPOSITE1": KEY_COMPOSITE1,
        "COMPOSITE2": KEY_COMPOSITE2,
        "DOWN": KEY_DOWN,
        "END": KEY_END,
        "ENTER": KEY_ENTER,
        "FAST_FORWARD": KEY_FAST_FORWARD,
        "GREEN": KEY_GREEN,
        "HDMI1": KEY_HDMI1,
        "HDMI2": KEY_HDMI2,
        "HDMI3": KEY_HDMI3,
        "HDMI4": KEY_HDMI4,
        "HOME": KEY_HOME,
        "INPUT": KEY_INPUT,
        "LEFT": KEY_LEFT,
        "MENU": KEY_MENU,
        "MOVE_HOME": KEY_MOVE_HOME,
        "MUTE": KEY_MUTE,
        "PAIRING": KEY_PAIRING,
        "POWER": KEY_POWER,
        "RED": KEY_RED,
        "RESUME": KEY_RESUME,
        "REWIND": KEY_REWIND,
        "RIGHT": KEY_RIGHT,
        "SAT": KEY_SAT,
        "SEARCH": KEY_SEARCH,
        "SETTINGS": KEY_SETTINGS,
        "SLEEP": KEY_SLEEP,
        "SUSPEND": KEY_SUSPEND,
        "SYSDOWN": KEY_SYSDOWN,
        "SYSLEFT": KEY_SYSLEFT,
        "SYSRIGHT": KEY_SYSRIGHT,
        "SYSUP": KEY_SYSUP,
        "TEXT": KEY_TEXT,
        "TOP": KEY_TOP,
        "UP": KEY_UP,
        "VGA": KEY_VGA,
        "VOLUME_DOWN": KEY_VOLUME_DOWN,
        "VOLUME_UP": KEY_VOLUME_UP,
        "YELLOW": KEY_YELLOW}


# Android TV / Fire TV states
STATE_ON = 'on'
STATE_IDLE = 'idle'
STATE_OFF = 'off'
STATE_PLAYING = 'playing'
STATE_PAUSED = 'paused'
STATE_STANDBY = 'standby'
STATE_STOPPED = 'stopped'
STATE_UNKNOWN = 'unknown'

#: States that are valid (used by :func:`~androidtv.basetv.state_detection_rules_validator`)
VALID_STATES = (STATE_IDLE, STATE_OFF, STATE_PLAYING, STATE_PAUSED, STATE_STANDBY)

#: Properties that can be used to determine the current state (used by :func:`~androidtv.basetv.state_detection_rules_validator`)
VALID_STATE_PROPERTIES = ("audio_state", "media_session_state")

#: Properties that can be checked for custom state detection (used by :func:`~androidtv.basetv.state_detection_rules_validator`)
VALID_PROPERTIES = VALID_STATE_PROPERTIES + ("wake_lock_size",)

#: The required type for each entry in :py:const:`VALID_PROPERTIES` (used by :func:`~androidtv.basetv.state_detection_rules_validator`)
VALID_PROPERTIES_TYPES = {"audio_state": str,
                          "media_session_state": int,
                          "wake_lock_size": int}

# https://developer.android.com/reference/android/media/session/PlaybackState.html
#: States for the :attr:`~androidtv.basetv.BaseTV.media_session_state` property
MEDIA_SESSION_STATES = {0: None,
                        1: STATE_STOPPED,
                        2: STATE_PAUSED,
                        3: STATE_PLAYING}


# Apps
APP_AMAZON_VIDEO = 'com.amazon.avod'
APP_ATV_LAUNCHER = 'com.google.android.tvlauncher'
APP_BELL_FIBE = 'com.quickplay.android.bellmediaplayer'
APP_FIREFOX = 'org.mozilla.tv.firefox'
APP_FIRETV_PACKAGE_LAUNCHER = "com.amazon.tv.launcher"
APP_FIRETV_PACKAGE_SETTINGS = "com.amazon.tv.settings"
APP_GOOGLE_CAST = 'com.google.android.apps.mediashell'
APP_HBO_GO = 'eu.hbogo.androidtv.production'
APP_HULU = 'com.hulu.plus'
APP_JELLYFIN_TV = 'org.jellyfin.androidtv'
APP_KODI = 'org.xbmc.kodi'
APP_NETFLIX = 'com.netflix.ninja'
APP_PLEX = 'com.plexapp.android'
APP_SPORT1 = 'de.sport1.firetv.video'
APP_SPOTIFY = 'com.spotify.tv.android'
APP_TVHEADEND = 'de.cyberdream.dreamepg.tvh.tv.player'
APP_TWITCH = 'tv.twitch.android.viewer'
APP_VLC = 'org.videolan.vlc'
APP_VRV = 'com.ellation.vrv'
APP_WAIPU_TV = 'de.exaring.waipu.firetv.live'
APP_YOUTUBE = 'com.google.android.youtube.tv'
APPS = {APP_AMAZON_VIDEO: 'Amazon Video',
        APP_ATV_LAUNCHER: 'Android TV Launcher',
        APP_BELL_FIBE: 'Bell Fibe',
        APP_FIREFOX: 'Firefox',
        APP_GOOGLE_CAST: 'Google Cast',
        APP_HBO_GO: 'HBO GO',
        APP_HULU: 'Hulu',
        APP_JELLYFIN_TV: 'Jellyfin',
        APP_KODI: 'Kodi',
        APP_NETFLIX: 'Netflix',
        APP_PLEX: 'Plex',
        APP_SPORT1: 'Sport 1',
        APP_SPOTIFY: 'Spotify',
        APP_TVHEADEND: 'DreamPLayer TVHeadend',
        APP_TWITCH: 'Twitch',
        APP_VLC: 'VLC',
        APP_VRV: 'VRV',
        APP_WAIPU_TV: 'Waipu TV',
        APP_YOUTUBE: 'YouTube'}


# Regular expressions
REGEX_MEDIA_SESSION_STATE = re.compile(r"state=(?P<state>[0-9]+)", re.MULTILINE)
REGEX_WAKE_LOCK_SIZE = re.compile(r"size=(?P<size>[0-9]+)")

# Regular expression patterns
DEVICE_REGEX_PATTERN = r"Devices: (.*?)\W"
MAC_REGEX_PATTERN = "ether (.*?) brd"
MAX_VOLUME_REGEX_PATTERN = r"Max: (\d{1,})"
MUTED_REGEX_PATTERN = r"Muted: (.*?)\W"
STREAM_MUSIC_REGEX_PATTERN = "STREAM_MUSIC(.*?)- STREAM"
VOLUME_REGEX_PATTERN = r"\): (\d{1,})"

#: Default authentication timeout (in s) for :meth:`adb_shell.tcp_handle.TcpHandle.connect`
DEFAULT_AUTH_TIMEOUT_S = 0.1
