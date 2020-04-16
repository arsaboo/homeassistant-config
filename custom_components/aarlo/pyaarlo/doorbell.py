from .device import ArloChildDevice


class ArloDoorBell(ArloChildDevice):

    def __init__(self, name, arlo, attrs):
        super().__init__(name, arlo, attrs)
        self._motion_time_job = None
        self._ding_time_job = None

    def _motion_stopped(self):
        self._save_and_do_callbacks('motionDetected', False)
        with self._lock:
            self._motion_time_job = None

    def _button_unpressed(self):
        self._save_and_do_callbacks('buttonPressed', False)
        with self._lock:
            self._ding_time_job = None

    def _event_handler(self, resource, event):
        self._arlo.debug(self.name + ' DOORBELL got one ' + resource)

        # create fake motion/button press event...
        if resource == self.resource_id:
            cons = event.get('properties', {}).get('connectionState', False)
            butp = event.get('properties', {}).get('buttonPressed', False)
            # acts = event.get('properties',{}).get('activityState',False)
            if cons and cons == 'available':
                self._save_and_do_callbacks('motionDetected', True)
                with self._lock:
                    self._arlo.bg.cancel(self._motion_time_job)
                    self._motion_time_job = self._arlo.bg.run_in(self._motion_stopped, self._arlo.cfg.db_motion_time)
            if butp:
                self._save_and_do_callbacks('buttonPressed', True)
                with self._lock:
                    self._arlo.bg.cancel(self._ding_time_job)
                    self._ding_time_job = self._arlo.bg.run_in(self._button_unpressed, self._arlo.cfg.db_ding_time)
            #  if acts and acts == 'idle':
            #  self._save_and_do_callbacks( 'motionDetected',False )
            #  self._save_and_do_callbacks( 'buttonPressed',False )

        # pass on to lower layer
        super()._event_handler(resource, event)

    @property
    def resource_type(self):
        return "doorbells"

    def has_capability(self, cap):
        if cap.startswith('button'):
            return True
        # video doorbell provides these as a camera type
        if not self.model_id.startswith('AVD1001'):
            if cap in 'motionDetected':
                return True
            if cap in ('battery_level', 'signal_strength'):
                return True
        return super().has_capability(cap)
