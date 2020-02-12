import pprint
import threading

from .constant import (BATTERY_KEY, BATTERY_TECH_KEY, CHARGING_KEY, CHARGER_KEY,
                       CONNECTION_KEY, RESOURCE_KEYS,
                       RESOURCE_UPDATE_KEYS, SIGNAL_STR_KEY,
                       XCLOUD_ID_KEY)


class ArloDevice(object):

    def __init__(self, name, arlo, attrs):
        self._name = name
        self._arlo = arlo
        self._attrs = attrs

        self._lock = threading.Lock()
        self._attr_cbs_ = []

        # stuff we use a lot
        self._device_id = attrs.get('deviceId', None)
        self._device_type = attrs.get('deviceType', None)
        self._unique_id = attrs.get('uniqueId', None)

        # add a listener
        self._arlo.be.add_listener(self, self._event_handler)

    def __repr__(self):
        # Representation string of object.
        return "<{0}:{1}:{2}>".format(self.__class__.__name__, self._device_type, self._name)

    def _event_handler(self, resource, event):
        self._arlo.vdebug("{}: got {} event {}".format(self.name, resource, pprint.pformat(event)))

        # Find properties. Event either contains a item called properites or it
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
        key = [self.device_id, attr]
        self._arlo.st.set(key, value)

    def _save_and_do_callbacks(self, attr, value):
        self._save(attr, value)
        self._do_callbacks(attr, value)

    @property
    def name(self):
        return self._name

    @property
    def device_id(self):
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
        return self._device_id

    @property
    def device_type(self):
        return self._device_type

    @property
    def model_id(self):
        return self._attrs.get('modelId', None)

    @property
    def hw_version(self):
        return self._attrs.get('properties', {}).get('hwVersion', None)

    @property
    def timezone(self):
        return self._attrs.get('properties', {}).get('olsonTimeZone', None)

    @property
    def user_id(self):
        return self._attrs.get('userId', None)

    @property
    def user_role(self):
        return self._attrs.get('userRole', None)

    @property
    def xcloud_id(self):
        return self._arlo.st.get([self._device_id, XCLOUD_ID_KEY], 'UNKNOWN')

    @property
    def web_id(self):
        return self.user_id + '_web'

    @property
    def unique_id(self):
        return self._unique_id

    def attribute(self, attr, default=None):
        value = self._arlo.st.get([self._device_id, attr], None)
        if value is None:
            value = self._attrs.get(attr, None)
        if value is None:
            value = self._attrs.get('properties', {}).get(attr, None)
        if value is None:
            value = default
        return value

    def add_attr_callback(self, attr, cb):
        with self._lock:
            self._attr_cbs_.append((attr, cb))

    def has_capability(self, cap):
        return False

    @property
    def state(self):
        return 'idle'

    @property
    def is_on(self):
        return True

    def turn_on(self):
        pass

    def turn_off(self):
        pass


class ArloChildDevice(ArloDevice):

    def __init__(self, name, arlo, attrs):
        super().__init__(name, arlo, attrs)

        self._parent_id = attrs.get('parentId', None)
        self._arlo.debug('parent is {}'.format(self._parent_id))
        self._arlo.vdebug('resource is {}'.format(self.resource_id))

    @property
    def resource_type(self):
        return "child"

    @property
    def resource_id(self):
        """ Shortcut for mostly used resource id.

        Some devices - certain cameras - can provide other types.
        """
        return self.resource_type + "/" + self._device_id

    @property
    def parent_id(self):
        if self._parent_id is not None:
            # self._arlo.debug('real parent is {}'.format(self._parent_id))
            return self._parent_id
        # self._arlo.debug('fake parent is {}'.format(self.device_id))
        return self.device_id

    @property
    def base_station(self):
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
        return self._arlo.st.get([self._device_id, BATTERY_KEY], 100)

    @property
    def battery_tech(self):
        return self._arlo.st.get([self._device_id, BATTERY_TECH_KEY], 'None')

    @property
    def charging(self):
        return self._arlo.st.get([self._device_id, CHARGING_KEY], 'off').lower() == 'on'

    @property
    def charger_type(self):
        return self._arlo.st.get([self._device_id, CHARGER_KEY], 'None')

    @property
    def wired(self):
        return self.charger_type.lower() != 'none'

    @property
    def wired_only(self):
        return self.battery_tech.lower() == 'none' and self.wired

    @property
    def signal_strength(self):
        return self._arlo.st.get([self._device_id, SIGNAL_STR_KEY], 3)

    @property
    def is_unavailable(self):
        return self._arlo.st.get([self._device_id, CONNECTION_KEY], 'unknown') == 'unavailable'

    @property
    def too_cold(self):
        return self._arlo.st.get([self._device_id, CONNECTION_KEY], 'unknown') == 'thermalShutdownCold'

    @property
    def state(self):
        if self.is_unavailable:
            return 'unavailable'
        if not self.is_on:
            return 'turned off'
        if self.too_cold:
            return 'offline, too cold'
        return 'idle'
