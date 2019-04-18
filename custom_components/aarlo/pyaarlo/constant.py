
DEVICES_URL         = 'https://arlo.netgear.com/hmsweb/users/devices'
DEFINITIONS_URL     = 'https://arlo.netgear.com/hmsweb/users/automation/definitions'
AUTOMATION_URL      = 'https://arlo.netgear.com/hmsweb/users/devices/automation/active'
LIBRARY_URL         = 'https://arlo.netgear.com/hmsweb/users/library'
LOGIN_URL           = 'https://arlo.netgear.com/hmsweb/login/v2'
LOGOUT_URL          = 'https://arlo.netgear.com/hmsweb/logout'
NOTIFY_URL          = 'https://arlo.netgear.com/hmsweb/users/devices/notify/'
SUBSCRIBE_URL       = 'https://arlo.netgear.com/hmsweb/client/subscribe?token='
UNSUBSCRIBE_URL     = 'https://arlo.netgear.com/hmsweb/client/unsubscribe'
MODES_URL           = 'https://arlo.netgear.com/hmsweb/users/devices/automation/active'
STREAM_SNAPSHOT_URL = 'https://arlo.netgear.com/hmsweb/users/devices/takeSnapshot'
STREAM_START_URL    = 'https://arlo.netgear.com/hmsweb/users/devices/startStream'
IDLE_SNAPSHOT_URL   = 'https://arlo.netgear.com/hmsweb/users/devices/fullFrameSnapshot'
TRANSID_PREFIX  = 'web'

PRELOAD_DAYS = 30
FAST_REFRESH_INTERVAL = (60)
SLOW_REFRESH_INTERVAL = (10*60)
EVENT_STREAM_TIMEOUT  = ((FAST_REFRESH_INTERVAL*2) + 5)

# update keys
ACTIVITY_STATE_KEY  = 'activityState'
AIR_QUALITY_KEY     = 'airQuality'
AUDIO_DETECTED_KEY  = 'audioDetected'
BATTERY_KEY         = 'batteryLevel'
BRIGHTNESS_KEY      = 'brightness'
CHARGER_KEY         = 'chargerTech'
CHARGING_KEY        = 'chargingState'
CONNECTION_KEY      = 'connectionState'
FLIP_KEY            = 'flip'
HUMIDITY_KEY        = 'humidity'
MIRROR_KEY          = 'mirror'
MOTION_DETECTED_KEY = 'motionDetected'
MOTION_ENABLED_KEY  = 'motionSetupModeEnabled'
MOTION_SENS_KEY     = 'motionSetupModeSensitivity'
POWER_SAVE_KEY      = 'powerSaveMode'
PRIVACY_KEY         = 'privacyActive'
SIGNAL_STR_KEY      = 'signalStrength'
TEMPERATURE_KEY     = 'temperature'

# we can get these from the resource; doorbell is subset
RESOURCE_KEYS = [ ACTIVITY_STATE_KEY, AIR_QUALITY_KEY, AUDIO_DETECTED_KEY, BATTERY_KEY,
                            BRIGHTNESS_KEY, CONNECTION_KEY, CHARGER_KEY, CHARGING_KEY, FLIP_KEY, HUMIDITY_KEY,
                            MIRROR_KEY, MOTION_DETECTED_KEY, MOTION_ENABLED_KEY,
                            MOTION_SENS_KEY, POWER_SAVE_KEY, PRIVACY_KEY,
                            SIGNAL_STR_KEY, TEMPERATURE_KEY ]

RESOURCE_UPDATE_KEYS = [ ACTIVITY_STATE_KEY, AIR_QUALITY_KEY, AUDIO_DETECTED_KEY, BATTERY_KEY, CHARGER_KEY, CHARGING_KEY,
                            HUMIDITY_KEY, MOTION_DETECTED_KEY, PRIVACY_KEY, SIGNAL_STR_KEY, TEMPERATURE_KEY ]

# device keys
DEVICE_ID_KEY       = 'deviceId'
DEVICE_NAME_KEY     = 'deviceName'
DEVICE_TYPE_KEY     = 'deviceType'
MEDIA_COUNT_KEY     = 'mediaObjectCount'
PARENT_ID_KEY       = 'parentId'
UNIQUE_ID_KEY       = 'uniqueId'
USER_ID_KEY         = 'userId'
LAST_IMAGE_KEY      = 'presignedLastImageUrl'
SNAPSHOT_KEY        = 'presignedFullFrameSnapshotUrl'
STREAM_SNAPSHOT_KEY = 'presignedContentUrl'
XCLOUD_ID_KEY       = 'xCloudId'

DEVICE_KEYS = [ DEVICE_ID_KEY, DEVICE_NAME_KEY, DEVICE_TYPE_KEY,
                    MEDIA_COUNT_KEY, PARENT_ID_KEY, UNIQUE_ID_KEY,
                    USER_ID_KEY, LAST_IMAGE_KEY, SNAPSHOT_KEY, XCLOUD_ID_KEY, ]

MEDIA_UPLOAD_KEYS = [ MEDIA_COUNT_KEY, LAST_IMAGE_KEY ]

# custom keys
CAPTURED_TODAY_KEY   = 'capturedToday'
LAST_CAPTURE_KEY     = 'lastCapture'
MODE_KEY             = 'activeMode'
MODES_KEY            = 'configuredMode'
LAST_IMAGE_DATA_KEY  = 'presignedLastImageData'
LAST_IMAGE_SRC_KEY   = 'lastImageSource'
MODE_NAME_TO_ID_KEY  = 'modeNameToId'
MODE_ID_TO_NAME_KEY  = 'modeIdToName'
TOTAL_BELLS_KEY      = 'totalDoorBells'
TOTAL_CAMERAS_KEY    = 'totalCameras'

BLANK_IMAGE = "iVBORw0KGgoAAAANSUhEUgAAAKAAAABaCAQAAACVz5XZAAAAh0lEQVR42u3QMQ0AAAgDMOZf9BDB" \
                    "RdJKaNrhIAIFChQoEIECBQpEoECBAhEoUKBABAoUKBCBAgUKRKBAgQIRKFCgQAQKFCgQgQIFCkSg" \
                    "QIECBSJQoECBCBQoUCACBQoUiECBAgUiUKBAgQgUKFAgAgUKFIhAgQIFIlCgQIEIFChQoECBAgV+" \
                    "tivOs6f/QsrFAAAAAElFTkSuQmCC"

#DEFAULT_MODES = [ { u'id':u'mode0',u'type':u'disarmed' }, { u'id':u'mode1',u'type':u'armed' } ]
DEFAULT_MODES = { 'disarmed':'mode0','armed':'mode1' }

