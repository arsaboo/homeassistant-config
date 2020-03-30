from .constant import MOTION_DETECTED_KEY, BUTTON_PRESSED_KEY, CONNECTION_KEY, BATTERY_KEY, SIGNAL_STR_KEY
from .device import ArloChildDevice


class ArloDoorBell(ArloChildDevice):

    def __init__(self, name, arlo, attrs):
        super().__init__(name, arlo, attrs)
        self._motion_time_job = None
        self._ding_time_job = None

    def _motion_stopped(self):
        self._save_and_do_callbacks(MOTION_DETECTED_KEY, False)
        with self._lock:
            self._motion_time_job = None

    def _button_unpressed(self):
        self._save_and_do_callbacks(BUTTON_PRESSED_KEY, False)
        with self._lock:
            self._ding_time_job = None

    def _event_handler(self, resource, event):
        self._arlo.debug(self.name + ' DOORBELL got one ' + resource)

        # create fake motion/button press event...
        if resource == self.resource_id:
            cons = event.get('properties', {}).get(CONNECTION_KEY, False)
            butp = event.get('properties', {}).get(BUTTON_PRESSED_KEY, False)
            # acts = event.get('properties',{}).get('activityState',False)
            if cons and cons == 'available':
                self._save_and_do_callbacks(MOTION_DETECTED_KEY, True)
                with self._lock:
                    self._arlo.bg.cancel(self._motion_time_job)
                    self._motion_time_job = self._arlo.bg.run_in(self._motion_stopped, self._arlo.cfg.db_motion_time)
            if butp:
                self._save_and_do_callbacks(BUTTON_PRESSED_KEY, True)
                with self._lock:
                    self._arlo.bg.cancel(self._ding_time_job)
                    self._ding_time_job = self._arlo.bg.run_in(self._button_unpressed, self._arlo.cfg.db_ding_time)
            #  if acts and acts == 'idle':
            #  self._save_and_do_callbacks( MOTION_DETECTED_KEY,False )
            #  self._save_and_do_callbacks( BUTTON_PRESSED_KEY,False )

        # pass on to lower layer
        super()._event_handler(resource, event)

    @property
    def resource_type(self):
        """ Return the resource type this object describes. """
        return "doorbells"

    def has_capability(self, cap):
        """ Is the camera capabale of performing an activity. """
        if cap in (BUTTON_PRESSED_KEY,):
            return True
        if cap in (MOTION_DETECTED_KEY, BATTERY_KEY, SIGNAL_STR_KEY):
            # video doorbell provides these as a camera type
            if self.model_id != 'AVD1001A':
                return True
        return super().has_capability(cap)
