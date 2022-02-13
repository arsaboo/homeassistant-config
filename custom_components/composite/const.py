"""Constants for Composite Integration."""
DOMAIN = "composite"

CONF_REQ_MOVEMENT = "require_movement"
CONF_TIME_AS = "time_as"

TZ_UTC = "utc"
TZ_LOCAL = "local"
TZ_DEVICE_UTC = "device_or_utc"
TZ_DEVICE_LOCAL = "device_or_local"
# First item in list is default.
TIME_AS_OPTS = [TZ_UTC, TZ_LOCAL, TZ_DEVICE_UTC, TZ_DEVICE_LOCAL]
