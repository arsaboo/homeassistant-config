
from custom_components.aarlo.pyaarlo.device import ArloDevice

from custom_components.aarlo.pyaarlo.util import ( time_to_arlotime )
from custom_components.aarlo.pyaarlo.constant import ( AUTOMATION_URL,
                                DEFAULT_MODES,
                                DEFINITIONS_URL,
                                MODES_KEY,
                                MODE_ID_TO_NAME_KEY,
                                MODE_KEY,
                                MODE_NAME_TO_ID_KEY,
                                MODE_IS_SCHEDULE_KEY,
                                SCHEDULE_KEY )

class ArloBase(ArloDevice):

    def __init__( self,name,arlo,attrs ):
        super().__init__( name,arlo,attrs )
        self._refresh_rate = 15

    def _id_to_name( self,mode_id ):
        return self._arlo._st.get( [self.device_id,MODE_ID_TO_NAME_KEY,mode_id],None )

    def _id_is_schedule( self,mode_id ):
        return self._arlo._st.get( [self.device_id,MODE_IS_SCHEDULE_KEY,mode_id],False )

    def _name_to_id( self,mode_name ):
        return self._arlo._st.get( [self.device_id,MODE_NAME_TO_ID_KEY,mode_name.lower()],None )

    def _parse_modes( self,modes ):
        for mode in modes:
            mode_id = mode.get( 'id',None )
            mode_name = mode.get( 'name','' )
            if mode_name == '':
                mode_name = mode.get( 'type','' )
                if mode_name == '':
                    mode_name = mode_id
            if mode_id and mode_name != '':
                self._arlo.debug( mode_id + '<=M=>' + mode_name )
                self._arlo._st.set( [self.device_id,MODE_ID_TO_NAME_KEY,mode_id],mode_name )
                self._arlo._st.set( [self.device_id,MODE_NAME_TO_ID_KEY,mode_name.lower()],mode_id )
                self._arlo._st.set( [self.device_id,MODE_IS_SCHEDULE_KEY,mode_name.lower()],False )

    def _parse_schedules( self,schedules ):
        for schedule in schedules:
            schedule_id = schedule.get( 'id',None )
            schedule_name = schedule.get( 'name','' )
            if schedule_name == '':
                schedule_name = schedule_id
            if schedule_id and schedule_name != '':
                self._arlo.debug( schedule_id + '<=S=>' + schedule_name )
                self._arlo._st.set( [self.device_id,MODE_ID_TO_NAME_KEY,schedule_id],schedule_name )
                self._arlo._st.set( [self.device_id,MODE_NAME_TO_ID_KEY,schedule_name.lower()],schedule_id )
                self._arlo._st.set( [self.device_id,MODE_IS_SCHEDULE_KEY,schedule_name.lower()],True )

    def _event_handler( self,resource,event ):
        self._arlo.debug( self.name + ' BASE got ' + resource )

        # modes on base station
        if resource == 'modes':
            props = event.get('properties',{})

            # list of modes - recheck?
            self._parse_modes( props.get('modes',[]) )

            # mode change?
            if 'activeMode' in props:
                self._save_and_do_callbacks( MODE_KEY,self._id_to_name(props['activeMode']) )
            elif 'active' in props:
                self._save_and_do_callbacks( MODE_KEY,self._id_to_name(props['active']) )

        # mode change?
        if resource == 'activeAutomations':

            # mode present? we just set to new ones...
            mode_ids = event.get( 'activeModes',[] )
            if mode_ids:
                self._arlo.debug( self.name + ' mode change ' + mode_ids[0] )
                mode_name = self._id_to_name( mode_ids[0] )
                self._save_and_do_callbacks( MODE_KEY,mode_name )

            # schedule on or off?
            schedule_ids = event.get( 'activeSchedules',[] )
            if schedule_ids:
                self._arlo.debug( self.name + ' schedule change ' + schedule_ids[0] )
                schedule_name = self._id_to_name( schedule_ids[0] )
                self._save_and_do_callbacks( SCHEDULE_KEY,schedule_name )
            else:
                self._arlo.debug( self.name + ' schedule cleared ' )
                self._save_and_do_callbacks( SCHEDULE_KEY,None )

    @property
    def _v1_modes(self):
        if self._arlo._mode_api.lower() == 'v1':
            self._arlo.debug( 'forced v1 api' )
            return True;
        if self._arlo._mode_api.lower() == 'v2':
            self._arlo.debug( 'forced v2 api' )
            return False;
        if self.model_id == 'ABC1000' or self.device_type == 'arloq' or self.device_type == 'arloqs':
            self._arlo.debug( 'deduced v1 api' )
            return True
        else:
            self._arlo.debug( 'deduced v2 api' )
            return False

    @property
    def available_modes(self):
        return list( self.available_modes_with_ids.keys() )

    @property
    def available_modes_with_ids(self):
        modes = {}
        for key,mode_id in self._arlo._st.get_matching( [self._device_id,MODE_NAME_TO_ID_KEY,'*'] ):
            modes[ key.split('/')[-1] ] = mode_id
        if not modes:
            modes = DEFAULT_MODES
        return modes

    @property
    def mode(self):
        return self._arlo._st.get( [self.device_id,MODE_KEY],'unknown' )

    @mode.setter
    def mode( self,mode_name ):
        mode_id = self._name_to_id( mode_name )
        if mode_id:

            # Schedule or mode? Manually set schedule key.
            if self._id_is_schedule( mode_id ):
                active = 'activeSchedules'
                inactive = 'activeModes'
                self._save_and_do_callbacks( SCHEDULE_KEY,mode_name )
            else:
                active = 'activeModes'
                inactive = 'activeSchedules'
                self._save_and_do_callbacks( SCHEDULE_KEY,None )

            # Post change.
            self._arlo.debug( self.name + ':new-mode=' + mode_name + ',id=' + mode_id )
            if self._v1_modes:
                self._arlo._bg.run( self._arlo._be.notify,base=self,
                                body={"action":"set",
                                        "resource":"modes",
                                        "publishResponse":True,
                                        "properties":{"active":mode_id}} )
            else:
                self._arlo._bg.run( self._arlo._be.post,url=AUTOMATION_URL,
                                params={'activeAutomations':
                                    [ {'deviceId':self.device_id,
                                        'timestamp':time_to_arlotime(),
                                        active:[mode_id],
                                        inactive:[] } ] } )
        else:
            self._arlo.warning( '{0}: mode {1} is unrecognised'.format( self.name,mode_name) )

    def update_mode( self ):
        data = self._arlo._be.get( AUTOMATION_URL )
        for mode in data:
            if mode.get('uniqueId','') == self.unique_id:
                active_modes = mode.get('activeModes',[])
                if active_modes:
                    self._save_and_do_callbacks( MODE_KEY,self._id_to_name(active_modes[0]) )
                active_schedules = mode.get('activeSchedules',[])
                if active_schedules:
                    self._save_and_do_callbacks( SCHEDULE_KEY,self._id_to_name(active_schedules[0]) )

    def update_modes( self ):
        if self._v1_modes:
            self._arlo._be.notify( base=self,body={"action":"get","resource":"modes","publishResponse":False} )
        else:
            modes = self._arlo._be.get( DEFINITIONS_URL + "?uniqueIds={}".format( self.unique_id ) )
            self._modes = modes.get( self.unique_id,{} )
            self._parse_modes( self._modes.get('modes',[]) )
            self._parse_schedules( self._modes.get('schedules',[]) )

    @property
    def schedule( self ):
        return self._arlo._st.get( [self.device_id,SCHEDULE_KEY],None )

    @property
    def on_schedule( self ):
        return self.schedule is not None

    @property
    def refresh_rate(self):
        return self._refresh_rate

    @refresh_rate.setter
    def refresh_rate(self, value):
        if isinstance(value, (int, float)):
            self._refresh_rate = value

    def has_capability( self,cap ):
        if cap in ('temperature', 'humidity', 'air_quality') and self.model_id == 'ABC1000':
            return True
        return super().has_capability( cap )

    def siren_on( self,duration=300,volume=8 ):
        body = {
            'action':'set',
            'resource':'siren',
            'publishResponse':True,
            'properties':{'sirenState':'on','duration':int(duration),'volume':int(volume),'pattern':'alarm'}
        }
        self._arlo.debug( str(body) )
        self._arlo._bg.run( self._arlo._be.notify,base=self,body=body )

    def siren_off( self ):
        body = {
            'action':'set',
            'resource':'siren',
            'publishResponse':True,
            'properties':{'sirenState':'off'}
        }
        self._arlo.debug( str(body) )
        self._arlo._bg.run( self._arlo._be.notify,base=self,body=body )

