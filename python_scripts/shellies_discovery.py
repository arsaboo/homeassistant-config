"""
This script adds MQTT discovery support for Shellies devices.
"""
ATTR_MANUFACTURER = "Allterco Robotics"
ATTR_POWER_AC = "ac"
ATTR_RELAY = "relay"
ATTR_ROLLER = "roller"
ATTR_SHELLY = "Shelly"

COMP_FAN = "fan"
COMP_LIGHT = "light"
COMP_SWITCH = "switch"

CONF_DEVELOP = "develop"
CONF_DISCOVERY_PREFIX = "discovery_prefix"
CONF_EXPIRE_AFTER = "expire_after"
CONF_FORCE_UPDATE_SENSORS = "force_update_sensors"
CONF_FRIENDLY_NAME = "friendly_name"
CONF_FW_VER = "fw_ver"
CONF_ID = "id"
CONF_MODEL_ID = "model"
CONF_IGNORED_DEVICES = "ignored_devices"
CONF_MAC = "mac"
CONF_MODE = "mode"
CONF_POWERED = "powered"
CONF_PUSH_OFF_DELAY = "push_off_delay"
CONF_QOS = "qos"

DEFAULT_DISC_PREFIX = "homeassistant"

DEVICE_CLASS_AWNING = "awning"
DEVICE_CLASS_BATTERY = "battery"
DEVICE_CLASS_BATTERY_CHARGING = "battery_charging"
DEVICE_CLASS_BLIND = "blind"
DEVICE_CLASS_COLD = "cold"
DEVICE_CLASS_CONNECTIVITY = "connectivity"
DEVICE_CLASS_CURRENT = "current"
DEVICE_CLASS_CURTAIN = "curtain"
DEVICE_CLASS_DAMPER = "damper"
DEVICE_CLASS_DOOR = "door"
DEVICE_CLASS_ENERGY = "energy"
DEVICE_CLASS_GARAGE = "garage"
DEVICE_CLASS_GARAGE_DOOR = "garage_door"
DEVICE_CLASS_GAS = "gas"
DEVICE_CLASS_GATE = "gate"
DEVICE_CLASS_HEAT = "heat"
DEVICE_CLASS_HUMIDITY = "humidity"
DEVICE_CLASS_ILLUMINANCE = "illuminance"
DEVICE_CLASS_LIGHT = "light"
DEVICE_CLASS_LOCK = "lock"
DEVICE_CLASS_MOISTURE = "moisture"
DEVICE_CLASS_MOTION = "motion"
DEVICE_CLASS_MOVING = "moving"
DEVICE_CLASS_OCCUPANCY = "occupancy"
DEVICE_CLASS_OPENING = "opening"
DEVICE_CLASS_PLUG = "plug"
DEVICE_CLASS_POWER = "power"
DEVICE_CLASS_POWER_FACTOR = "power_factor"
DEVICE_CLASS_PRESENCE = "presence"
DEVICE_CLASS_PRESSURE = "pressure"
DEVICE_CLASS_PROBLEM = "problem"
DEVICE_CLASS_SAFETY = "safety"
DEVICE_CLASS_SHADE = "shade"
DEVICE_CLASS_SHUTTER = "shutter"
DEVICE_CLASS_SIGNAL_STRENGTH = "signal_strength"
DEVICE_CLASS_SMOKE = "smoke"
DEVICE_CLASS_SOUND = "sound"
DEVICE_CLASS_TEMPERATURE = "temperature"
DEVICE_CLASS_TIMESTAMP = "timestamp"
DEVICE_CLASS_VIBRATION = "vibration"
DEVICE_CLASS_VOLTAGE = "voltage"
DEVICE_CLASS_WINDOW = "window"

EXPIRE_AFTER_FOR_BATTERY_POWERED = 43200
EXPIRE_AFTER_FOR_AC_POWERED = 7200

KEY_AVAILABILITY_TOPIC = "avty_t"
KEY_COMMAND_TOPIC = "cmd_t"
KEY_DEVICE = "dev"
KEY_DEVICE_CLASS = "dev_cla"
KEY_EXPIRE_AFTER = "exp_aft"
KEY_FORCE_UPDATE = "frc_upd"
KEY_ICON = "icon"
KEY_IDENTIFIERS = "ids"
KEY_JSON_ATTRIBUTES_TEMPLATE = "json_attr_tpl"
KEY_JSON_ATTRIBUTES_TOPIC = "json_attr_t"
KEY_MANUFACTURER = "mf"
KEY_MODEL = "mdl"
KEY_NAME = "name"
KEY_OFF_DELAY = "off_dly"
KEY_OPTIMISTIC = "opt"
KEY_PAYLOAD = "payload"
KEY_PAYLOAD_AVAILABLE = "pl_avail"
KEY_PAYLOAD_CLOSE = "pl_cls"
KEY_PAYLOAD_NOT_AVAILABLE = "pl_not_avail"
KEY_PAYLOAD_OFF = "pl_off"
KEY_PAYLOAD_ON = "pl_on"
KEY_PAYLOAD_OPEN = "pl_open"
KEY_PAYLOAD_STOP = "pl_stop"
KEY_POSITION_TOPIC = "pos_t"
KEY_QOS = "qos"
KEY_RETAIN = "retain"
KEY_SET_POSITION_TOPIC = "set_pos_t"
KEY_STATE_TEMPLATE = "stat_tpl"
KEY_STATE_TOPIC = "stat_t"
KEY_SW_VERSION = "sw"
KEY_TOPIC = "topic"
KEY_UNIQUE_ID = "uniq_id"
KEY_UNIT = "unit_of_meas"
KEY_VALUE_TEMPLATE = "val_tpl"

LIGHT_RGBW = "rgbw"
LIGHT_WHITE = "white"

# Firmware 1.6.5 release date
MIN_4PRO_FIRMWARE_DATE = 20200408

# Firmware 1.8.0 release date
MIN_FIRMWARE_DATE = 20200812

MODEL_SHELLY1 = f"{ATTR_SHELLY} 1"
MODEL_SHELLY1L = f"{ATTR_SHELLY} 1L"
MODEL_SHELLY1PM = f"{ATTR_SHELLY} 1PM"
MODEL_SHELLY2 = f"{ATTR_SHELLY} 2"
MODEL_SHELLY25 = f"{ATTR_SHELLY} 2.5"
MODEL_SHELLY3EM = f"{ATTR_SHELLY} 3EM"
MODEL_SHELLY4PRO = f"{ATTR_SHELLY} 4Pro"
MODEL_SHELLYAIR = f"{ATTR_SHELLY} Air"
MODEL_SHELLYBULB = f"{ATTR_SHELLY} Bulb"
MODEL_SHELLYBUTTON1 = f"{ATTR_SHELLY} Button1"
MODEL_SHELLYDIMMER = f"{ATTR_SHELLY} Dimmer"
MODEL_SHELLYDIMMER2 = f"{ATTR_SHELLY} Dimmer 2"
MODEL_SHELLYDUO = f"{ATTR_SHELLY} DUO"
MODEL_SHELLYDW = f"{ATTR_SHELLY} Door/Window"
MODEL_SHELLYDW2 = f"{ATTR_SHELLY} Door/Window 2"
MODEL_SHELLYEM = f"{ATTR_SHELLY} EM"
MODEL_SHELLYFLOOD = f"{ATTR_SHELLY} Flood"
MODEL_SHELLYGAS = f"{ATTR_SHELLY} Gas"
MODEL_SHELLYHT = f"{ATTR_SHELLY} H&T"
MODEL_SHELLYI3 = f"{ATTR_SHELLY} i3"
MODEL_SHELLYPLUG = f"{ATTR_SHELLY} Plug"
MODEL_SHELLYPLUG_S = f"{ATTR_SHELLY} Plug S"
MODEL_SHELLYPLUG_US = f"{ATTR_SHELLY} Plug US"
MODEL_SHELLYRGBW2 = f"{ATTR_SHELLY} RGBW2"
MODEL_SHELLYSENSE = f"{ATTR_SHELLY} Sense"
MODEL_SHELLYSMOKE = f"{ATTR_SHELLY} Smoke"
MODEL_SHELLYUNI = f"{ATTR_SHELLY} UNI"
MODEL_SHELLYVINTAGE = f"{ATTR_SHELLY} Vintage"

MODEL_SHELLY1_ID = "SHSW-1"  # Shelly 1
MODEL_SHELLY1_PREFIX = "shelly1"

MODEL_SHELLY1L_ID = "SHSW-L"  # Shelly 1L
MODEL_SHELLY1L_PREFIX = "shelly1l"

MODEL_SHELLY1PM_ID = "SHSW-PM"  # Shelly 1PM
MODEL_SHELLY1PM_PREFIX = "shelly1pm"

MODEL_SHELLY2_ID = "SHSW-21"  # Shelly 2
MODEL_SHELLY2_PREFIX = "shellyswitch"

MODEL_SHELLY25_ID = "SHSW-25"  # Shelly 2.5
MODEL_SHELLY25_PREFIX = "shellyswitch25"

MODEL_SHELLY3EM_ID = "SHEM-3"  # Shelly 3EM
MODEL_SHELLY3EM_PREFIX = "shellyem3"

MODEL_SHELLY4PRO_ID = "SHSW-44"  # Shelly 4Pro
MODEL_SHELLY4PRO_PREFIX = "shelly4pro"

MODEL_SHELLYAIR_ID = "SHAIR-1"  # Shelly Air
MODEL_SHELLYAIR_PREFIX = "shellyair"

MODEL_SHELLYBULB_ID = "SHBLB-1"  # Shelly Bulb
MODEL_SHELLYBULB_PREFIX = "shellybulb"

MODEL_SHELLYBUTTON1_ID = "SHBTN-1"  # Shelly Button1
MODEL_SHELLYBUTTON1_PREFIX = "shellybutton1"

MODEL_SHELLYDIMMER_ID = "SHDM-1"  # Shelly Dimmer
MODEL_SHELLYDIMMER_PREFIX = "shellydimmer"

MODEL_SHELLYDIMMER2_ID = "SHDM-2"  # Shelly Dimmer 2
MODEL_SHELLYDIMMER2_PREFIX = "shellydimmer2"

MODEL_SHELLYDUO_ID = "SHBDUO-1"  # Shelly Duo
MODEL_SHELLYDUO_PREFIX = "shellybulbduo"

MODEL_SHELLYDW_ID = "SHDW-1"  # Shelly Door/Window
MODEL_SHELLYDW_PREFIX = "shellydw"

MODEL_SHELLYDW2_ID = "SHDW-2"  # Shelly Door/Window 2
MODEL_SHELLYDW2_PREFIX = "shellydw2"

MODEL_SHELLYEM_ID = "SHEM"  # Shelly EM
MODEL_SHELLYEM_PREFIX = "shellyem"

MODEL_SHELLYFLOOD_ID = "SHWT-1"  # Shelly Flood
MODEL_SHELLYFLOOD_PREFIX = "shellyflood"

MODEL_SHELLYGAS_ID = "SHGS-1"  # Shelly Gas
MODEL_SHELLYGAS_PREFIX = "shellygas"

MODEL_SHELLYHT_ID = "SHHT-1"  # Shelly H&T
MODEL_SHELLYHT_PREFIX = "shellyht"

MODEL_SHELLYI3_ID = "SHIX3-1"  # Shelly i3
MODEL_SHELLYI3_PREFIX = "shellyix3"

MODEL_SHELLYPLUG_ID = "SHPLG-1"  # Shelly Plug
MODEL_SHELLYPLUG_E_ID = "SHPLG2-1"  # Shelly Plug E
MODEL_SHELLYPLUG_PREFIX = "shellyplug"

MODEL_SHELLYPLUG_S_ID = "SHPLG-S"  # Shelly Plug S
MODEL_SHELLYPLUG_S_PREFIX = "shellyplug-s"

MODEL_SHELLYPLUG_US_ID = "SHPLG-U1"  # Shelly Plug US
MODEL_SHELLYPLUG_US_PREFIX = "shellyplug-u1"

MODEL_SHELLYRGBW2_ID = "SHRGBW2"  # Shelly RGBW2
MODEL_SHELLYRGBW2_PREFIX = "shellyrgbw2"

MODEL_SHELLYSENSE_ID = "SHSEN-1"  # Shelly Sense
MODEL_SHELLYSENSE_PREFIX = "shellysense"

MODEL_SHELLYSMOKE_ID = "SHSM-01"  # Shelly Smoke
MODEL_SHELLYSMOKE_PREFIX = "shellysmoke"

MODEL_SHELLYVINTAGE_ID = "SHVIN-1"  # Shelly Vintage
MODEL_SHELLYVINTAGE_PREFIX = "shellyvintage"

MODEL_SHELLYUNI_ID = "SHUNI-1"  # Shelly UNI
MODEL_SHELLYUNI_PREFIX = "shellyuni"

OFF_DELAY = 2

SENSOR_ADC = "adc"
SENSOR_BATTERY = "battery"
SENSOR_CHARGER = "charger"
SENSOR_CONCENTRATION = "concentration"
SENSOR_CURRENT = "current"
SENSOR_DOUBLE_SHORTPUSH = "double shortpush"
SENSOR_DOUBLE_SHORTPUSH_0 = "double shortpush 0"
SENSOR_DOUBLE_SHORTPUSH_1 = "double shortpush 1"
SENSOR_DOUBLE_SHORTPUSH_2 = "double shortpush 2"
SENSOR_ENERGY = "energy"
SENSOR_EXT_HUMIDITY = "ext_humidity"
SENSOR_EXT_TEMPERATURE = "ext_temperature"
SENSOR_FIRMWARE_UPDATE = "firmware update"
SENSOR_FLOOD = "flood"
SENSOR_GAS = "gas"
SENSOR_HUMIDITY = "humidity"
SENSOR_ILLUMINATION = "illumination"
SENSOR_INPUT = "input"
SENSOR_INPUT_0 = "input 0"
SENSOR_INPUT_1 = "input 1"
SENSOR_INPUT_2 = "input 2"
SENSOR_LOADERROR = "loaderror"
SENSOR_LONGPUSH = "longpush"
SENSOR_LONGPUSH_0 = "longpush 0"
SENSOR_LONGPUSH_1 = "longpush 1"
SENSOR_LONGPUSH_2 = "longpush 2"
SENSOR_LONGPUSH_SHORTPUSH_0 = "longpush shortpush 0"
SENSOR_LONGPUSH_SHORTPUSH_1 = "longpush shortpush 1"
SENSOR_LONGPUSH_SHORTPUSH_2 = "longpush shortpush 2"
SENSOR_LUX = "lux"
SENSOR_MOTION = "motion"
SENSOR_OPENING = "opening"
SENSOR_OPERATION = "operation"
SENSOR_OVERLOAD = "overload"
SENSOR_OVERPOWER = "overpower"
SENSOR_OVERTEMPERATURE = "overtemperature"
SENSOR_POWER = "power"
SENSOR_POWER_FACTOR = "pf"
SENSOR_REACTIVE_POWER = "reactive_power"
SENSOR_RETURNED_ENERGY = "returned_energy"
SENSOR_RSSI = "rssi"
SENSOR_SELF_TEST = "self_test"
SENSOR_SHORTPUSH = "shortpush"
SENSOR_SHORTPUSH_0 = "shortpush/0"
SENSOR_SHORTPUSH_1 = "shortpush/1"
SENSOR_SHORTPUSH_2 = "shortpush/2"
SENSOR_SHORTPUSH_LONGPUSH_0 = "shortpush longpush 0"
SENSOR_SHORTPUSH_LONGPUSH_1 = "shortpush longpush 1"
SENSOR_SHORTPUSH_LONGPUSH_2 = "shortpush longpush 2"
SENSOR_SMOKE = "smoke"
SENSOR_SSID = "ssid"
SENSOR_TEMPERATURE = "temperature"
SENSOR_TILT = "tilt"
SENSOR_TOTAL = "total"
SENSOR_TOTALWORKTIME = "totalworktime"
SENSOR_TOTAL_RETURNED = "total_returned"
SENSOR_TRIPLE_SHORTPUSH = "triple shortpush"
SENSOR_TRIPLE_SHORTPUSH_0 = "triple shortpush 0"
SENSOR_TRIPLE_SHORTPUSH_1 = "triple shortpush 1"
SENSOR_TRIPLE_SHORTPUSH_2 = "triple shortpush 2"
SENSOR_UPTIME = "uptime"
SENSOR_VIBRATION = "vibration"
SENSOR_VOLTAGE = "voltage"

TOPIC_ADC = "adc/0"
TOPIC_ANNOUNCE = "announce"
TOPIC_COLOR_0_STATUS = "color/0/status"
TOPIC_INFO = "info"
TOPIC_INPUT_0 = "input/0"
TOPIC_INPUT_1 = "input/1"
TOPIC_INPUT_2 = "input/2"
TOPIC_INPUT_EVENT_0 = "input_event/0"
TOPIC_INPUT_EVENT_1 = "input_event/1"
TOPIC_INPUT_EVENT_2 = "input_event/2"
TOPIC_LONGPUSH = "longpush"
TOPIC_LONGPUSH_0 = "longpush/0"
TOPIC_LONGPUSH_1 = "longpush/1"
TOPIC_LONGPUSH_2 = "longpush/2"
TOPIC_OVERPOWER_VALUE = "overpower_value"
TOPIC_RELAY = "relay"

TPL_BATTERY = "{{value|float|round}}"
TPL_CONCENTRATION = "{%if 0<=value|int<=65535%}{{value}}{%endif%}"
TPL_CURRENT = "{{value|float|round(2)}}"
TPL_DOUBLE_SHORTPUSH = "{%if value_json.event==^SS^%}ON{%else%}OFF{%endif%}"
TPL_ENERGY_WH = "{{(value|float/1000)|round(2)}}"
TPL_ENERGY_WMIN = "{{(value|float/60/1000)|round(2)}}"
TPL_GAS = "{%if value in [^mild^,^heavy^]%}ON{%else%}OFF{%endif%}"
TPL_GAS_TO_JSON = "{{{^status^:value}|tojson}}"
TPL_HUMIDITY = "{{value|float|round(1)}}"
TPL_HUMIDITY_EXT = "{%if value!=999%}{{value|float|round(1)}}{%endif%}"
TPL_ILLUMINATION_TO_JSON = "{{{^illumination^:value}|tojson}}"
TPL_LONGPUSH = "{%if value_json.event==^L^%}ON{%else%}OFF{%endif%}"
TPL_LONGPUSH_SHORTPUSH = "{%if value_json.event==^LS^%}ON{%else%}OFF{%endif%}"
TPL_LUX = "{{value|float|round}}"
TPL_NEW_FIRMWARE_FROM_ANNOUNCE = "{%if value_json.new_fw==true%}ON{%else%}OFF{%endif%}"
TPL_NEW_FIRMWARE_FROM_INFO = (
    "{%if value_json[^update^].has_update==true%}ON{%else%}OFF{%endif%}"
)
TPL_OVERPOWER = "{%if value_json.overpower==true%}ON{%else%}OFF{%endif%}"
TPL_OVERPOWER_RELAY = "{%if value==^overpower^%}ON{%else%}OFF{%endif%}"
TPL_OVERPOWER_VALUE_TO_JSON = "{{{^overpower_value^:value}|tojson}}"
TPL_POSITION = "{%if value!=-1%}{{value}}{%endif%}"
TPL_POWER = "{{value|float|round(1)}}"
TPL_POWER_FACTOR = "{{value|float*100|round}}"
TPL_ROLLER_TO_JSON = "{{{^roller_state^:value}|tojson}}"
TPL_RSSI = "{{value_json[^wifi_sta^].rssi}}"
TPL_SHORTPUSH = "{%if value_json.event==^S^%}ON{%else%}OFF{%endif%}"
TPL_SHORTPUSH_LONGPUSH = "{%if value_json.event==^SL^%}ON{%else%}OFF{%endif%}"
TPL_SSID = "{{value_json[^wifi_sta^].ssid}}"
TPL_TEMPERATURE = "{{value|float|round(1)}}"
TPL_TEMPERATURE_EXT = "{%if value != 999%}{{value|float|round(1)}}{%endif%}"
TPL_TILT = "{{value|float}}"
TPL_TRIPLE_SHORTPUSH = "{%if value_json.event==^SSS^%}ON{%else%}OFF{%endif%}"
TPL_UPDATE_TO_JSON = "{{value_json[^update^]|tojson}}"
TPL_UPTIME = "{{(as_timestamp(now())-value_json.uptime)|timestamp_local}}"
TPL_VOLTAGE = "{{value|float|round(1)}}"

UNIT_AMPERE = "A"
UNIT_CELSIUS = "°C"
UNIT_DB = "dB"
UNIT_DEGREE = "°"
UNIT_KWH = "kWh"
UNIT_LUX = "lx"
UNIT_PERCENT = "%"
UNIT_PPM = "ppm"
UNIT_SECOND = "s"
UNIT_VAR = "VAR"
UNIT_VOLT = "V"
UNIT_WATT = "W"

VALUE_CLOSE = "close"
VALUE_FALSE = "false"
VALUE_OFF = "off"
VALUE_ON = "on"
VALUE_OPEN = "open"
VALUE_STOP = "stop"
VALUE_TRUE = "true"

PL_0_1 = {VALUE_ON: "0", VALUE_OFF: "1"}
PL_1_0 = {VALUE_ON: "1", VALUE_OFF: "0"}
PL_OPEN_CLOSE = {VALUE_ON: VALUE_OPEN, VALUE_OFF: VALUE_CLOSE}
PL_TRUE_FALSE = {VALUE_ON: VALUE_TRUE, VALUE_OFF: VALUE_FALSE}

ROLLER_DEVICE_CLASSES = [
    DEVICE_CLASS_AWNING,
    DEVICE_CLASS_BLIND,
    DEVICE_CLASS_CURTAIN,
    DEVICE_CLASS_DAMPER,
    DEVICE_CLASS_DOOR,
    DEVICE_CLASS_GARAGE,
    DEVICE_CLASS_GATE,
    DEVICE_CLASS_SHADE,
    DEVICE_CLASS_SHUTTER,
    DEVICE_CLASS_WINDOW,
]


def parse_version(version):
    """Parse version string and return version date integer."""
    return int(version.split("-", 1)[0])


def get_device_config(dev_id):
    """Get device configuration."""
    result = data.get(dev_id, data.get(dev_id.lower(), {}))  # noqa: F821
    if not result:
        result = {}
    try:
        if len(result) > 0:
            result[0]
    except TypeError:
        logger.error("Wrong configuration for %s", dev_id)  # noqa: F821
        result = {}
    finally:
        return result


def mqtt_publish(topic, payload, retain, qos):
    """Publish data to MQTT broker."""
    service_data = {
        KEY_TOPIC: topic,
        KEY_PAYLOAD: payload,
        KEY_RETAIN: retain,
        KEY_QOS: qos,
    }
    logger.debug("Sending to MQTT broker: %s %s", topic, payload)  # noqa: F821
    hass.services.call("mqtt", "publish", service_data, False)  # noqa: F821


expire_after = None

qos = 0
retain = True
roller_mode = False

no_battery_sensor = False

fw_ver = data.get(CONF_FW_VER)  # noqa: F821
dev_id = data.get(CONF_ID)  # noqa: F821
model_id = data.get(CONF_MODEL_ID)
ignored = [
    element.lower() for element in data.get(CONF_IGNORED_DEVICES, [])
]  # noqa: F821
mac = data.get(CONF_MAC).lower()  # noqa: F821

if not dev_id:
    raise ValueError(f"{dev_id} is wrong id argument")
if not mac:
    raise ValueError(f"{mac} is wrong mac argument")
if not fw_ver:
    raise ValueError(f"{fw_ver} is wrong fw_ver argument")

try:
    cur_ver_date = parse_version(fw_ver)
except (IndexError, ValueError):
    raise ValueError(
        f"Firmware version {fw_ver} is not supported, please update your device {dev_id}"
    )

dev_id_prefix = dev_id.rsplit("-", 1)[0].lower()

if (
    dev_id_prefix == MODEL_SHELLY4PRO_PREFIX or MODEL_SHELLY4PRO_ID == model_id
) and cur_ver_date < MIN_4PRO_FIRMWARE_DATE:
    raise ValueError(
        f"Firmware dated {MIN_4PRO_FIRMWARE_DATE} is required, please update your device {dev_id}"
    )

if (
    dev_id_prefix != MODEL_SHELLY4PRO_PREFIX and MODEL_SHELLY4PRO_ID != model_id
) and cur_ver_date < MIN_FIRMWARE_DATE:
    raise ValueError(
        f"Firmware dated {MIN_FIRMWARE_DATE} is required, please update your device {dev_id}"
    )

logger.debug(
    "id: %s, mac: %s, fw_ver: %s, model: %s", dev_id, mac, fw_ver, model_id
)  # noqa: F821

try:
    if int(data.get(CONF_QOS, 0)) in [0, 1, 2]:  # noqa: F821
        qos = int(data.get(CONF_QOS, 0))  # noqa: F821
    else:
        raise ValueError()
except ValueError:
    logger.error("Wrong qos argument, the default value 0 was used")  # noqa: F821

disc_prefix = data.get(CONF_DISCOVERY_PREFIX, DEFAULT_DISC_PREFIX)  # noqa: F821

develop = data.get(CONF_DEVELOP, False)  # noqa: F821
if develop:
    disc_prefix = "develop"
    retain = False
    logger.error("DEVELOP MODE !!!")  # noqa: F821

battery_powered = False
bin_sensors = []
bin_sensors_classes = []
bin_sensors_pl = []
bin_sensors_topics = []
bin_sensors_tpls = []
ext_humi_sensors = 0
ext_temp_sensors = 0
lights_bin_sensors = []
lights_bin_sensors_classes = []
lights_bin_sensors_pl = []
lights_bin_sensors_tpls = []
lights_sensors = []
lights_sensors_classes = []
lights_sensors_tpls = []
lights_sensors_units = []
meters = 0
meters_sensors = []
meters_sensors_classes = []
meters_sensors_tpls = []
meters_sensors_units = []
meters_sensors_units = []
model = None
relay_components = [COMP_SWITCH, COMP_LIGHT, COMP_FAN]
relays = 0
relays_bin_sensors = []
relays_bin_sensors_classes = []
relays_bin_sensors_pl = []
relays_bin_sensors_topics = []
relays_bin_sensors_tpls = []
relays_sensors = []
relays_sensors_classes = []
relays_sensors_tpls = []
relays_sensors_units = []
rgbw_lights = 0
rollers = 0
sensors = []
sensors_classes = []
sensors_topics = []
sensors_tpls = []
sensors_units = []
white_lights = 0

if model_id == MODEL_SHELLY1_ID or dev_id_prefix == MODEL_SHELLY1_PREFIX:
    model = MODEL_SHELLY1
    relays = 1
    relays_bin_sensors = [SENSOR_INPUT, SENSOR_LONGPUSH, SENSOR_SHORTPUSH]
    relays_bin_sensors_pl = [PL_1_0, PL_1_0, PL_0_1]
    relays_bin_sensors_topics = [None, TOPIC_LONGPUSH, TOPIC_LONGPUSH]
    relays_bin_sensors_tpls = [None, None, None]
    relays_bin_sensors_classes = [None, None, None]
    bin_sensors = [SENSOR_FIRMWARE_UPDATE]
    bin_sensors_classes = [None]
    bin_sensors_tpls = [TPL_NEW_FIRMWARE_FROM_INFO]
    bin_sensors_topics = [TOPIC_INFO]
    sensors = [SENSOR_RSSI, SENSOR_SSID, SENSOR_UPTIME]
    sensors_units = [UNIT_DB, None, None]
    sensors_classes = [DEVICE_CLASS_SIGNAL_STRENGTH, None, DEVICE_CLASS_TIMESTAMP]
    sensors_tpls = [TPL_RSSI, TPL_SSID, TPL_UPTIME]
    sensors_topics = [None, None, None]
    ext_humi_sensors = 1
    ext_temp_sensors = 3

if model_id == MODEL_SHELLY1L_ID or dev_id_prefix == MODEL_SHELLY1L_PREFIX:
    model = MODEL_SHELLY1L
    relays = 1
    relays_sensors = [SENSOR_POWER, SENSOR_ENERGY]
    relays_sensors_units = [UNIT_WATT, UNIT_KWH]
    relays_sensors_classes = [DEVICE_CLASS_POWER, DEVICE_CLASS_ENERGY]
    relays_sensors_tpls = [TPL_POWER, TPL_ENERGY_WMIN]
    sensors = [SENSOR_TEMPERATURE, SENSOR_RSSI, SENSOR_SSID, SENSOR_UPTIME]
    sensors_classes = [
        DEVICE_CLASS_TEMPERATURE,
        DEVICE_CLASS_SIGNAL_STRENGTH,
        None,
        DEVICE_CLASS_TIMESTAMP,
    ]
    sensors_units = [UNIT_CELSIUS, UNIT_DB, None, None]
    sensors_tpls = [TPL_TEMPERATURE, TPL_RSSI, TPL_SSID, TPL_UPTIME]
    sensors_topics = [None, None, None, None]
    bin_sensors = [
        SENSOR_INPUT_0,
        SENSOR_INPUT_1,
        SENSOR_SHORTPUSH_0,
        SENSOR_LONGPUSH_0,
        SENSOR_SHORTPUSH_1,
        SENSOR_LONGPUSH_1,
        SENSOR_FIRMWARE_UPDATE,
        SENSOR_OVERTEMPERATURE,
    ]
    bin_sensors_classes = [
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        DEVICE_CLASS_PROBLEM,
    ]
    bin_sensors_tpls = [
        None,
        None,
        TPL_SHORTPUSH,
        TPL_LONGPUSH,
        TPL_SHORTPUSH,
        TPL_LONGPUSH,
        TPL_NEW_FIRMWARE_FROM_INFO,
        None,
    ]
    bin_sensors_topics = [
        TOPIC_INPUT_0,
        TOPIC_INPUT_1,
        TOPIC_INPUT_EVENT_0,
        TOPIC_INPUT_EVENT_0,
        TOPIC_INPUT_EVENT_1,
        TOPIC_INPUT_EVENT_1,
        TOPIC_INFO,
        None,
    ]
    bin_sensors_pl = [
        PL_1_0,
        PL_1_0,
        None,
        None,
        None,
        None,
        None,
        PL_1_0,
    ]

if model_id == MODEL_SHELLY1PM_ID or dev_id_prefix == MODEL_SHELLY1PM_PREFIX:
    model = MODEL_SHELLY1PM
    relays = 1
    relays_sensors = [SENSOR_POWER, SENSOR_ENERGY]
    relays_sensors_units = [UNIT_WATT, UNIT_KWH]
    relays_sensors_classes = [DEVICE_CLASS_POWER, DEVICE_CLASS_ENERGY]
    relays_sensors_tpls = [TPL_POWER, TPL_ENERGY_WMIN]
    relays_bin_sensors = [
        SENSOR_INPUT,
        SENSOR_LONGPUSH,
        SENSOR_SHORTPUSH,
        SENSOR_OVERPOWER,
    ]
    relays_bin_sensors_pl = [PL_1_0, PL_1_0, PL_0_1, None]
    relays_bin_sensors_topics = [None, TOPIC_LONGPUSH, TOPIC_LONGPUSH, TOPIC_RELAY]
    relays_bin_sensors_tpls = [None, None, None, TPL_OVERPOWER_RELAY]
    relays_bin_sensors_classes = [None, None, None, DEVICE_CLASS_PROBLEM]
    sensors = [SENSOR_TEMPERATURE, SENSOR_RSSI, SENSOR_SSID, SENSOR_UPTIME]
    sensors_classes = [
        DEVICE_CLASS_TEMPERATURE,
        DEVICE_CLASS_SIGNAL_STRENGTH,
        None,
        DEVICE_CLASS_TIMESTAMP,
    ]
    sensors_units = [UNIT_CELSIUS, UNIT_DB, None, None]
    sensors_tpls = [TPL_TEMPERATURE, TPL_RSSI, TPL_SSID, TPL_UPTIME]
    sensors_topics = [None, None, None, None]
    bin_sensors = [SENSOR_OVERTEMPERATURE, SENSOR_FIRMWARE_UPDATE]
    bin_sensors_classes = [DEVICE_CLASS_PROBLEM, None]
    bin_sensors_pl = [PL_1_0, None]
    bin_sensors_tpls = [None, TPL_NEW_FIRMWARE_FROM_INFO]
    bin_sensors_topics = [None, TOPIC_INFO]
    ext_humi_sensors = 1
    ext_temp_sensors = 3

if model_id == MODEL_SHELLYAIR_ID or dev_id_prefix == MODEL_SHELLYAIR_PREFIX:
    model = MODEL_SHELLYAIR
    relays = 1
    relays_sensors = [SENSOR_POWER, SENSOR_ENERGY]
    relays_sensors_units = [UNIT_WATT, UNIT_KWH]
    relays_sensors_classes = [DEVICE_CLASS_POWER, DEVICE_CLASS_ENERGY]
    relays_sensors_tpls = [TPL_POWER, TPL_ENERGY_WMIN]
    relays_bin_sensors = [SENSOR_INPUT]
    relays_bin_sensors_pl = [PL_1_0]
    relays_bin_sensors_tpls = [None]
    relays_bin_sensors_classes = [None]
    sensors = [
        SENSOR_TEMPERATURE,
        SENSOR_TOTALWORKTIME,
        SENSOR_RSSI,
        SENSOR_SSID,
        SENSOR_UPTIME,
    ]
    sensors_classes = [
        DEVICE_CLASS_TEMPERATURE,
        None,
        DEVICE_CLASS_SIGNAL_STRENGTH,
        None,
        DEVICE_CLASS_TIMESTAMP,
    ]
    sensors_units = [UNIT_CELSIUS, UNIT_SECOND, UNIT_DB, None, None]
    sensors_tpls = [TPL_TEMPERATURE, None, TPL_RSSI, TPL_SSID, TPL_UPTIME]
    sensors_topics = [None, None, None, None, None]
    bin_sensors = [SENSOR_OVERTEMPERATURE, SENSOR_FIRMWARE_UPDATE]
    bin_sensors_classes = [DEVICE_CLASS_PROBLEM, None]
    bin_sensors_pl = [PL_1_0, None]
    bin_sensors_tpls = [None, TPL_NEW_FIRMWARE_FROM_INFO]
    bin_sensors_topics = [None, TOPIC_INFO]
    ext_temp_sensors = 1

if model_id == MODEL_SHELLY2_ID or dev_id_prefix == MODEL_SHELLY2_PREFIX:
    model = MODEL_SHELLY2
    relays = 2
    rollers = 1
    relays_sensors = [SENSOR_POWER, SENSOR_ENERGY]
    relays_sensors_units = [UNIT_WATT, UNIT_KWH]
    relays_sensors_classes = [DEVICE_CLASS_POWER, DEVICE_CLASS_ENERGY]
    relays_sensors_tpls = [TPL_POWER, TPL_ENERGY_WMIN]
    relays_bin_sensors = [
        SENSOR_INPUT,
        SENSOR_LONGPUSH,
        SENSOR_SHORTPUSH,
        SENSOR_OVERPOWER,
    ]
    relays_bin_sensors_pl = [PL_1_0, PL_1_0, PL_0_1, None]
    relays_bin_sensors_topics = [None, TOPIC_LONGPUSH, TOPIC_LONGPUSH, TOPIC_RELAY]
    relays_bin_sensors_tpls = [None, None, None, TPL_OVERPOWER_RELAY]
    relays_bin_sensors_classes = [None, None, None, DEVICE_CLASS_PROBLEM]
    bin_sensors = [SENSOR_FIRMWARE_UPDATE]
    bin_sensors_classes = [None]
    bin_sensors_tpls = [TPL_NEW_FIRMWARE_FROM_INFO]
    bin_sensors_topics = [TOPIC_INFO]
    sensors = [SENSOR_RSSI, SENSOR_SSID, SENSOR_UPTIME]
    sensors_units = [UNIT_DB, None, None]
    sensors_classes = [DEVICE_CLASS_SIGNAL_STRENGTH, None, DEVICE_CLASS_TIMESTAMP]
    sensors_tpls = [TPL_RSSI, TPL_SSID, TPL_UPTIME]
    sensors_topics = [None, None, None]

if model_id == MODEL_SHELLY25_ID or dev_id_prefix == MODEL_SHELLY25_PREFIX:
    model = MODEL_SHELLY25
    relays = 2
    rollers = 1
    relays_sensors = [SENSOR_POWER, SENSOR_ENERGY]
    relays_sensors_units = [UNIT_WATT, UNIT_KWH]
    relays_sensors_classes = [DEVICE_CLASS_POWER, DEVICE_CLASS_ENERGY]
    relays_sensors_tpls = [TPL_POWER, TPL_ENERGY_WMIN]
    relays_bin_sensors = [
        SENSOR_INPUT,
        SENSOR_LONGPUSH,
        SENSOR_SHORTPUSH,
        SENSOR_OVERPOWER,
    ]
    relays_bin_sensors_pl = [PL_1_0, PL_1_0, PL_0_1, None]
    relays_bin_sensors_topics = [None, TOPIC_LONGPUSH, TOPIC_LONGPUSH, TOPIC_RELAY]
    relays_bin_sensors_tpls = [None, None, None, TPL_OVERPOWER_RELAY]
    relays_bin_sensors_classes = [None, None, None, DEVICE_CLASS_PROBLEM]
    sensors = [SENSOR_TEMPERATURE, SENSOR_RSSI, SENSOR_SSID, SENSOR_UPTIME]
    sensors_classes = [
        DEVICE_CLASS_TEMPERATURE,
        DEVICE_CLASS_SIGNAL_STRENGTH,
        None,
        DEVICE_CLASS_TIMESTAMP,
    ]
    sensors_units = [UNIT_CELSIUS, UNIT_DB, None, None]
    sensors_tpls = [TPL_TEMPERATURE, TPL_RSSI, TPL_SSID, TPL_UPTIME]
    sensors_topics = [None, None, None, None]
    bin_sensors = [SENSOR_OVERTEMPERATURE, SENSOR_FIRMWARE_UPDATE]
    bin_sensors_classes = [DEVICE_CLASS_PROBLEM, None]
    bin_sensors_pl = [PL_1_0, None]
    bin_sensors_tpls = [None, TPL_NEW_FIRMWARE_FROM_INFO]
    bin_sensors_topics = [None, TOPIC_INFO]

if model_id == MODEL_SHELLYUNI_ID or dev_id_prefix == MODEL_SHELLYUNI_PREFIX:
    model = MODEL_SHELLYUNI
    relays = 2
    relays_bin_sensors = [SENSOR_INPUT]
    relays_bin_sensors_pl = [PL_1_0]
    relays_bin_sensors_topics = [None]
    relays_bin_sensors_tpls = [None]
    relays_bin_sensors_classes = [None]
    sensors = [SENSOR_ADC, SENSOR_RSSI, SENSOR_SSID, SENSOR_UPTIME]
    sensors_classes = [
        None,
        DEVICE_CLASS_SIGNAL_STRENGTH,
        None,
        DEVICE_CLASS_TIMESTAMP,
    ]
    sensors_units = [None, UNIT_DB, None, None]
    sensors_tpls = [None, TPL_RSSI, TPL_SSID, TPL_UPTIME]
    sensors_topics = [TOPIC_ADC, None, None, None]

if (
    model_id in [MODEL_SHELLYPLUG_ID, MODEL_SHELLYPLUG_E_ID]
    or dev_id_prefix == MODEL_SHELLYPLUG_PREFIX
):
    model = MODEL_SHELLYPLUG
    relays = 1
    relays_sensors = [SENSOR_POWER, SENSOR_ENERGY]
    relays_sensors_units = [UNIT_WATT, UNIT_KWH]
    relays_sensors_classes = [DEVICE_CLASS_POWER, DEVICE_CLASS_ENERGY]
    relays_sensors_tpls = [TPL_POWER, TPL_ENERGY_WMIN]
    relays_bin_sensors = [SENSOR_OVERPOWER]
    relays_bin_sensors_pl = [None]
    relays_bin_sensors_topics = [TOPIC_RELAY]
    relays_bin_sensors_tpls = [TPL_OVERPOWER_RELAY]
    relays_bin_sensors_classes = [DEVICE_CLASS_PROBLEM]
    bin_sensors = [SENSOR_FIRMWARE_UPDATE]
    bin_sensors_classes = [None]
    bin_sensors_tpls = [TPL_NEW_FIRMWARE_FROM_INFO]
    bin_sensors_topics = [TOPIC_INFO]
    sensors = [SENSOR_RSSI, SENSOR_SSID, SENSOR_UPTIME]
    sensors_units = [UNIT_DB, None, None]
    sensors_classes = [DEVICE_CLASS_SIGNAL_STRENGTH, None, DEVICE_CLASS_TIMESTAMP]
    sensors_tpls = [TPL_RSSI, TPL_SSID, TPL_UPTIME]
    sensors_topics = [None, None, None]

if model_id == MODEL_SHELLYPLUG_US_ID or dev_id_prefix == MODEL_SHELLYPLUG_US_PREFIX:
    model = MODEL_SHELLYPLUG_US
    relays = 1
    relays_sensors = [SENSOR_POWER, SENSOR_ENERGY]
    relays_sensors_units = [UNIT_WATT, UNIT_KWH]
    relays_sensors_classes = [DEVICE_CLASS_POWER, DEVICE_CLASS_ENERGY]
    relays_sensors_tpls = [TPL_POWER, TPL_ENERGY_WMIN]
    relays_bin_sensors = [SENSOR_OVERPOWER]
    relays_bin_sensors_pl = [None]
    relays_bin_sensors_topics = [TOPIC_RELAY]
    relays_bin_sensors_tpls = [TPL_OVERPOWER_RELAY]
    relays_bin_sensors_classes = [DEVICE_CLASS_PROBLEM]
    bin_sensors = [SENSOR_FIRMWARE_UPDATE]
    bin_sensors_classes = [None]
    bin_sensors_tpls = [TPL_NEW_FIRMWARE_FROM_INFO]
    bin_sensors_topics = [TOPIC_INFO]
    sensors = [SENSOR_RSSI, SENSOR_SSID, SENSOR_UPTIME]
    sensors_units = [UNIT_DB, None, None]
    sensors_classes = [DEVICE_CLASS_SIGNAL_STRENGTH, None, DEVICE_CLASS_TIMESTAMP]
    sensors_tpls = [TPL_RSSI, TPL_SSID, TPL_UPTIME]
    sensors_topics = [None, None, None]

if model_id == MODEL_SHELLYPLUG_S_ID or dev_id_prefix == MODEL_SHELLYPLUG_S_PREFIX:
    model = MODEL_SHELLYPLUG_S
    relays = 1
    relays_sensors = [SENSOR_POWER, SENSOR_ENERGY]
    relays_sensors_units = [UNIT_WATT, UNIT_KWH]
    relays_sensors_classes = [DEVICE_CLASS_POWER, DEVICE_CLASS_ENERGY]
    relays_sensors_tpls = [TPL_POWER, TPL_ENERGY_WMIN]
    relays_bin_sensors = [SENSOR_OVERPOWER]
    relays_bin_sensors_pl = [None]
    relays_bin_sensors_topics = [TOPIC_RELAY]
    relays_bin_sensors_tpls = [TPL_OVERPOWER_RELAY]
    relays_bin_sensors_classes = [DEVICE_CLASS_PROBLEM]
    sensors = [SENSOR_TEMPERATURE, SENSOR_RSSI, SENSOR_SSID, SENSOR_UPTIME]
    sensors_classes = [
        DEVICE_CLASS_TEMPERATURE,
        DEVICE_CLASS_SIGNAL_STRENGTH,
        None,
        DEVICE_CLASS_TIMESTAMP,
    ]
    sensors_units = [UNIT_CELSIUS, UNIT_DB, None, None]
    sensors_tpls = [TPL_TEMPERATURE, TPL_RSSI, TPL_SSID, TPL_UPTIME]
    sensors_topics = [None, None, None, None]
    bin_sensors = [SENSOR_OVERTEMPERATURE, SENSOR_FIRMWARE_UPDATE]
    bin_sensors_classes = [DEVICE_CLASS_PROBLEM, None]
    bin_sensors_pl = [PL_1_0, None]
    bin_sensors_tpls = [None, TPL_NEW_FIRMWARE_FROM_INFO]
    bin_sensors_topics = [None, TOPIC_INFO]

if model_id == MODEL_SHELLY4PRO_ID or dev_id_prefix == MODEL_SHELLY4PRO_PREFIX:
    model = MODEL_SHELLY4PRO
    relays = 4
    relays_sensors = [SENSOR_POWER, SENSOR_ENERGY]
    relays_sensors_units = [UNIT_WATT, UNIT_KWH]
    relays_sensors_classes = [DEVICE_CLASS_POWER, DEVICE_CLASS_ENERGY]
    relays_sensors_tpls = [TPL_POWER, TPL_ENERGY_WMIN]
    relays_bin_sensors = [SENSOR_OVERPOWER]
    relays_bin_sensors_pl = [None]
    relays_bin_sensors_topics = [TOPIC_RELAY]
    relays_bin_sensors_tpls = [TPL_OVERPOWER_RELAY]
    relays_bin_sensors_classes = [DEVICE_CLASS_PROBLEM]
    bin_sensors = [SENSOR_FIRMWARE_UPDATE]
    bin_sensors_classes = [None]
    bin_sensors_tpls = [
        TPL_NEW_FIRMWARE_FROM_ANNOUNCE
    ]  # TPL_NEW_FIRMWARE_FROM_INFO after released firmware 1.8.0
    bin_sensors_topics = [TOPIC_ANNOUNCE]  # TOPIC_INFO after released firmware 1.8.0
    # sensors = [SENSOR_RSSI, SENSOR_SSID, SENSOR_UPTIME]  # firmware 1.8.0 required
    # sensors_units = [UNIT_DB, None, None]  # firmware 1.8.0 required
    # sensors_classes = [DEVICE_CLASS_SIGNAL_STRENGTH, None, DEVICE_CLASS_TIMESTAMP]  # firmware 1.8.0 required
    # sensors_tpls = [TPL_RSSI, TPL_SSID, TPL_UPTIME]  # firmware 1.8.0 required
    # sensors_topics = [None, None, None]  # firmware 1.8.0 required

if model_id == MODEL_SHELLYHT_ID or dev_id_prefix == MODEL_SHELLYHT_PREFIX:
    model = MODEL_SHELLYHT
    sensors = [SENSOR_TEMPERATURE, SENSOR_HUMIDITY, SENSOR_BATTERY]
    sensors_classes = [
        DEVICE_CLASS_TEMPERATURE,
        DEVICE_CLASS_HUMIDITY,
        DEVICE_CLASS_BATTERY,
    ]
    sensors_units = [UNIT_CELSIUS, UNIT_PERCENT, UNIT_PERCENT]
    sensors_tpls = [TPL_TEMPERATURE, TPL_HUMIDITY, TPL_BATTERY]
    sensors_topics = [None, None, None]
    bin_sensors = [SENSOR_FIRMWARE_UPDATE]
    bin_sensors_classes = [None]
    bin_sensors_tpls = [TPL_NEW_FIRMWARE_FROM_ANNOUNCE]
    bin_sensors_topics = [TOPIC_ANNOUNCE]
    battery_powered = True

if model_id == MODEL_SHELLYGAS_ID or dev_id_prefix == MODEL_SHELLYGAS_PREFIX:
    model = MODEL_SHELLYGAS
    sensors = [
        SENSOR_OPERATION,
        SENSOR_SELF_TEST,
        SENSOR_CONCENTRATION,
        SENSOR_RSSI,
        SENSOR_SSID,
        SENSOR_UPTIME,
    ]
    sensors_classes = [
        None,
        None,
        None,
        None,
        DEVICE_CLASS_SIGNAL_STRENGTH,
        None,
        DEVICE_CLASS_TIMESTAMP,
    ]
    sensors_tpls = [None, None, None, TPL_CONCENTRATION, TPL_RSSI, TPL_SSID, TPL_UPTIME]
    sensors_topics = [None, None, None, None, None, None, None]
    sensors_units = [None, None, None, UNIT_PPM, UNIT_DB, None, None]
    bin_sensors = [SENSOR_FIRMWARE_UPDATE, SENSOR_GAS]
    bin_sensors_classes = [None, DEVICE_CLASS_GAS]
    bin_sensors_tpls = [TPL_NEW_FIRMWARE_FROM_INFO, TPL_GAS]
    bin_sensors_topics = [TOPIC_INFO, None]

if model_id == MODEL_SHELLYBUTTON1_ID or dev_id_prefix == MODEL_SHELLYBUTTON1_PREFIX:
    model = MODEL_SHELLYBUTTON1
    sensors = [SENSOR_BATTERY]
    sensors_classes = [DEVICE_CLASS_BATTERY]
    sensors_units = [UNIT_PERCENT]
    sensors_tpls = [TPL_BATTERY]
    sensors_topics = [None]
    bin_sensors = [
        SENSOR_INPUT_0,
        SENSOR_SHORTPUSH,
        SENSOR_DOUBLE_SHORTPUSH,
        SENSOR_TRIPLE_SHORTPUSH,
        SENSOR_LONGPUSH,
        SENSOR_FIRMWARE_UPDATE,
    ]
    bin_sensors_classes = [None, None, None, None, None, None]
    bin_sensors_tpls = [
        None,
        TPL_SHORTPUSH,
        TPL_DOUBLE_SHORTPUSH,
        TPL_TRIPLE_SHORTPUSH,
        TPL_LONGPUSH,
        TPL_NEW_FIRMWARE_FROM_ANNOUNCE,
    ]
    bin_sensors_pl = [PL_1_0, None, None, None, None, None]
    bin_sensors_topics = [
        None,
        TOPIC_INPUT_EVENT_0,
        TOPIC_INPUT_EVENT_0,
        TOPIC_INPUT_EVENT_0,
        TOPIC_INPUT_EVENT_0,
        TOPIC_ANNOUNCE,
    ]
    battery_powered = True

if model_id == MODEL_SHELLYDW_ID or dev_id_prefix == MODEL_SHELLYDW_PREFIX:
    model = MODEL_SHELLYDW
    sensors = [SENSOR_LUX, SENSOR_BATTERY, SENSOR_TILT]
    sensors_classes = [DEVICE_CLASS_ILLUMINANCE, DEVICE_CLASS_BATTERY, None]
    sensors_units = [UNIT_LUX, UNIT_PERCENT, UNIT_DEGREE]
    sensors_tpls = [TPL_LUX, TPL_BATTERY, TPL_TILT]
    sensors_topics = [None, None, None]
    bin_sensors = [SENSOR_OPENING, SENSOR_VIBRATION, SENSOR_FIRMWARE_UPDATE]
    bin_sensors_classes = [DEVICE_CLASS_OPENING, DEVICE_CLASS_VIBRATION, None]
    bin_sensors_pl = [PL_OPEN_CLOSE, PL_1_0, None]
    bin_sensors_tpls = [None, None, TPL_NEW_FIRMWARE_FROM_ANNOUNCE]
    bin_sensors_topics = [None, None, TOPIC_ANNOUNCE]
    battery_powered = True

if model_id == MODEL_SHELLYDW2_ID or dev_id_prefix == MODEL_SHELLYDW2_PREFIX:
    model = MODEL_SHELLYDW2
    sensors = [SENSOR_LUX, SENSOR_BATTERY, SENSOR_TILT, SENSOR_TEMPERATURE]
    sensors_classes = [
        DEVICE_CLASS_ILLUMINANCE,
        DEVICE_CLASS_BATTERY,
        None,
        DEVICE_CLASS_TEMPERATURE,
    ]
    sensors_units = [UNIT_LUX, UNIT_PERCENT, UNIT_DEGREE, UNIT_CELSIUS]
    sensors_tpls = [TPL_LUX, TPL_BATTERY, TPL_TILT, TPL_TEMPERATURE]
    sensors_topics = [None, None, None, None]
    bin_sensors = [SENSOR_OPENING, SENSOR_VIBRATION, SENSOR_FIRMWARE_UPDATE]
    bin_sensors_classes = [DEVICE_CLASS_OPENING, DEVICE_CLASS_VIBRATION, None]
    bin_sensors_pl = [PL_OPEN_CLOSE, PL_1_0, None]
    bin_sensors_tpls = [None, None, TPL_NEW_FIRMWARE_FROM_ANNOUNCE]
    bin_sensors_topics = [None, None, TOPIC_ANNOUNCE]
    battery_powered = True

if model_id == MODEL_SHELLYSMOKE_ID or dev_id_prefix == MODEL_SHELLYSMOKE_PREFIX:
    model = MODEL_SHELLYSMOKE
    sensors = [SENSOR_TEMPERATURE, SENSOR_BATTERY]
    sensors_classes = [DEVICE_CLASS_TEMPERATURE, DEVICE_CLASS_BATTERY]
    sensors_units = [UNIT_CELSIUS, UNIT_PERCENT]
    sensors_tpls = [TPL_TEMPERATURE, TPL_BATTERY]
    sensors_topics = [None, None]
    bin_sensors = [SENSOR_SMOKE, SENSOR_FIRMWARE_UPDATE]
    bin_sensors_classes = [DEVICE_CLASS_SMOKE, None]
    bin_sensors_pl = [PL_TRUE_FALSE, None]
    bin_sensors_tpls = [None, TPL_NEW_FIRMWARE_FROM_ANNOUNCE]
    bin_sensors_topics = [None, TOPIC_ANNOUNCE]
    battery_powered = True

if model_id == MODEL_SHELLYSENSE_ID or dev_id_prefix == MODEL_SHELLYSENSE_PREFIX:
    model = MODEL_SHELLYSENSE
    sensors = [SENSOR_TEMPERATURE, SENSOR_HUMIDITY, SENSOR_LUX, SENSOR_BATTERY]
    sensors_classes = [
        DEVICE_CLASS_TEMPERATURE,
        DEVICE_CLASS_HUMIDITY,
        DEVICE_CLASS_ILLUMINANCE,
        DEVICE_CLASS_BATTERY,
    ]
    sensors_units = [UNIT_CELSIUS, UNIT_PERCENT, UNIT_LUX, UNIT_PERCENT]
    sensors_tpls = [TPL_TEMPERATURE, TPL_HUMIDITY, TPL_LUX, TPL_BATTERY]
    sensors_topics = [None, None, None, None]
    bin_sensors = [SENSOR_MOTION, SENSOR_CHARGER, SENSOR_FIRMWARE_UPDATE]
    bin_sensors_classes = [DEVICE_CLASS_MOTION, DEVICE_CLASS_BATTERY_CHARGING, None]
    bin_sensors_pl = [PL_TRUE_FALSE, PL_TRUE_FALSE, None]
    bin_sensors_tpls = [None, None, TPL_NEW_FIRMWARE_FROM_ANNOUNCE]
    bin_sensors_topics = [None, None, TOPIC_ANNOUNCE]
    battery_powered = True

if model_id == MODEL_SHELLYRGBW2_ID or dev_id_prefix == MODEL_SHELLYRGBW2_PREFIX:
    model = MODEL_SHELLYRGBW2
    rgbw_lights = 1
    white_lights = 4
    lights_sensors = [SENSOR_POWER]
    lights_sensors_classes = [DEVICE_CLASS_POWER]
    lights_sensors_units = [UNIT_WATT]
    lights_sensors_tpls = ["{{value_json.power|float|round(1)}}"]
    bin_sensors = [
        SENSOR_OVERPOWER,
        SENSOR_INPUT_0,
        SENSOR_LONGPUSH_0,
        SENSOR_SHORTPUSH_0,
        SENSOR_FIRMWARE_UPDATE,
    ]
    bin_sensors_classes = [DEVICE_CLASS_PROBLEM, None, None, None, None]
    bin_sensors_tpls = [TPL_OVERPOWER, None, None, None, TPL_NEW_FIRMWARE_FROM_INFO]
    bin_sensors_pl = [None, PL_1_0, PL_1_0, PL_0_1, None]
    bin_sensors_topics = [
        TOPIC_COLOR_0_STATUS,
        TOPIC_INPUT_0,
        TOPIC_LONGPUSH_0,
        TOPIC_LONGPUSH_0,
        TOPIC_INFO,
    ]
    sensors = [SENSOR_RSSI, SENSOR_SSID, SENSOR_UPTIME]
    sensors_units = [UNIT_DB, None, None]
    sensors_classes = [DEVICE_CLASS_SIGNAL_STRENGTH, None, DEVICE_CLASS_TIMESTAMP]
    sensors_tpls = [TPL_RSSI, TPL_SSID, TPL_UPTIME]
    sensors_topics = [None, None, None]

if model_id == MODEL_SHELLYDIMMER_ID or dev_id_prefix == MODEL_SHELLYDIMMER_PREFIX:
    model = MODEL_SHELLYDIMMER
    white_lights = 1
    sensors = [SENSOR_TEMPERATURE, SENSOR_RSSI, SENSOR_SSID, SENSOR_UPTIME]
    sensors_classes = [
        DEVICE_CLASS_TEMPERATURE,
        DEVICE_CLASS_SIGNAL_STRENGTH,
        None,
        DEVICE_CLASS_TIMESTAMP,
    ]
    sensors_units = [UNIT_CELSIUS, UNIT_DB, None, None]
    sensors_tpls = [TPL_TEMPERATURE, TPL_RSSI, TPL_SSID, TPL_UPTIME]
    sensors_topics = [None, None, None, None]
    bin_sensors = [
        SENSOR_OVERTEMPERATURE,
        SENSOR_OVERLOAD,
        SENSOR_LOADERROR,
        SENSOR_INPUT_0,
        SENSOR_INPUT_1,
        SENSOR_LONGPUSH_0,
        SENSOR_LONGPUSH_1,
        SENSOR_SHORTPUSH_0,
        SENSOR_SHORTPUSH_1,
        SENSOR_FIRMWARE_UPDATE,
    ]
    bin_sensors_classes = [
        DEVICE_CLASS_PROBLEM,
        DEVICE_CLASS_PROBLEM,
        DEVICE_CLASS_PROBLEM,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ]
    bin_sensors_pl = [
        PL_1_0,
        PL_1_0,
        PL_1_0,
        PL_1_0,
        PL_1_0,
        PL_1_0,
        PL_1_0,
        PL_0_1,
        PL_0_1,
        None,
    ]
    bin_sensors_tpls = [
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        TPL_NEW_FIRMWARE_FROM_INFO,
    ]
    bin_sensors_topics = [
        None,
        None,
        None,
        TOPIC_INPUT_0,
        TOPIC_INPUT_1,
        TOPIC_LONGPUSH_0,
        TOPIC_LONGPUSH_1,
        TOPIC_LONGPUSH_0,
        TOPIC_LONGPUSH_1,
        TOPIC_INFO,
    ]
    lights_sensors = [SENSOR_POWER, SENSOR_ENERGY]
    lights_sensors_units = [UNIT_WATT, UNIT_KWH]
    lights_sensors_classes = [DEVICE_CLASS_POWER, DEVICE_CLASS_ENERGY]
    lights_sensors_tpls = [TPL_POWER, TPL_ENERGY_WMIN]

if model_id == MODEL_SHELLYDIMMER2_ID or dev_id_prefix == MODEL_SHELLYDIMMER2_PREFIX:
    model = MODEL_SHELLYDIMMER2
    white_lights = 1
    sensors = [SENSOR_TEMPERATURE, SENSOR_RSSI, SENSOR_SSID, SENSOR_UPTIME]
    sensors_classes = [
        DEVICE_CLASS_TEMPERATURE,
        DEVICE_CLASS_SIGNAL_STRENGTH,
        None,
        DEVICE_CLASS_TIMESTAMP,
    ]
    sensors_units = [UNIT_CELSIUS, UNIT_DB, None, None]
    sensors_tpls = [TPL_TEMPERATURE, TPL_RSSI, TPL_SSID, TPL_UPTIME]
    sensors_topics = [None, None, None, None]
    bin_sensors = [
        SENSOR_OVERTEMPERATURE,
        SENSOR_OVERLOAD,
        SENSOR_LOADERROR,
        SENSOR_INPUT_0,
        SENSOR_INPUT_1,
        SENSOR_LONGPUSH_0,
        SENSOR_LONGPUSH_1,
        SENSOR_SHORTPUSH_0,
        SENSOR_SHORTPUSH_1,
        SENSOR_FIRMWARE_UPDATE,
    ]
    bin_sensors_classes = [
        DEVICE_CLASS_PROBLEM,
        DEVICE_CLASS_PROBLEM,
        DEVICE_CLASS_PROBLEM,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ]
    bin_sensors_pl = [
        PL_1_0,
        PL_1_0,
        PL_1_0,
        PL_1_0,
        PL_1_0,
        PL_1_0,
        PL_1_0,
        PL_0_1,
        PL_0_1,
        None,
    ]
    bin_sensors_tpls = [
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        TPL_NEW_FIRMWARE_FROM_INFO,
    ]
    bin_sensors_topics = [
        None,
        None,
        None,
        TOPIC_INPUT_0,
        TOPIC_INPUT_1,
        TOPIC_LONGPUSH_0,
        TOPIC_LONGPUSH_1,
        TOPIC_LONGPUSH_0,
        TOPIC_LONGPUSH_1,
        TOPIC_INFO,
    ]
    lights_sensors = [SENSOR_POWER, SENSOR_ENERGY]
    lights_sensors_units = [UNIT_WATT, UNIT_KWH]
    lights_sensors_classes = [DEVICE_CLASS_POWER, DEVICE_CLASS_ENERGY]
    lights_sensors_tpls = [TPL_POWER, TPL_ENERGY_WMIN]

if model_id == MODEL_SHELLYBULB_ID or dev_id_prefix == MODEL_SHELLYBULB_PREFIX:
    model = MODEL_SHELLYBULB
    rgbw_lights = 1
    bin_sensors = [SENSOR_FIRMWARE_UPDATE]
    bin_sensors_classes = [None]
    bin_sensors_tpls = [TPL_NEW_FIRMWARE_FROM_INFO]
    bin_sensors_topics = [TOPIC_INFO]
    sensors = [SENSOR_RSSI, SENSOR_SSID, SENSOR_UPTIME]
    sensors_units = [UNIT_DB, None, None]
    sensors_classes = [DEVICE_CLASS_SIGNAL_STRENGTH, None, DEVICE_CLASS_TIMESTAMP]
    sensors_tpls = [TPL_RSSI, TPL_SSID, TPL_UPTIME]
    sensors_topics = [None, None, None]

if model_id == MODEL_SHELLYDUO_ID or dev_id_prefix == MODEL_SHELLYDUO_PREFIX:
    model = MODEL_SHELLYDUO
    white_lights = 1
    lights_sensors = [SENSOR_ENERGY, SENSOR_POWER]
    lights_sensors_units = [UNIT_KWH, UNIT_WATT]
    lights_sensors_classes = [DEVICE_CLASS_ENERGY, DEVICE_CLASS_POWER]
    lights_sensors_tpls = [TPL_ENERGY_WMIN, TPL_POWER]
    bin_sensors = [SENSOR_FIRMWARE_UPDATE]
    bin_sensors_classes = [None]
    bin_sensors_tpls = [TPL_NEW_FIRMWARE_FROM_INFO]
    bin_sensors_topics = [TOPIC_INFO]
    sensors = [SENSOR_RSSI, SENSOR_SSID, SENSOR_UPTIME]
    sensors_units = [UNIT_DB, None, None]
    sensors_classes = [DEVICE_CLASS_SIGNAL_STRENGTH, None, DEVICE_CLASS_TIMESTAMP]
    sensors_tpls = [TPL_RSSI, TPL_SSID, TPL_UPTIME]
    sensors_topics = [None, None, None]

if model_id == MODEL_SHELLYVINTAGE_ID or dev_id_prefix == MODEL_SHELLYVINTAGE_PREFIX:
    model = MODEL_SHELLYVINTAGE
    white_lights = 1
    lights_sensors = [SENSOR_ENERGY, SENSOR_POWER]
    lights_sensors_units = [UNIT_KWH, UNIT_WATT]
    lights_sensors_classes = [DEVICE_CLASS_ENERGY, DEVICE_CLASS_POWER]
    lights_sensors_tpls = [TPL_ENERGY_WMIN, TPL_POWER]
    bin_sensors = [SENSOR_FIRMWARE_UPDATE]
    bin_sensors_classes = [None]
    bin_sensors_tpls = [TPL_NEW_FIRMWARE_FROM_INFO]
    bin_sensors_topics = [TOPIC_INFO]
    sensors = [SENSOR_RSSI, SENSOR_SSID, SENSOR_UPTIME]
    sensors_units = [UNIT_DB, None, None]
    sensors_classes = [DEVICE_CLASS_SIGNAL_STRENGTH, None, DEVICE_CLASS_TIMESTAMP]
    sensors_tpls = [TPL_RSSI, TPL_SSID, TPL_UPTIME]
    sensors_topics = [None, None, None]

if model_id == MODEL_SHELLYEM_ID or dev_id_prefix == MODEL_SHELLYEM_PREFIX:
    model = MODEL_SHELLYEM
    relays = 1
    relays_sensors = [SENSOR_POWER, SENSOR_ENERGY]
    relays_sensors_units = [UNIT_WATT, UNIT_KWH]
    relays_sensors_classes = [DEVICE_CLASS_POWER, DEVICE_CLASS_ENERGY]
    relays_sensors_tpls = [TPL_POWER, TPL_ENERGY_WMIN]
    relays_bin_sensors = [SENSOR_OVERPOWER]
    relays_bin_sensors_pl = [None]
    relays_bin_sensors_topics = [TOPIC_RELAY]
    relays_bin_sensors_tpls = [TPL_OVERPOWER_RELAY]
    relays_bin_sensors_classes = [DEVICE_CLASS_PROBLEM]
    meters = 2
    meters_sensors = [
        SENSOR_POWER,
        SENSOR_REACTIVE_POWER,
        SENSOR_VOLTAGE,
        SENSOR_ENERGY,
        SENSOR_RETURNED_ENERGY,
        SENSOR_TOTAL,
        SENSOR_TOTAL_RETURNED,
    ]
    meters_sensors_units = [
        UNIT_WATT,
        UNIT_VAR,
        UNIT_VOLT,
        UNIT_KWH,
        UNIT_KWH,
        UNIT_KWH,
        UNIT_KWH,
    ]
    meters_sensors_classes = [
        DEVICE_CLASS_POWER,
        None,
        DEVICE_CLASS_VOLTAGE,
        DEVICE_CLASS_ENERGY,
        DEVICE_CLASS_ENERGY,
        DEVICE_CLASS_ENERGY,
        DEVICE_CLASS_ENERGY,
    ]
    meters_sensors_tpls = [
        TPL_POWER,
        TPL_POWER,
        TPL_VOLTAGE,
        TPL_ENERGY_WMIN,
        TPL_ENERGY_WMIN,
        TPL_ENERGY_WH,
        TPL_ENERGY_WH,
    ]
    bin_sensors = [SENSOR_FIRMWARE_UPDATE]
    bin_sensors_classes = [None]
    bin_sensors_tpls = [TPL_NEW_FIRMWARE_FROM_INFO]
    bin_sensors_topics = [TOPIC_INFO]
    sensors = [SENSOR_RSSI, SENSOR_SSID, SENSOR_UPTIME]
    sensors_units = [UNIT_DB, None, None]
    sensors_classes = [DEVICE_CLASS_SIGNAL_STRENGTH, None, DEVICE_CLASS_TIMESTAMP]
    sensors_tpls = [TPL_RSSI, TPL_SSID, TPL_UPTIME]
    sensors_topics = [None, None, None]

if model_id == MODEL_SHELLY3EM_ID or dev_id_prefix == MODEL_SHELLY3EM_PREFIX:
    model = MODEL_SHELLY3EM
    relays = 1
    meters = 3
    relays_bin_sensors = [SENSOR_OVERPOWER]
    relays_bin_sensors_pl = [None]
    relays_bin_sensors_topics = [TOPIC_RELAY]
    relays_bin_sensors_tpls = [TPL_OVERPOWER_RELAY]
    relays_bin_sensors_classes = [DEVICE_CLASS_PROBLEM]
    meters_sensors = [
        SENSOR_CURRENT,
        SENSOR_POWER,
        SENSOR_POWER_FACTOR,
        SENSOR_VOLTAGE,
        SENSOR_ENERGY,
        SENSOR_RETURNED_ENERGY,
        SENSOR_TOTAL,
        SENSOR_TOTAL_RETURNED,
    ]
    meters_sensors_units = [
        UNIT_AMPERE,
        UNIT_WATT,
        UNIT_PERCENT,
        UNIT_VOLT,
        UNIT_KWH,
        UNIT_KWH,
        UNIT_KWH,
        UNIT_KWH,
    ]
    meters_sensors_classes = [
        DEVICE_CLASS_CURRENT,
        DEVICE_CLASS_POWER,
        DEVICE_CLASS_POWER_FACTOR,
        DEVICE_CLASS_VOLTAGE,
        DEVICE_CLASS_ENERGY,
        DEVICE_CLASS_ENERGY,
        DEVICE_CLASS_ENERGY,
        DEVICE_CLASS_ENERGY,
    ]
    meters_sensors_tpls = [
        TPL_CURRENT,
        TPL_POWER,
        TPL_POWER_FACTOR,
        TPL_VOLTAGE,
        TPL_ENERGY_WMIN,
        TPL_ENERGY_WMIN,
        TPL_ENERGY_WH,
        TPL_ENERGY_WH,
    ]
    bin_sensors = [SENSOR_FIRMWARE_UPDATE]
    bin_sensors_classes = [None]
    bin_sensors_tpls = [TPL_NEW_FIRMWARE_FROM_INFO]
    bin_sensors_topics = [TOPIC_INFO]
    sensors = [SENSOR_RSSI, SENSOR_SSID, SENSOR_UPTIME]
    sensors_units = [UNIT_DB, None, None]
    sensors_classes = [DEVICE_CLASS_SIGNAL_STRENGTH, None, DEVICE_CLASS_TIMESTAMP]
    sensors_tpls = [TPL_RSSI, TPL_SSID, TPL_UPTIME]
    sensors_topics = [None, None, None]

if model_id == MODEL_SHELLYFLOOD_ID or dev_id_prefix == MODEL_SHELLYFLOOD_PREFIX:
    model = MODEL_SHELLYFLOOD
    sensors = [SENSOR_TEMPERATURE, SENSOR_BATTERY]
    sensors_classes = [DEVICE_CLASS_TEMPERATURE, DEVICE_CLASS_BATTERY]
    sensors_units = [UNIT_CELSIUS, UNIT_PERCENT]
    sensors_tpls = [TPL_TEMPERATURE, TPL_BATTERY]
    sensors_topics = [None, None]
    bin_sensors = [SENSOR_FLOOD, SENSOR_FIRMWARE_UPDATE]
    bin_sensors_classes = [DEVICE_CLASS_MOISTURE, None]
    bin_sensors_pl = [PL_TRUE_FALSE, None]
    bin_sensors_tpls = [None, TPL_NEW_FIRMWARE_FROM_ANNOUNCE]
    bin_sensors_topics = [None, TOPIC_ANNOUNCE]
    battery_powered = True

if model_id == MODEL_SHELLYI3_ID or dev_id_prefix == MODEL_SHELLYI3_PREFIX:
    model = MODEL_SHELLYI3
    bin_sensors = [
        SENSOR_INPUT_0,
        SENSOR_INPUT_1,
        SENSOR_INPUT_2,
        SENSOR_SHORTPUSH_0,
        SENSOR_DOUBLE_SHORTPUSH_0,
        SENSOR_TRIPLE_SHORTPUSH_0,
        SENSOR_LONGPUSH_0,
        SENSOR_SHORTPUSH_1,
        SENSOR_DOUBLE_SHORTPUSH_1,
        SENSOR_TRIPLE_SHORTPUSH_1,
        SENSOR_LONGPUSH_1,
        SENSOR_SHORTPUSH_2,
        SENSOR_DOUBLE_SHORTPUSH_2,
        SENSOR_TRIPLE_SHORTPUSH_2,
        SENSOR_LONGPUSH_2,
        SENSOR_SHORTPUSH_LONGPUSH_0,
        SENSOR_SHORTPUSH_LONGPUSH_1,
        SENSOR_SHORTPUSH_LONGPUSH_2,
        SENSOR_LONGPUSH_SHORTPUSH_0,
        SENSOR_LONGPUSH_SHORTPUSH_1,
        SENSOR_LONGPUSH_SHORTPUSH_2,
        SENSOR_FIRMWARE_UPDATE,
    ]
    bin_sensors_classes = [
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ]
    bin_sensors_tpls = [
        None,
        None,
        None,
        TPL_SHORTPUSH,
        TPL_DOUBLE_SHORTPUSH,
        TPL_TRIPLE_SHORTPUSH,
        TPL_LONGPUSH,
        TPL_SHORTPUSH,
        TPL_DOUBLE_SHORTPUSH,
        TPL_TRIPLE_SHORTPUSH,
        TPL_LONGPUSH,
        TPL_SHORTPUSH,
        TPL_DOUBLE_SHORTPUSH,
        TPL_TRIPLE_SHORTPUSH,
        TPL_LONGPUSH,
        TPL_SHORTPUSH_LONGPUSH,
        TPL_SHORTPUSH_LONGPUSH,
        TPL_SHORTPUSH_LONGPUSH,
        TPL_LONGPUSH_SHORTPUSH,
        TPL_LONGPUSH_SHORTPUSH,
        TPL_LONGPUSH_SHORTPUSH,
        TPL_NEW_FIRMWARE_FROM_INFO,
    ]
    bin_sensors_topics = [
        TOPIC_INPUT_0,
        TOPIC_INPUT_1,
        TOPIC_INPUT_2,
        TOPIC_INPUT_EVENT_0,
        TOPIC_INPUT_EVENT_0,
        TOPIC_INPUT_EVENT_0,
        TOPIC_INPUT_EVENT_0,
        TOPIC_INPUT_EVENT_1,
        TOPIC_INPUT_EVENT_1,
        TOPIC_INPUT_EVENT_1,
        TOPIC_INPUT_EVENT_1,
        TOPIC_INPUT_EVENT_2,
        TOPIC_INPUT_EVENT_2,
        TOPIC_INPUT_EVENT_2,
        TOPIC_INPUT_EVENT_2,
        TOPIC_INPUT_EVENT_0,
        TOPIC_INPUT_EVENT_1,
        TOPIC_INPUT_EVENT_2,
        TOPIC_INPUT_EVENT_0,
        TOPIC_INPUT_EVENT_1,
        TOPIC_INPUT_EVENT_2,
        TOPIC_INFO,
    ]
    bin_sensors_pl = [
        PL_1_0,
        PL_1_0,
        PL_1_0,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    ]
    sensors = [SENSOR_RSSI, SENSOR_SSID, SENSOR_UPTIME]
    sensors_units = [UNIT_DB, None, None]
    sensors_classes = [DEVICE_CLASS_SIGNAL_STRENGTH, None, DEVICE_CLASS_TIMESTAMP]
    sensors_tpls = [TPL_RSSI, TPL_SSID, TPL_UPTIME]
    sensors_topics = [None, None, None]

# rollers
for roller_id in range(rollers):
    device_config = get_device_config(dev_id)
    config_mode = ATTR_RELAY
    if device_config.get(CONF_MODE):
        config_mode = device_config[CONF_MODE]
    device_name = f"{model} {dev_id.split('-')[-1]}"
    if device_config.get(f"roller-{roller_id}-name"):
        roller_name = device_config[f"roller-{roller_id}-name"]
    else:
        roller_name = f"{device_name} Roller {roller_id}"
    device_class = None
    if device_config.get(f"roller-{roller_id}-class"):
        if device_config[f"roller-{roller_id}-class"] in ROLLER_DEVICE_CLASSES:
            device_class = device_config[f"roller-{roller_id}-class"]
        else:
            logger.error(
                "Wrong roller class, the default value None was used"
            )  # noqa: F821
    default_topic = f"shellies/{dev_id}/"
    state_topic = f"~roller/{roller_id}"
    command_topic = f"{state_topic}/command"
    position_topic = f"{state_topic}/pos"
    set_position_topic = f"{state_topic}/command/pos"
    availability_topic = "~online"
    unique_id = f"{dev_id}-roller-{roller_id}".lower()
    config_topic = f"{disc_prefix}/cover/{dev_id}-roller-{roller_id}/config"
    if config_mode == ATTR_ROLLER:
        roller_mode = True
        payload = {
            KEY_NAME: roller_name,
            KEY_COMMAND_TOPIC: command_topic,
            KEY_POSITION_TOPIC: position_topic,
            KEY_VALUE_TEMPLATE: TPL_POSITION,
            KEY_SET_POSITION_TOPIC: set_position_topic,
            KEY_PAYLOAD_OPEN: VALUE_OPEN,
            KEY_PAYLOAD_CLOSE: VALUE_CLOSE,
            KEY_PAYLOAD_STOP: VALUE_STOP,
            KEY_OPTIMISTIC: VALUE_FALSE,
            KEY_AVAILABILITY_TOPIC: availability_topic,
            KEY_PAYLOAD_AVAILABLE: VALUE_TRUE,
            KEY_PAYLOAD_NOT_AVAILABLE: VALUE_FALSE,
            KEY_UNIQUE_ID: unique_id,
            KEY_QOS: qos,
            KEY_DEVICE: {
                KEY_IDENTIFIERS: [mac],
                KEY_NAME: device_name,
                KEY_MODEL: model,
                KEY_SW_VERSION: fw_ver,
                KEY_MANUFACTURER: ATTR_MANUFACTURER,
            },
            "~": default_topic,
            KEY_JSON_ATTRIBUTES_TOPIC: f"~roller/{roller_id}",
            KEY_JSON_ATTRIBUTES_TEMPLATE: TPL_ROLLER_TO_JSON,
        }
    else:
        payload = ""
    if device_class:
        payload[KEY_DEVICE_CLASS] = device_class
    if dev_id.lower() in ignored:
        payload = ""
    mqtt_publish(
        config_topic, str(payload).replace("'", '"').replace("^", "'"), retain, qos
    )

# relays
for relay_id in range(relays):
    device_config = get_device_config(dev_id)
    device_name = f"{model} {dev_id.split('-')[-1]}"
    if device_config.get(f"relay-{relay_id}-name"):
        relay_name = device_config[f"relay-{relay_id}-name"]
    else:
        relay_name = f"{device_name} Relay {relay_id}"
    default_topic = f"shellies/{dev_id}/"
    state_topic = f"~relay/{relay_id}"
    command_topic = f"{state_topic}/command"
    availability_topic = "~online"
    unique_id = f"{dev_id}-relay-{relay_id}".lower()
    config_component = COMP_SWITCH
    if device_config.get(f"relay-{relay_id}"):
        config_component = device_config[f"relay-{relay_id}"]
    for component in relay_components:
        config_topic = f"{disc_prefix}/{component}/{dev_id}-relay-{relay_id}/config"
        if component == config_component and not roller_mode:
            payload = {
                KEY_NAME: relay_name,
                KEY_COMMAND_TOPIC: command_topic,
                KEY_STATE_TOPIC: state_topic,
                KEY_PAYLOAD_OFF: VALUE_OFF,
                KEY_PAYLOAD_ON: VALUE_ON,
                KEY_AVAILABILITY_TOPIC: availability_topic,
                KEY_PAYLOAD_AVAILABLE: VALUE_TRUE,
                KEY_PAYLOAD_NOT_AVAILABLE: VALUE_FALSE,
                KEY_UNIQUE_ID: unique_id,
                KEY_QOS: qos,
                KEY_DEVICE: {
                    KEY_IDENTIFIERS: [mac],
                    KEY_NAME: device_name,
                    KEY_MODEL: model,
                    KEY_SW_VERSION: fw_ver,
                    KEY_MANUFACTURER: ATTR_MANUFACTURER,
                },
                "~": default_topic,
            }
        else:
            payload = ""
        if dev_id.lower() in ignored:
            payload = ""
        mqtt_publish(config_topic, str(payload).replace("'", '"'), retain, qos)

    # relay's sensors
    if relay_id == relays - 1:
        for sensor_id in range(len(relays_sensors)):
            device_config = get_device_config(dev_id)
            force_update = False
            if isinstance(device_config.get(CONF_FORCE_UPDATE_SENSORS), bool):
                force_update = device_config.get(CONF_FORCE_UPDATE_SENSORS)
            unique_id = f"{dev_id}-relay-{relays_sensors[sensor_id]}".lower()
            config_topic = (
                f"{disc_prefix}/sensor/{dev_id}-{relays_sensors[sensor_id]}/config"
            )
            if device_config.get(f"relay-{relay_id}-name"):
                sensor_name = f"{device_config[f'relay-{relay_id}-name']} {relays_sensors[sensor_id].title()}"
            else:
                sensor_name = f"{device_name} {relays_sensors[sensor_id].title()}"
            state_topic = f"~relay/{relays_sensors[sensor_id]}"
            if model == MODEL_SHELLY2 or roller_mode:
                payload = {
                    KEY_NAME: sensor_name,
                    KEY_STATE_TOPIC: state_topic,
                    KEY_UNIT: relays_sensors_units[sensor_id],
                    KEY_VALUE_TEMPLATE: relays_sensors_tpls[sensor_id],
                    KEY_DEVICE_CLASS: relays_sensors_classes[sensor_id],
                    KEY_AVAILABILITY_TOPIC: availability_topic,
                    KEY_PAYLOAD_AVAILABLE: VALUE_TRUE,
                    KEY_PAYLOAD_NOT_AVAILABLE: VALUE_FALSE,
                    KEY_FORCE_UPDATE: str(force_update),
                    KEY_UNIQUE_ID: unique_id,
                    KEY_QOS: qos,
                    KEY_DEVICE: {
                        KEY_IDENTIFIERS: [mac],
                        KEY_NAME: device_name,
                        KEY_MODEL: model,
                        KEY_SW_VERSION: fw_ver,
                        KEY_MANUFACTURER: ATTR_MANUFACTURER,
                    },
                    "~": default_topic,
                }
            else:
                payload = ""
            if dev_id.lower() in ignored:
                payload = ""
            mqtt_publish(config_topic, str(payload).replace("'", '"'), retain, qos)

    # relay's sensors
    for sensor_id in range(len(relays_sensors)):
        device_config = get_device_config(dev_id)
        force_update = False
        if isinstance(device_config.get(CONF_FORCE_UPDATE_SENSORS), bool):
            force_update = device_config.get(CONF_FORCE_UPDATE_SENSORS)
        unique_id = f"{dev_id}-relay-{relays_sensors[sensor_id]}-{relay_id}".lower()
        config_topic = f"{disc_prefix}/sensor/{dev_id}-{relays_sensors[sensor_id]}-{relay_id}/config"
        if device_config.get(f"relay-{relay_id}-name"):
            sensor_name = f"{device_config[f'relay-{relay_id}-name']} {relays_sensors[sensor_id].title()}"
        else:
            sensor_name = (
                f"{device_name} {relays_sensors[sensor_id].title()} {relay_id}"
            )
        state_topic = f"~relay/{relay_id}/{relays_sensors[sensor_id]}"
        if model != MODEL_SHELLY2 and not roller_mode:
            payload = {
                KEY_NAME: sensor_name,
                KEY_STATE_TOPIC: state_topic,
                KEY_UNIT: relays_sensors_units[sensor_id],
                KEY_VALUE_TEMPLATE: relays_sensors_tpls[sensor_id],
                KEY_DEVICE_CLASS: relays_sensors_classes[sensor_id],
                KEY_AVAILABILITY_TOPIC: availability_topic,
                KEY_PAYLOAD_AVAILABLE: VALUE_TRUE,
                KEY_PAYLOAD_NOT_AVAILABLE: VALUE_FALSE,
                KEY_FORCE_UPDATE: str(force_update),
                KEY_UNIQUE_ID: unique_id,
                KEY_QOS: qos,
                KEY_DEVICE: {
                    KEY_IDENTIFIERS: [mac],
                    KEY_NAME: device_name,
                    KEY_MODEL: model,
                    KEY_SW_VERSION: fw_ver,
                    KEY_MANUFACTURER: ATTR_MANUFACTURER,
                },
                "~": default_topic,
            }
        else:
            payload = ""
        if dev_id.lower() in ignored:
            payload = ""
        mqtt_publish(config_topic, str(payload).replace("'", '"'), retain, qos)

    # relay's binary sensors
    for bin_sensor_id in range(len(relays_bin_sensors)):
        device_config = get_device_config(dev_id)
        push_off_delay = True
        if isinstance(device_config.get(CONF_PUSH_OFF_DELAY), bool):
            push_off_delay = device_config.get(CONF_PUSH_OFF_DELAY)
        unique_id = f"{dev_id}-{relays_bin_sensors[bin_sensor_id]}-{relay_id}".lower()
        config_topic = f"{disc_prefix}/binary_sensor/{dev_id}-{relays_bin_sensors[bin_sensor_id]}-{relay_id}/config"
        if device_config.get(f"relay-{relay_id}-name"):
            sensor_name = f"{device_config[f'relay-{relay_id}-name']} {relays_bin_sensors[bin_sensor_id].title()}"
        else:
            sensor_name = (
                f"{device_name} {relays_bin_sensors[bin_sensor_id].title()} {relay_id}"
            )
        if relays_bin_sensors_topics and relays_bin_sensors_topics[bin_sensor_id]:
            state_topic = f"~{relays_bin_sensors_topics[bin_sensor_id]}/{relay_id}"
        else:
            state_topic = f"~{relays_bin_sensors[bin_sensor_id]}/{relay_id}"
        if not roller_mode:
            payload = {
                KEY_NAME: sensor_name,
                KEY_STATE_TOPIC: state_topic,
                KEY_AVAILABILITY_TOPIC: availability_topic,
                KEY_PAYLOAD_AVAILABLE: VALUE_TRUE,
                KEY_PAYLOAD_NOT_AVAILABLE: VALUE_FALSE,
                KEY_UNIQUE_ID: unique_id,
                KEY_QOS: qos,
                KEY_DEVICE: {
                    KEY_IDENTIFIERS: [mac],
                    KEY_NAME: device_name,
                    KEY_MODEL: model,
                    KEY_SW_VERSION: fw_ver,
                    KEY_MANUFACTURER: ATTR_MANUFACTURER,
                },
                "~": default_topic,
            }
            if (
                relays_bin_sensors[bin_sensor_id]
                in [
                    SENSOR_LONGPUSH,
                    SENSOR_LONGPUSH_0,
                    SENSOR_LONGPUSH_1,
                    SENSOR_LONGPUSH_2,
                    SENSOR_SHORTPUSH,
                    SENSOR_SHORTPUSH_0,
                    SENSOR_SHORTPUSH_1,
                    SENSOR_SHORTPUSH_2,
                    SENSOR_DOUBLE_SHORTPUSH,
                    SENSOR_DOUBLE_SHORTPUSH_0,
                    SENSOR_DOUBLE_SHORTPUSH_1,
                    SENSOR_DOUBLE_SHORTPUSH_2,
                    SENSOR_TRIPLE_SHORTPUSH,
                    SENSOR_TRIPLE_SHORTPUSH_0,
                    SENSOR_TRIPLE_SHORTPUSH_1,
                    SENSOR_TRIPLE_SHORTPUSH_2,
                ]
                and push_off_delay
            ):
                payload[KEY_OFF_DELAY] = OFF_DELAY
            if relays_bin_sensors_tpls[bin_sensor_id]:
                payload[KEY_VALUE_TEMPLATE] = relays_bin_sensors_tpls[bin_sensor_id]
            else:
                payload[KEY_PAYLOAD_ON] = relays_bin_sensors_pl[bin_sensor_id][VALUE_ON]
                payload[KEY_PAYLOAD_OFF] = relays_bin_sensors_pl[bin_sensor_id][
                    VALUE_OFF
                ]
            if relays_bin_sensors_classes[bin_sensor_id]:
                payload[KEY_DEVICE_CLASS] = relays_bin_sensors_classes[bin_sensor_id]
            if (
                model
                in [
                    MODEL_SHELLY1PM,
                    MODEL_SHELLY2,
                    MODEL_SHELLY25,
                    MODEL_SHELLY4PRO,
                    MODEL_SHELLYPLUG,
                    MODEL_SHELLYPLUG_S,
                    MODEL_SHELLYPLUG_US,
                ]
                and relays_bin_sensors[bin_sensor_id] == SENSOR_OVERPOWER
            ):
                payload[
                    KEY_JSON_ATTRIBUTES_TOPIC
                ] = f"~{relays_bin_sensors_topics[bin_sensor_id]}/{relay_id}/{TOPIC_OVERPOWER_VALUE}"
                payload[KEY_JSON_ATTRIBUTES_TEMPLATE] = TPL_OVERPOWER_VALUE_TO_JSON
        else:
            payload = ""
        if dev_id.lower() in ignored:
            payload = ""
        mqtt_publish(
            config_topic, str(payload).replace("'", '"').replace("^", "'"), retain, qos
        )

# sensors
for sensor_id in range(len(sensors)):
    device_config = get_device_config(dev_id)
    force_update = False
    if isinstance(device_config.get(CONF_FORCE_UPDATE_SENSORS), bool):
        force_update = device_config.get(CONF_FORCE_UPDATE_SENSORS)
    device_name = f"{model} {dev_id.split('-')[-1]}"
    unique_id = f"{dev_id}-{sensors[sensor_id]}".lower()
    config_topic = f"{disc_prefix}/sensor/{dev_id}-{sensors[sensor_id]}/config"
    default_topic = f"shellies/{dev_id}/"
    availability_topic = "~online"
    if sensors[sensor_id] in [SENSOR_RSSI, SENSOR_SSID, SENSOR_ADC]:
        sensor_name = f"{device_name} {sensors[sensor_id].upper()}"
    else:
        sensor_name = f"{device_name} {sensors[sensor_id].title()}"
    if sensors[sensor_id] in [SENSOR_RSSI, SENSOR_SSID, SENSOR_UPTIME]:
        state_topic = f"~{TOPIC_INFO}"
    elif relays > 0 or white_lights > 0:
        state_topic = f"~{sensors[sensor_id]}"
    else:
        state_topic = f"~sensor/{sensors[sensor_id]}"

    config_component = COMP_SWITCH
    if battery_powered:
        expire_after = device_config.get(
            CONF_EXPIRE_AFTER, EXPIRE_AFTER_FOR_BATTERY_POWERED
        )
        if device_config.get(CONF_POWERED) == ATTR_POWER_AC:
            no_battery_sensor = True
            expire_after = device_config.get(
                CONF_EXPIRE_AFTER, EXPIRE_AFTER_FOR_AC_POWERED
            )
        if not isinstance(expire_after, int):
            raise TypeError(f"expire_after value {expire_after} is not an integer")
    payload = {
        KEY_NAME: sensor_name,
        KEY_STATE_TOPIC: state_topic,
        KEY_FORCE_UPDATE: str(force_update),
        KEY_UNIQUE_ID: unique_id,
        KEY_QOS: qos,
        KEY_DEVICE: {
            KEY_IDENTIFIERS: [mac],
            KEY_NAME: device_name,
            KEY_MODEL: model,
            KEY_SW_VERSION: fw_ver,
            KEY_MANUFACTURER: ATTR_MANUFACTURER,
        },
        "~": default_topic,
    }
    if model == MODEL_SHELLYDW2 and sensors[sensor_id] == SENSOR_LUX:
        payload[KEY_JSON_ATTRIBUTES_TOPIC] = f"~sensor/{SENSOR_ILLUMINATION}"
        payload[KEY_JSON_ATTRIBUTES_TEMPLATE] = TPL_ILLUMINATION_TO_JSON
    if sensors_units[sensor_id]:
        payload[KEY_UNIT] = sensors_units[sensor_id]
    if sensors_classes[sensor_id]:
        payload[KEY_DEVICE_CLASS] = sensors_classes[sensor_id]
    if sensors_topics[sensor_id]:
        payload[KEY_STATE_TOPIC] = sensors_topics[sensor_id]
    if sensors_tpls[sensor_id]:
        payload[KEY_VALUE_TEMPLATE] = sensors_tpls[sensor_id]
    if sensors[sensor_id] == SENSOR_SSID:
        payload[KEY_ICON] = "mdi:wifi"
    elif sensors[sensor_id] == SENSOR_UPTIME:
        payload[KEY_ICON] = "mdi:timer-outline"
    if battery_powered:
        payload[KEY_EXPIRE_AFTER] = expire_after
    else:
        payload[KEY_AVAILABILITY_TOPIC] = availability_topic
        payload[KEY_PAYLOAD_AVAILABLE] = VALUE_TRUE
        payload[KEY_PAYLOAD_NOT_AVAILABLE] = VALUE_FALSE
    if no_battery_sensor and sensors[sensor_id] == SENSOR_BATTERY:
        payload = ""
    if dev_id.lower() in ignored:
        payload = ""
    mqtt_publish(
        config_topic, str(payload).replace("'", '"').replace("^", "'"), retain, qos
    )

# external temperature sensors
for sensor_id in range(ext_temp_sensors):
    device_config = get_device_config(dev_id)
    force_update = False
    if isinstance(device_config.get(CONF_FORCE_UPDATE_SENSORS), bool):
        force_update = device_config.get(CONF_FORCE_UPDATE_SENSORS)
    device_name = f"{model} {dev_id.split('-')[-1]}"
    unique_id = f"{dev_id}-ext-temperature-{sensor_id}".lower()
    config_topic = f"{disc_prefix}/sensor/{dev_id}-ext-temperature-{sensor_id}/config"
    default_topic = f"shellies/{dev_id}/"
    availability_topic = "~online"
    sensor_name = f"{device_name} External Temperature {sensor_id}"
    state_topic = f"~{SENSOR_EXT_TEMPERATURE}/{sensor_id}"
    if device_config.get(f"ext-temperature-{sensor_id}"):
        payload = {
            KEY_NAME: sensor_name,
            KEY_STATE_TOPIC: state_topic,
            KEY_VALUE_TEMPLATE: TPL_TEMPERATURE_EXT,
            KEY_UNIT: UNIT_CELSIUS,
            KEY_DEVICE_CLASS: SENSOR_TEMPERATURE,
            KEY_FORCE_UPDATE: str(force_update),
            KEY_AVAILABILITY_TOPIC: availability_topic,
            KEY_PAYLOAD_AVAILABLE: VALUE_TRUE,
            KEY_PAYLOAD_NOT_AVAILABLE: VALUE_FALSE,
            KEY_UNIQUE_ID: unique_id,
            KEY_QOS: qos,
            KEY_DEVICE: {
                KEY_IDENTIFIERS: [mac],
                KEY_NAME: device_name,
                KEY_MODEL: model,
                KEY_SW_VERSION: fw_ver,
                KEY_MANUFACTURER: ATTR_MANUFACTURER,
            },
            "~": default_topic,
        }
    else:
        payload = ""
    if dev_id.lower() in ignored:
        payload = ""
    mqtt_publish(config_topic, str(payload).replace("'", '"'), retain, qos)

# external humidity sensors
for sensor_id in range(ext_humi_sensors):
    device_config = get_device_config(dev_id)
    force_update = False
    if isinstance(device_config.get(CONF_FORCE_UPDATE_SENSORS), bool):
        force_update = device_config.get(CONF_FORCE_UPDATE_SENSORS)
    device_name = f"{model} {dev_id.split('-')[-1]}"
    unique_id = f"{dev_id}-ext-humidity-{sensor_id}".lower()
    config_topic = f"{disc_prefix}/sensor/{dev_id}-ext-humidity-{sensor_id}/config"
    default_topic = f"shellies/{dev_id}/"
    availability_topic = "~online"
    sensor_name = f"{device_name} External Humidity {sensor_id}"
    state_topic = f"~{SENSOR_EXT_HUMIDITY}/{sensor_id}"
    if device_config.get(f"ext-temperature-{sensor_id}"):
        payload = {
            KEY_NAME: sensor_name,
            KEY_STATE_TOPIC: state_topic,
            KEY_VALUE_TEMPLATE: TPL_HUMIDITY_EXT,
            KEY_UNIT: UNIT_PERCENT,
            KEY_DEVICE_CLASS: SENSOR_HUMIDITY,
            KEY_FORCE_UPDATE: str(force_update),
            KEY_AVAILABILITY_TOPIC: availability_topic,
            KEY_PAYLOAD_AVAILABLE: VALUE_TRUE,
            KEY_PAYLOAD_NOT_AVAILABLE: VALUE_FALSE,
            KEY_UNIQUE_ID: unique_id,
            KEY_QOS: qos,
            KEY_DEVICE: {
                KEY_IDENTIFIERS: [mac],
                KEY_NAME: device_name,
                KEY_MODEL: model,
                KEY_SW_VERSION: fw_ver,
                KEY_MANUFACTURER: ATTR_MANUFACTURER,
            },
            "~": default_topic,
        }
    else:
        payload = ""
    if dev_id.lower() in ignored:
        payload = ""
    mqtt_publish(config_topic, str(payload).replace("'", '"'), retain, qos)

# binary sensors
for bin_sensor_id in range(len(bin_sensors)):
    device_config = get_device_config(dev_id)
    push_off_delay = True
    if isinstance(device_config.get(CONF_PUSH_OFF_DELAY), bool):
        push_off_delay = device_config.get(CONF_PUSH_OFF_DELAY)
    if battery_powered:
        expire_after = device_config.get(
            CONF_EXPIRE_AFTER, EXPIRE_AFTER_FOR_BATTERY_POWERED
        )
        if device_config.get(CONF_POWERED) == ATTR_POWER_AC:
            no_battery_sensor = True
            expire_after = device_config.get(
                CONF_EXPIRE_AFTER, EXPIRE_AFTER_FOR_AC_POWERED
            )
        if not isinstance(expire_after, int):
            raise TypeError(f"expire_after value {expire_after} is not an integer")
    config_mode = LIGHT_RGBW
    if device_config.get(CONF_MODE):
        config_mode = device_config[CONF_MODE]
    device_name = f"{model} {dev_id.split('-')[-1]}"
    unique_id = f"{dev_id}-{bin_sensors[bin_sensor_id].replace(' ', '-').replace('/', '-')}".lower()
    config_topic = f"{disc_prefix}/binary_sensor/{dev_id}-{bin_sensors[bin_sensor_id].replace(' ', '-').replace('/', '-')}/config"
    default_topic = f"shellies/{dev_id}/"
    availability_topic = "~online"
    sensor_name = (
        f"{device_name} {bin_sensors[bin_sensor_id].replace('/', ' ').title()}"
    )
    if bin_sensors_topics and bin_sensors_topics[bin_sensor_id]:
        state_topic = f"~{bin_sensors_topics[bin_sensor_id]}"
    elif relays > 0 or white_lights > 0:
        state_topic = f"~{bin_sensors[bin_sensor_id]}"
    elif bin_sensors[bin_sensor_id] == SENSOR_OPENING:
        state_topic = "~sensor/state"
    else:
        state_topic = f"~sensor/{bin_sensors[bin_sensor_id]}"
    payload = {
        KEY_NAME: sensor_name,
        KEY_STATE_TOPIC: state_topic,
        KEY_UNIQUE_ID: unique_id,
        KEY_QOS: qos,
        KEY_DEVICE: {
            KEY_IDENTIFIERS: [mac],
            KEY_NAME: device_name,
            KEY_MODEL: model,
            KEY_SW_VERSION: fw_ver,
            KEY_MANUFACTURER: ATTR_MANUFACTURER,
        },
        "~": default_topic,
    }
    if bin_sensors_tpls[bin_sensor_id]:
        payload[KEY_VALUE_TEMPLATE] = bin_sensors_tpls[bin_sensor_id]
    else:
        payload[KEY_PAYLOAD_ON] = bin_sensors_pl[bin_sensor_id][VALUE_ON]
        payload[KEY_PAYLOAD_OFF] = bin_sensors_pl[bin_sensor_id][VALUE_OFF]
    if battery_powered and bin_sensors[bin_sensor_id] != SENSOR_FIRMWARE_UPDATE:
        payload[KEY_EXPIRE_AFTER] = expire_after
    if not battery_powered:
        payload[KEY_AVAILABILITY_TOPIC] = availability_topic
        payload[KEY_PAYLOAD_AVAILABLE] = VALUE_TRUE
        payload[KEY_PAYLOAD_NOT_AVAILABLE] = VALUE_FALSE
    if bin_sensors_classes[bin_sensor_id]:
        payload[KEY_DEVICE_CLASS] = bin_sensors_classes[bin_sensor_id]
    if (
        bin_sensors[bin_sensor_id]
        in [
            SENSOR_LONGPUSH,
            SENSOR_LONGPUSH_0,
            SENSOR_LONGPUSH_1,
            SENSOR_LONGPUSH_2,
            SENSOR_SHORTPUSH,
            SENSOR_SHORTPUSH_0,
            SENSOR_SHORTPUSH_1,
            SENSOR_SHORTPUSH_2,
            SENSOR_DOUBLE_SHORTPUSH,
            SENSOR_DOUBLE_SHORTPUSH_0,
            SENSOR_DOUBLE_SHORTPUSH_1,
            SENSOR_DOUBLE_SHORTPUSH_2,
            SENSOR_TRIPLE_SHORTPUSH,
            SENSOR_TRIPLE_SHORTPUSH_0,
            SENSOR_TRIPLE_SHORTPUSH_1,
            SENSOR_TRIPLE_SHORTPUSH_2,
        ]
        and push_off_delay
    ):
        payload[KEY_OFF_DELAY] = OFF_DELAY
    if (
        model == MODEL_SHELLYRGBW2
        and config_mode == LIGHT_WHITE
        and bin_sensors[bin_sensor_id] == SENSOR_OVERPOWER
    ):
        payload = ""
    if model == MODEL_SHELLYGAS and bin_sensors[bin_sensor_id] == SENSOR_GAS:
        payload[KEY_JSON_ATTRIBUTES_TOPIC] = state_topic
        payload[KEY_JSON_ATTRIBUTES_TEMPLATE] = TPL_GAS_TO_JSON
    if (
        bin_sensors[bin_sensor_id] == SENSOR_FIRMWARE_UPDATE
        and bin_sensors_tpls[bin_sensor_id] == TPL_NEW_FIRMWARE_FROM_INFO
    ):
        payload[KEY_JSON_ATTRIBUTES_TOPIC] = f"~{TOPIC_INFO}"
        payload[KEY_JSON_ATTRIBUTES_TEMPLATE] = TPL_UPDATE_TO_JSON
    if dev_id.lower() in ignored:
        payload = ""
    mqtt_publish(
        config_topic, str(payload).replace("'", '"').replace("^", "'"), retain, qos
    )

# color lights
for light_id in range(rgbw_lights):
    device_config = get_device_config(dev_id)
    device_name = f"{model} {dev_id.split('-')[-1]}"
    if device_config.get(f"light-{light_id}-name"):
        light_name = device_config[f"light-{light_id}-name"]
    else:
        light_name = f"{device_name} Light {light_id}"
    default_topic = f"shellies/{dev_id}/"
    state_topic = f"~color/{light_id}/status"
    command_topic = f"~color/{light_id}/set"
    availability_topic = "~online"
    unique_id = f"{dev_id}-light-{light_id}".lower()
    config_topic = f"{disc_prefix}/light/{dev_id}-{light_id}/config"
    config_mode = LIGHT_RGBW
    if device_config.get(CONF_MODE):
        config_mode = device_config[CONF_MODE]
    if config_mode == LIGHT_RGBW and model == MODEL_SHELLYRGBW2:
        payload = (
            '{"schema":"template",'
            '"name":"' + light_name + '",'
            '"cmd_t":"' + command_topic + '",'
            '"stat_t":"' + state_topic + '",'
            '"avty_t":"' + availability_topic + '",'
            '"pl_avail":"true",'
            '"pl_not_avail":"false",'
            '"fx_list":["Off", "Meteor Shower", "Gradual Change", "Flash"],'
            '"cmd_on_tpl":"{\\"turn\\":\\"on\\"{%if brightness is defined%},\\"gain\\":{{brightness|float|multiply(0.3922)|round}}{%endif%}{%if red is defined and green is defined and blue is defined%},\\"red\\":{{red}},\\"green\\":{{green}},\\"blue\\":{{blue}}{%endif%}{%if white_value is defined%},\\"white\\":{{white_value}}{%endif%}{%if effect is defined%}{%if effect==\\"Meteor Shower\\"%}\\"effect\\":1{%elif effect==\\"Gradual Change\\"%}\\"effect\\":2{%elif effect==\\"Flash\\"%}\\"effect\\":3{%else%}\\"effect\\":0{%endif%}{%else%}\\"effect\\":0{%endif%}}",'
            '"cmd_off_tpl":"{\\"turn\\":\\"off\\"}",'
            '"stat_tpl":"{%if value_json.ison%}on{%else%}off{%endif%}",'
            '"bri_tpl":"{{value_json.gain|float|multiply(2.55)|round}}",'
            '"r_tpl":"{{value_json.red}}",'
            '"g_tpl":"{{value_json.green}}",'
            '"b_tpl":"{{value_json.blue}}",'
            '"whit_val_tpl":"{{value_json.white}}",'
            '"fx_tpl":"{%if value_json.effect==1%}Meteor Shower{%elif value_json.effect==2%}Gradual Change{%elif value_json.effect==3%}Flash{%else%}Off{%endif%}",'
            '"uniq_id":"' + unique_id + '",'
            '"qos":"' + str(qos) + '",'
            '"dev": {"ids": ["' + mac + '"],'
            '"name":"' + device_name + '",'
            '"mdl":"' + model + '",'
            '"sw":"' + fw_ver + '",'
            '"mf":"' + ATTR_MANUFACTURER + '"},'
            '"~":"' + default_topic + '"}'
        )
    elif config_mode == LIGHT_RGBW and model == MODEL_SHELLYBULB:
        payload = (
            '{"schema":"template",'
            '"name":"' + light_name + '",'
            '"cmd_t":"' + command_topic + '",'
            '"stat_t":"' + state_topic + '",'
            '"avty_t":"' + availability_topic + '",'
            '"pl_avail":"true",'
            '"pl_not_avail":"false",'
            '"fx_list":["Off", "Meteor Shower", "Gradual Change", "Breath", "Flash", "On/Off Gradual", "Red/Green Change"],'
            '"cmd_on_tpl":"{\\"turn\\":\\"on\\",\\"mode\\":\\"color\\",{%if red is defined and green is defined and blue is defined%}\\"red\\":{{red}},\\"green\\":{{green}},\\"blue\\":{{blue}},{%endif%}{%if white_value is defined%}\\"white\\":{{white_value}},{%endif%}{%if brightness is defined%}\\"gain\\":{{brightness|float|multiply(0.3922)|round}},{%endif%}{%if effect is defined%}{%if effect == \\"Meteor Shower\\"%}\\"effect\\":1{%elif effect == \\"Gradual Change\\"%}\\"effect\\":2{%elif effect == \\"Breath\\"%}\\"effect\\":3{%elif effect == \\"Flash\\"%}\\"effect\\":4{%elif effect == \\"On/Off Gradual\\"%}\\"effect\\":5{%elif effect == \\"Red/Green Change\\"%}\\"effect\\":6{%else%}\\"effect\\":0{%endif%}{%else%}\\"effect\\":0{%endif%}}",'
            '"cmd_off_tpl":"{\\"turn\\":\\"off\\",\\"mode\\":\\"color\\",\\"effect\\": 0}",'
            '"stat_tpl":"{%if value_json.ison==true and value_json.mode==\\"color\\"%}on{%else%}off{%endif%}",'
            '"bri_tpl":"{{value_json.gain|float|multiply(2.55)|round}}",'
            '"r_tpl":"{{value_json.red}}",'
            '"g_tpl":"{{value_json.green}}",'
            '"b_tpl":"{{value_json.blue}}",'
            '"whit_val_tpl":"{{value_json.white}}",'
            '"fx_tpl":"{%if value_json.effect==1%}Meteor Shower{%elif value_json.effect==2%}Gradual Change{%elif value_json.effect==3%}Breath{%elif value_json.effect==4%}Flash{%elif value_json.effect==5%}On/Off Gradual{%elif value_json.effect==6%}Red/Green Change{%else%}Off{%endif%}",'
            '"uniq_id":"' + unique_id + '",'
            '"qos":"' + str(qos) + '",'
            '"dev": {"ids": ["' + mac + '"],'
            '"name":"' + device_name + '",'
            '"mdl":"' + model + '",'
            '"sw":"' + fw_ver + '",'
            '"mf":"' + ATTR_MANUFACTURER + '"},'
            '"~":"' + default_topic + '"}'
        )
    else:
        payload = ""
    if dev_id.lower() in ignored:
        payload = ""
    mqtt_publish(config_topic, payload, retain, qos)

    # color light's binary sensors
    for bin_sensor_id in range(len(lights_bin_sensors)):
        sensor_name = (
            f"{device_name} {lights_bin_sensors[bin_sensor_id].title()} {light_id}"
        )
        config_topic = f"{disc_prefix}/binary_sensor/{dev_id}-color-{lights_bin_sensors[bin_sensor_id]}-{light_id}/config"
        unique_id = (
            f"{dev_id}-color-{lights_bin_sensors[bin_sensor_id]}-{light_id}".lower()
        )
        if lights_bin_sensors[bin_sensor_id] == SENSOR_INPUT:
            state_topic = f"~{lights_bin_sensors[bin_sensor_id]}/{light_id}"
        else:
            state_topic = f"~color/{light_id}/status"
        if config_mode == LIGHT_RGBW:
            payload = {
                KEY_NAME: sensor_name,
                KEY_STATE_TOPIC: state_topic,
                KEY_AVAILABILITY_TOPIC: availability_topic,
                KEY_PAYLOAD_AVAILABLE: VALUE_TRUE,
                KEY_PAYLOAD_NOT_AVAILABLE: VALUE_FALSE,
                KEY_UNIQUE_ID: unique_id,
                KEY_QOS: qos,
                KEY_DEVICE: {
                    KEY_IDENTIFIERS: [mac],
                    KEY_NAME: device_name,
                    KEY_MODEL: model,
                    KEY_SW_VERSION: fw_ver,
                    KEY_MANUFACTURER: ATTR_MANUFACTURER,
                },
                "~": default_topic,
            }
            if lights_bin_sensors_classes and lights_bin_sensors_classes[bin_sensor_id]:
                payload[KEY_DEVICE_CLASS] = lights_bin_sensors_classes[bin_sensor_id]
            if lights_bin_sensors_tpls and lights_bin_sensors_tpls[bin_sensor_id]:
                payload[KEY_VALUE_TEMPLATE] = lights_bin_sensors_tpls[bin_sensor_id]
            else:
                payload[KEY_PAYLOAD_ON] = lights_bin_sensors_pl[bin_sensor_id][VALUE_ON]
                payload[KEY_PAYLOAD_OFF] = lights_bin_sensors_pl[bin_sensor_id][
                    VALUE_OFF
                ]
        else:
            payload = ""
        if dev_id.lower() in ignored:
            payload = ""
        mqtt_publish(config_topic, str(payload).replace("'", '"'), retain, qos)

    # color light's sensors
    for sensor_id in range(len(lights_sensors)):
        device_config = get_device_config(dev_id)
        force_update = False
        if isinstance(device_config.get(CONF_FORCE_UPDATE_SENSORS), bool):
            force_update = device_config.get(CONF_FORCE_UPDATE_SENSORS)
        unique_id = f"{dev_id}-color-{lights_sensors[sensor_id]}-{light_id}".lower()
        config_topic = f"{disc_prefix}/sensor/{dev_id}-color-{lights_sensors[sensor_id]}-{light_id}/config"
        sensor_name = f"{device_name} {lights_sensors[sensor_id].title()} {light_id}"
        state_topic = f"~color/{light_id}/status"
        if config_mode == LIGHT_RGBW:
            payload = {
                KEY_NAME: sensor_name,
                KEY_STATE_TOPIC: state_topic,
                KEY_UNIT: lights_sensors_units[sensor_id],
                KEY_VALUE_TEMPLATE: lights_sensors_tpls[sensor_id],
                KEY_DEVICE_CLASS: lights_sensors_classes[sensor_id],
                KEY_AVAILABILITY_TOPIC: availability_topic,
                KEY_PAYLOAD_AVAILABLE: VALUE_TRUE,
                KEY_PAYLOAD_NOT_AVAILABLE: VALUE_FALSE,
                KEY_FORCE_UPDATE: str(force_update),
                KEY_UNIQUE_ID: unique_id,
                KEY_QOS: qos,
                KEY_DEVICE: {
                    KEY_IDENTIFIERS: [mac],
                    KEY_NAME: device_name,
                    KEY_MODEL: model,
                    KEY_SW_VERSION: fw_ver,
                    KEY_MANUFACTURER: ATTR_MANUFACTURER,
                },
                "~": default_topic,
            }
        else:
            payload = ""
        if dev_id.lower() in ignored:
            payload = ""
        mqtt_publish(config_topic, str(payload).replace("'", '"'), retain, qos)

# white lights
for light_id in range(white_lights):
    device_config = get_device_config(dev_id)
    device_name = f"{model} {dev_id.split('-')[-1]}"
    if device_config.get(f"light-{light_id}-name"):
        light_name = device_config[f"light-{light_id}-name"]
    else:
        light_name = f"{device_name} Light {light_id}"
    default_topic = f"shellies/{dev_id}/"
    if model in [
        MODEL_SHELLYDIMMER,
        MODEL_SHELLYDIMMER2,
        MODEL_SHELLYDUO,
        MODEL_SHELLYVINTAGE,
    ]:
        state_topic = f"~light/{light_id}/status"
        command_topic = f"~light/{light_id}/set"
        unique_id = f"{dev_id}-light-{light_id}".lower()
        config_topic = f"{disc_prefix}/light/{dev_id}-{light_id}/config"
    else:
        state_topic = f"~white/{light_id}/status"
        command_topic = f"~white/{light_id}/set"
        unique_id = f"{dev_id}-light-white-{light_id}".lower()
        config_topic = f"{disc_prefix}/light/{dev_id}-white-{light_id}/config"
    availability_topic = "~online"
    config_mode = LIGHT_RGBW
    if device_config.get(CONF_MODE):
        config_mode = device_config[CONF_MODE]
    if config_mode == LIGHT_WHITE and model == MODEL_SHELLYRGBW2:
        payload = (
            '{"schema":"template",'
            '"name":"' + light_name + '",'
            '"cmd_t":"' + command_topic + '",'
            '"stat_t":"' + state_topic + '",'
            '"avty_t":"' + availability_topic + '",'
            '"pl_avail":"true",'
            '"pl_not_avail":"false",'
            '"cmd_on_tpl":"{\\"turn\\":\\"on\\"{%if brightness is defined%},\\"brightness\\":{{brightness|float|multiply(0.3922)|round}}{%endif%}{%if white_value is defined%},\\"white\\":{{white_value}}{%endif%}{%if effect is defined%},\\"effect\\":{{effect}}{%endif%}}",'
            '"cmd_off_tpl":"{\\"turn\\":\\"off\\"}",'
            '"stat_tpl":"{%if value_json.ison%}on{%else%}off{%endif%}",'
            '"bri_tpl":"{{value_json.brightness|float|multiply(2.55)|round}}",'
            '"uniq_id":"' + unique_id + '",'
            '"qos":"' + str(qos) + '",'
            '"dev": {"ids": ["' + mac + '"],'
            '"name":"' + device_name + '",'
            '"mdl":"' + model + '",'
            '"sw":"' + fw_ver + '",'
            '"mf":"' + ATTR_MANUFACTURER + '"},'
            '"~":"' + default_topic + '"}'
        )
    elif model in [MODEL_SHELLYDIMMER, MODEL_SHELLYDIMMER2]:
        payload = (
            '{"schema":"template",'
            '"name":"' + light_name + '",'
            '"cmd_t":"' + command_topic + '",'
            '"stat_t":"' + state_topic + '",'
            '"avty_t":"' + availability_topic + '",'
            '"pl_avail":"true",'
            '"pl_not_avail":"false",'
            '"cmd_on_tpl":"{\\"turn\\":\\"on\\"{%if brightness is defined%},\\"brightness\\":{{brightness|float|multiply(0.3922)|round}}{%endif%}}",'
            '"cmd_off_tpl":"{\\"turn\\":\\"off\\"}",'
            '"stat_tpl":"{%if value_json.ison%}on{%else%}off{%endif%}",'
            '"bri_tpl":"{{value_json.brightness|float|multiply(2.55)|round}}",'
            '"uniq_id":"' + unique_id + '",'
            '"qos":"' + str(qos) + '",'
            '"dev": {"ids": ["' + mac + '"],'
            '"name":"' + device_name + '",'
            '"mdl":"' + model + '",'
            '"sw":"' + fw_ver + '",'
            '"mf":"' + ATTR_MANUFACTURER + '"},'
            '"~":"' + default_topic + '"}'
        )
    elif model == MODEL_SHELLYDUO:
        payload = (
            '{"schema":"template",'
            '"name":"' + light_name + '",'
            '"cmd_t":"' + command_topic + '",'
            '"stat_t":"' + state_topic + '",'
            '"avty_t":"' + availability_topic + '",'
            '"pl_avail":"true",'
            '"pl_not_avail":"false",'
            '"cmd_on_tpl":"{\\"turn\\":\\"on\\"{%if brightness is defined%},\\"brightness\\":{{brightness|float|multiply(0.3922)|round}}{%endif%}{%if color_temp is defined%},\\"temp\\":{{(1000000/(color_temp|int))|round(0,\\"floor\\")}}{%endif%}}",'
            '"cmd_off_tpl":"{\\"turn\\":\\"off\\"}",'
            '"stat_tpl":"{%if value_json.ison%}on{%else%}off{%endif%}",'
            '"bri_tpl":"{{value_json.brightness|float|multiply(2.55)|round}}",'
            '"clr_temp_tpl":"{{((1000000/(value_json.temp|int,2700)|max)|round(0,\\"floor\\"))}}",'
            '"max_mireds":370,'
            '"min_mireds":153,'
            '"uniq_id":"' + unique_id + '",'
            '"qos":"' + str(qos) + '",'
            '"dev": {"ids": ["' + mac + '"],'
            '"name":"' + device_name + '",'
            '"mdl":"' + model + '",'
            '"sw":"' + fw_ver + '",'
            '"mf":"' + ATTR_MANUFACTURER + '"},'
            '"~":"' + default_topic + '"}'
        )
    elif model == MODEL_SHELLYVINTAGE:
        payload = (
            '{"schema":"template",'
            '"name":"' + light_name + '",'
            '"cmd_t":"' + command_topic + '",'
            '"stat_t":"' + state_topic + '",'
            '"avty_t":"' + availability_topic + '",'
            '"pl_avail":"true",'
            '"pl_not_avail":"false",'
            '"cmd_on_tpl":"{\\"turn\\":\\"on\\"{%if brightness is defined%},\\"brightness\\":{{brightness|float|multiply(0.3922)|round}}{%endif%}}",'
            '"cmd_off_tpl":"{\\"turn\\":\\"off\\"}",'
            '"stat_tpl":"{%if value_json.ison%}on{%else%}off{%endif%}",'
            '"bri_tpl":"{{value_json.brightness|float|multiply(2.55)|round}}",'
            '"uniq_id":"' + unique_id + '",'
            '"qos":"' + str(qos) + '",'
            '"dev": {"ids": ["' + mac + '"],'
            '"name":"' + device_name + '",'
            '"mdl":"' + model + '",'
            '"sw":"' + fw_ver + '",'
            '"mf":"' + ATTR_MANUFACTURER + '"},'
            '"~":"' + default_topic + '"}'
        )
    else:
        payload = ""
    if dev_id.lower() in ignored:
        payload = ""
    mqtt_publish(config_topic, payload, retain, qos)

    # white light's binary sensors
    for bin_sensor_id in range(len(lights_bin_sensors)):
        if (
            lights_bin_sensors[bin_sensor_id] == SENSOR_INPUT and light_id == 0
        ) or lights_bin_sensors[bin_sensor_id] != SENSOR_INPUT:
            unique_id = (
                f"{dev_id}-white-{lights_bin_sensors[bin_sensor_id]}-{light_id}".lower()
            )
            config_topic = f"{disc_prefix}/binary_sensor/{dev_id}-white-{lights_bin_sensors[bin_sensor_id]}-{light_id}/config"
            if lights_bin_sensors[bin_sensor_id] == SENSOR_INPUT:
                state_topic = f"~{lights_bin_sensors[bin_sensor_id]}/{light_id}"
            else:
                state_topic = f"~white/{light_id}/status"
            sensor_name = (
                f"{device_name} {lights_bin_sensors[bin_sensor_id].title()} {light_id}"
            )
            if config_mode != LIGHT_RGBW:
                payload = {
                    KEY_NAME: sensor_name,
                    KEY_STATE_TOPIC: state_topic,
                    KEY_AVAILABILITY_TOPIC: availability_topic,
                    KEY_PAYLOAD_AVAILABLE: VALUE_TRUE,
                    KEY_PAYLOAD_NOT_AVAILABLE: VALUE_FALSE,
                    KEY_UNIQUE_ID: unique_id,
                    KEY_QOS: qos,
                    KEY_DEVICE: {
                        KEY_IDENTIFIERS: [mac],
                        KEY_NAME: device_name,
                        KEY_MODEL: model,
                        KEY_SW_VERSION: fw_ver,
                        KEY_MANUFACTURER: ATTR_MANUFACTURER,
                    },
                    "~": default_topic,
                }
                if (
                    lights_bin_sensors_classes
                    and lights_bin_sensors_classes[bin_sensor_id]
                ):
                    payload[KEY_DEVICE_CLASS] = lights_bin_sensors_classes[
                        bin_sensor_id
                    ]
                if lights_bin_sensors_tpls and lights_bin_sensors_tpls[bin_sensor_id]:
                    payload[KEY_VALUE_TEMPLATE] = lights_bin_sensors_tpls[bin_sensor_id]
                else:
                    payload[KEY_PAYLOAD_ON] = lights_bin_sensors_pl[bin_sensor_id][
                        VALUE_ON
                    ]
                    payload[KEY_PAYLOAD_OFF] = lights_bin_sensors_pl[bin_sensor_id][
                        VALUE_OFF
                    ]

            else:
                payload = ""
            if dev_id.lower() in ignored:
                payload = ""
            mqtt_publish(config_topic, str(payload).replace("'", '"'), retain, qos)

    # white light's sensors
    for sensor_id in range(len(lights_sensors)):
        device_config = get_device_config(dev_id)
        force_update = False
        if isinstance(device_config.get(CONF_FORCE_UPDATE_SENSORS), bool):
            force_update = device_config.get(CONF_FORCE_UPDATE_SENSORS)
        unique_id = f"{dev_id}-white-{lights_sensors[sensor_id]}-{light_id}".lower()
        config_topic = f"{disc_prefix}/sensor/{dev_id}-white-{lights_sensors[sensor_id]}-{light_id}/config"
        sensor_name = f"{device_name} {lights_sensors[sensor_id].title()} {light_id}"
        if model in [
            MODEL_SHELLYDIMMER,
            MODEL_SHELLYDIMMER2,
            MODEL_SHELLYDUO,
            MODEL_SHELLYVINTAGE,
        ]:
            state_topic = f"~light/{light_id}/{lights_sensors[sensor_id]}"
        else:
            state_topic = f"~white/{light_id}/status"
        if model in [
            MODEL_SHELLYDIMMER,
            MODEL_SHELLYDIMMER2,
            MODEL_SHELLYDUO,
            MODEL_SHELLYVINTAGE,
        ]:
            payload = {
                KEY_NAME: sensor_name,
                KEY_STATE_TOPIC: state_topic,
                KEY_UNIT: lights_sensors_units[sensor_id],
                KEY_VALUE_TEMPLATE: lights_sensors_tpls[sensor_id],
                KEY_DEVICE_CLASS: lights_sensors_classes[sensor_id],
                KEY_AVAILABILITY_TOPIC: availability_topic,
                KEY_PAYLOAD_AVAILABLE: VALUE_TRUE,
                KEY_PAYLOAD_NOT_AVAILABLE: VALUE_FALSE,
                KEY_FORCE_UPDATE: str(force_update),
                KEY_UNIQUE_ID: unique_id,
                KEY_QOS: qos,
                KEY_DEVICE: {
                    KEY_IDENTIFIERS: [mac],
                    KEY_NAME: device_name,
                    KEY_MODEL: model,
                    KEY_SW_VERSION: fw_ver,
                    KEY_MANUFACTURER: ATTR_MANUFACTURER,
                },
                "~": default_topic,
            }
        else:
            payload = ""
        if dev_id.lower() in ignored:
            payload = ""
        mqtt_publish(config_topic, str(payload).replace("'", '"'), retain, qos)

# meters
for meter_id in range(meters):
    device_config = get_device_config(dev_id)
    force_update = False
    if isinstance(device_config.get(CONF_FORCE_UPDATE_SENSORS), bool):
        force_update = device_config.get(CONF_FORCE_UPDATE_SENSORS)
    device_name = f"{model} {dev_id.split('-')[-1]}"
    default_topic = f"shellies/{dev_id}/"
    availability_topic = "~online"
    for sensor_id in range(len(meters_sensors)):
        unique_id = f"{dev_id}-emeter-{meters_sensors[sensor_id]}-{meter_id}".lower()
        config_topic = f"{disc_prefix}/sensor/{dev_id}-emeter-{meters_sensors[sensor_id]}-{meter_id}/config"
        sensor_name = (
            f"{device_name} Meter {meters_sensors[sensor_id].title()} {meter_id}"
        )
        state_topic = f"~emeter/{meter_id}/{meters_sensors[sensor_id]}"
        payload = {
            KEY_NAME: sensor_name,
            KEY_STATE_TOPIC: state_topic,
            KEY_UNIT: meters_sensors_units[sensor_id],
            KEY_VALUE_TEMPLATE: meters_sensors_tpls[sensor_id],
            KEY_AVAILABILITY_TOPIC: availability_topic,
            KEY_PAYLOAD_AVAILABLE: VALUE_TRUE,
            KEY_PAYLOAD_NOT_AVAILABLE: VALUE_FALSE,
            KEY_FORCE_UPDATE: str(force_update),
            KEY_UNIQUE_ID: unique_id,
            KEY_QOS: qos,
            KEY_DEVICE: {
                KEY_IDENTIFIERS: [mac],
                KEY_NAME: device_name,
                KEY_MODEL: model,
                KEY_SW_VERSION: fw_ver,
                KEY_MANUFACTURER: ATTR_MANUFACTURER,
            },
            "~": default_topic,
        }
        if meters_sensors_classes and meters_sensors_classes[sensor_id]:
            payload[KEY_DEVICE_CLASS] = meters_sensors_classes[sensor_id]
        if dev_id.lower() in ignored:
            payload = ""
        mqtt_publish(config_topic, str(payload).replace("'", '"'), retain, qos)
