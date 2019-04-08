
import os
import logging
import time
import datetime
import base64
import pprint
import threading

from custom_components.aarlo.pyaarlo.background import ArloBackground
from custom_components.aarlo.pyaarlo.storage import ArloStorage
from custom_components.aarlo.pyaarlo.backend import ArloBackEnd
from custom_components.aarlo.pyaarlo.media import ArloMediaLibrary
from custom_components.aarlo.pyaarlo.base import ArloBase
from custom_components.aarlo.pyaarlo.camera import ArloCamera
from custom_components.aarlo.pyaarlo.doorbell import ArloDoorBell

from custom_components.aarlo.pyaarlo.constant import ( BLANK_IMAGE,
                                DEVICE_KEYS,
                                DEVICES_URL,
                                FAST_REFRESH_INTERVAL,
                                SLOW_REFRESH_INTERVAL,
                                TOTAL_BELLS_KEY,
                                TOTAL_CAMERAS_KEY )

_LOGGER = logging.getLogger('pyaarlo')

class PyArlo(object):

    def __init__( self,username,password,name='aarlo',
                        storage_dir='/config/.aarlo',dump=False,max_days=365,
                        db_motion_time=30,db_ding_time=10,
                        request_timeout=60,stream_timeout=0,
                        recent_time=600,last_format='%m-%d %H:%M',
                        no_media_upload=False,
                        user_agent='apple'):

        try:
            os.mkdir( storage_dir )
        except:
            pass

        self._name = name
        self._user_agent = user_agent
        self._bg   = ArloBackground( self )
        self._st   = ArloStorage( self,name=name,storage_dir=storage_dir )
        self._be   = ArloBackEnd( self,username,password,dump=dump,storage_dir=storage_dir,
                                        request_timeout=request_timeout,stream_timeout=stream_timeout )
        self._ml   = ArloMediaLibrary( self,max_days=max_days )

        self._lock = threading.Lock()
        self._bases       = []
        self._cameras     = []
        self._doorbells   = []
        self._recent_time = recent_time
        self._last_format = last_format
        self._no_media_upload = no_media_upload

        # on day flip we reload image count
        self._today = datetime.date.today()

        # default blank image whe waiting for camera image to appear
        self._blank_image = base64.standard_b64decode( BLANK_IMAGE )

        # slow piece.
        # get devices and fill local db, and create device instance
        self.info('pyaarlo starting')
        self._devices = self._be.get( DEVICES_URL )
        self._parse_devices()
        for device in self._devices:
            dname = device.get('deviceName')
            dtype = device.get('deviceType')
            if device.get('state','unknown') != 'provisioned':
                self.info('skipping ' + dname + ': state unknown')
                continue

            if dtype == 'basestation' or device.get('modelId') == 'ABC1000' or dtype == 'arloq' or dtype == 'arloqs':
                self._bases.append( ArloBase( dname,self,device ) )
            if dtype == 'camera' or dtype == 'arloq' or dtype == 'arloqs':
                self._cameras.append( ArloCamera( dname,self,device ) )
            if dtype == 'doorbell':
                self._doorbells.append( ArloDoorBell( dname,self,device,
                                            motion_time=db_motion_time,ding_time=db_ding_time ) )

        # save out unchanging stats!
        self._st.set( ['ARLO',TOTAL_CAMERAS_KEY],len(self._cameras) )
        self._st.set( ['ARLO',TOTAL_BELLS_KEY],len(self._doorbells) )

        # queue up initial config retrieval
        self.debug('getting initial settings' )
        self._bg.run_in( self._ml.load,1 )
        self._bg.run_in( self._refresh_cameras,2 )
        self._bg.run_in( self._fast_refresh,5 )
        self._bg.run_in( self._slow_refresh,10 )

        # register house keeping cron jobs
        self.debug('registering cron jobs')
        self._bg.run_every( self._fast_refresh,FAST_REFRESH_INTERVAL )
        self._bg.run_every( self._slow_refresh,SLOW_REFRESH_INTERVAL )

    def __repr__(self):
        # Representation string of object.
        return "<{0}: {1}>".format(self.__class__.__name__, self._name)

    def _parse_devices( self ):
        for device in self._devices:
            device_id = device.get('deviceId',None)
            if device_id is not None:
                for key in DEVICE_KEYS:
                    value = device.get(key,None)
                    if value is not None:
                        self._st.set( [device_id,key],value )

    def _refresh_cameras( self ):
        for camera in self._cameras:
            camera.update_last_image()
            camera.update_media()

    def _refresh_ambient_sensors( self ):
        for camera in self._cameras:
            camera.update_ambient_sensors()

    def _refresh_bases( self ):
        for base in self._bases:
            self._be.notify( base=base,body={"action":"get","resource":"modes","publishResponse":False} )
            self._be.notify( base=base,body={"action":"get","resource":"cameras","publishResponse":False} )
            self._be.notify( base=base,body={"action":"get","resource":"doorbells","publishResponse":False} )

    def _fast_refresh( self ):
        self.debug( 'fast refresh' )
        self._bg.run( self._st.save )

        # alway ping bases
        for base in self._bases:
            self._bg.run( self._be.async_ping,base=base )

        # if day changes then reload recording library and camera counts
        today = datetime.date.today()
        if self._today != today:
            self.debug( 'day changed!' )
            self._today = today
            self._bg.run( self._ml.load )
            self._bg.run( self._refresh_cameras )

    def _slow_refresh( self ):
        self.debug( 'slow refresh' )
        self._bg.run( self._refresh_bases )
        self._bg.run( self._refresh_ambient_sensors )

    def stop( self ):
        self._st.save()
        self._be.logout()

    @property
    def name( self ):
        return self._name

    @property
    def is_connected( self ):
        return self._be.is_connected()

    @property
    def cameras( self ):
        return self._cameras

    @property
    def doorbells( self ):
        return self._doorbells

    @property
    def base_stations( self ):
        return self._bases

    @property
    def blank_image( self ):
        return self._blank_image

    @property
    def recent_time( self ):
        return self._recent_time

    def lookup_camera_by_id( self,device_id ):
        camera = list(filter( lambda cam: cam.device_id == device_id, self.cameras ))
        if camera:
            return camera[0]
        return None

    def lookup_camera_by_name( self,name ):
        camera = list(filter( lambda cam: cam.name == name, self.cameras ))
        if camera:
            return camera[0]
        return None

    def lookup_doorbell_by_id( self,device_id ):
        doorbell = list(filter( lambda cam: cam.device_id == device_id, self.doorbells ))
        if doorbell:
            return doorbell[0]
        return None

    def lookup_doorbell_by_name( self,name ):
        doorbell = list(filter( lambda cam: cam.name == name, self.doorbells ))
        if doorbell:
            return doorbell[0]
        return None

    def attribute( self,attr ):
        return self._st.get( ['ARLO',attr],None )

    def add_attr_callback( self,attr,cb ):
        pass

    # needs thinking about... track new cameras for example..
    def update(self, update_cameras=False, update_base_station=False):
        pass

    def error( self,msg ):
        _LOGGER.error( msg  )

    def warning( self,msg ):
        _LOGGER.warning( msg  )

    def info( self,msg ):
        _LOGGER.info( msg  )

    def debug( self,msg ):
        _LOGGER.debug( msg  )

