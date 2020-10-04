from .constant import (MOTION_DETECTED_KEY, BUTTON_PRESSED_KEY, CONNECTION_KEY,
                       BATTERY_KEY, SIGNAL_STR_KEY, SILENT_MODE_KEY,
                       SILENT_MODE_CALL_KEY, SILENT_MODE_ACTIVE_KEY)
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

            silent_mode = event.get('properties', {}).get(SILENT_MODE_KEY, {})
            if silent_mode:
                self._save_and_do_callbacks(SILENT_MODE_KEY, silent_mode)

        # pass on to lower layer
        super()._event_handler(resource, event)

    @property
    def resource_type(self):
        return "doorbells"

    def has_capability(self, cap):
        if cap in (BUTTON_PRESSED_KEY, SILENT_MODE_KEY):
            return True
        if cap in (MOTION_DETECTED_KEY, BATTERY_KEY, SIGNAL_STR_KEY):
            # video doorbell provides these as a camera type
            if not self.model_id.startswith('AVD1001'):
                return True
        if cap in (CONNECTION_KEY,):
            # If video door bell is its own base station then don't provide connectivity here.
            if self.model_id.startswith('AVD1001') and self.parent_id == self.device_id:
                return False
        return super().has_capability(cap)

    def silent_mode(self, active, block_call):
      self._arlo.be.notify(base=self.base_station,
                           body={
                               'action': 'set',
                               'properties': {
                                   SILENT_MODE_KEY: {
                                      SILENT_MODE_ACTIVE_KEY: active,
                                      SILENT_MODE_CALL_KEY: block_call,
                                   },
                               },
                               'publishResponse': True,
                               'resource': self.resource_id,
                           })

    def update_silent_mode(self):
        """Requests the latest silent mode settings.

        Queues a job that requests the info from Arlo.
        """
        self._arlo.be.notify(base=self.base_station,
                             body={"action": "get",
                                   "resource": self.resource_id,
                                   "publishResponse": False})
