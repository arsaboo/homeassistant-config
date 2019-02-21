
import pprint
from custom_components.aarlo.pyaarlo.device import ArloChildDevice

class ArloDoorBell(ArloChildDevice):

    def __init__( self,name,arlo,attrs,motion_time,ding_time ):
        super().__init__( name,arlo,attrs )
        self._mt     = motion_time
        self._mt_job = None
        self._dt     = ding_time
        self._dt_job = None

    def _motion_stopped( self ):
        self._save_and_do_callbacks( 'motionDetected',False )
        with self._lock:
            self._mt_job = None

    def _button_unpressed( self ):
        self._save_and_do_callbacks( 'buttonPressed',False )
        with self._lock:
            self._dt_job = None

    def _event_handler( self,resource,event ):
        self._arlo.debug( self.name + ' DOORBELL got one ' + resource )

        # create fake motion/button press event...
        if resource.startswith('doorbells/'):
            cons = event.get('properties',{}).get('connectionState',False)
            butp = event.get('properties',{}).get('buttonPressed',False)
            #acts = event.get('properties',{}).get('activityState',False)
            if cons and cons == 'available':
                self._save_and_do_callbacks( 'motionDetected',True )
                with self._lock:
                    self._arlo._bg.cancel( self._mt_job )
                    self._mt_job = self._arlo._bg.run_in( self._motion_stopped,self._mt )
            if butp:
                self._save_and_do_callbacks( 'buttonPressed',True )
                with self._lock:
                    self._arlo._bg.cancel( self._dt_job )
                    self._dt_job = self._arlo._bg.run_in( self._button_unpressed,self._dt )
            #  if acts and acts == 'idle':
                #  self._save_and_do_callbacks( 'motionDetected',False )
                #  self._save_and_do_callbacks( 'buttonPressed',False )

        # pass on to lower layer
        super()._event_handler( resource,event )

    @property
    def resource_id(self):
        return 'doorbells/' + self._device_id

    def has_capability( self,cap ):
        if cap.startswith( 'button' ):
            return True
        return super().has_capability( cap )

