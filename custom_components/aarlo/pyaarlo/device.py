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

        # Activities. Used by camera for now but made available to all.
        self._activities = {}

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
        self._arlo.vdebug("{}: got {} event **".format(self.name, resource))

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
    def entity_id(self):
        if self._arlo.cfg.serial_ids:
            return self.device_id
        else:
            return self.name.lower().replace(' ', '_')

    @property
    def name(self):
        """Returns the device name.
        """
        return self._name

    @property
    def device_id(self):
        """Returns the device's id.

        """
        return self._device_id

    @property
    def resource_id(self):
        """Returns the resource id, used for making requests and checking responses.

        For base stations has the format [DEVICE-ID] and for other devices has
        the format [RESOURCE-TYPE]/[DEVICE-ID]
        """
        return self._device_id

    @property
    def resource_type(self):
        """Returns the type of resource this is.

        For now it's, `cameras`, `doorbells`, `lights` or `basestations`.
        """
        return None

    @property
    def serial_number(self):
        """Returns the device serial number.
        """
        return self._device_id

    @property
    def device_type(self):
        """Returns the Arlo reported device type.
\
        """
        return self._device_type

    @property
    def model_id(self):
        """Returns the model id.
        """
        return self._attrs.get('modelId', None)

    @property
    def hw_version(self):
        """Returns the hardware version.
        """
        return self._attrs.get('properties', {}).get('hwVersion', None)

    @property
    def timezone(self):
        """Returns the timezone.
        """
        return self._attrs.get('properties', {}).get('olsonTimeZone', None)

    @property
    def user_id(self):
        """Returns the user id.
        """
        return self._attrs.get('userId', None)

    @property
    def user_role(self):
        """Returns the user role.
        """
        return self._attrs.get('userRole', None)

    @property
    def xcloud_id(self):
        """Returns the device's xcloud id.
        """
        return self._load(XCLOUD_ID_KEY, 'UNKNOWN')

    @property
    def web_id(self):
        """Return the device's web id.
        """
        return self.user_id + '_web'

    @property
    def unique_id(self):
        """Returns the device's unique id.
        """
        return self._unique_id

    def attribute(self, attr, default=None):
        """Return the value of attribute attr.

        PyArlo stores its state in key/value pairs. This returns the value associated with the key.

        See PyArlo for a non-exhaustive list of attributes.

        :param attr: Attribute to look up.
        :type attr: str
        :param default: value to return if not found.
        :return: The value associated with attribute or `default` if not found.
        """
        value = self._load(attr, None)
        if value is None:
            value = self._attrs.get(attr, None)
        if value is None:
            value = self._attrs.get('properties', {}).get(attr, None)
        if value is None:
            value = default
        return value

    def add_attr_callback(self, attr, cb):
        """Add an callback to be triggered when an attribute changes.

        Used to register callbacks to track device activity. For example, get a notification whenever
        motion stop and starts.

        See PyArlo for a non-exhaustive list of attributes.

        :param attr: Attribute - eg `motionStarted` - to monitor.
        :type attr: str
        :param cb: Callback to run.
        """
        with self._lock:
            self._attr_cbs_.append((attr, cb))

    def has_capability(self, cap):
        """Is the device capable of performing activity cap:.

        Used to determine if devices can perform certain actions, like motion or audio detection.

        See attribute list against PyArlo.

        :param cap: Attribute - eg `motionStarted` - to check.
        :return: `True` it is, `False` it isn't.
        """
        if cap in (CONNECTION_KEY,):
            return True
        return False

    @property
    def state(self):
        """Returns a string describing the device's current state.
        """
        return 'idle'

    @property
    def is_on(self):
        """Returns `True` if the device is on, `False` otherwise.
        """
        return True

    def turn_on(self):
        """Turn the device on.
        """
        pass

    def turn_off(self):
        """Turn the device off.
        """
        pass

    @property
    def is_unavailable(self):
        """Returns `True` if the device is unavailable, `False` otherwise.

        **Note:** Sorry about the double negative.
        """
        return self._load(CONNECTION_KEY, 'unknown') == 'unavailable'


class ArloChildDevice(ArloDevice):
    """Base class for all Arlo devices that attach to a base station.
    """

    def __init__(self, name, arlo, attrs):
        super().__init__(name, arlo, attrs)

        self._parent_id = attrs.get('parentId', None)
        self._arlo.debug('parent is {}'.format(self._parent_id))
        self._arlo.vdebug('resource is {}'.format(self.resource_id))

    def _event_handler(self, resource, event):
        self._arlo.vdebug("{}: child got {} event **".format(self.name, resource))

        if resource.endswith('/states'):
            self._arlo.bg.run(self.base_station.update_mode)
            return

        # Pass event to lower level.
        super()._event_handler(resource, event)

    @property
    def resource_type(self):
        """Return the resource type this child device describes.

        Currently limited to `camera`, `doorbell` and `light`.
        """
        return "child"

    @property
    def resource_id(self):
        """Returns the child device resource id.

        Some devices - certain cameras - can provide other types.
        """
        return self.resource_type + "/" + self._device_id

    @property
    def parent_id(self):
        """Returns the parent device id.

        **Note:** Some devices - ArloBaby for example - are their own parents.
        """
        if self._parent_id is not None:
            return self._parent_id
        return self.device_id

    @property
    def base_station(self):
        """Returns the base station controlling this device.

        Some devices - ArloBaby for example - are their own parents. If we
        can't find a basestation, this returns the first one (if any exist).
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
        if len(self._arlo.base_stations) > 0:
            return self._arlo.base_stations[0]

        self._arlo.error("Could not find any base stations for device " + self._name)
        return None

        
    @property
    def battery_level(self):
        """Returns the current battery level.
        """
        return self._load(BATTERY_KEY, 100)

    @property
    def battery_tech(self):
        """Returns the current battery technology.

        Is it rechargable, wired...
        """
        return self._load(BATTERY_TECH_KEY, 'None')

    @property
    def charging(self):
        """Returns `True` if the device is recharging, `False` otherwise.
        """
        return self._load(CHARGING_KEY, 'off').lower() == 'on'

    @property
    def charger_type(self):
        """Returns how the device is recharging.
        """
        return self._load(CHARGER_KEY, 'None')

    @property
    def wired(self):
        """Returns `True` if the device plugged in, `False` otherwise.
        """
        return self.charger_type.lower() != 'none'

    @property
    def wired_only(self):
        """Returns `True` if the device is plugged in with no batteries, `False` otherwise.
        """
        return self.battery_tech.lower() == 'none' and self.wired

    @property
    def signal_strength(self):
        """Returns the WiFi signal strength (0-5).
        """
        return self._load(SIGNAL_STR_KEY, 3)

    @property
    def is_unavailable(self):
        if not self.base_station:
            return True

        return self.base_station.is_unavailable or self._load(CONNECTION_KEY, 'unknown') == 'unavailable'

    @property
    def too_cold(self):
        """Returns `True` if the device too cold to operate, `False` otherwise.
        """
        return self._load(CONNECTION_KEY, 'unknown') == 'thermalShutdownCold'

    @property
    def state(self):
        if self.is_unavailable:
            return 'unavailable'
        if not self.is_on:
            return 'off'
        if self.too_cold:
            return 'offline, too cold'
        return 'idle'
