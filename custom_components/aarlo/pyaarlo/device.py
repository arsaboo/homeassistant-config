import pprint
import threading

from .constant import (BATTERY_KEY, BATTERY_TECH_KEY, CHARGING_KEY, CHARGER_KEY,
                       CONNECTION_KEY, DEVICE_KEYS, RESOURCE_KEYS,
                       RESOURCE_UPDATE_KEYS, SIGNAL_STR_KEY,
                       XCLOUD_ID_KEY)


class ArloDevice(object):
    """ Base class for all Arlo devices.

    Has code to handle providing common attributes and comment event handling.
    """

    def __init__(self, name, arlo, attrs):
        self._name = name
        self._arlo = arlo
        self._attrs = attrs

        self._lock = threading.Lock()
        self._attr_cbs_ = []

        # stuff we use a lot
        self._device_id = attrs.get('deviceId', None)
        self._device_type = attrs.get('deviceType', 'unknown')
        self._unique_id = attrs.get('uniqueId', None)

        # Build initial values... attrs is device state
        for key in DEVICE_KEYS:
            value = attrs.get(key, None)
            if value is not None:
                self._save(key, value)

        # add a listener
        self._arlo.be.add_listener(self, self._event_handler)

    def __repr__(self):
        # Representation string of object.
        return "<{0}:{1}:{2}>".format(self.__class__.__name__, self._device_type, self._name)

    def _to_storage_key(self, attr):
        # Build a key incorporating the type!
        if isinstance(attr, list):
            return [self.__class__.__name__, self._device_id] + attr
        else:
            return [self.__class__.__name__, self._device_id, attr]

    def _event_handler(self, resource, event):
        self._arlo.vdebug("{}: got {} event {}".format(self.name, resource, pprint.pformat(event)))

        # Find properties. Event either contains a item called properties or it
        # is the whole thing.
        props = event.get("properties", event)

        # Save out new values.
        for key in props:
            if key in RESOURCE_KEYS or key in RESOURCE_UPDATE_KEYS:
                value = props.get(key, None)
                if value is not None:
                    self._save_and_do_callbacks(key, value)

    def _do_callbacks(self, attr, value):
        cbs = []
        with self._lock:
            for watch, cb in self._attr_cbs_:
                if watch == attr or watch == '*':
                    cbs.append(cb)
        for cb in cbs:
            cb(self, attr, value)

    def _save(self, attr, value):
        # TODO only care if it changes?
        self._arlo.st.set(self._to_storage_key(attr), value)

    def _save_and_do_callbacks(self, attr, value):
        self._save(attr, value)
        self._do_callbacks(attr, value)

    def _load(self, attr, default=None):
        return self._arlo.st.get(self._to_storage_key(attr), default)

    def _load_matching(self, attr, default=None):
        return self._arlo.st.get_matching(self._to_storage_key(attr), default)

    @property
    def name(self):
        """ Return the device name. """
        return self._name

    @property
    def device_id(self):
        """ Return the Arlo provided device id. """
        return self._device_id

    @property
    def resource_id(self):
        """ The resource id, used for making requests and checking responses.

        For base stations has the format [DEVICE-ID] and for other devices has
        the format [RESOURCE-TYPE]/[DEVICE-ID]
        """
        return self._device_id

    @property
    def resource_type(self):
        """ The type of resource this is.

        For example, cameras, doorbells or basestations.
        """
        return None

    @property
    def serial_number(self):
        """ Return the device serial number. """
        return self._device_id

    @property
    def device_type(self):
        """ Return the device type. """
        return self._device_type

    @property
    def model_id(self):
        """ Return the model id. """
        return self._attrs.get('modelId', None)

    @property
    def hw_version(self):
        """ Return the hardware version. """
        return self._attrs.get('properties', {}).get('hwVersion', None)

    @property
    def timezone(self):
        """ Return the timezone. """
        return self._attrs.get('properties', {}).get('olsonTimeZone', None)

    @property
    def user_id(self):
        """ Return the user id. """
        return self._attrs.get('userId', None)

    @property
    def user_role(self):
        """ Return the user role. """
        return self._attrs.get('userRole', None)

    @property
    def xcloud_id(self):
        """ Return the xcloud id. """
        return self._load(XCLOUD_ID_KEY, 'UNKNOWN')

    @property
    def web_id(self):
        """ Return the web id. """
        return self.user_id + '_web'

    @property
    def unique_id(self):
        """ Return the unique id. """
        return self._unique_id

    def attribute(self, attr, default=None):
        """ Return the value of a given attribute. """
        value = self._load(attr, None)
        if value is None:
            value = self._attrs.get(attr, None)
        if value is None:
            value = self._attrs.get('properties', {}).get(attr, None)
        if value is None:
            value = default
        return value

    def add_attr_callback(self, attr, cb):
        """ Add an callback to be triggered when an attribute changes. """
        with self._lock:
            self._attr_cbs_.append((attr, cb))

    def has_capability(self, cap):
        """ Is the camera capabale of performing an activity. """
        return False

    @property
    def state(self):
        """ Return the current state. """
        return 'idle'

    @property
    def is_on(self):
        """ Is the device turned on? """
        return True

    def turn_on(self):
        """ Turn the device on. """
        pass

    def turn_off(self):
        """ Turn the device off. """
        pass

    @property
    def is_unavailable(self):
        """ Is the device available. """
        return self._load(CONNECTION_KEY, 'unknown') == 'unavailable'


class ArloChildDevice(ArloDevice):
    """ Base class for all Arlo devices that attach to a base station.
    """

    def __init__(self, name, arlo, attrs):
        super().__init__(name, arlo, attrs)

        self._parent_id = attrs.get('parentId', None)
        self._arlo.debug('parent is {}'.format(self._parent_id))
        self._arlo.vdebug('resource is {}'.format(self.resource_id))

    @property
    def resource_type(self):
        """ Return the resource type this object describes. """
        return "child"

    @property
    def resource_id(self):
        """ Shortcut for mostly used resource id.

        Some devices - certain cameras - can provide other types.
        """
        return self.resource_type + "/" + self._device_id

    @property
    def parent_id(self):
        """ Parent device id.

        Some devices - ArloBaby for example - are their own parents.
        """
        if self._parent_id is not None:
            return self._parent_id
        return self.device_id

    @property
    def base_station(self):
        """ Return the base station controlling this device.

        Some devices - ArloBaby for example - are their own parents. If we
        can't find a basestation we return the first one.
        """
        # look for real parents
        for base in self._arlo.base_stations:
            if base.device_id == self.parent_id:
                return base
        # some cameras don't have base stations... it's its own basestation...
        for base in self._arlo.base_stations:
            if base.device_id == self.device_id:
                return base
        # no idea!
        return self._arlo.base_stations[0]

    @property
    def battery_level(self):
        """ Return the current battery level. """
        return self._load(BATTERY_KEY, 100)

    @property
    def battery_tech(self):
        """ Return the current battery technology. """
        return self._load(BATTERY_TECH_KEY, 'None')

    @property
    def charging(self):
        """ Is the device recharging. """
        return self._load(CHARGING_KEY, 'off').lower() == 'on'

    @property
    def charger_type(self):
        """ How the device is recharging. """
        return self._load(CHARGER_KEY, 'None')

    @property
    def wired(self):
        """ Is the device plugged in? """
        return self.charger_type.lower() != 'none'

    @property
    def wired_only(self):
        """ Is the device plugged only in?

        ie. Does it have battery back up?
        """
        return self.battery_tech.lower() == 'none' and self.wired

    @property
    def signal_strength(self):
        """ Return the WiFi signal strength. """
        return self._load(SIGNAL_STR_KEY, 3)

    @property
    def is_unavailable(self):
        """ Is the device available. """
        return self.base_station.is_unavailable or self._load(CONNECTION_KEY, 'unknown') == 'unavailable'

    @property
    def too_cold(self):
        """ Is the device too cold to operate? """
        return self._load(CONNECTION_KEY, 'unknown') == 'thermalShutdownCold'

    @property
    def state(self):
        """ Return the camera current state. """
        if self.is_unavailable:
            return 'unavailable'
        if not self.is_on:
            return 'turned off'
        if self.too_cold:
            return 'offline, too cold'
        return 'idle'
