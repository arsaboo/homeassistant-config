import pprint

from .constant import (LAMP_STATE_KEY, BRIGHTNESS_KEY, BATTERY_KEY, MOTION_DETECTED_KEY)
from .device import ArloChildDevice


class ArloLight(ArloChildDevice):

    def __init__(self, name, arlo, attrs):
        super().__init__(name, arlo, attrs)

    @property
    def resource_type(self):
        """ Return the resource type this object describes. """
        return "lights"

    def _event_handler(self, resource, event):
        self._arlo.debug(self.name + ' LIGHT got one ' + resource)

        # pass on to lower layer
        super()._event_handler(resource, event)

    @property
    def is_on(self):
        """ Is the light on? """
        return self._load(LAMP_STATE_KEY, "off") == "on"

    def turn_on(self, brightness=None, rgb=None):
        """ Turn the light on. """
        properties = {LAMP_STATE_KEY: 'on'}
        if brightness is not None:
            properties[BRIGHTNESS_KEY] = brightness
        if rgb is not None:
            # properties["single"] = rgb_to_hex(rgb)
            pass

        self._arlo.debug("{} sending {}".format(self._name, pprint.pformat(properties)))
        self._arlo.bg.run(self._arlo.be.notify,
                          base=self.base_station,
                          body={
                              'action': 'set',
                              'properties': properties,
                              'publishResponse': True,
                              'resource': self.resource_id,
                          })
        return True

    def turn_off(self):
        """ Turn the light off. """
        self._arlo.bg.run(self._arlo.be.notify,
                          base=self.base_station,
                          body={
                              'action': 'set',
                              'properties': {LAMP_STATE_KEY: 'off'},
                              'publishResponse': True,
                              'resource': self.resource_id,
                          })
        return True

    def set_brightness(self, brightness):
        """ Set the light brightness. """
        self._arlo.bg.run(self._arlo.be.notify,
                          base=self.base_station,
                          body={
                              'action': 'set',
                              'properties': {BRIGHTNESS_KEY: brightness},
                              'publishResponse': True,
                              'resource': self.resource_id,
                          })
        return True

    def has_capability(self, cap):
        """ Is the camera capabale of performing an activity. """
        if cap in (MOTION_DETECTED_KEY, BATTERY_KEY):
            return True
        return super().has_capability(cap)
